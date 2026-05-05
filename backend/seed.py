from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from attendance.models import Attendance
from employees.models import Department
from leaves.models import LeaveRequest
from meetings.models import Meeting, MeetingParticipant

User = get_user_model()


def set_if_has(obj, field, value):
    if hasattr(obj, field):
        setattr(obj, field, value)


def aware_datetime(days_offset, hour, minute=0):
    naive = datetime.combine(
        timezone.localdate() + timedelta(days=days_offset),
        time(hour, minute),
    )
    return timezone.make_aware(naive)


def upsert_user(
    username,
    employee_id,
    email,
    first_name,
    last_name,
    role_value,
    position_value,
    department,
    is_staff=False,
    is_superuser=False,
    manager=None,
    password="password123",
):
    user, created = User.objects.update_or_create(
        username=username,
        defaults={
            "employee_id": employee_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "is_staff": is_staff,
            "is_superuser": is_superuser,
            "is_active": True,
        },
    )

    set_if_has(user, "position", position_value)
    set_if_has(user, "role", role_value)
    set_if_has(user, "department", department)
    set_if_has(user, "manager", manager)

    if hasattr(user, "date_joined") and not user.date_joined:
        user.date_joined = timezone.now()

    if hasattr(user, "hire_date") and not user.hire_date:
        user.hire_date = timezone.localdate() - timedelta(days=365)

    user.set_password(password)
    user.save()

    print(
        ("CREATED" if created else "UPDATED"),
        username,
        "| role:",
        getattr(user, "role", None),
    )
    return user


def seed_attendance(employees):
    today = timezone.localdate()
    patterns = [
        (-4, "ON_TIME", (8, 55), (17, 10)),
        (-3, "LATE", (9, 20), (18, 0)),
        (-2, "ON_TIME", (8, 45), (17, 45)),
        (-1, "ON_TIME", (8, 50), (16, 55)),
        (0, "ON_TIME", (8, 40), None),
    ]

    for index, employee in enumerate(employees):
        for day_offset, status_value, check_in_tuple, check_out_tuple in patterns:
            work_date = today + timedelta(days=day_offset)
            check_in_dt = timezone.make_aware(
                datetime.combine(work_date, time(*check_in_tuple))
            )

            defaults = {
                "check_in": check_in_dt,
                "status": status_value,
                "location": "Main Office",
            }

            if check_out_tuple:
                check_out_dt = timezone.make_aware(
                    datetime.combine(work_date, time(*check_out_tuple))
                )
                duration = check_out_dt - check_in_dt
                defaults["check_out"] = check_out_dt
                defaults["work_duration"] = duration
                defaults["overtime_minutes"] = max(
                    0, int(duration.total_seconds() / 60) - 480
                )
            else:
                defaults["check_out"] = None
                defaults["work_duration"] = None
                defaults["overtime_minutes"] = 0

            attendance, created = Attendance.objects.update_or_create(
                employee=employee,
                date=work_date,
                defaults=defaults,
            )
            print(
                ("CREATED" if created else "UPDATED"),
                "attendance",
                employee.username,
                work_date,
            )

        absent_date = today - timedelta(days=5 + index)
        attendance, created = Attendance.objects.update_or_create(
            employee=employee,
            date=absent_date,
            defaults={
                "check_in": None,
                "check_out": None,
                "work_duration": None,
                "overtime_minutes": 0,
                "location": "Main Office",
                "status": "ABSENT",
            },
        )
        print(
            ("CREATED" if created else "UPDATED"),
            "attendance",
            employee.username,
            absent_date,
        )


def seed_leaves(sample_users):
    leave_specs = [
        {
            "username": "employee",
            "start_date": timezone.localdate() + timedelta(days=3),
            "end_date": timezone.localdate() + timedelta(days=5),
            "leave_type": "CP",
            "status": "PENDING",
            "reason": "Family trip",
            "manager_comment": "",
        },
        {
            "username": "employee1",
            "start_date": timezone.localdate() - timedelta(days=10),
            "end_date": timezone.localdate() - timedelta(days=8),
            "leave_type": "RTT",
            "status": "APPROVED",
            "reason": "Long weekend",
            "manager_comment": "Approved, balance available.",
        },
        {
            "username": "employee2",
            "start_date": timezone.localdate() + timedelta(days=7),
            "end_date": timezone.localdate() + timedelta(days=7),
            "leave_type": "SICK",
            "status": "REJECTED",
            "reason": "Medical appointment",
            "manager_comment": "Please attach a medical certificate.",
        },
        {
            "username": "employee3",
            "start_date": timezone.localdate() + timedelta(days=14),
            "end_date": timezone.localdate() + timedelta(days=18),
            "leave_type": "TRAINING",
            "status": "CANCELLED",
            "reason": "External training",
            "manager_comment": "",
        },
    ]

    for spec in leave_specs:
        employee = sample_users[spec["username"]]
        leave, created = LeaveRequest.objects.update_or_create(
            employee=employee,
            start_date=spec["start_date"],
            end_date=spec["end_date"],
            leave_type=spec["leave_type"],
            defaults={
                "status": spec["status"],
                "reason": spec["reason"],
                "manager_comment": spec["manager_comment"],
            },
        )
        print(("CREATED" if created else "UPDATED"), "leave", leave)


def seed_meetings(sample_users):
    manager = sample_users["manager"]
    meetings = [
        {
            "title": "Weekly Team Sync",
            "description": "Review progress and blockers.",
            "start_time": aware_datetime(1, 10, 0),
            "end_time": aware_datetime(1, 11, 0),
            "participants": [
                ("employee", "ACCEPTED"),
                ("employee1", "INVITED"),
                ("employee2", "DECLINED"),
            ],
            "is_cancelled": False,
        },
        {
            "title": "HR Policy Review",
            "description": "Discuss upcoming HR process updates.",
            "start_time": aware_datetime(2, 14, 0),
            "end_time": aware_datetime(2, 15, 0),
            "participants": [
                ("hr_manager", "ACCEPTED"),
                ("manager", "ACCEPTED"),
                ("employee3", "INVITED"),
            ],
            "is_cancelled": False,
        },
        {
            "title": "Project Retrospective",
            "description": "Sprint retrospective and action items.",
            "start_time": aware_datetime(-2, 16, 0),
            "end_time": aware_datetime(-2, 17, 0),
            "participants": [
                ("employee", "ACCEPTED"),
                ("employee1", "ACCEPTED"),
                ("employee2", "ACCEPTED"),
                ("employee3", "ACCEPTED"),
            ],
            "is_cancelled": True,
        },
    ]

    for spec in meetings:
        meeting, created = Meeting.objects.update_or_create(
            title=spec["title"],
            start_time=spec["start_time"],
            defaults={
                "description": spec["description"],
                "end_time": spec["end_time"],
                "created_by": manager,
                "is_cancelled": spec["is_cancelled"],
            },
        )
        print(("CREATED" if created else "UPDATED"), "meeting", meeting.title)

        for username, status_value in spec["participants"]:
            participant, participant_created = MeetingParticipant.objects.update_or_create(
                meeting=meeting,
                employee=sample_users[username],
                defaults={
                    "status": status_value,
                    "responded_at": timezone.now()
                    if status_value in ("ACCEPTED", "DECLINED")
                    else None,
                },
            )
            print(
                ("CREATED" if participant_created else "UPDATED"),
                "participant",
                participant.employee.username,
                "->",
                meeting.title,
            )


# Fix any existing users with blank employee IDs
bad_qs = User.objects.filter(employee_id__isnull=True) | User.objects.filter(employee_id="")
for user in bad_qs:
    user.employee_id = f"AUTO-{user.id:04d}"
    user.save(update_fields=["employee_id"])

departments = {
    "IT": Department.objects.get_or_create(
        name="IT",
        defaults={"description": "Information Technology"},
    )[0],
    "HR": Department.objects.get_or_create(
        name="HR",
        defaults={"description": "Human Resources"},
    )[0],
    "SALES": Department.objects.get_or_create(
        name="Sales",
        defaults={"description": "Sales Department"},
    )[0],
}

admin = upsert_user(
    username="admin",
    employee_id="EMP-0001",
    email="admin@test.com",
    first_name="Admin",
    last_name="Root",
    role_value="ADMIN",
    position_value="System Administrator",
    department=departments["HR"],
    is_staff=True,
    is_superuser=True,
)

hr_manager = upsert_user(
    username="hr_manager",
    employee_id="EMP-0004",
    email="hr@test.com",
    first_name="Hana",
    last_name="HR",
    role_value="HR",
    position_value="HR Manager",
    department=departments["HR"],
    is_staff=True,
)

manager = upsert_user(
    username="manager",
    employee_id="EMP-0002",
    email="manager@test.com",
    first_name="Manager",
    last_name="Boss",
    role_value="MANAGER",
    position_value="Engineering Manager",
    department=departments["IT"],
    is_staff=True,
)

employee = upsert_user(
    username="employee",
    employee_id="EMP-0003",
    email="employee@test.com",
    first_name="Test",
    last_name="Employee",
    role_value="EMPLOYEE",
    position_value="Backend Developer",
    department=departments["IT"],
    manager=manager,
)

employee1 = upsert_user(
    username="employee1",
    employee_id="EMP-0005",
    email="employee1@test.com",
    first_name="Alice",
    last_name="Developer",
    role_value="EMPLOYEE",
    position_value="Frontend Developer",
    department=departments["IT"],
    manager=manager,
)

employee2 = upsert_user(
    username="employee2",
    employee_id="EMP-0006",
    email="employee2@test.com",
    first_name="Bob",
    last_name="Sales",
    role_value="EMPLOYEE",
    position_value="Sales Representative",
    department=departments["SALES"],
    manager=manager,
)

employee3 = upsert_user(
    username="employee3",
    employee_id="EMP-0007",
    email="employee3@test.com",
    first_name="Sara",
    last_name="Support",
    role_value="EMPLOYEE",
    position_value="Support Specialist",
    department=departments["HR"],
    manager=hr_manager,
)

sample_users = {
    "admin": admin,
    "hr_manager": hr_manager,
    "manager": manager,
    "employee": employee,
    "employee1": employee1,
    "employee2": employee2,
    "employee3": employee3,
}

seed_attendance([employee, employee1, employee2, employee3])
seed_leaves(sample_users)
seed_meetings(sample_users)

print("\nDONE ✅")
print("Database:", "PostgreSQL / pfe")
print("Logins:")
print("admin / password123")
print("hr_manager / password123")
print("manager / password123")
print("employee / password123")
print("employee1 / password123")
print("employee2 / password123")
print("employee3 / password123")
