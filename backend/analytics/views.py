from io import BytesIO
from datetime import date, datetime

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.models import Attendance
from employees.models import Employee
from leaves.models import LeaveRequest


class DashboardStats(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        employees_total = Employee.objects.count()

        present_today = Attendance.objects.filter(
            date=today, status="ON_TIME"
        ).count()
        late_today = Attendance.objects.filter(
            date=today, status="LATE"
        ).count()
        absent_today = Attendance.objects.filter(
            date=today, status="ABSENT"
        ).count()

        on_leave_today = LeaveRequest.objects.filter(
            status="APPROVED",
            start_date__lte=today,
            end_date__gte=today,
        ).count()

        pending_leaves = LeaveRequest.objects.filter(
            status="PENDING"
        ).count()

        attendance_rate = 0.0
        if employees_total:
            attendance_rate = round(
                (present_today + late_today) / employees_total * 100, 1
            )

        monthly_qs = (
            Attendance.objects
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(
                total=Count("id"),
                present=Count("id", filter=Q(status="ON_TIME")),
                late=Count("id", filter=Q(status="LATE")),
                absent=Count("id", filter=Q(status="ABSENT")),
            )
            .order_by("month")
        )

        monthly_trend = []
        for entry in monthly_qs:
            m = entry["month"]
            total = entry["total"]
            present = entry["present"]
            late = entry["late"]
            absent = entry["absent"]
            rate = round((present + late) / total * 100, 1) if total else 0.0
            monthly_trend.append({
                "month": m.strftime("%Y-%m"),
                "rate": rate,
                "total": total,
                "present": present,
                "late": late,
                "absent": absent,
            })

        leave_by_type_qs = (
            LeaveRequest.objects
            .filter(status="APPROVED")
            .values("leave_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        leave_by_type = [
            {"type": entry["leave_type"], "count": entry["count"]}
            for entry in leave_by_type_qs
        ]

        dept_qs = (
            Employee.objects
            .values("department__name")
            .annotate(total=Count("id"))
            .order_by("department__name")
        )

        department_stats = []
        for entry in dept_qs:
            dept_name = entry["department__name"] or "Unassigned"
            total = entry["total"]
            present = Attendance.objects.filter(
                employee__department__name=entry["department__name"],
                date=today,
                status="ON_TIME",
            ).count()
            late = Attendance.objects.filter(
                employee__department__name=entry["department__name"],
                date=today,
                status="LATE",
            ).count()
            department_stats.append({
                "name": dept_name,
                "total": total,
                "present": present,
                "late": late,
            })

        return Response({
            "total_employees": employees_total,
            "present_today": present_today,
            "on_leave_today": on_leave_today,
            "late_today": late_today,
            "absent_today": absent_today,
            "pending_leaves": pending_leaves,
            "attendance_rate": attendance_rate,
            "monthly_trend": monthly_trend,
            "leave_by_type": leave_by_type,
            "department_stats": department_stats,
        })


class GenerateReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month_str = request.query_params.get("month")
        fmt = request.query_params.get("export_format", "pdf")

        if not month_str:
            month_str = timezone.localdate().strftime("%Y-%m")

        try:
            year, month = map(int, month_str.split("-"))
        except (ValueError, AttributeError):
            return Response(
                {"error": "Invalid month format, use YYYY-MM"},
                status=400,
            )

        attendances = Attendance.objects.filter(
            date__year=year, date__month=month
        ).select_related("employee")

        leaves = LeaveRequest.objects.filter(
            start_date__year=year, start_date__month=month,
            status="APPROVED",
        ).select_related("employee")

        if fmt == "pdf":
            return self._pdf_report(month_str, attendances, leaves, year, month)
        return self._html_report(month_str, attendances, leaves, year, month)

    def _pdf_report(self, month_str, attendances, leaves, year, month):
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            topMargin=20*mm, bottomMargin=20*mm,
        )
        styles = getSampleStyleSheet()

        elements = []
        title_style = ParagraphStyle(
            "Title2", parent=styles["Title"],
            alignment=TA_CENTER, fontSize=18, spaceAfter=6*mm,
        )
        elements.append(Paragraph(
            f"Attendance & Leave Report — {month_str}", title_style
        ))
        elements.append(HRFlowable(
            width="100%", thickness=1, color=colors.grey
        ))
        elements.append(Spacer(1, 6*mm))

        # Attendance summary
        elements.append(Paragraph(
            "<b>Attendance Summary</b>", styles["Heading2"]
        ))
        elements.append(Spacer(1, 3*mm))

        total_present = attendances.filter(status="ON_TIME").count()
        total_late = attendances.filter(status="LATE").count()
        total_absent = attendances.filter(status="ABSENT").count()
        total_records = attendances.count()

        summary_data = [
            ["Metric", "Count"],
            ["Total Records", str(total_records)],
            ["Present (On Time)", str(total_present)],
            ["Late", str(total_late)],
            ["Absent", str(total_absent)],
        ]
        summary_table = Table(summary_data, colWidths=[80*mm, 60*mm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 6*mm))

        # Leave summary
        elements.append(Paragraph(
            "<b>Approved Leaves</b>", styles["Heading2"]
        ))
        elements.append(Spacer(1, 3*mm))

        leave_data = [
            ["Employee", "Type", "Start", "End", "Days"],
        ]
        for lv in leaves:
            name = lv.employee.get_full_name() or lv.employee.username
            leave_data.append([
                name, lv.leave_type,
                lv.start_date.isoformat(),
                lv.end_date.isoformat(),
                str(lv.duration_days),
            ])

        if len(leave_data) > 1:
            leave_table = Table(
                leave_data, colWidths=[50*mm, 25*mm, 30*mm, 30*mm, 20*mm],
            )
            leave_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
            ]))
            elements.append(leave_table)
        else:
            elements.append(Paragraph(
                "No approved leaves for this period.", styles["Normal"]
            ))

        doc.build(elements)
        pdf_bytes = buf.getvalue()
        buf.close()

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="report-{month_str}.pdf"'
        )
        return response

    def _html_report(self, month_str, attendances, leaves, year, month):
        total_present = attendances.filter(status="ON_TIME").count()
        total_late = attendances.filter(status="LATE").count()
        total_absent = attendances.filter(status="ABSENT").count()
        total_records = attendances.count()

        rows = []
        for lv in leaves:
            name = lv.employee.get_full_name() or lv.employee.username
            rows.append(f"""
                <tr>
                    <td>{name}</td>
                    <td>{lv.leave_type}</td>
                    <td>{lv.start_date}</td>
                    <td>{lv.end_date}</td>
                    <td>{lv.duration_days}</td>
                </tr>
            """)

        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Report {month_str}</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
h1 {{ color: #2563eb; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
th {{ background: #2563eb; color: white; }}
tr:nth-child(even) {{ background: #f1f5f9; }}
</style></head>
<body>
<h1>Attendance &amp; Leave Report — {month_str}</h1>
<h2>Attendance Summary</h2>
<table>
<tr><th>Metric</th><th>Count</th></tr>
<tr><td>Total Records</td><td>{total_records}</td></tr>
<tr><td>Present (On Time)</td><td>{total_present}</td></tr>
<tr><td>Late</td><td>{total_late}</td></tr>
<tr><td>Absent</td><td>{total_absent}</td></tr>
</table>
<h2>Approved Leaves</h2>
<table>
<tr><th>Employee</th><th>Type</th><th>Start</th><th>End</th><th>Days</th></tr>
{''.join(rows) if rows else '<tr><td colspan="5">No approved leaves for this period.</td></tr>'}
</table>
</body></html>"""
        return HttpResponse(html)
