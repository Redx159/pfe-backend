from django.contrib import admin, messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Department

class EmployeeAdmin(UserAdmin):
    list_display = ('employee_id', 'email', 'first_name', 'last_name', 'position', 'department', 'role', 'is_active')
    list_filter = ('role', 'department', 'is_active')
    search_fields = ('employee_id', 'email', 'first_name', 'last_name')
    actions = ['approve_users']

    fieldsets = UserAdmin.fieldsets + (
        ('Informations professionnelles', {
            'fields': ('employee_id', 'department', 'position', 'hire_date', 'phone_number', 'photo_url', 'manager', 'role')
        }),
        ('Soldes de congés', {
            'fields': ('cp_balance', 'rtt_balance')
        }),
    )

    def approve_users(self, request, queryset):
        """Admin action to activate selected user accounts and send notification emails."""
        success = 0
        failures = []

        for user in queryset:
            if user.is_active:
                continue
            user.is_active = True
            user.save()

            if user.email:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or 'noreply@example.com'
                try:
                    send_mail(
                        'Your account has been approved',
                        'Hello,\n\nYour account has been approved by an administrator. You can now log in.',
                        from_email,
                        [user.email],
                        fail_silently=False,
                    )
                    success += 1
                except Exception as exc:
                    # revert activation on send failure
                    user.is_active = False
                    user.save()
                    failures.append((user.pk, str(exc)))
            else:
                # no email address — count as success of activation but note missing email
                success += 1

        if success:
            messages.success(request, f"{success} users activated and notified (if email present).")
        if failures:
            messages.error(request, f"{len(failures)} users failed to be notified: {failures}")
    approve_users.short_description = 'Approve selected users'

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department)
