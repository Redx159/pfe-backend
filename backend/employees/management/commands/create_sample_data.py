from django.core.management.base import BaseCommand
from employees.models import Department, Employee
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create departments
        dept_it = Department.objects.get_or_create(
            name='IT',
            defaults={'description': 'Information Technology'}
        )[0]
        
        dept_hr = Department.objects.get_or_create(
            name='HR',
            defaults={'description': 'Human Resources'}
        )[0]
        
        dept_sales = Department.objects.get_or_create(
            name='Sales',
            defaults={'description': 'Sales'}
        )[0]
        
        # Create admin user
        admin_user = Employee.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@company.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'employee_id': 'EMP001',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'password': make_password('admin123'),
            }
        )[0]
        
        # Create HR user
        hr_user = Employee.objects.get_or_create(
            username='hr_manager',
            defaults={
                'email': 'hr@company.com',
                'first_name': 'HR',
                'last_name': 'Manager',
                'employee_id': 'EMP002',
                'department': dept_hr,
                'position': 'HR Manager',
                'role': 'HR',
                'password': make_password('hr123'),
            }
        )[0]
        
        # Create manager
        manager = Employee.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@company.com',
                'first_name': 'John',
                'last_name': 'Manager',
                'employee_id': 'EMP003',
                'department': dept_it,
                'position': 'IT Manager',
                'role': 'MANAGER',
                'password': make_password('manager123'),
            }
        )[0]
        
        # Create regular employees
        emp1 = Employee.objects.get_or_create(
            username='employee1',
            defaults={
                'email': 'emp1@company.com',
                'first_name': 'Alice',
                'last_name': 'Developer',
                'employee_id': 'EMP004',
                'department': dept_it,
                'position': 'Software Developer',
                'manager': manager,
                'role': 'EMPLOYEE',
                'password': make_password('emp123'),
            }
        )[0]
        
        emp2 = Employee.objects.get_or_create(
            username='employee2',
            defaults={
                'email': 'emp2@company.com',
                'first_name': 'Bob',
                'last_name': 'Sales',
                'employee_id': 'EMP005',
                'department': dept_sales,
                'position': 'Sales Representative',
                'manager': manager,
                'role': 'EMPLOYEE',
                'password': make_password('emp123'),
            }
        )[0]
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created sample data:\n'
                '- Admin: admin / admin123\n'
                '- HR Manager: hr_manager / hr123\n'
                '- Manager: manager / manager123\n'
                '- Employee 1: employee1 / emp123\n'
                '- Employee 2: employee2 / emp123'
            )
        )
