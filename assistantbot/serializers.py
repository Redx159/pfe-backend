from rest_framework import serializers

from .models import AssistantConversation, AssistantMessage


class AssistantMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantMessage
        fields = [
            "id",
            "role",
            "content",
            "metadata",
            "created_at",
        ]


class AssistantConversationSerializer(serializers.ModelSerializer):
    messages = AssistantMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AssistantConversation
        fields = [
            "id",
            "title",
            "created_at",
            "updated_at",
            "messages",
        ]


class AssistantSendMessageSerializer(serializers.Serializer):
    message = serializers.CharField(allow_blank=False, trim_whitespace=True)


class AssistantMobileResponseSerializer(serializers.Serializer):
    intent = serializers.CharField()
    message = serializers.CharField()
    cards = serializers.ListField(child=serializers.DictField(), required=False)
    actions = serializers.ListField(child=serializers.DictField(), required=False)
    quick_replies = serializers.ListField(child=serializers.DictField(), required=False)
    context = serializers.DictField(required=False)
