from employees.serializers import EmployeeSerializer
from leaves.models import LeaveRequest
from rest_framework import serializers


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = "__all__"
        read_only_fields = [
            'id',
            'employee',
            'status',
            'created_at',
            'updated_at',
            'duration_days',
        ]
