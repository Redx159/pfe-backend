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

    class Meta:
        model = Meeting
        fields = [
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "created_by",
            "is_cancelled",
            "created_at",
            "participants",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "is_cancelled",
            "created_at",
            "participants",
        ]
