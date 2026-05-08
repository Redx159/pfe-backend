import os
import logging

import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

logger = logging.getLogger(__name__)

_initialized = False


def _init_firebase():
    global _initialized
    if _initialized:
        return
    base_dir = getattr(settings, "BASE_DIR", None)
    default_path = os.path.join(base_dir, "secrets", "firebase-credentials.json") if base_dir else None
    cred_path = os.environ.get("FIREBASE_CREDENTIALS") or default_path
    logger.info(f"Looking for Firebase credentials at: {cred_path}")
    if cred_path and os.path.exists(cred_path):
        logger.info("Found Firebase credentials, initializing...")
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _initialized = True
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Firebase init failed: {e}")
    else:
        logger.warning(f"Credentials not found at: {cred_path}")


def send_push_notification(fcm_token, title, body, data=None):
    _init_firebase()
    if not _initialized:
        logger.warning("Firebase not initialized, skipping push")
        return

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
        token=fcm_token,
    )
    try:
        response = messaging.send(message)
        logger.info(f"Push sent: {response}")
    except Exception as e:
        logger.error(f"Push failed: {e}")
