import ast

import openpyxl
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import make_aware
from pytz import timezone
from .messaging import send_message_to_recipient
from .tasks import send_scheduled_message, send_immediate_message

from website.models import Registered
from .forms import MessageTemplateForm
from .models import *
from django.contrib import messages
from datetime import datetime
from functools import wraps

import json
import pandas as pd

# Create your views here.

def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.warning(request, "You do not have permission to access this page.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@superuser_required
def create_template(request):
    if request.method == 'POST':
        form = MessageTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Message template created successfully.')
            return redirect('message_template_create')  # Redirect to the same page
        else:
            # If the form is invalid, re-render the page with the form and error messages
            return render(request, 'create_template.html', {'form': form})
    else:
        form = MessageTemplateForm()  # Ensure form is instantiated correctly

    # Always return a response
    return render(request, 'create_template.html', {'form': form})

@superuser_required
def message_template_edit(request, message_id):
    return render(request, 'edit_template.html', {})

@superuser_required
def send_message(request):
    if request.method == "GET":
        templates = MessageTemplate.objects.all()
        return render(request, 'send_message.html', {'templates': templates})

    if request.method == "POST":
        # try:
            data = request.POST
            excel_file = request.FILES.get('excel_file')

            # Validate the data
            validate_message_data(data, request)

            template = get_object_or_404(MessageTemplate, id=data.get('template_id'))

            # Create the message
            message = Message.objects.create(
                template=template,
                delivery_method=json.loads(data.get("delivery_method", "[]")),
                delivery_time=data.get("delivery_time"),
                schedule_date=data.get("scheduleDate") or None,
                schedule_time=data.get("scheduleTime") or None,
                status="Pending"
            )

            recipient_id = data.get("recipient_id")
            if recipient_id:
                registered_user = get_object_or_404(Registered, id=recipient_id)
                data = {
                    "registered_ref": registered_user.unique_id,
                    "s_name": registered_user.s_name,
                    "f_name_m": registered_user.f_name_m,
                    "phone_no_m": registered_user.phone_no_m,
                    "email_m": registered_user.email_m,
                    "f_name_f": registered_user.f_name_f,
                    "phone_no_f": registered_user.phone_no_f,
                    "email_f": registered_user.email_f,
                }

                # Add recipient if it's unique
                recipient, reason = add_recipient_if_unique(data, is_user=True)

                if recipient:
                    message.recipients.add(recipient)
                else:
                    return JsonResponse({"error": f"Recipient skipped: {reason}"}, status=400)
            else:
                recipient_source = data.get("recipientSource")
                if recipient_source == "excel":
                    result = process_excel_file(excel_file)
                    added_recipients = result['added']
                    if added_recipients:
                        message.recipients.add(*added_recipients)

                elif recipient_source == "db":
                    result = process_db()
                    added_recipients = result['added']
                    valid_recipients = Recipient.objects.filter(is_user=True, id__in=[r.id for r in added_recipients])
                    if valid_recipients:
                        message.recipients.add(*valid_recipients)


                elif recipient_source == "custom":

                    filter_field = data.get("filter_field")
                    filter_operator = data.get("filter_operator")
                    filter_value = data.get("filter_value")

                    if not filter_field or not filter_operator:
                        return JsonResponse({"error": "Custom filter field/operator is missing."}, status=400)

                    queryset_or_none, error = get_registered_queryset_from_filter(filter_field, filter_operator, filter_value)

                    if queryset_or_none is None:
                        return JsonResponse({"error": error}, status=400)

                    queryset = queryset_or_none

                    if not queryset.exists():
                        return JsonResponse({"error": "No records match the selected filter criteria."}, status=404)

                    added_recipients = []

                    for reg in queryset:

                        reg_data = {
                            "registered_ref": reg.unique_id,
                            "s_name": reg.s_name,
                            "f_name_m": reg.f_name_m,
                            "phone_no_m": reg.phone_no_m,
                            "email_m": reg.email_m,
                            "f_name_f": reg.f_name_f,
                            "phone_no_f": reg.phone_no_f,
                            "email_f": reg.email_f,
                        }

                        recipient, reason = add_recipient_if_unique(reg_data, is_user=True)

                        if recipient:
                            added_recipients.append(recipient)

                    if added_recipients:
                        message.recipients.add(*added_recipients)

                else:
                    return JsonResponse({"error": "Invalid recipient source."}, status=400)

            # Handle scheduling messages
            if message.schedule_date and message.schedule_time:
                # Convert to Nigeria timezone before scheduling
                schedule_date = datetime.strptime(str(message.schedule_date), "%Y-%m-%d").date()
                schedule_time = datetime.strptime(data.get("scheduleTime", "00:00"), "%H:%M").time()
                print(f"Type of message.schedule_date: {type(schedule_date)}")
                print(f"Type of message.schedule_time: {type(schedule_time)}")
                schedule_datetime = datetime.combine(schedule_date, schedule_time)
                NIGERIA_TZ = timezone("Africa/Lagos")
                schedule_datetime = NIGERIA_TZ.localize(schedule_datetime)

                print(f"Scheduling message for: {schedule_datetime} (Nigeria Time)")

                send_scheduled_message.apply_async(
                    args=[message.id],
                    eta=schedule_datetime
                )
            else:
                # Send immediately
                print(f"Immediate message for: {message.template.title} (Nigeria Time)")
                send_immediate_message.apply_async(args=[message.id])

            message.status = "Received"
            message.save()

            return JsonResponse({"message": "Message sending has been initiated.", "redirect_url": "/messaging_engine/message_dashboard"}, status=200)
            # return JsonResponse({"message": "Message scheduled successfully!"}, status=200)

        # except ValidationError as e:
        #     return JsonResponse({"error": e.message_dict}, status=400)
        # except Exception as e:
        #     return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)

def get_registered_queryset_from_filter(filter_field, filter_operator, filter_value):
    try:
        if filter_operator in ["true", "false"]:
            filter_value = True if filter_operator == "true" else False
            filter_kwargs = {f"{filter_field}": filter_value}

        elif filter_operator in ["Yes", "No"]:
            filter_kwargs = {f"{filter_field}": filter_operator}

        else:
            if not filter_value:
                return None, "Filter value is required for the selected filter."

            if filter_operator == "ne":
                filter_kwargs = {f"{filter_field}__exact": filter_value}
                queryset = Registered.objects.exclude(**filter_kwargs)
                return queryset, None
            else:
                filter_kwargs = {f"{filter_field}__{filter_operator}": filter_value}

        queryset = Registered.objects.filter(**filter_kwargs)
        return queryset, None

    except Exception as e:
        return None, str(e)

def process_excel_file(file):
    wb = openpyxl.load_workbook(file)
    sheet = wb.active

    added_recipients = []
    skipped_recipients = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        data = {
            "s_name": row[0],
            "f_name_m": row[1],
            "phone_no_m": row[2],
            "email_m": row[3],
            "f_name_f": row[4],
            "phone_no_f": row[5],
            "email_f": row[6],
        }

        recipient, reason = add_recipient_if_unique(data, is_user=False)
        if recipient:
            print("Here in recipient....: " + recipient.s_name)
            added_recipients.append(recipient)
        else:
            print(f"Skipped recipient: {data} - Reason: {reason}")
            skipped_recipients.append({"data": data, "reason": reason})

    print(f"Records added: {len(added_recipients)}")
    print(f"Records skipped: {len(skipped_recipients)}")

    return {"added": added_recipients, "skipped": skipped_recipients}

def process_db():
    registered_records = Registered.objects.all()
    added_recipients = []
    skipped_recipients = []

    for record in registered_records:
        data = {
            "registered_ref": record.unique_id,
            "s_name": record.s_name,
            "f_name_m": record.f_name_m,
            "phone_no_m": record.phone_no_m,
            "email_m": record.email_m,
            "f_name_f": record.f_name_f,
            "phone_no_f": record.phone_no_f,
            "email_f": record.email_f,
        }

        recipient, reason = add_recipient_if_unique(data, is_user=True)
        if recipient:
            added_recipients.append(recipient)
        else:
            skipped_recipients.append({"record": record, "reason": reason})

    print(f"Total records processed: {registered_records.count()}")
    print(f"Records added: {len(added_recipients)}")
    print(f"Records skipped: {len(skipped_recipients)}")

    return {"total": registered_records, "added": added_recipients, "skipped": skipped_recipients}

def add_recipient_if_unique(data, is_user):
    registered_ref = data.get("registered_ref", None)
    s_name = data.get("s_name")
    f_name_m = data.get("f_name_m")
    phone_no_m = data.get("phone_no_m")
    email_m = data.get("email_m")
    f_name_f = data.get("f_name_f")
    phone_no_f = data.get("phone_no_f")
    email_f = data.get("email_f")

    # Ensure at least one contact field is provided
    if not phone_no_m and not email_m and not f_name_m and not phone_no_f:
        return None, "Missing contact information"

    query = Q()
    if phone_no_m:
        query &= Q(phone_no_m=phone_no_m)
    if email_m:
        query &= Q(email_m=email_m)
    if phone_no_f:
        query &= Q(phone_no_f=phone_no_f)
    if email_f:
        query &= Q(email_f=email_f)

    # Check for duplicates
    existing_recipient = Recipient.objects.filter(query).first()

    if existing_recipient:
        # existing_recipient.registered_ref = registered_ref
        # existing_recipient.save()
        # print("Registered REF: ", existing_recipient.registered_ref)
        return existing_recipient, "Duplicate entry"

    # Create new recipient
    recipient = Recipient.objects.create(
        registered_ref=registered_ref,
        s_name=s_name,
        f_name_m=f_name_m,
        phone_no_m=phone_no_m,
        email_m=email_m,
        f_name_f=f_name_f,
        phone_no_f=phone_no_f,
        email_f=email_f,
        is_user=is_user
    )
    return recipient, None



def validate_message_data(data, request):
    print("Received data: ", data)
    errors = {}

    # Validate recipientSource
    recipient_source = data.get("recipientSource")
    if recipient_source not in ['db', 'excel', 'custom']:
        errors["recipient_source"] = "Invalid Recipient Source"

    # Validate template_id
    template_id = data.get('template_id')
    if template_id is None or not MessageTemplate.objects.filter(id=template_id).exists():
        errors["template_id"] = "Invalid template ID"

        # Validate delivery_method
        valid_methods = ['SMS', 'WhatsApp', 'Email']
        delivery_method = data.getlist('delivery_method')  # Get as list directly

        # If the value is a string that looks like a list, convert it to a real list
        if isinstance(delivery_method, list) and len(delivery_method) == 1:
            delivery_method_str = delivery_method[0]
            # Check if it's a string that looks like a list and remove unnecessary characters
            if isinstance(delivery_method_str, str) and delivery_method_str.startswith(
                    "[") and delivery_method_str.endswith("]"):
                # Remove the surrounding quotes, e.g., ["['SMS', WhatsApp]"] becomes ['SMS', WhatsApp]
                delivery_method_str = delivery_method_str[1:-1].strip()
                # Now split the string on commas
                delivery_method = [item.strip().strip("'") for item in delivery_method_str.split(',')]


        # Validate delivery_method
        if not set(delivery_method).intersection(valid_methods):
            errors["delivery_method"] = "At least one valid delivery method is required"

    # Validate delivery_time
    delivery_time = data.get("delivery_time")
    if delivery_time not in ['immediate', 'scheduled', 'recurring']:
        errors["delivery_time"] = "Invalid delivery time option"

    # Validate scheduleDate and scheduleTime
    if delivery_time == 'scheduled':
        try:
            datetime.strptime(data.get('scheduleDate', ''), '%Y-%m-%d')
            datetime.strptime(data.get('scheduleTime', ''), '%H:%M')
        except (ValueError, TypeError):
            errors["schedule"] = "Invalid schedule date or time"

    # Validate recurringData and recurringTime
    if delivery_time == 'recurring':
        try:
            datetime.strptime(data.get('recurringDate', ''), '%Y-%m-%d')
            datetime.strptime(data.get('recurringTime', ''), '%H:%M')
        except (ValueError, TypeError):
            errors["recurring"] = "Invalid recurring date or time"

    # Validate Excel file if recipientSource is 'excel'
    recipient_source = data.get("recipientSource")
    if recipient_source == "excel":
        if not request.FILES.get('excel_file'):
            errors["excel_file"] = "Excel file is required for recipient source 'excel'."
        else:
            # Call validate_excel_template function
            try:
                validation_response = validate_excel_template(request)
                validation_response_data = json.loads(validation_response.content)
                if "error" in validation_response_data:
                    errors["excel_file"] = validation_response_data.get("error", "Invalid Excel file.")
            except Exception as e:
                errors["excel_file"] = f"An error occurred while validating the Excel file, Try Again."

    # Raise ValidationError if errors exist
    if errors:
        raise ValidationError(errors)

@superuser_required
def render_template(request, template_id, user_id):
    # Fetch the template and user
    template = get_object_or_404(MessageTemplate, id=template_id)
    if int(user_id) != 0:
        user = get_object_or_404(Registered, id=user_id)
    else:
        user = Registered.objects.order_by("id").first()

    # Retrieve SMS and Email/WhatsApp content
    content_sms = template.content_sms
    content_email_whatsapp = template.content_email_whatsapp

    # Define the placeholders and their corresponding values from the user
    placeholders = {
        "{{unique_id}}": str(user.unique_id),
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

    return JsonResponse({
        "sms": content_sms,
        "email_whatsapp": content_email_whatsapp,
        "sms_empty": not bool(content_sms.strip()),
        "email_whatsapp_empty": not bool(content_email_whatsapp.strip()),
    })

@superuser_required
def preview_template_excel(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    template_id = request.POST.get("template_id")
    excel_file = request.FILES.get("excel_file")

    # Validate the Excel file
    validation_response = validate_excel_template(request)
    if validation_response.status_code != 200:
        return validation_response

    # Fetch the template
    template = get_object_or_404(MessageTemplate, id=template_id)
    content_sms = template.content_sms
    content_email_whatsapp = template.content_email_whatsapp

    # Parse Excel file and check for empty rows
    try:
        df = pd.read_excel(excel_file)
        non_empty_rows = df.dropna(how="all")
        # Extract the first non-empty row
        first_row = non_empty_rows.iloc[0]
        placeholders = {f"{{{{{col}}}}}": str(value) for col, value in first_row.items()}

    except Exception as e:
        return JsonResponse({"error": f"An error occurred while processing the file: {str(e)}"}, status=400)

    # Replace placeholders in the template content
    for placeholder, value in placeholders.items():
        content_sms = content_sms.replace(placeholder, value)
        content_email_whatsapp = content_email_whatsapp.replace(placeholder, value)

    return JsonResponse({
        "sms": content_sms,
        "email_whatsapp": content_email_whatsapp,
        "sms_empty": not bool(content_sms.strip()),
        "email_whatsapp_empty": not bool(content_email_whatsapp.strip()),
    })

@superuser_required
def preview_template_custom(request):
    filter_field = request.POST.get("filter_field")
    filter_operator = request.POST.get("filter_operator")
    filter_value = request.POST.get("filter_value")

    queryset, error = get_registered_queryset_from_filter(filter_field, filter_operator, filter_value)

    if error:
        return JsonResponse({"error": error}, status=400)

    match = queryset.first()

    if match:
        return JsonResponse({"success": True, "registered_id": match.id})
    else:
        return JsonResponse({"success": False, "message": "No matching record found, Try another Combination!!!"})

@superuser_required
def view_templates(request):
    templates = MessageTemplate.objects.all()
    return render(request, 'view_templates.html', {'templates': templates})

@superuser_required
def delete_template(request, message_id):
    # Ensure the template exists or return a 404 page
    template_to_delete = get_object_or_404(MessageTemplate, id=message_id)

    try:
        # Store the title for success message before deletion
        message_title = template_to_delete.title

        # Perform the deletion
        template_to_delete.delete()

        # Provide success feedback
        messages.success(request, f"Message template '{message_title}' deleted successfully.")
        return redirect('view_templates')
    except Exception as e:
        # Log the error (optional)

        # Provide error feedback
        messages.error(request, f"An error occurred while deleting the template. Please try again.")
        return HttpResponseServerError("An error occurred.")

@superuser_required
def update_template(request, message_id):
    template_to_update = get_object_or_404(MessageTemplate, id=message_id)
    message_title = template_to_update.title
    template_form  = MessageTemplateForm(request.POST or None, instance=template_to_update)
    if template_form.is_valid():
        template_form.save()
        messages.success(request, f"Message template '{message_title}' updated successfully.")
        return redirect('view_templates')
    messages.error(request, f"An error occurred while updating the template. Please try again.")
    return redirect('view_templates')

@superuser_required
def validate_excel_template(request):
    if request.method == "POST":
        excel_file = request.FILES.get("excel_file")
        if not excel_file:
            return JsonResponse({"error": "No File Uploaded"}, status=400)

        if not excel_file.name.endswith((".xlsx", ".xls")):
            return JsonResponse({"error": "Invalid Excel File"}, status=400)

        try:
            df = pd.read_excel(excel_file)
            df.columns = df.columns.str.lower()

            # Check if the DataFrame is empty
            if df.empty:
                return JsonResponse({"error": "The Excel file contains no data."}, status=400)

            # Check for empty rows
            non_empty_rows = df.dropna(how="all")
            if non_empty_rows.empty:
                return JsonResponse({"error": "The Excel file contains only empty rows."}, status=400)

            required_fields = [
                "s_name", "f_name_m", "phone_no_m", "email_m",
                "f_name_f", "phone_no_f", "email_f"
            ]
            missing_fields = [field for field in required_fields if field not in df.columns]

            if missing_fields:
                return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)} in Excel File"}, status=400)

            return JsonResponse({"success": "File is Valid"}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred while processing the file: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@superuser_required
def message_dashboard(request):
    messages_initiated = Message.objects.all().order_by('-created_at')

    context = {
        "messages_initiated": messages_initiated,
    }

    return render(request, 'message_dashboard.html', context)

@superuser_required
def message_detail(request, message_id):
    current_message = get_object_or_404(Message, id=message_id)

    message_logs = MessageLog.objects.filter(message=current_message).order_by('-created_at')

    context = {
        'current_message': current_message,
        'message_logs': message_logs,
    }

    return render(request, 'message_detail.html', context)

@superuser_required
def message_log_detail(request, log_id):
    log = get_object_or_404(MessageLog, id=log_id)

    try:
        response_data_json = json.dumps(json.loads(log.response_data), indent=4)
    except json.JSONDecodeError:
        response_data_json = log.response_data  # If not valid JSON, show raw text

    return render(request, 'message_log_detail.html', {
        'log': log,
        'response_data_json': response_data_json})

@superuser_required
def delete_logs(request, log_type, message_id):
    message = get_object_or_404(Message, id=message_id)

    if log_type == "all":
        logs = MessageLog.objects.filter(message=message)
    elif log_type == "success":
        logs = MessageLog.objects.filter(message=message, status="Success")
    elif log_type == "failure":
        logs = MessageLog.objects.filter(message=message, status="Failure")
    else:
        messages.error(request, "Invalid log type.")
        return redirect("message_detail", message_id=message.id)

    deleted_count, _ = logs.delete()

    if deleted_count > 0:
        messages.success(request, f"Deleted {deleted_count} {log_type} log(s).")
    else:
        messages.warning(request, f"No {log_type} logs found to delete.")

    return redirect("message_detail", message_id=message.id)