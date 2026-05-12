from employees.serializers import EmployeeSerializer
from leaves.models import LeaveRequest
from rest_framework import serializers


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    attachment_url = serializers.SerializerMethodField()

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

    def get_attachment_url(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
            return obj.attachment.url
        return None
