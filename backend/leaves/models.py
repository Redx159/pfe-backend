from django.db import models
from employees.models import Employee

class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    
    LEAVE_TYPES = [
        ('CP', 'Congés Payés'),
        ('RTT', 'RTT'),
        ('SICK', 'Maladie'),
        ('TRAINING', 'Formation'),
        ('UNPAID', 'Sans solde'),
        ('MATERNITY', 'Maternité'),
        ('PATERNITY', 'Paternité'),
    ]
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Refusé'),
        ('CANCELLED', 'Annulé'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    reason = models.TextField(blank=True)
    manager_comment = models.TextField(blank=True)
    attachment = models.FileField(upload_to='leave_attachments/', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1