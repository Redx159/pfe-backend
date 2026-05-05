from django.utils import timezone
from django.contrib.auth import get_user_model
from employees.models import Department

User = get_user_model()

def set_if_has(obj, field, value):
    if hasattr(obj, field):
        setattr(obj, field, value)

# 1) Fix ANY existing users with employee_id NULL/empty (this includes admin)
bad_qs = User.objects.filter(employee_id__isnull=True) | User.objects.filter(employee_id="")
bad_list = list(bad_qs)
for u in bad_list:
    # must be unique + non-empty
    u.employee_id = f"AUTO-{u.id:04d}"
    u.save(update_fields=["employee_id"])

print("Fixed bad employee_id rows:", len(bad_list))

# 2) Department
dept, _ = Department.objects.get_or_create(
    id=1,
    defaults={"name": "IT", "description": "Department IT"},
)

def upsert_user(
    username,
    employee_id,
    email,
    first_name,
    last_name,
    role_value,
    position_value,
    is_staff,
):
    # Ensure employee_id is present at creation time (avoid UNIQUE constraint error on empty employee_id)
    u, created = User.objects.update_or_create(
        username=username,
        defaults={
            "employee_id": employee_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "is_staff": is_staff,
            "is_active": True,
        },
    )

    # Required in your DB: position is NOT NULL (your screenshot error)
    set_if_has(u, "position", position_value)
    set_if_has(u, "role", role_value)
    set_if_has(u, "department_id", dept.id)

    # Some projects have date_joined already set, but keep safe
    if hasattr(u, "date_joined") and not u.date_joined:
        u.date_joined = timezone.now()

    # all passwords => password123
    u.set_password("password123")
    u.save()

    print(("CREATED" if created else "UPDATED"), username, "| employee_id:", getattr(u, "employee_id", None))
    return u

# 3) Create/update manager + employee
manager = upsert_user(
    username="manager",
    employee_id="EMP-0002",
    email="manager@test.com",
    first_name="Manager",
    last_name="Boss",
    role_value="MANAGER",
    position_value="Manager",
    is_staff=True,
)

employee = upsert_user(
    username="employee",
    employee_id="EMP-0003",
    email="tester@test.com",
    first_name="Test",
    last_name="Employee",
    role_value="EMPLOYEE",
    position_value="Employee",
    is_staff=False,
)

# 4) Link employee -> manager (only if your model has manager_id)
if hasattr(employee, "manager_id"):
    if employee.manager_id != manager.id:
        employee.manager_id = manager.id
        employee.save(update_fields=["manager_id"])
        print("Linked employee -> manager:", manager.username)

print("DONE ✅")
print("LOGIN:")
print("manager / password123")
print("employee / password123")
