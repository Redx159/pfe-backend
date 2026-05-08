from datetime import date, timedelta


def count_workdays(start, end):
    days = 0
    current = start
    while current <= end:
        if current.weekday() < 5:
            days += 1
        current += timedelta(days=1)
    return days


def get_annual_history(employee, year):
    from leaves.models import LeaveRequest
    leaves = LeaveRequest.objects.filter(
        employee=employee,
        status="APPROVED",
        start_date__year=year,
    ).order_by("start_date")
    total_days = 0
    by_type = {}
    for lv in leaves:
        days = count_workdays(lv.start_date, lv.end_date)
        total_days += days
        by_type[lv.leave_type] = by_type.get(lv.leave_type, 0) + days
    return {
        "year": year,
        "total_days_used": total_days,
        "by_type": by_type,
        "leaves": [
            {
                "id": lv.id,
                "leave_type": lv.leave_type,
                "start_date": lv.start_date.isoformat(),
                "end_date": lv.end_date.isoformat(),
                "workdays": count_workdays(lv.start_date, lv.end_date),
                "status": lv.status,
            }
            for lv in leaves
        ],
    }


def get_projections(employee):
    today = date.today()
    year_end = date(today.year, 12, 31)
    year_start = date(today.year, 1, 1)

    history = get_annual_history(employee, today.year)
    cp_remaining = max(0, employee.cp_balance)
    rtt_remaining = max(0, employee.rtt_balance)

    pending_cp = 0
    pending_rtt = 0
    from leaves.models import LeaveRequest
    pending = LeaveRequest.objects.filter(
        employee=employee,
        status="PENDING",
        start_date__year=today.year,
    )
    for lv in pending:
        days = count_workdays(lv.start_date, lv.end_date)
        if lv.leave_type == "CP":
            pending_cp += days
        elif lv.leave_type == "RTT":
            pending_rtt += days

    return {
        "year": today.year,
        "cp": {
            "initial": 25,
            "used": history["by_type"].get("CP", 0),
            "pending": pending_cp,
            "remaining": cp_remaining,
        },
        "rtt": {
            "initial": 10,
            "used": history["by_type"].get("RTT", 0),
            "pending": pending_rtt,
            "remaining": rtt_remaining,
        },
        "projected_end_of_year": {
            "cp": cp_remaining - pending_cp,
            "rtt": rtt_remaining - pending_rtt,
        },
    }
