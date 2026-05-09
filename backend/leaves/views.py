import csv

from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from .utils import get_annual_history, get_projections, count_workdays
from backend.cache_utils import cache_response


def _restore_balance(leave):
    employee = leave.employee
    days = leave.duration_days
    if leave.leave_type == "CP":
        employee.cp_balance += days
    elif leave.leave_type == "RTT":
        employee.rtt_balance += days
    employee.save()


class LeaveRequestViewSet(viewsets.ModelViewSet):

    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = [
        'get', 'post', 'put', 'patch', 'delete', 'head', 'options',
    ]

    @cache_response()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.role in ('ADMIN', 'HR'):
            return LeaveRequest.objects.all()
        if user.role == 'MANAGER':
            return (
                LeaveRequest.objects.filter(employee__manager=user)
                | LeaveRequest.objects.filter(employee=user)
            )
        return LeaveRequest.objects.filter(employee=user)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def perform_destroy(self, instance):
        if instance.status == "APPROVED":
            _restore_balance(instance)
        instance.delete()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()

        if request.user.role not in ('ADMIN', 'HR', 'MANAGER'):
            return Response({'error': 'Permission denied'}, status=403)

        if leave.status != 'PENDING':
            return Response({'error': 'Only pending leaves can be approved'}, status=400)

        comment = request.data.get('manager_comment')
        if not comment:
            return Response({'error': 'Manager comment is required'}, status=400)

        employee = leave.employee
        days = leave.duration_days

        if leave.leave_type == "CP":
            if employee.cp_balance < days:
                return Response({"error": "Not enough CP balance"}, status=400)
            employee.cp_balance -= days
        elif leave.leave_type == "RTT":
            if employee.rtt_balance < days:
                return Response({"error": "Not enough RTT balance"}, status=400)
            employee.rtt_balance -= days

        employee.save()

        leave.status = 'APPROVED'
        leave.manager_comment = comment
        leave.save()

        return Response({'success': True, 'data': LeaveRequestSerializer(leave).data})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()

        if request.user.role not in ('ADMIN', 'HR', 'MANAGER'):
            return Response({'error': 'Permission denied'}, status=403)

        if leave.status != 'PENDING':
            return Response({'error': 'Only pending leaves can be rejected'}, status=400)

        comment = request.data.get('manager_comment')
        if not comment:
            return Response({'error': 'Manager comment is required'}, status=400)

        leave.status = 'REJECTED'
        leave.manager_comment = comment
        leave.save()

        return Response({'success': True, 'data': LeaveRequestSerializer(leave).data})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        leave = self.get_object()

        if leave.employee != request.user:
            return Response({'error': 'You can only cancel your own leave requests'}, status=403)

        if leave.status not in ('PENDING', 'APPROVED'):
            return Response({'error': 'Only pending or approved leaves can be cancelled'}, status=400)

        if leave.status == "APPROVED":
            _restore_balance(leave)

        leave.status = 'CANCELLED'
        leave.save()

        return Response({'success': True, 'data': LeaveRequestSerializer(leave).data})

    @action(detail=False, methods=['get'])
    @cache_response()
    def pending(self, request):
        queryset = self.get_queryset().filter(status='PENDING')
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    @cache_response()
    def approved(self, request):
        queryset = self.get_queryset().filter(status='APPROVED')
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    @cache_response()
    def history(self, request):
        year = request.query_params.get("year")
        if year:
            year = int(year)
        else:
            from datetime import date
            year = date.today().year
        data = get_annual_history(request.user, year)
        return Response(data)

    @action(detail=False, methods=['get'])
    @cache_response()
    def projections(self, request):
        data = get_projections(request.user)
        return Response(data)

    @action(detail=False, methods=['get'])
    def export(self, request):
        status_filter = request.query_params.get("status")
        month = request.query_params.get("month")

        queryset = self.get_queryset().select_related("employee").order_by("-start_date")

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if month:
            queryset = queryset.filter(start_date__startswith=month)

        response = HttpResponse(content_type="text/csv")
        suffix = month or "all"
        response["Content-Disposition"] = f'attachment; filename="leave-report-{suffix}.csv"'

        writer = csv.writer(response)
        writer.writerow(["Employee", "Leave Type", "Status", "Start Date", "End Date", "Duration Days", "Reason", "Manager Comment"])

        for leave in queryset:
            writer.writerow([
                leave.employee.get_full_name() or leave.employee.username,
                leave.leave_type, leave.status,
                leave.start_date.isoformat(), leave.end_date.isoformat(),
                leave.duration_days, leave.reason, leave.manager_comment,
            ])

        return response
