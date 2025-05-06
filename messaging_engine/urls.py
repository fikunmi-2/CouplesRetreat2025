from django.urls import path
from . import views

urlpatterns = [
    path('create_template', views.create_template, name="message_template_create"),
    path('send_message', views.send_message, name="send_message"),
    path('edit_template/<message_id>', views.message_template_edit, name="message_template_edit"),
    path('view_templates', views.view_templates, name="view_templates"),
    path('delete_template/<message_id>', views.delete_template, name="delete_template"),
    path('update_template/<message_id>', views.update_template, name="update_template"),
    path('preview_template/<template_id>/<user_id>', views.render_template, name='preview_template'),
    path('validate_excel_template', views.validate_excel_template, name='validate_excel_template'),
    path('preview_template_excel', views.preview_template_excel, name='preview_template_excel'),
    path("message_dashboard", views.message_dashboard, name="message_dashboard"),
    path('message_detail/<int:message_id>', views.message_detail, name="message_detail"),
    path('message_log_detail/<int:log_id>', views.message_log_detail, name="message_log_detail"),
    path('delete_logs/<str:log_type>/<int:message_id>', views.delete_logs, name="delete_logs"),
    path('preview_template_custom', views.preview_template_custom, name='preview_template_custom'),
]