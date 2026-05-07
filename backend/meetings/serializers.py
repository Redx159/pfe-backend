from rest_framework import serializers
from django.utils import timezone

from .models import Meeting, MeetingParticipant
from employees.serializers import EmployeeSerializer


class MeetingParticipantSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = MeetingParticipant
        fields = [
            "id",
            "employee",
            "status",
            "responded_at",
        ]


class MeetingSerializer(serializers.ModelSerializer):

    created_by = EmployeeSerializer(read_only=True)
    participants = MeetingParticipantSerializer(
        many=True,
        read_only=True,
    )
    my_status = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "created_by",
            "is_online",
            "meeting_url",
            "location",
            "is_cancelled",
            "created_at",
            "participants",
            "my_status",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "is_cancelled",
            "created_at",
            "participants",
            "my_status",
        ]

    def get_my_status(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            try:
                participant = obj.participants.get(employee=request.user)
                return participant.status
            except MeetingParticipant.DoesNotExist:
                pass
        return None
