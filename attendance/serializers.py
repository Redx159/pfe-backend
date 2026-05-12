from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(
        source="employee.get_full_name",
        read_only=True,
    )

    check_in_time = serializers.SerializerMethodField()
    check_out_time = serializers.SerializerMethodField()
    work_duration_str = serializers.SerializerMethodField()
    overtime_minutes = serializers.IntegerField(read_only=True)


    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee_name",
            "date",
            "status",
            "check_in_time",
            "check_out_time",
            "work_duration_str",
            "overtime_minutes",
        ]

    def get_check_in_time(self, obj):
        if obj.check_in:
            return obj.check_in.strftime("%H:%M")
        return None

    def get_check_out_time(self, obj):
        if obj.check_out:
            return obj.check_out.strftime("%H:%M")
        return None

    def get_work_duration_str(self, obj):
        duration = obj.work_duration
        if not duration and obj.check_in and obj.check_out:
            duration = obj.check_out - obj.check_in
        if duration:
            total = int(duration.total_seconds())
            h = total // 3600
            m = (total % 3600) // 60
            return f"{h:02d}:{m:02d}"
        return None
