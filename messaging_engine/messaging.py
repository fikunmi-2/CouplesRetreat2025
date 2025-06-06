# messaging.py - Handling all the messaging functions (SMS, Whatsapp, Email)
import json

import requests
from django.conf import settings
import time

from messaging_engine.models import MessageLog
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import send_mail

SMARTSMS_API_URL = settings.SMARTSMS_API_URL
SMARTSMS_API_KEY = settings.SMARTSMS_API_KEY
SMARTSMS_SENDER_ID = settings.SMARTSMS_SENDER_ID
WHATSAPP_ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN

def send_sms(recipient, message_obj, message_text):
    # Logic to send SMS
    # Collect valid phone numbers
    phone_numbers = [recipient.phone_no_m, recipient.phone_no_f]
    phone_numbers = [num for num in phone_numbers if num]  # Filter out None values

    if not phone_numbers:
        error_message = f"Recipient {recipient.s_name} has no valid phone numbers"
        MessageLog.objects.create(
            recipient=recipient,
            message=message_obj,
            phone_number="",
            message_content=message_text,
            channel="SMS",
            status="Failure",
            response_data=json.dumps({"error": error_message}),
        )
        return

    for phone_no in phone_numbers:
        payload = {
            "to": phone_no,
            "message": message_text,
            "sender": SMARTSMS_SENDER_ID,
            "type": 0,
            "routing": 3,
            "token": SMARTSMS_API_KEY,
        }

        try:
            response = requests.post(SMARTSMS_API_URL, data=payload)
            response_data = response.json()  # Get the API response

            # If HTTP request fails, log and continue
            response.raise_for_status()

            # Check response for success
            status = "Success" if response_data.get("code") == 1000 else "Failure"

        except requests.exceptions.RequestException as e:
            status = "Failure"
            response_data = {"error": str(e)}

        except Exception as e:
            status = "Failure"
            response_data = {"error": f"Unexpected error: {str(e)}"}

        # Log the message delivery per phone number
        MessageLog.objects.create(
            recipient=recipient,
            message=message_obj,
            phone_number=phone_no,  # Log each phone number separately
            message_content=message_text,
            channel="SMS",
            status=status,
            response_data=json.dumps(response_data),  # Store API response
        )

        print("SMS response_data: ", response_data)

def emails_sent_today():
    today = now().date()
    return MessageLog.objects.filter(
        channel="Email",
        status="Success",
        created_at__date=today
    ).count()

def emails_sent_last_hour():
    one_hour_ago = now() - timedelta(hours=1)
    return MessageLog.objects.filter(
        channel="Email",
        status="Success",
        created_at__gte=one_hour_ago
    ).count()

def send_email(recipient, message_text, message_obj):
    subject = message_obj.template.title
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_emails = [recipient.email_m, recipient.email_f]
    recipient_emails = [email for email in recipient_emails if email]

    if not recipient_emails:
        MessageLog.objects.create(
            recipient=recipient,
            message=message_obj,
            phone_number="",
            message_content=message_text,
            channel="Email",
            status="Failure",
            response_data=json.dumps({"error": "No valid email addresses available"}),
        )
        return

    for email in recipient_emails:
        if emails_sent_today() >= 500:
            print("Daily email limit reached. Halting.")
            break

        while emails_sent_last_hour() >= 100:
            print("Hourly limit reached. Waiting 60 seconds...")
            time.sleep(60)

        status = "Failure"
        response_data = {}

        try:
            send_mail(
                subject=subject,
                message=message_text,
                from_email=from_email,
                recipient_list=[email],
                html_message=message_text,
            )
            status = "Success"
            print(f"Email sent to {email}")
        except Exception as e:
            response_data = {"error": str(e)}
            print(f"Error sending to {email}: {e}")

        MessageLog.objects.create(
            recipient=recipient,
            message=message_obj,
            phone_number=email,
            message_content=message_text,
            channel="Email",
            status=status,
            response_data=json.dumps(response_data),
        )

        time.sleep(3)  # Pause between sends

def send_whatsapp(recipient, message_text, message_obj):
    print(f"Sending WhatsApp to {recipient.s_name}: {message_text}")

    placeholders = {
        "{{unique_id}}": str(recipient.registered_ref),
        "{{s_name}}": recipient.s_name,
        "{{f_name_m}}": recipient.f_name_m,
        "{{phone_no_m}}": recipient.phone_no_m,
        "{{email_m}}": recipient.email_m,
        "{{f_name_f}}": recipient.f_name_f,
        "{{phone_no_f}}": recipient.phone_no_f,
        "{{email_f}}": recipient.email_f,
    }

    # Extract placeholders present in the template content
    extracted_placeholders = [
        match for match in placeholders.keys() if match in message_obj.template.content_email_whatsapp
    ]

    # Generate parameters with "name" field
    parameters = [
        {"type": "text", "parameter_name": ph.strip("{}"), "text": str(placeholders[ph])}
        for ph in extracted_placeholders
    ]

    # WhatsApp API endpoint and credentials
    WHATSAPP_API_URL = "https://graph.facebook.com/v21.0/491545590719661/messages"
    TEMPLATE_NAME = message_obj.template.title.lower().replace(" ", "_")  # Template name
    LANGUAGE_CODE = "en"  # Language code

    # Collect recipient's valid phone numbers
    phone_numbers = [recipient.phone_no_m, recipient.phone_no_f]
    phone_numbers = [num for num in phone_numbers if num]

    if not phone_numbers:
        print(f"Recipient {recipient.s_name} has no valid phone numbers for WhatsApp")

        # Log failure due to missing phone numbers
        MessageLog.objects.create(
            recipient=recipient,
            message=message_obj,
            phone_number="",
            message_content=message_text,
            channel="WhatsApp",
            status="Failure",
            response_data=json.dumps({"error": "No valid phone numbers available"}),
        )
        return

    for phone_no in phone_numbers:
        status = "Failure"
        response_data = {}

        try:
            # Prepare the message payload for WhatsApp API
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_no,
                "type": "template",
                "template": {
                    "name": TEMPLATE_NAME,
                    "language": {"code": LANGUAGE_CODE},
                    "components": [{"type": "body", "parameters": parameters}],
                }
            }

            # Set the headers for the API request
            headers = {
                'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
                'Content-Type': 'application/json',
            }

            # Send the POST request to WhatsApp API
            response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
            response_data = response.json()

            print("Whatsapp Response Data: ", response_data)

            # Check if response contains "messages" and "message_status"
            if "messages" in response_data and isinstance(response_data["messages"], list):
                message_status = response_data["messages"][0].get("message_status")
                if message_status == "accepted":
                    print(f"WhatsApp message sent successfully to {phone_no}")
                    status = "Success"
                else:
                    print(f"Failed to send WhatsApp message to {phone_no}. Status: {message_status}")
            else:
                # Handle API errors (e.g., missing template, authentication issues)
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                print(f"Failed to send WhatsApp message to {phone_no}. Error: {error_message}")

        except Exception as e:
            response_data = {"error": str(e)}
            print(f"Error sending WhatsApp message to {phone_no}: {e}")

        # Log message delivery attempt
        MessageLog.objects.create(
            recipient=recipient,
            message=message_obj,
            phone_number=phone_no,  # Store the phone number used
            message_content=message_text,
            channel="WhatsApp",
            status=status,
            response_data=json.dumps(response_data),
        )

def send_message_to_recipient(recipient, message, delivery_methods):
    print("Sending message to recipient {}")
    message_for_recipient = generate_message_for_recipient(message.template, recipient)
    for method in delivery_methods:
        if method == "SMS" and not message_for_recipient['sms_empty']:
            send_sms(recipient, message ,message_for_recipient['sms'])
            print("sending SMS message to recipient {}")
        elif method == "Email" and not message_for_recipient['email_whatsapp_empty']:
            send_email(recipient, message_for_recipient['email_whatsapp'], message)
            print("sending Email message to recipient {}")
        elif method == "WhatsApp" and not message_for_recipient['email_whatsapp_empty']:
            send_whatsapp(recipient, message_for_recipient['email_whatsapp'], message)
            print("sending WhatsApp message to recipient {}")

    # Update message status and save the change
    message.status = "In progress"
    message.save()

def generate_message_for_recipient(template, user):
    content_sms = template.content_sms
    content_email_whatsapp = template.content_email_whatsapp

    # Define placeholders and values for this user
    placeholders = {
        "{{unique_id}}": str(user.registered_ref),
        "{{s_name}}": user.s_name,
        "{{f_name_m}}": user.f_name_m,
        "{{phone_no_m}}": user.phone_no_m,
        "{{email_m}}": user.email_m,
        "{{f_name_f}}": user.f_name_f,
        "{{phone_no_f}}": user.phone_no_f,
        "{{email_f}}": user.email_f,
    }

    # Replace placeholders in both SMS and Email/WhatsApp content
    for placeholder, value in placeholders.items():
        content_sms = content_sms.replace(placeholder, value)
        content_email_whatsapp = content_email_whatsapp.replace(placeholder, value)

    # Return the customized message for this recipient
    return {
        "recipient_id": user.id,
        "sms": content_sms,
        "email_whatsapp": content_email_whatsapp,
        "sms_empty": not bool(content_sms.strip()),
        "email_whatsapp_empty": not bool(content_email_whatsapp.strip()),
        "phone_number": user.phone_no_m,  # Add phone number for reference
        "email": user.email_m,  # Add email for reference
    }

def send_verification_email(surname, first_name_male, first_name_female, email, code):
    subject = "Your Couples Retreat 2025 Verification Code"
    from_email = settings.DEFAULT_FROM_EMAIL
    message = f"""
    <p>Dear {first_name_male}/{first_name_female} {surname},</p>

    <p>Thank you for registering for <strong>Couples Retreat 2025</strong>.</p>

    <p>Your <strong>Registration Code</strong> is: <strong><u>{code}</u></strong></p>

    <p>Please use this code to log in to the portal, download your name tag, and access all resources provided for the retreat.</p>

    <p>We look forward to a refreshing and impactful experience together.</p>

    <p>Shalom,<br>
    <em>The Couples Retreat Team</em></p>
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[email],
            html_message=message,
        )
        return True, f"Verification code sent to email: {email}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def send_verification_sms(surname, first_name, phone_no, code):
    message = (
        f"Dear {surname}, your Registration ID is {code}. "
        "Use this to login to the portal to download your tag and access all resources. Shalom!"
    )

    payload = {
        "to": phone_no,
        "message": message,
        "sender": SMARTSMS_SENDER_ID,
        "type": 0,
        "routing": 3,
        "token": SMARTSMS_API_KEY,
    }

    try:
        response = requests.post(SMARTSMS_API_URL, data=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 1000:
            return True, f"Verification code sent to phone: +{phone_no}"
        else:
            print(f"SMS Response data: {data}")
            return False, f"SMS failed: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return False, f"Error sending SMS: {str(e)}"

# def send_email(recipient, message_text, message_obj):
#     # Logic to send Email
#     ses_client = boto3.client('ses', region_name='us-east-1', aws_access_key_id=settings.AWS_SES_ACCESS_KEY_ID,
#     aws_secret_access_key=settings.AWS_SES_SECRET_ACCESS_KEY)
#
#     sender_email = SENDER_EMAIL
#     subject = message_obj.template.title
#
#     # Collect recipient emails
#     recipient_emails = [recipient.email_m, recipient.email_f]
#     recipient_emails = [email for email in recipient_emails if email]  # Remove empty emails
#
#     if not recipient_emails:
#
#         # Log failure due to missing email addresses
#         MessageLog.objects.create(
#             recipient=recipient,
#             message=message_obj,
#             phone_number="",  # Not applicable for email
#             message_content=message_text,
#             channel="Email",
#             status="Failure",
#             response_data=json.dumps({"error": "No valid email addresses available"}),
#         )
#         return
#
#     for email in recipient_emails:
#         status = "Failure"
#         response_data = {}
#
#         try:
#             response = ses_client.send_email(
#                 Source=sender_email,
#                 Destination={'ToAddresses': [email]},
#                 Message={
#                     'Subject': {'Data': subject},
#                     'Body': {
#                         'Html': {'Data': message_text},
#                         'Text': {'Data': message_text},
#                     },
#                 }
#             )
#
#             response_data = response
#             http_status = response["ResponseMetadata"]["HTTPStatusCode"]
#
#             if http_status == 200:
#                 status = "Success"
#
#         except Exception as e:
#             response_data = {"error": str(e)}
#
#         # Log message delivery attempt
#         MessageLog.objects.create(
#             recipient=recipient,
#             message=message_obj,
#             phone_number=email,  # Store the email address used
#             message_content=message_text,
#             channel="Email",
#             status=status,
#             response_data=json.dumps(response_data),
#         )