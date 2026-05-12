from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AssistantConversation, AssistantMessage
from .serializers import (
    AssistantConversationSerializer,
    AssistantSendMessageSerializer,
)
from .services import build_mobile_bootstrap, generate_assistant_reply


def get_or_create_default_conversation(user):
    conversation = (
        AssistantConversation.objects.filter(user=user).order_by("-updated_at", "-id").first()
    )
    if conversation:
        return conversation

    return AssistantConversation.objects.create(user=user)


def get_request_language(request):
    requested = request.query_params.get("lang") or request.headers.get("Accept-Language", "")
    return "en" if requested.lower().startswith("en") else "fr"


class AssistantConversationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        conversation = get_or_create_default_conversation(request.user)
        return Response(
            {
                "conversation": AssistantConversationSerializer(conversation).data,
                "assistant": build_mobile_bootstrap(
                    request.user,
                    get_request_language(request),
                ),
            }
        )


class AssistantMobileBootstrapView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(build_mobile_bootstrap(request.user, get_request_language(request)))


class AssistantSendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AssistantSendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = get_or_create_default_conversation(request.user)
        prompt = serializer.validated_data["message"].strip()

        AssistantMessage.objects.create(
            conversation=conversation,
            role="user",
            content=prompt,
        )

        assistant_reply = generate_assistant_reply(
            request.user,
            conversation,
            prompt,
        )

        assistant_message = AssistantMessage.objects.create(
            conversation=conversation,
            role="assistant",
            content=assistant_reply["message"],
            metadata={
                "intent": assistant_reply["intent"],
                "language": assistant_reply.get("language"),
                "cards": assistant_reply["cards"],
                "actions": assistant_reply["actions"],
                "quick_replies": assistant_reply["quick_replies"],
                "context": assistant_reply.get("context", {}),
            },
        )

        return Response(
            {
                "conversation": AssistantConversationSerializer(conversation).data,
                "message": {
                    "id": assistant_message.id,
                    "role": assistant_message.role,
                    "content": assistant_message.content,
                    "metadata": assistant_message.metadata,
                    "created_at": assistant_message.created_at,
                },
                "assistant": assistant_reply,
            },
            status=status.HTTP_200_OK,
        )


class AssistantResetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        AssistantConversation.objects.filter(user=request.user).delete()
        conversation = AssistantConversation.objects.create(user=request.user)
        return Response(AssistantConversationSerializer(conversation).data)
