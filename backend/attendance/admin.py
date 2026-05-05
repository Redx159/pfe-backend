from django.contrib import admin
from .models import CheckInOut

@admin.register(CheckInOut)
class CheckInOutAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'checkin_time', 'checkout_time', 'status')
    list_filter = ('status', 'date', 'anomaly_detected')
    search_fields = ('employee__employee_id', 'employee__first_name', 'employee__last_name')