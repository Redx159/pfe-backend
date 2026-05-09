from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from employees.models import Employee

from .models import Meeting, MeetingParticipant
from .serializers import (
    MeetingSerializer,
    MeetingParticipantSerializer,
)
from .permissions import CanManageMeetings
from backend.cache_utils import cache_response


class MeetingViewSet(viewsets.ModelViewSet):

    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    @cache_response()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):

        user = self.request.user

        if user.role in ("ADMIN", "HR", "MANAGER"):
            return Meeting.objects.all().order_by("is_cancelled", "start_time")

        return Meeting.objects.filter(
            Q(participants__employee=user) | Q(created_by=user)
        ).distinct().order_by("is_cancelled", "start_time")

    # ==========================
    # CREATE MEETING
    # ==========================

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ==========================
    # FILTERS
    # ==========================

    @action(detail=False, methods=["get"])
    @cache_response()
    def upcoming(self, request):
        qs = self.get_queryset().filter(
            is_cancelled=False,
            start_time__gte=timezone.now(),
        ).order_by("start_time")
        return Response(MeetingSerializer(qs, many=True, context={"request": request}).data)

    @action(detail=False, methods=["get"])
    @cache_response()
    def active(self, request):
        now = timezone.now()
        qs = self.get_queryset().filter(
            is_cancelled=False,
            start_time__lte=now,
            end_time__gte=now,
        ).order_by("start_time")
        return Response(MeetingSerializer(qs, many=True, context={"request": request}).data)

    @action(detail=False, methods=["get"])
    @cache_response()
    def ended(self, request):
        qs = self.get_queryset().filter(
            is_cancelled=False,
            end_time__lt=timezone.now(),
        ).order_by("-end_time")
        return Response(MeetingSerializer(qs, many=True, context={"request": request}).data)

    @action(detail=False, methods=["get"])
    @cache_response()
    def cancelled(self, request):
        qs = self.get_queryset().filter(is_cancelled=True).order_by("-created_at")
        return Response(MeetingSerializer(qs, many=True, context={"request": request}).data)

    # ==========================
    # ADD PARTICIPANTS
    # ==========================

    @action(detail=True, methods=["post"])
    def invite(self, request, pk=None):

        meeting = self.get_object()

        if meeting.created_by_id != request.user.id:
            return Response(
                {"error": "You can only invite employees to meetings you created."},
                status=status.HTTP_403_FORBIDDEN,
            )

        employee_ids = request.data.get("employee_ids", [])
        if not isinstance(employee_ids, list) or not employee_ids:
            return Response(
                {"error": "Please provide at least one employee to invite."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        employee_qs = Employee.objects.filter(id__in=employee_ids)

        if request.user.role == "MANAGER":
            allowed_ids = set(
                Employee.objects.filter(manager=request.user).values_list("id", flat=True)
            )
        else:
            allowed_ids = set(employee_qs.values_list("id", flat=True))

        requested_ids = set(employee_qs.values_list("id", flat=True))
        disallowed_ids = requested_ids - allowed_ids

        if disallowed_ids:
            return Response(
                {
                    "error": "Managers can only invite employees they manage directly."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        created = []

        for employee in employee_qs:

            obj, _ = MeetingParticipant.objects.get_or_create(
                meeting=meeting,
                employee=employee,
            )
            created.append(obj)

        return Response(
            MeetingParticipantSerializer(created, many=True).data
        )

    # ==========================
    # RESPOND
    # ==========================

    @action(detail=True, methods=["post"])
    def respond(self, request, pk=None):

        meeting = self.get_object()

        status_value = request.data.get("status")

        if status_value not in ("ACCEPTED", "DECLINED"):
            return Response(
                {"error": "Invalid status"},
                status=400,
            )

        try:
            participant = MeetingParticipant.objects.get(
                meeting=meeting,
                employee=request.user,
            )
        except MeetingParticipant.DoesNotExist:
            return Response(
                {"error": "Not invited"},
                status=403,
            )

        if status_value == "DECLINED":
            reason = request.data.get("decline_reason", "").strip()
            participant.decline_reason = reason

        participant.status = status_value
        participant.responded_at = timezone.now()
        participant.save()

        return Response(
            MeetingParticipantSerializer(participant).data
        )

    # ==========================
    # CANCEL
    # ==========================

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):

        meeting = self.get_object()

        if meeting.created_by_id != request.user.id:
            return Response(
                {"error": "You can only cancel meetings you created."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if meeting.is_cancelled:
            return Response(
                {"error": "Meeting is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        meeting.is_cancelled = True
        meeting.save()

        return Response({"success": True})
