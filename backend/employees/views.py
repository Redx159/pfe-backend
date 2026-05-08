import csv
from datetime import datetime, timedelta

from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from attendance.models import Attendance
from leaves.models import LeaveRequest
from meetings.models import Meeting

from .permissions import IsAdminOrHR

from .serializers import (
    EmployeeSerializer,
    LoginSerializer,
    RegisterSerializer,
    DepartmentSerializer,
    EmployeeTokenObtainPairSerializer,
)
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import IsAdminUser
from .models import Employee, Department


def get_scope_employees(user):
    if user.role in ("ADMIN", "HR"):
        return Employee.objects.all()

    if user.role == "MANAGER":
        return Employee.objects.filter(Q(id=user.id) | Q(manager=user)).distinct()

    return Employee.objects.filter(id=user.id)


def serialize_employee_brief(employee):
    return {
        "id": employee.id,
        "name": employee.get_full_name() or employee.username,
        "role": employee.role,
        "department": employee.department.name if employee.department else None,
        "position": employee.position,
    }


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            user_data = EmployeeSerializer(user).data

            return Response({
                'success': True,
                'message': 'Login successful',
                'user': user_data,
                'tokens': {
                    'refresh': serializer.validated_data['refresh'],
                    'access': serializer.validated_data['access']
                }
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ============================
# SIGNUP VIEW (NEW)
# ============================

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'success': True,
                    'message': 'Account created. Waiting for admin approval.'
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                'success': False,
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmployeeTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmployeeTokenObtainPairSerializer


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({
            'success': True,
            'message': 'Logout successful'
        })


class ApproveUserView(APIView):
    """Admin-only endpoint to approve (activate) a user account."""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(Employee, pk=pk)

        if user.is_active:
            return Response({'success': False, 'message': 'User already active.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        # send a simple notification email (uses configured EMAIL_BACKEND)
        if user.email:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or 'noreply@example.com'
            try:
                # Do not fail silently here — surface errors so caller can know if send failed
                send_mail(
                    'Your account has been approved',
                    'Hello,\n\nYour account has been approved by an administrator. You can now log in.',
                    from_email,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as exc:
                # Roll back activation if email couldn't be delivered (optional safety)
                user.is_active = False
                user.save()
                return Response({'success': False, 'message': 'Failed to send approval email', 'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': True, 'message': 'User approved', 'user': EmployeeSerializer(user).data})
   
class EmployeeListView(generics.ListAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_scope_employees(self.request.user)


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_scope_employees(self.request.user)


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()
        start_date = today - timedelta(days=6)

        scoped_employees = get_scope_employees(user)
        scoped_employee_ids = list(scoped_employees.values_list("id", flat=True))

        attendance_qs = Attendance.objects.filter(employee_id__in=scoped_employee_ids)
        leaves_qs = LeaveRequest.objects.filter(employee_id__in=scoped_employee_ids)
        meetings_qs = Meeting.objects.filter(
            Q(created_by_id__in=scoped_employee_ids)
            | Q(participants__employee_id__in=scoped_employee_ids)
        ).distinct()

        today_attendance = attendance_qs.filter(date=today)
        pending_leaves_qs = leaves_qs.filter(status="PENDING")
        upcoming_leaves_qs = leaves_qs.filter(
            status__in=["PENDING", "APPROVED"],
            end_date__gte=today,
        ).select_related("employee").order_by("start_date", "employee__first_name")[:8]
        upcoming_meetings_qs = meetings_qs.filter(
            start_time__date__gte=today,
        ).select_related("created_by").order_by("start_time")[:6]
        recent_attendance_qs = attendance_qs.select_related("employee").order_by("-date")[:8]

        trend_rows = (
            attendance_qs.filter(date__gte=start_date, date__lte=today)
            .values("date")
            .annotate(
                on_time=Count("id", filter=Q(status="ON_TIME")),
                late=Count("id", filter=Q(status="LATE")),
                absent=Count("id", filter=Q(status="ABSENT")),
            )
            .order_by("date")
        )
        trend_map = {row["date"]: row for row in trend_rows}
        attendance_trend = []
        for offset in range(7):
            day = start_date + timedelta(days=offset)
            row = trend_map.get(day, {})
            attendance_trend.append(
                {
                    "date": day.isoformat(),
                    "on_time": row.get("on_time", 0),
                    "late": row.get("late", 0),
                    "absent": row.get("absent", 0),
                }
            )

        department_rows = (
            scoped_employees.values("department__name")
            .annotate(total=Count("id"))
            .order_by("-total", "department__name")
        )

        data = {
            "scope": "company" if user.role in ("ADMIN", "HR") else "team",
            "totals": {
                "employees": scoped_employees.count(),
                "active_accounts": scoped_employees.filter(is_active=True).count(),
                "pending_leaves": pending_leaves_qs.count(),
                "approved_leaves": leaves_qs.filter(status="APPROVED").count(),
                "meetings": meetings_qs.count(),
                "today_present": today_attendance.filter(status="ON_TIME").count(),
                "today_late": today_attendance.filter(status="LATE").count(),
                "today_absent": today_attendance.filter(status="ABSENT").count(),
            },
            "attendance_today": {
                "on_time": today_attendance.filter(status="ON_TIME").count(),
                "late": today_attendance.filter(status="LATE").count(),
                "absent": today_attendance.filter(status="ABSENT").count(),
            },
            "attendance_trend": attendance_trend,
            "departments": [
                {
                    "department": row["department__name"] or "Unassigned",
                    "total": row["total"],
                }
                for row in department_rows
            ],
            "pending_leaves": [
                {
                    "id": leave.id,
                    "employee_name": leave.employee.get_full_name() or leave.employee.username,
                    "leave_type": leave.leave_type,
                    "start_date": leave.start_date.isoformat(),
                    "end_date": leave.end_date.isoformat(),
                    "status": leave.status,
                }
                for leave in pending_leaves_qs.select_related("employee").order_by("start_date")[:6]
            ],
            "upcoming_leaves": [
                {
                    "id": leave.id,
                    "employee_name": leave.employee.get_full_name() or leave.employee.username,
                    "leave_type": leave.leave_type,
                    "start_date": leave.start_date.isoformat(),
                    "end_date": leave.end_date.isoformat(),
                    "status": leave.status,
                }
                for leave in upcoming_leaves_qs
            ],
            "upcoming_meetings": [
                {
                    "id": meeting.id,
                    "title": meeting.title,
                    "start_time": meeting.start_time.isoformat(),
                    "end_time": meeting.end_time.isoformat(),
                    "is_cancelled": meeting.is_cancelled,
                    "created_by": meeting.created_by.get_full_name() or meeting.created_by.username,
                }
                for meeting in upcoming_meetings_qs
            ],
            "recent_attendance": [
                {
                    "id": record.id,
                    "employee_name": record.employee.get_full_name() or record.employee.username,
                    "date": record.date.isoformat(),
                    "status": record.status,
                    "check_in": record.check_in.isoformat() if record.check_in else None,
                    "check_out": record.check_out.isoformat() if record.check_out else None,
                }
                for record in recent_attendance_qs
            ],
            "team_members": [
                serialize_employee_brief(employee)
                for employee in scoped_employees.select_related("department").order_by(
                    "first_name", "last_name"
                )[:8]
            ],
        }

        return Response(data)


class DashboardMonthlyReportExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        month = request.query_params.get("month")

        if month:
            year, month_num = month.split("-")
            start_date = datetime(int(year), int(month_num), 1).date()
        else:
            today = timezone.localdate()
            start_date = today.replace(day=1)

        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1)

        scoped_employees = get_scope_employees(user)
        scoped_employee_ids = list(scoped_employees.values_list("id", flat=True))

        attendance_qs = Attendance.objects.filter(
            employee_id__in=scoped_employee_ids,
            date__gte=start_date,
            date__lt=end_date,
        )
        leaves_qs = LeaveRequest.objects.filter(
            employee_id__in=scoped_employee_ids,
            start_date__lt=end_date,
            end_date__gte=start_date,
        )
        meetings_qs = Meeting.objects.filter(
            Q(created_by_id__in=scoped_employee_ids)
            | Q(participants__employee_id__in=scoped_employee_ids),
            start_time__date__gte=start_date,
            start_time__date__lt=end_date,
        ).distinct()

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="monthly-dashboard-report-{start_date.strftime("%Y-%m")}.csv"'
        )
        writer = csv.writer(response)

        writer.writerow(["Monthly Dashboard Report"])
        writer.writerow(["Scope", "company" if user.role in ("ADMIN", "HR") else "team"])
        writer.writerow(["Month", start_date.strftime("%Y-%m")])
        writer.writerow([])

        writer.writerow(["Summary"])
        writer.writerow(["Employees", scoped_employees.count()])
        writer.writerow(["Attendance Records", attendance_qs.count()])
        writer.writerow(["On Time", attendance_qs.filter(status="ON_TIME").count()])
        writer.writerow(["Late", attendance_qs.filter(status="LATE").count()])
        writer.writerow(["Absent", attendance_qs.filter(status="ABSENT").count()])
        writer.writerow(["Leave Requests", leaves_qs.count()])
        writer.writerow(["Pending Leaves", leaves_qs.filter(status="PENDING").count()])
        writer.writerow(["Approved Leaves", leaves_qs.filter(status="APPROVED").count()])
        writer.writerow(["Meetings", meetings_qs.count()])
        writer.writerow([])

        writer.writerow(["Employees by Department"])
        writer.writerow(["Department", "Total"])
        for row in (
            scoped_employees.values("department__name")
            .annotate(total=Count("id"))
            .order_by("-total", "department__name")
        ):
            writer.writerow([row["department__name"] or "Unassigned", row["total"]])
        writer.writerow([])

        writer.writerow(["Attendance Detail"])
        writer.writerow(["Employee", "Date", "Status", "Check In", "Check Out"])
        for item in attendance_qs.select_related("employee").order_by("date", "employee__first_name"):
            writer.writerow(
                [
                    item.employee.get_full_name() or item.employee.username,
                    item.date.isoformat(),
                    item.status,
                    item.check_in.isoformat() if item.check_in else "",
                    item.check_out.isoformat() if item.check_out else "",
                ]
            )

        return response





class ApproveUserView(APIView):

    permission_classes = [IsAdminOrHR]

    def post(self, request, pk):

        user = get_object_or_404(Employee, pk=pk)

        if user.is_active:
            return Response(
                {"success": False, "message": "User already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()

        return Response({
            "success": True,
            "message": "User approved",
            "user": EmployeeSerializer(user).data,
        })
