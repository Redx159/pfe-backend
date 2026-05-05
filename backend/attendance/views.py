import csv
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsHRAdminOrManager
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

from .models import Attendance, DailyQR
from .serializers import AttendanceSerializer


QR_EXPIRY_MINUTES = 10


# Generate a short-lived QR for check-in
class GenerateCheckInQR(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        qr = DailyQR.objects.create(
            employee=request.user,
            date=timezone.localdate(),
            expires_at=timezone.now() + timedelta(minutes=QR_EXPIRY_MINUTES),
            purpose="CHECK_IN",
        )

        return Response({
            "token": str(qr.token),
            "purpose": qr.purpose,
            "expires_at": qr.expires_at,
        })


# Generate a short-lived QR for check-out
class GenerateCheckOutQR(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        qr = DailyQR.objects.create(
            employee=request.user,
            date=timezone.localdate(),
            expires_at=timezone.now() + timedelta(minutes=QR_EXPIRY_MINUTES),
            purpose="CHECK_OUT",
        )

        return Response({
            "token": str(qr.token),
            "purpose": qr.purpose,
            "expires_at": qr.expires_at,
        })


# Scan a QR token and perform check-in or check-out
class ScanQRView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        try:
            qr = DailyQR.objects.get(token=token)
        except DailyQR.DoesNotExist:
            return Response({"error": "Invalid QR"}, status=400)

        if not qr.is_valid():
            return Response({"error": "Expired or used QR"}, status=400)

        now = timezone.now()
        today = timezone.localdate()

        if qr.date != today:
            return Response({"error": "QR is not valid for today"}, status=400)

        attendance, _ = Attendance.objects.get_or_create(
            employee=qr.employee,
            date=today,
        )

        # CHECK IN
        if qr.purpose == "CHECK_IN":
            if attendance.check_in:
                return Response({"error": "Already checked in"}, status=400)

            status_val = "ON_TIME"
            if now.hour >= 9:
                status_val = "LATE"

            attendance.check_in = now
            attendance.status = status_val
            attendance.save()

        # CHECK OUT
        elif qr.purpose == "CHECK_OUT":

            if not attendance.check_in:
                return Response(
                    {"error": "Must check in first"},
                    status=400,
                )

            if attendance.check_out:
                return Response(
                    {"error": "Already checked out"},
                    status=400,
                )

            attendance.check_out = now

            duration = attendance.check_out - attendance.check_in
            attendance.work_duration = duration

            worked_minutes = int(duration.total_seconds() / 60)

            overtime = max(0, worked_minutes - 480)   # 8h = 480min

            attendance.overtime_minutes = overtime

            attendance.save()

            # ===========================
            # ADD RTT IF PASSED THRESHOLD
            # ===========================

            if overtime >= 480:
                employee = attendance.employee
                employee.rtt_balance += 1
                employee.save()

        qr.is_used = True
        qr.save(update_fields=["is_used"])


        return Response({
            "message": "Scan successful",
            "purpose": qr.purpose,
            "check_in": attendance.check_in,
            "check_out": attendance.check_out,
            "duration": str(attendance.work_duration),
        })


# Employee personal history
class MyAttendance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Attendance.objects.filter(employee=request.user).order_by("-date")
        return Response(AttendanceSerializer(qs, many=True).data)


# Admin monitoring
class AllAttendance(APIView):
    permission_classes = [IsHRAdminOrManager]

    def get(self, request):
        qs = Attendance.objects.select_related("employee").order_by("-date")
        return Response(AttendanceSerializer(qs, many=True).data)


class ExportAttendanceCSV(APIView):
    permission_classes = [IsHRAdminOrManager]

    def get(self, request):
        month = request.query_params.get("month")
        status_filter = request.query_params.get("status")

        qs = Attendance.objects.select_related("employee").order_by("-date")

        if month:
            qs = qs.filter(date__startswith=month)

        if status_filter:
            qs = qs.filter(status=status_filter)

        response = HttpResponse(content_type="text/csv")
        suffix = month or timezone.localdate().strftime("%Y-%m")
        response["Content-Disposition"] = f'attachment; filename="attendance-report-{suffix}.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Employee",
                "Date",
                "Status",
                "Check In",
                "Check Out",
                "Work Duration",
                "Overtime Minutes",
            ]
        )

        for item in qs:
            writer.writerow(
                [
                    item.employee.get_full_name() or item.employee.username,
                    item.date.isoformat(),
                    item.status,
                    item.check_in.isoformat() if item.check_in else "",
                    item.check_out.isoformat() if item.check_out else "",
                    str(item.work_duration) if item.work_duration else "",
                    item.overtime_minutes,
                ]
            )

        return response


# Backwards-compatible alias for older imports
class GenerateDailyQR(GenerateCheckInQR):
    pass
