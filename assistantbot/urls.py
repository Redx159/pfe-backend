from django.urls import path

from .views import (
    AssistantConversationView,
    AssistantMobileBootstrapView,
    AssistantResetView,
    AssistantSendMessageView,
)


urlpatterns = [
    path("conversation/", AssistantConversationView.as_view(), name="assistant_conversation"),
    path("mobile/bootstrap/", AssistantMobileBootstrapView.as_view(), name="assistant_mobile_bootstrap"),
    path("message/", AssistantSendMessageView.as_view(), name="assistant_message"),
    path("reset/", AssistantResetView.as_view(), name="assistant_reset"),
]
