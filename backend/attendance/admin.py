from django.contrib import admin
from .models import Attendance, DailyQR


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "date",
        "check_in",
        "check_out",
        "status",
        "overtime_minutes",
    )
    list_filter = ("status", "date")
    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
    )


@admin.register(DailyQR)
class DailyQRAdmin(admin.ModelAdmin):
    list_display = ("employee", "purpose", "date", "expires_at", "is_used")
    list_filter = ("purpose", "date", "is_used")
    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "token",
    )
