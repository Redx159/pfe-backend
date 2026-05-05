from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Meeting, MeetingParticipant
from .serializers import (
    MeetingSerializer,
    MeetingParticipantSerializer,
)
from .permissions import CanManageMeetings


class MeetingViewSet(viewsets.ModelViewSet):

    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role in ("ADMIN", "HR", "MANAGER"):
            return Meeting.objects.all()

        return Meeting.objects.filter(
            participants__employee=user
        ).distinct()

    # ==========================
    # CREATE MEETING
    # ==========================

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ==========================
    # ADD PARTICIPANTS
    # ==========================

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[CanManageMeetings],
    )
    def invite(self, request, pk=None):

        meeting = self.get_object()

        employee_ids = request.data.get("employee_ids", [])

        created = []

        for emp_id in employee_ids:

            obj, _ = MeetingParticipant.objects.get_or_create(
                meeting=meeting,
                employee_id=emp_id,
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

        participant.status = status_value
        participant.responded_at = timezone.now()
        participant.save()

        return Response(
            MeetingParticipantSerializer(participant).data
        )

    # ==========================
    # CANCEL
    # ==========================

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[CanManageMeetings],
    )
    def cancel(self, request, pk=None):

        meeting = self.get_object()

        meeting.is_cancelled = True
        meeting.save()

        return Response({"success": True})
