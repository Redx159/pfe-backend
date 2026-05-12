from django.contrib import admin
from django.utils.html import format_html

from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):

    # ===============================
    # LIST VIEW
    # ===============================

    list_display = (
    'id',
    'employee',
    'leave_type',
    'start_date',
    'end_date',
    'reason',
    'colored_status',
    'created_at',
)


    list_filter = ('status', 'leave_type')

    search_fields = (
        'employee__username',
        'employee__first_name',
        'employee__last_name',
    )

    # ===============================
    # DETAIL PAGE
    # ===============================

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (
        (
            "Employee",
            {
                "fields": ("employee",),
            },
        ),
        (
            "Leave Information",
            {
                "fields": (
                    "leave_type",
                    "start_date",
                    "end_date",
                    "reason",
                    "status",
                    "manager_comment",
                ),
            },
        ),
    )

    # ===============================
    # BULK ACTIONS
    # ===============================

    actions = ['approve_leaves', 'reject_leaves']

    def approve_leaves(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='APPROVED')
        self.message_user(request, f"Successfully approved {updated} leaves.")

    approve_leaves.short_description = "Approve selected leaves"

    def reject_leaves(self, request, queryset):
        for leave in queryset:

            if leave.status != 'PENDING':
                continue

            if not leave.manager_comment:
                self.message_user(
                    request,
                    f"Leave {leave.id} has no manager comment. Rejection skipped.",
                    level="error",
                )
                continue

            leave.status = 'REJECTED'
            leave.save()

        self.message_user(request, "Rejection finished.")

    # ===============================
    # COLORED STATUS
    # ===============================

    def colored_status(self, obj):

        colors = {
            'APPROVED': 'green',
            'REJECTED': 'red',
            'PENDING': 'orange',
            'CANCELLED': 'gray',
        }

        return format_html(
            '<b style="color:{};">{}</b>',
            colors.get(obj.status, 'black'),
            obj.status,
        )

    colored_status.short_description = "Status"
