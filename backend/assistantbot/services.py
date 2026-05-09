import json
import os
import re
from datetime import datetime, time, timedelta
from urllib import error, request
from functools import lru_cache

from django.db.models import Q
from django.utils import timezone

from attendance.models import Attendance
from employees.models import Employee
from leaves.models import LeaveRequest
from meetings.models import Meeting

try:
    from thefuzz import fuzz, process
    HAS_FUZZY = True
except ImportError:
    HAS_FUZZY = False


MOBILE_ASSISTANT_INTENTS = {
    "attendance_status": {
        "label": "Pointage du jour",
        "examples": [
            "Est-ce que j'ai pointe aujourd'hui ?",
            "Ai-je oublie ma sortie ?",
        ],
    },
    "working_hours": {
        "label": "Horaires",
        "examples": [
            "Mes heures demain ?",
            "Quand commence ma journee ?",
        ],
    },
    "leave_balance": {
        "label": "Solde de conges",
        "examples": [
            "Combien me reste-t-il de CP ?",
            "Quel est mon solde RTT ?",
        ],
    },
    "leave_requests": {
        "label": "Demandes de conges",
        "examples": [
            "Mes prochains conges ?",
            "Mes demandes en attente ?",
        ],
    },
    "upcoming_meetings": {
        "label": "Reunions",
        "examples": [
            "Ma prochaine reunion ?",
            "Mes reunions aujourd'hui ?",
        ],
    },
    "hr_procedure": {
        "label": "Procedure RH",
        "examples": [
            "Comment demander un conge maladie ?",
            "Comment annuler une demande ?",
        ],
    },
    "profile": {
        "label": "Profil",
        "examples": [
            "Qui est mon manager ?",
            "Montre mon profil",
        ],
    },
}


MOBILE_ASSISTANT_USE_CASES = {
    "fr": MOBILE_ASSISTANT_INTENTS,
    "en": {
        "attendance_status": {
            "label": "Today's attendance",
            "examples": [
                "Did I check in today?",
                "Did I forget to check out?",
            ],
        },
        "working_hours": {
            "label": "Working hours",
            "examples": [
                "My hours tomorrow?",
                "When does my day start?",
            ],
        },
        "leave_balance": {
            "label": "Leave balance",
            "examples": [
                "How many paid leave days do I have left?",
                "What is my RTT balance?",
            ],
        },
        "leave_requests": {
            "label": "Leave requests",
            "examples": [
                "My next leave?",
                "My pending leave requests?",
            ],
        },
        "upcoming_meetings": {
            "label": "Meetings",
            "examples": [
                "My next meeting?",
                "My meetings today?",
            ],
        },
        "hr_procedure": {
            "label": "HR procedure",
            "examples": [
                "How do I request sick leave?",
                "How do I cancel a request?",
            ],
        },
        "profile": {
            "label": "Profile",
            "examples": [
                "Who is my manager?",
                "Show my profile",
            ],
        },
    },
}


TRANSLATIONS = {
    "fr": {
        "ai_scope": (
            "Je peux t'aider avec ton pointage, tes horaires, tes conges, tes reunions "
            "et les procedures RH."
        ),
        "greeting": "Bonjour {name}. Je suis ton assistant RH. Tu peux me demander ton solde de conges, ton pointage, tes reunions ou une procedure RH.",
        "thanks": "Avec plaisir. Je reste la si tu veux verifier ton pointage, tes conges ou ton agenda.",
        "out_of_scope": "Je suis specialise dans les sujets RH de cette application: pointage, horaires, conges, reunions et profil. Reformule ta demande sur l'un de ces sujets et je t'aide.",
        "leave_can_take": "Oui, ton solde {leave_type} actuel couvre {days} jour(s). Tu peux envoyer une demande.",
        "leave_cannot_take": "Pas encore: ton solde {leave_type} est de {balance} jour(s), donc il manque {missing} jour(s) pour demander {days} jour(s).",
        "leave_type_unknown": "Je peux verifier CP ou RTT. Precise le type de conge et le nombre de jours.",
        "profile_summary": "Ton profil: {name}, {position}, departement {department}. Manager: {manager}.",
        "profile_missing_manager": "Ton profil ne contient pas encore de manager hierarchique.",
        "attendance_none": "Tu n'as pas encore de pointage enregistre aujourd'hui.",
        "attendance_missing_checkout": "Oui, tu as pointe l'entree a {check_in}. Il manque encore ton pointage de sortie.",
        "attendance_done": "Tu as pointe aujourd'hui: entree {check_in}, sortie {check_out}.",
        "attendance_status": "Ton pointage du jour est enregistre avec le statut {status}.",
        "hours_missing_schedule_tomorrow": (
            "Je n'ai pas encore de table d'emploi du temps de travail pour demain. "
            "Je peux en revanche te montrer ton agenda et tes reunions a venir."
        ),
        "hours_started": "Tu as commence aujourd'hui a {check_in}.",
        "hours_no_checkin": "Je n'ai pas encore de pointage d'entree pour aujourd'hui.",
        "hours_next_meeting": "Ta prochaine reunion du jour est '{title}' a {start_label}.",
        "hours_no_meeting": "Aucune reunion n'est prevue aujourd'hui dans ton agenda.",
        "leave_balance": "Il te reste {cp} jours CP et {rtt} jours RTT.{warning}",
        "leave_low_warning": " Attention, au moins un solde est faible.",
        "leave_pending": "Tu as {count} demande(s) de conge en attente.",
        "leave_upcoming": "Ta prochaine absence approuvee est du {start} au {end}.",
        "leave_none": "Tu n'as pas de demande en attente.",
        "meeting_none": "Tu n'as aucune reunion a venir dans ton agenda.",
        "meeting_next": "Ta prochaine reunion est '{title}' le {start_label}.",
        "procedure_leave": (
            "Pour demander un conge, ouvre l'onglet Conges, choisis Nouvelle demande, "
            "selectionne les dates et le type de conge, ajoute un justificatif si besoin, puis valide. "
            "Une demande en attente peut etre annulee depuis son detail."
        ),
        "title_attendance": "Pointage du jour",
        "title_meeting_next": "Prochaine reunion",
        "title_leave_balance": "Solde de conges",
        "title_leave_next": "Prochain conge",
        "title_leave_pending": "Demande en attente",
        "title_leave_approved": "Conge approuve",
        "title_meeting": "Reunion",
        "title_leave_procedure": "Demande de conge",
        "title_profile": "Profil employe",
        "action_generate_qr": "Generer mon QR",
        "action_open_attendance": "Ouvrir le pointage",
        "action_generate_checkout": "Generer QR sortie",
        "action_history": "Voir l'historique",
        "action_schedule": "Voir mon planning",
        "action_new_leave": "Nouvelle demande",
        "action_open_leaves": "Ouvrir les conges",
        "action_view_requests": "Voir mes demandes",
        "action_open_calendar": "Ouvrir l'agenda",
        "action_request_leave": "Demander un conge",
        "action_attendance_short": "Pointage",
        "action_leaves_short": "Conges",
        "action_schedule_short": "Agenda",
        "qr_leave_balance": "Mon solde de conges",
        "qr_next_meeting": "Ma prochaine reunion",
        "qr_checked_in": "Ai-je pointe ?",
        "qr_attendance_history": "Historique pointage",
        "qr_hours_tomorrow": "Mes heures demain",
        "qr_my_requests": "Mes demandes",
        "qr_how_request": "Comment demander ?",
        "qr_meetings_today": "Reunions aujourd'hui",
        "qr_week_schedule": "Planning semaine",
        "msg_leave_balance": "Quel est mon solde de conges ?",
        "msg_next_meeting": "Ma prochaine reunion ?",
        "msg_checked_in": "Est-ce que j'ai pointe aujourd'hui ?",
        "msg_attendance_history": "Montre mon historique de pointage",
        "msg_hours_tomorrow": "Mes heures demain ?",
        "msg_my_requests": "Mes demandes de conges en attente ?",
        "msg_how_request": "Comment demander un conge ?",
        "msg_meetings_today": "Mes reunions aujourd'hui ?",
        "msg_week_schedule": "Mon planning de la semaine ?",
        "msg_profile": "Qui est mon manager ?",
        "step_open_leaves": "Ouvrir Conges",
        "step_new_request": "Choisir Nouvelle demande",
        "step_select_dates": "Selectionner dates et type",
        "step_attachment": "Ajouter un justificatif si necessaire",
        "step_submit": "Valider et suivre le statut",
    },
    "en": {
        "ai_scope": (
            "I can help with your attendance, working hours, leave, meetings, "
            "and HR procedures."
        ),
        "greeting": "Hi {name}. I am your HR assistant. You can ask me about your leave balance, attendance, meetings, or HR procedures.",
        "thanks": "You're welcome. I am here if you want to check attendance, leave, or your agenda.",
        "out_of_scope": "I specialize in HR topics inside this app: attendance, working hours, leave, meetings, and profile. Ask me about one of those and I will help.",
        "leave_can_take": "Yes, your current {leave_type} balance covers {days} day(s). You can submit a request.",
        "leave_cannot_take": "Not yet: your {leave_type} balance is {balance} day(s), so you are missing {missing} day(s) to request {days} day(s).",
        "leave_type_unknown": "I can check CP or RTT. Please specify the leave type and number of days.",
        "profile_summary": "Your profile: {name}, {position}, {department} department. Manager: {manager}.",
        "profile_missing_manager": "Your profile does not have a manager assigned yet.",
        "attendance_none": "You do not have an attendance record for today yet.",
        "attendance_missing_checkout": "Yes, you checked in at {check_in}. Your check-out is still missing.",
        "attendance_done": "You checked in today at {check_in} and checked out at {check_out}.",
        "attendance_status": "Today's attendance is recorded with status {status}.",
        "hours_missing_schedule_tomorrow": (
            "I do not have a work schedule table for tomorrow yet. "
            "I can still show your agenda and upcoming meetings."
        ),
        "hours_started": "You started today at {check_in}.",
        "hours_no_checkin": "I do not have a check-in record for today yet.",
        "hours_next_meeting": "Your next meeting today is '{title}' at {start_label}.",
        "hours_no_meeting": "No meeting is planned today in your agenda.",
        "leave_balance": "You have {cp} CP days and {rtt} RTT days left.{warning}",
        "leave_low_warning": " At least one balance is low.",
        "leave_pending": "You have {count} pending leave request(s).",
        "leave_upcoming": "Your next approved absence is from {start} to {end}.",
        "leave_none": "You have no pending leave requests.",
        "meeting_none": "You have no upcoming meetings in your agenda.",
        "meeting_next": "Your next meeting is '{title}' on {start_label}.",
        "procedure_leave": (
            "To request leave, open the Leave tab, choose New request, select the dates "
            "and leave type, attach a document if needed, then submit. A pending request "
            "can be cancelled from its detail screen."
        ),
        "title_attendance": "Today's attendance",
        "title_meeting_next": "Next meeting",
        "title_leave_balance": "Leave balance",
        "title_leave_next": "Next leave",
        "title_leave_pending": "Pending request",
        "title_leave_approved": "Approved leave",
        "title_meeting": "Meeting",
        "title_leave_procedure": "Leave request",
        "title_profile": "Employee profile",
        "action_generate_qr": "Generate my QR",
        "action_open_attendance": "Open attendance",
        "action_generate_checkout": "Generate check-out QR",
        "action_history": "View history",
        "action_schedule": "View my schedule",
        "action_new_leave": "New request",
        "action_open_leaves": "Open leave",
        "action_view_requests": "View my requests",
        "action_open_calendar": "Open agenda",
        "action_request_leave": "Request leave",
        "action_attendance_short": "Attendance",
        "action_leaves_short": "Leave",
        "action_schedule_short": "Agenda",
        "qr_leave_balance": "My leave balance",
        "qr_next_meeting": "My next meeting",
        "qr_checked_in": "Did I check in?",
        "qr_attendance_history": "Attendance history",
        "qr_hours_tomorrow": "My hours tomorrow",
        "qr_my_requests": "My requests",
        "qr_how_request": "How to request?",
        "qr_meetings_today": "Meetings today",
        "qr_week_schedule": "Week schedule",
        "msg_leave_balance": "What is my leave balance?",
        "msg_next_meeting": "My next meeting?",
        "msg_checked_in": "Did I check in today?",
        "msg_attendance_history": "Show my attendance history",
        "msg_hours_tomorrow": "My hours tomorrow?",
        "msg_my_requests": "My pending leave requests?",
        "msg_how_request": "How do I request leave?",
        "msg_meetings_today": "My meetings today?",
        "msg_week_schedule": "My schedule this week?",
        "msg_profile": "Who is my manager?",
        "step_open_leaves": "Open Leave",
        "step_new_request": "Choose New request",
        "step_select_dates": "Select dates and type",
        "step_attachment": "Attach a document if needed",
        "step_submit": "Submit and track the status",
    },
}


def translate(language, key, **kwargs):
    text = TRANSLATIONS.get(language, TRANSLATIONS["fr"]).get(key, TRANSLATIONS["fr"][key])
    return text.format(**kwargs) if kwargs else text


def normalize_text(value):
    return (
        value.lower()
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("à", "a")
        .replace("ù", "u")
        .replace("ç", "c")
        .replace("’", "'")
    )


def employee_display_name(employee):
    return employee.get_full_name() or employee.username


def iso_datetime(value):
    return value.isoformat() if value else None


def format_time(value):
    if not value:
        return None
    return timezone.localtime(value).strftime("%H:%M")


def get_scope_employees_for_assistant(user):
    if user.role in ("ADMIN", "HR"):
        return Employee.objects.all()

    if user.role == "MANAGER":
        return Employee.objects.filter(Q(id=user.id) | Q(manager=user)).distinct()

    return Employee.objects.filter(id=user.id)


def get_mobile_meetings_queryset(user):
    base = Meeting.objects.filter(is_cancelled=False).select_related("created_by").prefetch_related(
        "participants__employee"
    )

    if user.role in ("ADMIN", "HR"):
        return base

    return base.filter(Q(created_by=user) | Q(participants__employee=user)).distinct()


def serialize_meeting(meeting, user=None):
    participants = [
        {
            "id": participant.employee_id,
            "name": employee_display_name(participant.employee),
            "status": participant.status,
        }
        for participant in meeting.participants.all()
    ]
    current_user_participation = None
    if user:
        current_user_participation = next(
            (
                participant["status"]
                for participant in participants
                if participant["id"] == user.id
            ),
            None,
        )

    return {
        "id": meeting.id,
        "title": meeting.title,
        "description": meeting.description,
        "start_time": iso_datetime(meeting.start_time),
        "end_time": iso_datetime(meeting.end_time),
        "start_label": timezone.localtime(meeting.start_time).strftime("%d/%m %H:%M"),
        "organizer": employee_display_name(meeting.created_by),
        "participants": participants,
        "participation_status": current_user_participation,
        "mode": "DISTANTIEL" if "http" in meeting.description.lower() else "PRESENTIEL",
    }


def serialize_leave(leave):
    return {
        "id": leave.id,
        "type": leave.leave_type,
        "status": leave.status,
        "start_date": leave.start_date.isoformat(),
        "end_date": leave.end_date.isoformat(),
        "duration_days": leave.duration_days,
        "reason": leave.reason,
        "manager_comment": leave.manager_comment,
    }


def serialize_attendance(attendance):
    if not attendance:
        return None

    missing_checkout = bool(attendance.check_in and not attendance.check_out)
    return {
        "id": attendance.id,
        "date": attendance.date.isoformat(),
        "status": attendance.status,
        "check_in": iso_datetime(attendance.check_in),
        "check_in_label": format_time(attendance.check_in),
        "check_out": iso_datetime(attendance.check_out),
        "check_out_label": format_time(attendance.check_out),
        "work_duration": str(attendance.work_duration) if attendance.work_duration else None,
        "overtime_minutes": attendance.overtime_minutes,
        "missing_checkout": missing_checkout,
    }


def build_mobile_assistant_context(user):
    today = timezone.localdate()
    now = timezone.now()
    start_of_today = timezone.make_aware(datetime.combine(today, time.min))
    end_of_today = timezone.make_aware(datetime.combine(today, time.max))
    week_end = today + timedelta(days=7)

    scoped_employees = get_scope_employees_for_assistant(user)
    scoped_ids = list(scoped_employees.values_list("id", flat=True))

    personal_attendance = Attendance.objects.filter(employee=user).order_by("-date")
    today_attendance = personal_attendance.filter(date=today).first()
    personal_leaves = LeaveRequest.objects.filter(employee=user)
    personal_meetings = get_mobile_meetings_queryset(user)

    meetings_today = list(
        personal_meetings.filter(start_time__gte=now, start_time__lte=end_of_today)
        .order_by("start_time")[:5]
    )
    upcoming_meetings = list(personal_meetings.filter(start_time__gte=now).order_by("start_time")[:5])

    taken_this_year = {}
    for leave in personal_leaves.filter(status="APPROVED", start_date__year=today.year):
        taken_this_year[leave.leave_type] = taken_this_year.get(leave.leave_type, 0) + leave.duration_days

    return {
        "today": today.isoformat(),
        "now": now.isoformat(),
        "scope": "company" if user.role in ("ADMIN", "HR") else "team" if user.role == "MANAGER" else "personal",
        "current_user": {
            "id": user.id,
            "name": employee_display_name(user),
            "role": user.role,
            "department": user.department.name if user.department else None,
            "position": user.position,
            "hire_date": user.hire_date.isoformat() if user.hire_date else None,
            "manager": employee_display_name(user.manager) if user.manager else None,
            "cp_balance": user.cp_balance,
            "rtt_balance": user.rtt_balance,
        },
        "attendance": {
            "today": serialize_attendance(today_attendance),
            "recent": [serialize_attendance(item) for item in personal_attendance[:5]],
            "missing_checkout": bool(today_attendance and today_attendance.check_in and not today_attendance.check_out),
        },
        "leave": {
            "balances": {
                "CP": user.cp_balance,
                "RTT": user.rtt_balance,
            },
            "pending": [
                serialize_leave(leave)
                for leave in personal_leaves.filter(status="PENDING").order_by("start_date")[:5]
            ],
            "upcoming_approved": [
                serialize_leave(leave)
                for leave in personal_leaves.filter(status="APPROVED", end_date__gte=today).order_by("start_date")[:5]
            ],
            "history": [
                serialize_leave(leave)
                for leave in personal_leaves.order_by("-created_at")[:5]
            ],
            "taken_this_year": taken_this_year,
        },
        "meetings": {
            "today": [serialize_meeting(meeting, user) for meeting in meetings_today],
            "upcoming": [serialize_meeting(meeting, user) for meeting in upcoming_meetings],
        },
        "manager_scope": {
            "employees": scoped_employees.count(),
            "pending_leaves": LeaveRequest.objects.filter(
                employee_id__in=scoped_ids,
                status="PENDING",
            ).count(),
            "late_today": Attendance.objects.filter(
                employee_id__in=scoped_ids,
                date=today,
                status="LATE",
            ).count(),
            "absent_today": Attendance.objects.filter(
                employee_id__in=scoped_ids,
                date=today,
                status="ABSENT",
            ).count(),
        },
    }


def _fuzzy_match_keywords(text, keywords, threshold=75):
    if not HAS_FUZZY:
        return any(word in text for word in keywords)
    for kw in keywords:
        if fuzz.partial_ratio(kw, text) >= threshold:
            return True
    return False


INTENT_PATTERNS = {
    "greeting": [
        ["bonjour", "salut", "hello", "hi", "hey", "coucou", "good morning", "good evening", "bonsoir"],
        ["what's up", "how are you", "ca va", "comment ca va"],
    ],
    "thanks": [
        ["merci", "thanks", "thank you", "thx", "merci beaucoup"],
    ],
    "profile": [
        ["mon profil", "my profile", "qui suis-je", "who am i", "my position", "mon poste", "mon departement", "my department", "my manager", "mon manager"],
        ["manager", "profile", "poste", "position", "department", "departement"],
    ],
    "leave_planning": [
        ["peux-je", "puis-je", "can i", "can we", "possible", "est-ce que", "puis je", "i want", "je veux", "j aimerais", "i would like"],
    ],
    "attendance_status": [
        ["pointage", "pointe", "check in", "check-in", "check out", "check-out", "sortie", "entree", "mes pointages", "my attendance"],
        ["suis-je pointe", "did i check", "ai-je pointe", "have i checked"],
    ],
    "working_hours": [
        ["horaire", "heures", "journee", "travail", "working hour", "schedule", "my hour", "ma journee", "mon planning", "ma semaine", "this week", "cette semaine", "mon emploi du temps"],
        ["what time do i work", "quelle heure", "combien d heures"],
    ],
    "leave_balance": [
        ["solde", "balance", "reste", "left", "remaining", "combien de jours", "how many days"],
        ["mes conges", "my leave", "mes rtt", "my rtt"],
    ],
    "leave_requests": [
        ["mes demandes", "my requests", "mes conges", "my leaves", "leave status", "statut conge"],
        ["conge", "absence", "demande", "annuler", "leave", "request", "sick", "cancel"],
    ],
    "hr_procedure": [
        ["comment", "how to", "procedure", "aide", "help", "demander", "soumettre", "submit", "guide"],
        ["how do i", "comment faire", "marche a suivre"],
    ],
    "upcoming_meetings": [
        ["reunion", "meeting", "agenda", "planning", "calendrier", "evenement", "events", "my meetings", "mes reunions"],
        ["what meetings", "quand est la prochaine reunion", "next meeting"],
    ],
}


def detect_mobile_intent(prompt):
    normalized = normalize_text(prompt)

    if len(normalized.strip()) <= 3:
        return "greeting"

    # Check for leave-related secondary intent (for compound detection)
    is_leave_related = _fuzzy_match_keywords(
        normalized,
        ["conge", "leave", "cp", "rtt", "vacation", "vacance", "absence", "maladie", "sick"]
    )
    is_planning = _fuzzy_match_keywords(
        normalized,
        ["peux-je", "puis-je", "can i", "can we", "possible", "est-ce que", "puis je", "i want", "je veux", "j aimerais", "i would like"]
    )

    # Score-based intent detection
    scores = {}
    for intent, pattern_groups in INTENT_PATTERNS.items():
        score = 0
        for group in pattern_groups:
            if _fuzzy_match_keywords(normalized, group):
                score += 1
        if intent == "leave_planning" and is_planning and is_leave_related:
            score += 2
        if intent in ("leave_balance", "leave_requests") and is_leave_related:
            score += 1
        scores[intent] = score

    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    if best_score == 0:
        return "out_of_scope"

    # Refine leave vs balance vs planning vs procedure
    if best_intent in ("leave_requests", "leave_balance", "leave_planning"):
        if is_planning and is_leave_related:
            return "leave_planning"
        procedural_markers = ["how do i", "how to", "comment faire", "comment", "procedure"]
        if _fuzzy_match_keywords(normalized, procedural_markers):
            return "hr_procedure"
        balance_words = ["solde", "balance", "reste", "left", "remaining", "combien", "how many"]
        request_words = ["demande", "request", "status", "mes", "my", "annuler", "cancel", "statut"]
        if _fuzzy_match_keywords(normalized, balance_words):
            return "leave_balance"
        if _fuzzy_match_keywords(normalized, request_words):
            return "leave_requests"
        return "leave_balance"

    return best_intent if best_score >= 1 else "out_of_scope"


def detect_compound_intents(prompt):
    compound_delimiters = [" and ", " et ", " also ", " aussi ", " then ", " puis ", " ainsi que "]
    segments = [prompt]
    for delim in compound_delimiters:
        new_segments = []
        for seg in segments:
            new_segments.extend(seg.split(delim))
        segments = [s.strip() for s in new_segments if s.strip()]
    if len(segments) <= 1:
        return None
    intents = [detect_mobile_intent(s) for s in segments]
    intents = [i for i in intents if i not in ("greeting", "thanks", "out_of_scope")]
    if len(intents) >= 2:
        return intents
    return None


def detect_language(prompt):
    normalized = normalize_text(prompt)
    compact = normalized.strip()

    english_exact = {
        "thanks",
        "thank you",
        "thx",
        "ty",
        "hello",
        "hi",
        "hey",
        "ok thanks",
        "okay thanks",
        "thanks a lot",
    }
    french_exact = {
        "merci",
        "merci beaucoup",
        "bonjour",
        "salut",
        "coucou",
        "ok merci",
        "d'accord merci",
    }

    if compact in english_exact:
        return "en"
    if compact in french_exact:
        return "fr"

    english_markers = [
        "hello",
        "hi",
        "how",
        "can",
        "what",
        "when",
        "where",
        "tell",
        "did",
        "do i",
        "my ",
        "leave",
        "take",
        "meeting",
        "check in",
        "check-in",
        "check out",
        "check-out",
        "today",
        "tomorrow",
        "schedule",
        "hours",
        "days",
        "joke",
    ]
    french_markers = [
        "bonjour",
        "salut",
        "comment",
        "quel",
        "quand",
        "est-ce",
        "mes ",
        "mon ",
        "conge",
        "reunion",
        "pointe",
        "pointage",
        "aujourd",
        "demain",
        "horaire",
        "heures",
    ]
    english_score = sum(1 for marker in english_markers if marker in normalized)
    french_score = sum(1 for marker in french_markers if marker in normalized)
    return "en" if english_score > french_score else "fr"


def extract_query_context(prompt):
    normalized = normalize_text(prompt)
    today = timezone.localdate()

    if "demain" in normalized or "tomorrow" in normalized:
        return {"date_label": "tomorrow", "date": (today + timedelta(days=1)).isoformat()}
    if "semaine prochaine" in normalized or "next week" in normalized:
        return {"date_label": "next_week", "date": None}
    if "aujourd" in normalized or "today" in normalized:
        return {"date_label": "today", "date": today.isoformat()}

    return {"date_label": None, "date": None}


def extract_leave_planning_request(prompt):
    normalized = normalize_text(prompt)
    match = re.search(r"(\d+)\s*(?:jours?|days?)", normalized)
    days = int(match.group(1)) if match else None

    leave_type = None
    if "rtt" in normalized:
        leave_type = "RTT"
    elif "cp" in normalized or "paid" in normalized or "conge" in normalized or "leave" in normalized:
        leave_type = "CP"

    return {"days": days, "leave_type": leave_type}


def latest_assistant_intent(history):
    for item in reversed(history or []):
        metadata = item.get("metadata") or {}
        intent = metadata.get("intent")
        if item.get("role") == "assistant" and intent:
            return intent
    return None


def resolve_follow_up_intent(prompt, detected_intent, history):
    normalized = normalize_text(prompt).strip()
    if detected_intent not in ("out_of_scope", "mobile_overview"):
        return detected_intent

    follow_up_triggers = ["and", "et", "what about", "et pour", "also", "aussi", "et aussi", "what else"]
    agreement = ["yes", "oui", "ok", "d'accord", "sure", "yeah", "ouais", "yep", "go ahead"]

    if any(word in normalized for word in follow_up_triggers) or normalized in agreement or _fuzzy_match_keywords(normalized, follow_up_triggers + agreement):
        previous_intent = latest_assistant_intent(history)
        if previous_intent:
            return previous_intent

    return detected_intent


def build_card(card_type, title, data, action=None):
    return {
        "type": card_type,
        "title": title,
        "data": data,
        "action": action,
    }


def quick_replies_for_intent(intent, language):
    t = lambda key: translate(language, key)
    common = [
        {"label": t("qr_leave_balance"), "message": t("msg_leave_balance")},
        {"label": t("qr_next_meeting"), "message": t("msg_next_meeting")},
        {"label": t("qr_checked_in"), "message": t("msg_checked_in")},
    ]

    specific = {
        "attendance_status": [
            {"label": t("qr_attendance_history"), "message": t("msg_attendance_history")},
            {"label": t("qr_hours_tomorrow"), "message": t("msg_hours_tomorrow")},
        ],
        "leave_balance": [
            {"label": t("qr_my_requests"), "message": t("msg_my_requests")},
            {"label": t("qr_how_request"), "message": t("msg_how_request")},
        ],
        "upcoming_meetings": [
            {"label": t("qr_meetings_today"), "message": t("msg_meetings_today")},
            {"label": t("qr_week_schedule"), "message": t("msg_week_schedule")},
        ],
        "profile": [
            {"label": t("qr_leave_balance"), "message": t("msg_leave_balance")},
            {"label": t("qr_next_meeting"), "message": t("msg_next_meeting")},
        ],
        "out_of_scope": common,
        "greeting": common,
        "thanks": common,
    }

    return specific.get(intent, common)


def mobile_response(intent, message, cards=None, actions=None, context=None, language="fr"):
    return {
        "intent": intent,
        "language": language,
        "message": message,
        "cards": [],
        "actions": actions or [],
        "quick_replies": [],
        "context": context or {},
    }


def build_attendance_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    attendance = context["attendance"]["today"]
    cards = []

    if not attendance:
        return mobile_response(
            "attendance_status",
            t("attendance_none"),
            cards=[
                build_card(
                    "attendance_today",
                    t("title_attendance"),
                    {"date": context["today"], "status": "NOT_STARTED"},
                    {"type": "OPEN_QR", "label": t("action_generate_qr")},
                )
            ],
            actions=[{"type": "OPEN_ATTENDANCE", "label": t("action_open_attendance")}],
            language=language,
        )

    cards.append(build_card("attendance_today", t("title_attendance"), attendance))
    if attendance["missing_checkout"]:
        message = t("attendance_missing_checkout", check_in=attendance["check_in_label"])
        actions = [{"type": "OPEN_QR_CHECKOUT", "label": t("action_generate_checkout")}]
    elif attendance["check_out_label"]:
        message = t(
            "attendance_done",
            check_in=attendance["check_in_label"],
            check_out=attendance["check_out_label"],
        )
        actions = [{"type": "OPEN_ATTENDANCE_HISTORY", "label": t("action_history")}]
    else:
        message = t("attendance_status", status=attendance["status"])
        actions = [{"type": "OPEN_ATTENDANCE", "label": t("action_open_attendance")}]

    return mobile_response("attendance_status", message, cards=cards, actions=actions, language=language)


def build_working_hours_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    query = context.get("query", {})
    if query.get("date_label") == "tomorrow":
        return mobile_response(
            "working_hours",
            t("hours_missing_schedule_tomorrow"),
            cards=[
                build_card("meeting", t("title_meeting_next"), meeting, {"type": "OPEN_MEETING", "id": meeting["id"]})
                for meeting in context["meetings"]["upcoming"][:2]
            ],
            actions=[{"type": "OPEN_SCHEDULE", "label": t("action_schedule")}],
            context={"missing_data": ["work_schedule"]},
            language=language,
        )

    attendance = context["attendance"]["today"]
    meetings = context["meetings"]["today"]
    cards = []
    parts = []

    if attendance and attendance["check_in_label"]:
        parts.append(t("hours_started", check_in=attendance["check_in_label"]))
        cards.append(build_card("attendance_today", t("title_attendance"), attendance))
    else:
        parts.append(t("hours_no_checkin"))

    if meetings:
        next_meeting = meetings[0]
        parts.append(t("hours_next_meeting", title=next_meeting["title"], start_label=next_meeting["start_label"]))
        cards.append(build_card("meeting", t("title_meeting_next"), next_meeting, {"type": "OPEN_MEETING", "id": next_meeting["id"]}))
    else:
        parts.append(t("hours_no_meeting"))

    return mobile_response(
        "working_hours",
        " ".join(parts),
        cards=cards,
        actions=[{"type": "OPEN_SCHEDULE", "label": t("action_schedule")}],
        language=language,
    )


def build_leave_balance_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    balances = context["leave"]["balances"]
    upcoming = context["leave"]["upcoming_approved"]
    cards = [
        build_card(
            "leave_balance",
            t("title_leave_balance"),
            {
                "balances": balances,
                "low_balance_alerts": [
                    leave_type for leave_type, days in balances.items() if days <= 2
                ],
            },
            {"type": "OPEN_LEAVE_REQUEST", "label": t("action_new_leave")},
        )
    ]
    if upcoming:
        cards.append(build_card("leave", t("title_leave_next"), upcoming[0], {"type": "OPEN_LEAVE", "id": upcoming[0]["id"]}))

    warning = ""
    if balances["CP"] <= 2 or balances["RTT"] <= 2:
        warning = t("leave_low_warning")

    return mobile_response(
        "leave_balance",
        t("leave_balance", cp=balances["CP"], rtt=balances["RTT"], warning=warning),
        cards=cards,
        actions=[{"type": "OPEN_LEAVES", "label": t("action_open_leaves")}],
        language=language,
    )


def build_leave_requests_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    pending = context["leave"]["pending"]
    upcoming = context["leave"]["upcoming_approved"]

    if pending:
        message = t("leave_pending", count=len(pending))
    else:
        message = t("leave_none")

    return mobile_response(
        "leave_requests",
        message,
        actions=[{"type": "OPEN_LEAVES", "label": t("action_view_requests")}],
        language=language,
    )


def build_meetings_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    query = context.get("query", {})
    if query.get("date_label") == "today":
        meetings = context["meetings"]["today"]
    else:
        meetings = context["meetings"]["upcoming"]

    if not meetings:
        message = t("meeting_none")
    else:
        first = meetings[0]
        message = t("meeting_next", title=first["title"], start_label=first["start_label"])

    return mobile_response(
        "upcoming_meetings",
        message,
        actions=[{"type": "OPEN_SCHEDULE", "label": t("action_open_calendar")}],
        language=language,
    )


def build_hr_procedure_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    return mobile_response(
        "hr_procedure",
        t("procedure_leave"),
        cards=[
            build_card(
                "procedure",
                t("title_leave_procedure"),
                {
                    "steps": [
                        t("step_open_leaves"),
                        t("step_new_request"),
                        t("step_select_dates"),
                        t("step_attachment"),
                        t("step_submit"),
                    ]
                },
                {"type": "OPEN_LEAVE_REQUEST", "label": t("action_new_leave")},
            )
        ],
        actions=[{"type": "OPEN_LEAVE_REQUEST", "label": t("action_request_leave")}],
        language=language,
    )


def build_greeting_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    user = context["current_user"]
    return mobile_response(
        "greeting",
        t("greeting", name=user["name"]),
        cards=[
            build_card("attendance_today", t("title_attendance"), context["attendance"]["today"] or {"status": "NOT_STARTED"}),
            build_card("leave_balance", t("title_leave_balance"), {"balances": context["leave"]["balances"]}),
        ],
        actions=[
            {"type": "OPEN_ATTENDANCE", "label": t("action_attendance_short")},
            {"type": "OPEN_LEAVES", "label": t("action_leaves_short")},
            {"type": "OPEN_SCHEDULE", "label": t("action_schedule_short")},
        ],
        language=language,
    )


def build_thanks_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    return mobile_response("thanks", t("thanks"), language=language)


def build_out_of_scope_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    return mobile_response(
        "out_of_scope",
        t("out_of_scope"),
        actions=[
            {"type": "OPEN_ATTENDANCE", "label": t("action_attendance_short")},
            {"type": "OPEN_LEAVES", "label": t("action_leaves_short")},
            {"type": "OPEN_SCHEDULE", "label": t("action_schedule_short")},
        ],
        language=language,
    )


def build_profile_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    user = context["current_user"]
    manager = user["manager"] or t("profile_missing_manager")
    profile = {
        "id": user["id"],
        "name": user["name"],
        "role": user["role"],
        "position": user["position"],
        "department": user["department"],
        "hire_date": user["hire_date"],
        "manager": user["manager"],
    }
    return mobile_response(
        "profile",
        t(
            "profile_summary",
            name=user["name"],
            position=user["position"] or "-",
            department=user["department"] or "-",
            manager=manager,
        ),
        cards=[build_card("profile", t("title_profile"), profile)],
        language=language,
    )


def build_leave_planning_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    planning = context.get("leave_planning", {})
    days = planning.get("days")
    leave_type = planning.get("leave_type")
    balances = context["leave"]["balances"]

    if not days or not leave_type:
        return mobile_response(
            "leave_planning",
            t("leave_type_unknown"),
            cards=[build_card("leave_balance", t("title_leave_balance"), {"balances": balances})],
            actions=[{"type": "OPEN_LEAVE_REQUEST", "label": t("action_new_leave")}],
            language=language,
        )

    balance = balances.get(leave_type, 0)
    if balance >= days:
        message = t("leave_can_take", leave_type=leave_type, days=days)
    else:
        message = t("leave_cannot_take", leave_type=leave_type, balance=balance, missing=days - balance, days=days)

    return mobile_response(
        "leave_planning",
        message,
        cards=[build_card("leave_balance", t("title_leave_balance"), {"balances": balances, "requested": planning})],
        actions=[{"type": "OPEN_LEAVE_REQUEST", "label": t("action_new_leave")}],
        language=language,
    )


def build_mobile_overview_response(context):
    language = context.get("language", "fr")
    t = lambda key, **kwargs: translate(language, key, **kwargs)
    cards = [
        build_card("attendance_today", t("title_attendance"), context["attendance"]["today"] or {"status": "NOT_STARTED"}),
        build_card("leave_balance", t("title_leave_balance"), {"balances": context["leave"]["balances"]}),
    ]
    if context["meetings"]["upcoming"]:
        cards.append(build_card("meeting", t("title_meeting_next"), context["meetings"]["upcoming"][0]))

    return mobile_response(
        "mobile_overview",
        t("ai_scope"),
        cards=cards,
        actions=[
            {"type": "OPEN_ATTENDANCE", "label": t("action_attendance_short")},
            {"type": "OPEN_LEAVES", "label": t("action_leaves_short")},
            {"type": "OPEN_SCHEDULE", "label": t("action_schedule_short")},
        ],
        language=language,
    )


LOCAL_INTENT_BUILDERS = {
    "greeting": build_greeting_response,
    "thanks": build_thanks_response,
    "out_of_scope": build_out_of_scope_response,
    "attendance_status": build_attendance_response,
    "working_hours": build_working_hours_response,
    "leave_balance": build_leave_balance_response,
    "leave_planning": build_leave_planning_response,
    "leave_requests": build_leave_requests_response,
    "upcoming_meetings": build_meetings_response,
    "hr_procedure": build_hr_procedure_response,
    "profile": build_profile_response,
    "mobile_overview": build_mobile_overview_response,
}


def build_mobile_bootstrap(user, language="fr"):
    context = build_mobile_assistant_context(user)
    context["language"] = language
    response = build_mobile_overview_response(context)
    response["use_cases"] = MOBILE_ASSISTANT_USE_CASES.get(language, MOBILE_ASSISTANT_USE_CASES["fr"])
    response["context"]["user"] = context["current_user"]
    return response


def _merge_compound_responses(responses):
    """Merge multiple intent responses into one (message text only)."""
    combined_message = "\n\n".join(r["message"] for r in responses)
    result = dict(responses[-1])
    result["message"] = combined_message
    result["cards"] = []
    result["actions"] = []
    return result


def build_local_mobile_reply(user, prompt, context=None, history=None):
    assistant_context = context or build_mobile_assistant_context(user)
    assistant_context["language"] = detect_language(prompt)
    assistant_context["query"] = extract_query_context(prompt)
    assistant_context["leave_planning"] = extract_leave_planning_request(prompt)

    compound = assistant_context.get("compound_intents", [])
    if compound:
        responses = [
            LOCAL_INTENT_BUILDERS[intent](assistant_context)
            for intent in compound
            if intent in LOCAL_INTENT_BUILDERS
        ]
        if len(responses) >= 2:
            return _merge_compound_responses(responses)

    intent = resolve_follow_up_intent(prompt, detect_mobile_intent(prompt), history)
    return LOCAL_INTENT_BUILDERS[intent](assistant_context)


def build_system_prompt(user, context):
    language = context.get("language", "fr")
    return (
        "You are the mobile HR assistant for a Flutter employee hub. "
        "Answer only from the provided JSON context and the existing app procedures. "
        "Focus on the cahier use cases: attendance/working hours, leave balance and planning, "
        "leave request tracking, upcoming meetings, employee profile, and HR procedures. "
        "Be conversational, useful, and concise. If data is missing, say what is missing. "
        "For unrelated questions, politely redirect to HR app topics. "
        "Never invent company policy, schedules, meetings, balances, or approvals. "
        f"Reply language: {language}. "
        f"Current user role: {user.role}. Current scope: {context['scope']}."
    )


def call_openai_responses_api(user, prompt, context, history):
    api_key = os.environ.get("OPENAI_API_KEY")
    local_response = build_local_mobile_reply(user, prompt, context, history)
    if not api_key:
        return local_response

    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    ai_context = {
        "intent": local_response["intent"],
        "language": local_response["language"],
        "local_draft": local_response["message"],
        "cards_available": [
            {"type": card.get("type"), "title": card.get("title"), "data": card.get("data")}
            for card in local_response.get("cards", [])
        ],
        "actions_available": local_response.get("actions", []),
    }
    payload = {
        "model": model,
        "temperature": 0.2,
        "input": [
            {
                "role": "system",
                "content": [
                    {"type": "input_text", "text": build_system_prompt(user, context)},
                    {"type": "input_text", "text": f"Context JSON: {json.dumps(context, default=str)}"},
                    {
                        "type": "input_text",
                        "text": (
                            "Return only the best final user-facing message as plain text. "
                            "Do not return JSON. The backend will attach this structured envelope: "
                            f"{json.dumps(ai_context, default=str)}"
                        ),
                    },
                ],
            },
            *[
                {
                    "role": item["role"],
                    "content": [{"type": "input_text", "text": item["content"]}],
                }
                for item in history
            ],
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
    }

    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
    except error.HTTPError:
        return local_response
    except Exception:
        return local_response

    output_text = body.get("output_text")
    if not output_text:
        for item in body.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output_text = content.get("text", "").strip()
                    break

    if output_text:
        local_response["message"] = output_text.strip()

    return local_response


def generate_assistant_reply(user, conversation, prompt):
    context = build_mobile_assistant_context(user)
    history = list(
        conversation.messages.exclude(role="system")
        .order_by("-created_at", "-id")
        .values("role", "content", "metadata")[:10]
    )
    history.reverse()

    compound = detect_compound_intents(prompt)
    if compound:
        context["compound_intents"] = compound

    return call_openai_responses_api(user, prompt, context, history)
