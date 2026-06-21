from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from employees.models import Department, Employee
from leaves.models import LeaveRequest
from meetings.models import Meeting, MeetingParticipant
from attendance.models import Attendance
from notifications.models import Notification, NotificationPreference, Device
from attendance.models import Attendance, DailyQR
from assistantbot.models import AssistantConversation, AssistantMessage
from datetime import date, timedelta, datetime


DEPARTMENTS = [
    (1, "Informatique", "Departement developpement et infrastructure IT"),
    (2, "Ressources Humaines", "Gestion du personnel et administration"),
    (3, "Finance", "Comptabilite et gestion financiere"),
    (4, "Marketing", "Communication et marketing"),
    (5, "Commercial", "Ventes et relation client"),
]

EMPLOYEES = [
    (1, "admin", "Admin", "Principal", "admin@company.ma", "EMP-001", 2,
     "Administrateur RH", "2024-01-01", "0600000001", 25, 10, "ADMIN", None, True, True),
    (2, "manager1", "Karim", "Benali", "karim.benali@company.ma", "EMP-002", 1,
     "Chef de projet IT", "2023-06-01", "0600000002", 22, 8, "MANAGER", None, False, True),
    (3, "manager2", "Sara", "El Amrani", "sara.amrani@company.ma", "EMP-003", 4,
     "Responsable Marketing", "2023-09-01", "0600000003", 20, 7, "MANAGER", None, False, True),
    (4, "manager3", "Youssef", "Idrissi", "youssef.idrissi@company.ma", "EMP-004", 3,
     "Chef Comptable", "2022-11-01", "0600000004", 18, 6, "MANAGER", None, False, True),
    (5, "employee1", "Ahmed", "Alaoui", "ahmed.alaoui@company.ma", "EMP-005", 1,
     "Developpeur Full Stack", "2024-04-01", "0600000005", 25, 10, "EMPLOYEE", 2, False, True),
    (6, "employee2", "Fatima", "Zahra", "fatima.zahra@company.ma", "EMP-006", 1,
     "Developpeur Mobile", "2024-05-01", "0600000006", 24, 9, "EMPLOYEE", 2, False, True),
    (7, "employee3", "Hassan", "Moujtahid", "hassan.moujtahid@company.ma", "EMP-007", 1,
     "Data Analyst", "2024-06-01", "0600000007", 23, 8, "EMPLOYEE", 2, False, True),
    (8, "employee4", "Nadia", "Bennani", "nadia.bennani@company.ma", "EMP-008", 4,
     "Community Manager", "2024-07-01", "0600000008", 22, 7, "EMPLOYEE", 3, False, True),
    (9, "employee5", "Omar", "Tazi", "omar.tazi@company.ma", "EMP-009", 3,
     "Comptable", "2024-08-01", "0600000009", 21, 6, "EMPLOYEE", 4, False, True),
    (10, "employee6", "Leila", "Chraibi", "leila.chraibi@company.ma", "EMP-010", 5,
     "Commercial", "2024-09-01", "0600000010", 20, 5, "EMPLOYEE", None, False, True),
]

LEAVES = [
    (5, "2026-06-01", "2026-06-05", "CP", "APPROVED", "Vacances en famille", "Approuve"),
    (6, "2026-06-10", "2026-06-10", "SICK", "APPROVED", "Rendez-vous medical", "Bon retablissement"),
    (7, "2026-06-20", "2026-06-25", "CP", "PENDING", "Vacances ete", ""),
    (8, "2026-05-25", "2026-05-26", "RTT", "REJECTED", "Affaire personnelle", "Refuse - conflit avec reunion client"),
    (9, "2026-07-01", "2026-07-15", "CP", "PENDING", "Vacances annuelles", ""),
    (10, "2026-06-15", "2026-06-15", "SICK", "APPROVED", "Maladie", "Approuve"),
    (2, "2026-06-28", "2026-06-30", "CP", "PENDING", "Conges perso", ""),
    (5, "2026-07-20", "2026-07-22", "RTT", "APPROVED", "Recuperation", "Ok"),
    (6, "2026-05-10", "2026-05-12", "CP", "CANCELLED", "Annule pour raison pro", ""),
    (3, "2026-06-22", "2026-06-26", "CP", "PENDING", "Vacances", ""),
    # Week 22-30 June
    (8, "2026-06-24", "2026-06-24", "RTT", "APPROVED", "Demarche administrative", "Approuve"),
    (5, "2026-06-29", "2026-06-30", "CP", "APPROVED", "Fin de mois", "Accorde"),
    (10, "2026-06-22", "2026-06-23", "CP", "PENDING", "Conges perso", ""),
    (9, "2026-06-25", "2026-06-25", "SICK", "REJECTED", "Maladie legere", "Refuse - equipe reduite cette semaine"),
    (6, "2026-06-23", "2026-06-23", "SICK", "APPROVED", "Visite medicale", "OK"),
]

MEETINGS_DATA = [
    (1, "Sprint Review", "Revue du sprint en cours", "2026-06-22 10:00", "2026-06-22 11:00", 2, True, "", "https://meet.google.com/abc-defg-hij", False),
    (2, "Point hebdo equipe", "Reunion hebdomadaire equipe IT", "2026-06-23 14:00", "2026-06-23 15:00", 2, False, "Salle A-203", "", False),
    (3, "Strategie marketing", "Campagne Q3", "2026-06-24 09:00", "2026-06-24 11:00", 3, False, "Salle B-101", "", False),
    (4, "Entretien annuel", "Evaluation annuelle equipe finance", "2026-06-25 15:00", "2026-06-25 16:30", 4, False, "Bureau RH", "", False),
    (5, "Presentation projet", "Nouveau projet client", "2026-06-15 11:00", "2026-06-15 12:00", 2, True, "", "https://zoom.us/j/123456789", False),
    (6, "Formation Django", "Workshop Django avance", "2026-06-19 09:00", "2026-06-19 17:00", 2, False, "Salle formation", "", False),
    (7, "Reunion annulee", "Test annulation", "2026-06-20 10:00", "2026-06-20 11:00", 2, False, "Salle C", "", True),
    (8, "Brainstorming produit", "Idees nouvelles fonctionnalites", "2026-06-26 13:00", "2026-06-26 14:00", 5, False, "Salle creative", "", False),
    (9, "Point direction", "Reunion mensuelle direction", "2026-06-30 10:00", "2026-06-30 12:00", 1, False, "Salle conseil", "", False),
    (10, "Retrospective sprint", "Bilan du sprint et ameliorations", "2026-06-22 11:00", "2026-06-22 12:00", 2, True, "", "https://meet.google.com/abc-defg-hij", False),
    # Week 22-30 June — additional meetings
    (11, "Daily standup", "Point quotidien equipe IT", "2026-06-22 09:00", "2026-06-22 09:30", 2, False, "Salle A-203", "", False),
    (12, "Daily standup", "Point quotidien equipe IT", "2026-06-23 09:00", "2026-06-23 09:30", 2, False, "Salle A-203", "", False),
    (13, "Daily standup", "Point quotidien equipe IT", "2026-06-24 09:00", "2026-06-24 09:30", 2, False, "Salle A-203", "", False),
    (14, "Daily standup", "Point quotidien equipe IT", "2026-06-25 09:00", "2026-06-25 09:30", 2, False, "Salle A-203", "", False),
    (15, "Daily standup", "Point quotidien equipe IT", "2026-06-26 09:00", "2026-06-26 09:30", 2, False, "Salle A-203", "", False),
    (16, "Formation Angular", "Workshop Angular intermediaire", "2026-06-23 10:00", "2026-06-23 12:00", 2, False, "Salle formation", "", False),
    (17, "Reunion fournisseur", "Point avec prestataire", "2026-06-24 14:00", "2026-06-24 15:00", 3, True, "", "https://teams.microsoft.com/meeting/456", False),
    (18, "Atelier SEO", "Strategie referencement naturel", "2026-06-25 09:00", "2026-06-25 11:00", 3, False, "Salle B-101", "", False),
    (19, "Point commercial", "Bilan hebdomadaire ventes", "2026-06-26 10:00", "2026-06-26 11:00", 10, False, "Salle reunion RDC", "", False),
    (20, "Lancement projet", "Kickoff nouveau projet client", "2026-06-29 09:00", "2026-06-29 10:30", 2, False, "Salle conseil", "", False),
    (21, "Reunion RH", "Point recrutement et paie", "2026-06-29 14:00", "2026-06-29 15:00", 1, False, "Bureau RH", "", False),
    (22, "Formation Excel avance", "Workshop tableaux croises", "2026-06-30 14:00", "2026-06-30 16:00", 4, False, "Salle formation", "", False),
]

MEETING_PARTICIPANTS = [
    (1, 5, "ACCEPTED"),
    (1, 6, "ACCEPTED"),
    (1, 7, "DECLINED"),
    (2, 5, "ACCEPTED"),
    (2, 6, "ACCEPTED"),
    (2, 7, "INVITED"),
    (3, 8, "ACCEPTED"),
    (3, 3, "ACCEPTED"),
    (4, 9, "INVITED"),
    (8, 6, "ACCEPTED"),
    (8, 7, "ACCEPTED"),
    (8, 5, "INVITED"),
    (9, 2, "ACCEPTED"),
    (9, 3, "ACCEPTED"),
    (9, 4, "ACCEPTED"),
    (11, 5, "ACCEPTED"),
    (11, 6, "ACCEPTED"),
    (11, 7, "ACCEPTED"),
    (12, 5, "ACCEPTED"),
    (12, 6, "INVITED"),
    (12, 7, "ACCEPTED"),
    (13, 5, "ACCEPTED"),
    (13, 6, "ACCEPTED"),
    (13, 7, "ACCEPTED"),
    (14, 5, "INVITED"),
    (14, 6, "ACCEPTED"),
    (14, 7, "ACCEPTED"),
    (15, 5, "ACCEPTED"),
    (15, 6, "ACCEPTED"),
    (15, 7, "ACCEPTED"),
    (16, 5, "ACCEPTED"),
    (16, 6, "ACCEPTED"),
    (17, 8, "INVITED"),
    (17, 3, "ACCEPTED"),
    (18, 8, "ACCEPTED"),
    (18, 3, "ACCEPTED"),
    (19, 10, "ACCEPTED"),
    (20, 5, "INVITED"),
    (20, 6, "INVITED"),
    (20, 7, "INVITED"),
    (20, 2, "ACCEPTED"),
    (21, 1, "ACCEPTED"),
    (21, 2, "INVITED"),
    (22, 9, "ACCEPTED"),
    (22, 4, "ACCEPTED"),
]

ATTENDANCE_RECORDS = [
    (5, "2026-06-20", "2026-06-20 08:45", "2026-06-20 17:15", "30600", 0, "Bureau", "ON_TIME"),
    (6, "2026-06-20", "2026-06-20 09:05", "2026-06-20 18:00", "32100", 60, "Bureau", "LATE"),
    (7, "2026-06-20", None, None, None, 0, "", "ABSENT"),
    (5, "2026-06-21", "2026-06-21 08:30", "2026-06-21 17:00", "30600", 0, "Bureau", "ON_TIME"),
    (6, "2026-06-21", "2026-06-21 08:50", "2026-06-21 17:10", "30000", 0, "Bureau", "ON_TIME"),
    (7, "2026-06-21", "2026-06-21 09:15", "2026-06-21 18:30", "33300", 90, "Bureau", "LATE"),
    (8, "2026-06-20", "2026-06-20 08:00", "2026-06-20 16:30", "30600", 0, "Bureau", "ON_TIME"),
    (9, "2026-06-20", "2026-06-20 08:55", "2026-06-20 17:00", "29100", 0, "Bureau", "ON_TIME"),
    (10, "2026-06-20", "2026-06-20 09:30", "2026-06-20 17:30", "28800", 0, "Client externe", "LATE"),
    (5, "2026-06-22", "2026-06-22 08:40", "2026-06-22 17:00", "30000", 0, "Bureau", "ON_TIME"),
    (6, "2026-06-22", "2026-06-22 08:55", "2026-06-22 17:15", "30800", 0, "Bureau", "ON_TIME"),
    (7, "2026-06-22", "2026-06-22 09:10", "2026-06-22 17:30", "30000", 0, "Bureau", "LATE"),
    (8, "2026-06-22", "2026-06-22 08:15", "2026-06-22 16:45", "30600", 0, "Bureau", "ON_TIME"),
    (9, "2026-06-22", "2026-06-22 08:50", "2026-06-22 17:00", "29400", 0, "Bureau", "ON_TIME"),
    (10, "2026-06-22", None, None, None, 0, "", "ABSENT"),
    (5, "2026-06-23", "2026-06-23 08:30", "2026-06-23 16:30", "28800", 0, "Bureau", "ON_TIME"),
    (6, "2026-06-23", None, None, None, 0, "", "ABSENT"),
    (7, "2026-06-23", "2026-06-23 08:45", "2026-06-23 17:00", "29700", 0, "Bureau", "ON_TIME"),
    (8, "2026-06-23", "2026-06-23 08:30", "2026-06-23 17:00", "30600", 0, "Bureau", "ON_TIME"),
    (9, "2026-06-23", "2026-06-23 08:55", "2026-06-23 17:10", "29700", 0, "Bureau", "ON_TIME"),
    (10, "2026-06-23", "2026-06-23 09:00", "2026-06-23 17:00", "28800", 0, "Bureau", "ON_TIME"),
    (5, "2026-06-24", "2026-06-24 08:45", "2026-06-24 17:15", "30600", 0, "Bureau", "ON_TIME"),
    (6, "2026-06-24", "2026-06-24 09:00", "2026-06-24 18:00", "32400", 60, "Bureau", "ON_TIME"),
    (7, "2026-06-24", "2026-06-24 08:30", "2026-06-24 17:00", "30600", 0, "Bureau", "ON_TIME"),
    (8, "2026-06-24", None, None, None, 0, "", "ABSENT"),
    (9, "2026-06-24", "2026-06-24 09:05", "2026-06-24 17:00", "28500", 0, "Bureau", "LATE"),
    (10, "2026-06-24", "2026-06-24 08:50", "2026-06-24 17:10", "29600", 0, "Bureau", "ON_TIME"),
    (5, "2026-06-25", "2026-06-25 08:40", "2026-06-25 17:30", "31800", 30, "Bureau", "ON_TIME"),
    (6, "2026-06-25", "2026-06-25 08:55", "2026-06-25 17:00", "29100", 0, "Bureau", "ON_TIME"),
    (7, "2026-06-25", "2026-06-25 09:00", "2026-06-25 17:15", "29700", 0, "Bureau", "ON_TIME"),
    (8, "2026-06-25", "2026-06-25 08:00", "2026-06-25 16:30", "30600", 0, "Bureau", "ON_TIME"),
    (10, "2026-06-25", "2026-06-25 09:30", "2026-06-25 17:30", "28800", 0, "Client", "LATE"),
    (5, "2026-06-26", "2026-06-26 08:45", "2026-06-26 16:45", "28800", 0, "Bureau", "ON_TIME"),
    (6, "2026-06-26", "2026-06-26 08:50", "2026-06-26 17:00", "29400", 0, "Bureau", "ON_TIME"),
    (7, "2026-06-26", "2026-06-26 09:15", "2026-06-26 17:30", "29700", 0, "Bureau", "LATE"),
    (8, "2026-06-26", "2026-06-26 08:10", "2026-06-26 16:00", "28200", 0, "Bureau", "ON_TIME"),
    (9, "2026-06-26", "2026-06-26 08:50", "2026-06-26 17:00", "29400", 0, "Bureau", "ON_TIME"),
    (10, "2026-06-26", "2026-06-26 09:00", "2026-06-26 17:00", "28800", 0, "Bureau", "ON_TIME"),
]

NOTIFICATIONS = [
    (5, "Conges approuves", "Votre demande de conges du 01/06 au 05/06 a ete approuvee", "LEAVE_APPROVED", True, "/leaves/1"),
    (6, "Conges approuves", "Votre conge maladie du 10/06 a ete approuve", "LEAVE_APPROVED", True, "/leaves/2"),
    (8, "Conges refuses", "Votre demande RTT du 25/05 au 26/05 a ete refusee", "LEAVE_REJECTED", False, "/leaves/4"),
    (5, "Invitation reunion", "Vous etes invite a Sprint Review le 22/06 a 10h00", "MEETING_INVITE", True, "/meetings/1"),
    (6, "Invitation reunion", "Vous etes invite a Sprint Review le 22/06 a 10h00", "MEETING_INVITE", False, "/meetings/1"),
    (5, "Invitation reunion", "Point hebdo equipe le 23/06 a 14h00", "MEETING_INVITE", True, "/meetings/2"),
    (6, "Invitation reunion", "Point hebdo equipe le 23/06 a 14h00", "MEETING_INVITE", False, "/meetings/2"),
    (10, "Conges approuves", "Votre conge maladie du 15/06 a ete approuve", "LEAVE_APPROVED", False, "/leaves/6"),
    (5, "Invitation brainstorming", "Brainstorming produit le 26/06 a 13h00", "MEETING_INVITE", True, "/meetings/8"),
    (6, "Reunion annulee", "La reunion Test annulation a ete annulee", "MEETING_CANCELLED", False, "/meetings/7"),
    # Week 22-30
    (8, "RTT approuve", "Votre jour RTT du 24/06 a ete approuve", "LEAVE_APPROVED", True, "/leaves/11"),
    (5, "Conges approuves", "Vos conges des 29-30/06 ont ete approuves", "LEAVE_APPROVED", True, "/leaves/12"),
    (6, "Invitation reunion", "Formation Angular le 23/06 a 10h00", "MEETING_INVITE", True, "/meetings/16"),
    (5, "Invitation reunion", "Daily standup 22/06 a 09h00", "MEETING_INVITE", True, "/meetings/11"),
    (7, "Invitation reunion", "Daily standup 22/06 a 09h00", "MEETING_INVITE", True, "/meetings/11"),
    (6, "Invitation reunion", "Daily standup 22/06 a 09h00", "MEETING_INVITE", True, "/meetings/11"),
    (5, "Rappel", "Sprint Review demain a 10h00", "MEETING_INVITE", False, "/meetings/1"),
    (10, "Rappel", "Point commercial vendredi 26/06 a 10h00", "MEETING_INVITE", False, "/meetings/19"),
    (5, "Invitation reunion", "Kickoff projet lundi 29/06 a 09h00", "MEETING_INVITE", False, "/meetings/20"),
    (9, "Conge refuse", "Votre conge maladie du 25/06 a ete refuse", "LEAVE_REJECTED", False, "/leaves/14"),
]


def parse_dt(s):
    return timezone.make_aware(datetime.strptime(s, "%Y-%m-%d %H:%M"))


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


class Command(BaseCommand):
    help = "Seed deterministic test data for development / demo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Delete existing data before seeding",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if force:
            self.stdout.write("  Deleting existing data (reverse dependency order)...")
            AssistantMessage.objects.all().delete()
            AssistantConversation.objects.all().delete()
            Notification.objects.all().delete()
            NotificationPreference.objects.all().delete()
            Device.objects.all().delete()
            MeetingParticipant.objects.all().delete()
            Meeting.objects.all().delete()
            Attendance.objects.all().delete()
            DailyQR.objects.all().delete()
            LeaveRequest.objects.all().delete()
            Employee.objects.all().delete()
            Department.objects.all().delete()
            self.stdout.write("  Done deleting")
        # ── Departments ──
        for pk, name, desc in DEPARTMENTS:
            Department.objects.update_or_create(
                pk=pk, defaults={"name": name, "description": desc}
            )
        self.stdout.write(f"  Created {len(DEPARTMENTS)} departments")

        # ── Employees ──
        emp_cache = {}
        for pk, username, first, last, email, eid, dept_pk, pos, hire, phone, cp, rtt, role, mgr_pk, staff, active in EMPLOYEES:
            emp, _ = Employee.objects.update_or_create(
                username=username,
                defaults={
                    "pk": pk,
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                    "employee_id": eid,
                    "department_id": dept_pk,
                    "position": pos,
                    "hire_date": parse_date(hire),
                    "phone_number": phone,
                    "cp_balance": cp,
                    "rtt_balance": rtt,
                    "role": role,
                    "is_staff": staff,
                    "is_active": active,
                    "password": make_password("test123"),
                },
            )
            emp_cache[pk] = emp
        self.stdout.write(f"  Created {len(EMPLOYEES)} employees")

        # Set managers (second pass)
        for pk, _, _, _, _, _, _, _, _, _, _, _, _, mgr_pk, _, _ in EMPLOYEES:
            if mgr_pk is not None:
                Employee.objects.filter(pk=pk).update(manager=emp_cache[mgr_pk])
        self.stdout.write("  Set manager relationships")

        # ── Leave Requests ──
        for emp_pk, start, end, ltype, status, reason, comment in LEAVES:
            LeaveRequest.objects.update_or_create(
                employee_id=emp_pk,
                start_date=parse_date(start),
                end_date=parse_date(end),
                defaults={
                    "leave_type": ltype,
                    "status": status,
                    "reason": reason,
                    "manager_comment": comment,
                },
            )
        self.stdout.write(f"  Created {len(LEAVES)} leave requests")

        # ── Meetings ──
        for pk, title, desc, start, end, creator_pk, online, loc, url, cancelled in MEETINGS_DATA:
            Meeting.objects.update_or_create(
                pk=pk,
                defaults={
                    "title": title,
                    "description": desc,
                    "start_time": parse_dt(start),
                    "end_time": parse_dt(end),
                    "created_by_id": creator_pk,
                    "is_online": online,
                    "location": loc,
                    "meeting_url": url,
                    "is_cancelled": cancelled,
                },
            )
        self.stdout.write(f"  Created {len(MEETINGS_DATA)} meetings")

        # ── Meeting participants ──
        for meeting_num, emp_pk, status in MEETING_PARTICIPANTS:
            MeetingParticipant.objects.update_or_create(
                meeting_id=meeting_num,
                employee_id=emp_pk,
                defaults={"status": status},
            )
        self.stdout.write(f"  Created {len(MEETING_PARTICIPANTS)} meeting participants")

        # ── Attendance ──
        for emp_pk, dt, cin, cout, dur, ot, loc, status in ATTENDANCE_RECORDS:
            defaults = {
                "status": status,
                "location": loc,
                "overtime_minutes": ot,
                "work_duration": None,
            }
            if dur is not None:
                defaults["work_duration"] = timedelta(seconds=int(dur))
            if cin:
                defaults["check_in"] = parse_dt(cin)
            else:
                defaults["check_in"] = None
            if cout:
                defaults["check_out"] = parse_dt(cout)
            else:
                defaults["check_out"] = None

            Attendance.objects.update_or_create(
                employee_id=emp_pk,
                date=parse_date(dt),
                defaults=defaults,
            )
        self.stdout.write(f"  Created {len(ATTENDANCE_RECORDS)} attendance records")

        # ── Notification Preferences ──
        for i in range(1, 11):
            NotificationPreference.objects.update_or_create(
                employee_id=i,
                defaults={
                    "meeting_invites": True,
                    "leave_status": True,
                    "reminders": i not in (3, 7),
                    "vacation_mode": False,
                    "vacation_until": None,
                },
            )
        # employee10 has meeting_invites=False
        NotificationPreference.objects.filter(employee_id=10).update(meeting_invites=False)
        self.stdout.write("  Created notification preferences")

        # ── Notifications ──
        for recipient_id, title, body, ntype, is_read, link in NOTIFICATIONS:
            Notification.objects.get_or_create(
                recipient_id=recipient_id,
                title=title,
                body=body,
                type=ntype,
                defaults={"is_read": is_read, "related_link": link},
            )
        self.stdout.write(f"  Created {len(NOTIFICATIONS)} notifications")

        # ── Chatbot conversations ──
        for conv_id, user_id, title, created, updated in [
            (1, 5, "HR Assistant", "2026-06-20 09:00", "2026-06-20 09:05"),
            (2, 6, "HR Assistant", "2026-06-21 14:00", "2026-06-21 14:03"),
        ]:
            AssistantConversation.objects.update_or_create(
                pk=conv_id,
                defaults={
                    "user_id": user_id,
                    "title": title,
                    "created_at": parse_dt(created),
                    "updated_at": parse_dt(updated),
                },
            )

        for msg_id, conv_id, role, content, created in [
            (1, 1, "user", "Combien de conges il me reste ?", "2026-06-20 09:00:00"),
            (2, 1, "assistant", "Il vous reste 25 jours de conges payes et 10 jours de RTT.", "2026-06-20 09:00:01"),
            (3, 1, "user", "Comment faire une demande de conges ?", "2026-06-20 09:02:00"),
            (4, 1, "assistant", "Allez dans longlet Conges, cliquez sur +, remplissez le formulaire et soumettez.", "2026-06-20 09:02:01"),
            (5, 1, "user", "Merci", "2026-06-20 09:05:00"),
            (6, 2, "user", "Quelles sont mes reunions aujourd hui ?", "2026-06-21 14:00:00"),
            (7, 2, "assistant", "Vous avez une reunion : Sprint Review a 10h00.", "2026-06-21 14:00:02"),
            (8, 2, "user", "Je peux la reporter ?", "2026-06-21 14:03:00"),
            (9, 2, "assistant", "Contactez votre manager pour modifier la reunion.", "2026-06-21 14:03:01"),
        ]:
            AssistantMessage.objects.update_or_create(
                pk=msg_id,
                defaults={
                    "conversation_id": conv_id,
                    "role": role,
                    "content": content,
                    "metadata": {},
                    "created_at": parse_dt(created),
                },
            )
        self.stdout.write("  Created chatbot conversations & messages")

        self.stdout.write(self.style.SUCCESS(
            "\nSeed data created successfully!\n"
            "All accounts use password: test123\n"
            "Run: python manage.py seed_data"
        ))
