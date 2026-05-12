from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Employee(AbstractUser):
    # Champs hérités : username, email, first_name, last_name, password, etc.
    
    # Champs supplémentaires
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100)
    hire_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    photo_url = models.URLField(blank=True)
    
    # Soldes de congés
    cp_balance = models.IntegerField(default=25)  # Congés payés
    rtt_balance = models.IntegerField(default=10)  # RTT
    
    # Manager hiérarchique
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    
    # Rôle
    ROLE_CHOICES = [
        ('EMPLOYEE', 'Employé'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Administrateur'),
        ('HR', 'RH'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    
    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()

        if name:
            return f"{name} — {self.employee_id}"

        return self.username
