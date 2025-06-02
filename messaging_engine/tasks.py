from celery import shared_task
from .messaging import send_message_to_recipient
from messaging_engine.models import Message
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@shared_task
def send_scheduled_message(message_id):
    logger.info("In CELERY TASK working")
    try:
        message = Message.objects.get(id=message_id)

        for recipient in message.recipients.all():
            send_message_to_recipient(recipient, message, message.delivery_method)

    except Message.DoesNotExist:
        return "Message not found"
    except Exception as e:
        return f"Error sending message: {str(e)}"

@shared_task
def send_immediate_message(message_id):
    try:
        message = Message.objects.get(id=message_id)

        for recipient in message.recipients.all():
            send_message_to_recipient(recipient, message, message.delivery_method)\

        # All recipients processed — now mark as sent
        message.status = "Sent"
        message.save()

    except Message.DoesNotExist:
        return "Message not found"
    except Exception as e:
        return f"Error sending message: {str(e)}"