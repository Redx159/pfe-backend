from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from employees.models import Department, Employee
from attendance.models import Attendance
from leaves.models import LeaveRequest
from meetings.models import Meeting, MeetingParticipant
from datetime import date, timedelta, datetime
import random


DEPARTMENTS = [
    ("Engineering", "Software and infrastructure engineering"),
    ("HR", "Human Resources"),
    ("Sales", "Sales and business development"),
    ("Marketing", "Marketing and communications"),
    ("Finance", "Finance and accounting"),
    ("Operations", "Operations and logistics"),
]

EMPLOYEES = [
    # (username, email, first, last, employee_id, dept_name, position, role, manager_idx)
    # Index in DEPARTMENTS: 0=Engineering, 1=HR, 2=Sales, 3=Marketing, 4=Finance, 5=Operations
    ("admin", "admin@company.com", "Admin", "User", "EMP001", 0, "System Admin", "ADMIN", None),
    ("hr_manager", "hr@company.com", "Sophie", "Martin", "EMP002", 1, "HR Director", "HR", None),
    ("manager1", "mgr1@company.com", "Ahmed", "Benali", "EMP003", 0, "Engineering Manager", "MANAGER", None),
    ("manager2", "mgr2@company.com", "Fatima", "Zahra", "EMP004", 2, "Sales Director", "MANAGER", None),
    ("manager3", "mgr3@company.com", "Youssef", "El Amrani", "EMP005", 3, "Marketing Director", "MANAGER", None),
    ("manager4", "mgr4@company.com", "Karim", "Idrissi", "EMP006", 4, "Finance Director", "MANAGER", None),
    ("alice", "alice@company.com", "Alice", "Johnson", "EMP007", 0, "Senior Developer", "EMPLOYEE", 2),
    ("bob", "bob@company.com", "Bob", "Smith", "EMP008", 0, "Backend Developer", "EMPLOYEE", 2),
    ("charlie", "charlie@company.com", "Charlie", "Brown", "EMP009", 0, "Frontend Developer", "EMPLOYEE", 2),
    ("diana", "diana@company.com", "Diana", "El Ghali", "EMP010", 0, "DevOps Engineer", "EMPLOYEE", 2),
    ("emma", "emma@company.com", "Emma", "Wilson", "EMP011", 0, "Data Analyst", "EMPLOYEE", 2),
    ("farid", "farid@company.com", "Farid", "Belkacem", "EMP012", 2, "Sales Representative", "EMPLOYEE", 3),
    ("ghita", "ghita@company.com", "Ghita", "Lamrani", "EMP013", 2, "Account Executive", "EMPLOYEE", 3),
    ("hanae", "hanae@company.com", "Hanae", "Bennani", "EMP014", 3, "Marketing Specialist", "EMPLOYEE", 4),
    ("imane", "imane@company.com", "Imane", "Tazi", "EMP015", 3, "Content Writer", "EMPLOYEE", 4),
    ("jalal", "jalal@company.com", "Jalal", "Ouazzani", "EMP016", 4, "Accountant", "EMPLOYEE", 5),
    ("khadija", "khadija@company.com", "Khadija", "Rahmani", "EMP017", 4, "Financial Analyst", "EMPLOYEE", 5),
    ("larbi", "larbi@company.com", "Larbi", "Mokhtari", "EMP018", 5, "Operations Coordinator", "EMPLOYEE", 5),
    ("mohamed", "mohamed@company.com", "Mohamed", "El Fassi", "EMP019", 5, "Logistics Lead", "EMPLOYEE", 5),
    ("nadia", "nadia@company.com", "Nadia", "Chraibi", "EMP020", 1, "HR Coordinator", "EMPLOYEE", 1),
    ("omar", "omar@company.com", "Omar", "Slaoui", "EMP021", 5, "Office Manager", "EMPLOYEE", 5),
]

LEAVE_REASONS = {
    "CP": ["Congés annuels", "Vacances en famille", "Voyage"],
    "SICK": ["Fièvre et fatigue", "Rendez-vous médical", "Arrêt maladie"],
    "RTT": ["Journée RTT", "Départ anticipé"],
    "TRAINING": ["Formation Django", "Certification AWS", "Conférence technique"],
    "UNPAID": ["Raisons personnelles", "Démarches administratives"],
}

MEETINGS = [
    {
        "title": "Sprint Planning",
        "description": "Weekly sprint planning meeting",
        "is_online": True,
        "meeting_url": "https://meet.google.com/abc-defg-hij",
        "location": "",
        "days_from_now": 0,
        "hour": 9,
        "duration_hours": 1,
        "participant_indices": [6, 7, 8, 9, 10],
    },
    {
        "title": "All-Hands Meeting",
        "description": "Company-wide quarterly update",
        "is_online": True,
        "meeting_url": "https://zoom.us/j/123456789",
        "location": "",
        "days_from_now": 2,
        "hour": 14,
        "duration_hours": 1.5,
        "participant_indices": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    },
    {
        "title": "Performance Review",
        "description": "Review team performance metrics",
        "is_online": False,
        "meeting_url": "",
        "location": "Conference Room B",
        "days_from_now": 1,
        "hour": 11,
        "duration_hours": 1,
        "participant_indices": [0, 2, 3, 4, 5],
    },
    {
        "title": "Client Presentation",
        "description": "Present Q2 results to client",
        "is_online": True,
        "meeting_url": "https://teams.microsoft.com/meeting/123",
        "location": "",
        "days_from_now": 3,
        "hour": 10,
        "duration_hours": 2,
        "participant_indices": [3, 11, 12, 13, 14],
    },
    {
        "title": "Team Standup",
        "description": "Daily engineering standup",
        "is_online": False,
        "meeting_url": "",
        "location": "Engineering Floor",
        "days_from_now": 0,
        "hour": 8,
        "duration_hours": 0.5,
        "participant_indices": [6, 7, 8, 9, 10],
    },
]


class Command(BaseCommand):
    help = "Generate comprehensive test data for development"

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()

        # ── Departments ──
        dept_map = {}
        for name, desc in DEPARTMENTS:
            dept, created = Department.objects.get_or_create(
                name=name, defaults={"description": desc}
            )
            dept_map[name] = dept
            if created:
                self.stdout.write(f"  Created department: {name}")

        # ── Employees ──
        employee_objects = []
        for username, email, first, last, eid, dept_idx, pos, role, mgr_idx in EMPLOYEES:
            dept = dept_map[DEPARTMENTS[dept_idx][0]]
            emp, created = Employee.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "employee_id": eid,
                    "department": dept,
                    "position": pos,
                    "role": role,
                    "hire_date": today - timedelta(days=random.randint(90, 730)),
                    "cp_balance": random.randint(10, 25),
                    "rtt_balance": random.randint(3, 10),
                    "is_active": True,
                    "is_staff": role in ("ADMIN", "HR"),
                    "password": make_password("test123"),
                },
            )
            if created:
                self.stdout.write(f"  Created employee: {first} {last} ({role})")

            employee_objects.append(emp)

        # Set managers (second pass, after all employees exist)
        for i, (username, _, _, _, _, _, _, role, mgr_idx) in enumerate(EMPLOYEES):
            emp = employee_objects[i]
            if mgr_idx is not None:
                emp.manager = employee_objects[mgr_idx]
                emp.save(update_fields=["manager"])

        # ── Backfill work_duration for existing records ──
        backfilled = 0
        for att in Attendance.objects.filter(work_duration__isnull=True, check_in__isnull=False, check_out__isnull=False):
            att.work_duration = att.check_out - att.check_in
            att.overtime_minutes = max(0, int(att.work_duration.total_seconds() // 60 - 480))
            att.save(update_fields=["work_duration", "overtime_minutes"])
            backfilled += 1
        if backfilled:
            self.stdout.write(f"  Backfilled work_duration for {backfilled} records")

        # ── Attendance (last 30 working days + today) ──
        attendance_count = 0
        approved_leaves = LeaveRequest.objects.filter(
            status="APPROVED",
        ).values("employee_id", "start_date", "end_date")
        leave_dates = set()
        for lv in approved_leaves:
            start = lv["start_date"]
            end = lv["end_date"]
            cur = start
            while cur <= end:
                leave_dates.add((lv["employee_id"], cur))
                cur += timedelta(days=1)

        for emp in employee_objects:
            for days_ago in range(30, -1, -1):
                d = today - timedelta(days=days_ago)
                if d.weekday() >= 5:
                    continue
                if (emp.id, d) in leave_dates:
                    continue

                status = random.choices(
                    ["ON_TIME", "LATE", "ABSENT"],
                    weights=[70, 20, 10],
                    k=1,
                )[0]

                check_in = None
                check_out = None
                work_duration = None
                overtime_minutes = 0
                if status != "ABSENT":
                    h_in = random.randint(7, 9)
                    m_in = random.randint(0, 59)
                    check_in = timezone.make_aware(datetime(d.year, d.month, d.day, h_in, m_in))
                    h_out = random.randint(16, 18)
                    m_out = random.randint(0, 59)
                    check_out = timezone.make_aware(datetime(d.year, d.month, d.day, h_out, m_out))
                    work_duration = check_out - check_in
                    overtime_minutes = max(0, int(work_duration.total_seconds() // 60 - 480))

                _, created = Attendance.objects.get_or_create(
                    employee=emp,
                    date=d,
                    defaults={
                        "status": status,
                        "check_in": check_in,
                        "check_out": check_out,
                        "work_duration": work_duration,
                        "overtime_minutes": overtime_minutes,
                        "location": random.choice(
                            ["Main Office", "Remote", "Client Site", "Branch Office"]
                        ),
                    },
                )
                if created:
                    attendance_count += 1

        self.stdout.write(f"  Created {attendance_count} attendance records")

        # ── Leaves ──
        leave_count = 0
        for emp in employee_objects:
            if random.random() > 0.4:
                continue
            leave_type = random.choice(
                ["CP", "CP", "CP", "SICK", "SICK", "RTT", "TRAINING", "UNPAID"]
            )
            start = today - timedelta(days=random.randint(1, 60))
            duration = random.randint(1, 5)
            end = start + timedelta(days=duration - 1)

            if start.weekday() >= 5:
                start += timedelta(days=(7 - start.weekday()))

            status = random.choices(
                ["APPROVED", "APPROVED", "PENDING", "REJECTED", "CANCELLED"],
                weights=[40, 20, 20, 10, 10],
                k=1,
            )[0]

            _, created = LeaveRequest.objects.get_or_create(
                employee=emp,
                start_date=start,
                end_date=end,
                defaults={
                    "leave_type": leave_type,
                    "status": status,
                    "reason": random.choice(LEAVE_REASONS.get(leave_type, ["Personal reasons"])),
                    "manager_comment": "Approved" if status == "APPROVED" else "",
                },
            )
            if created:
                leave_count += 1

        self.stdout.write(f"  Created {leave_count} leave requests")

        # ── Meetings ──
        meeting_count = 0
        for m in MEETINGS:
            start_dt = timezone.make_aware(
                datetime(
                    today.year, today.month, today.day,
                    m["hour"], 0,
                )
            ) + timedelta(days=m["days_from_now"])
            end_dt = start_dt + timedelta(hours=m["duration_hours"])

            creator = employee_objects[0]

            meeting, created = Meeting.objects.get_or_create(
                title=m["title"],
                start_time=start_dt,
                end_time=end_dt,
                defaults={
                    "description": m["description"],
                    "is_online": m["is_online"],
                    "meeting_url": m["meeting_url"],
                    "location": m["location"],
                    "created_by": creator,
                    "is_cancelled": False,
                },
            )
            if created:
                meeting_count += 1

                for pi in m["participant_indices"]:
                    participant = employee_objects[pi]
                    MeetingParticipant.objects.get_or_create(
                        meeting=meeting,
                        employee=participant,
                        defaults={
                            "status": "ACCEPTED" if random.random() > 0.2 else "INVITED",
                        },
                    )

        # Also create one past meeting for history
        past_start = timezone.make_aware(
            datetime(today.year, today.month, today.day, 15, 0)
        ) - timedelta(days=5)
        past_end = past_start + timedelta(hours=1)
        past_meeting, created = Meeting.objects.get_or_create(
            title="Past Code Review",
            start_time=past_start,
            end_time=past_end,
            defaults={
                "description": "Code review session from last week",
                "is_online": True,
                "meeting_url": "https://meet.google.com/past-review",
                "location": "",
                "created_by": employee_objects[2],
                "is_cancelled": False,
            },
        )
        if created:
            meeting_count += 1
            for pi in [6, 7, 8]:
                MeetingParticipant.objects.get_or_create(
                    meeting=past_meeting,
                    employee=employee_objects[pi],
                    defaults={"status": "ACCEPTED"},
                )

        self.stdout.write(f"  Created {meeting_count} meetings")

        self.stdout.write(self.style.SUCCESS(
            "\nTest data generated successfully!\n"
            "All accounts use password: test123\n"
            f"Total employees: {len(employee_objects)}"
        ))
