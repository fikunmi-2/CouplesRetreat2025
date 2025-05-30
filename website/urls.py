from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('viewregistered', views.registered, name="view-registered"),
    path('register', views.register, name="register"),
    path('mark_present/<uuid:unique_id>', views.mark_present, name='mark_present'),
    path('view_registee/<uuid:unique_id>', views.view_registee, name='view_registee'),
    path('update_registee/<uuid:unique_id>', views.update_registee, name='update_registee'),
    path('delete_registee/<uuid:unique_id>', views.delete_registee, name='delete_registee'),
    path('pdf_registee/<uuid:unique_id>', views.pdf_registee, name='pdf_registee'),
    path('download_tag/<str:surname>/<uuid:unique_id>', views.download_tag, name='download_tag'),
    path('confirm_attendance/<surname>/<uuid:unique_id>/', views.confirm_attendance, name='confirm_attendance'),
    path('thank-you/<uuid:unique_id>/', views.thank_you, name='thank_you'),
    path('view_comments', views.view_comments, name='view_comments'),
    path('resources', views.resources, name='resources'),
    path('resources/manage', views.manage_resources, name='manage_resources'),
    path('resources/add', views.add_resource, name='add_resource'),
    path('resources/edit/<int:pk>', views.edit_resource, name='edit_resource'),
    path('resources/delete/<int:pk>', views.delete_resource, name='delete_resource'),
    path('upload_excel', views.upload_excel, name='upload_registered_excel'),
    path('export_excel', views.export_registered_excel, name='export_registered_excel'),
    path('privacy_policy', views.privacy_policy, name='privacy_policy'),
    path('breakouts/', views.breakout_admin_dashboard, name='breakout_admin_dashboard'),
    path('breakouts/create/', views.create_breakout, name='create_breakout'),
    path('breakouts/<int:breakout_id>/edit/', views.edit_breakout, name='edit_breakout'),
    path('breakouts/<int:breakout_id>/delete/', views.delete_breakout, name='delete_breakout'),
    path('choose_breakout/<uuid:unique_id>/', views.choose_breakout, name='choose_breakout'),
    path('welcome/<str:surname>/<uuid:unique_id>/', views.couple_welcome, name='couple_welcome'),

]
