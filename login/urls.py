from django.urls import path
from . import views

urlpatterns = [
    path('admin_login', views.admin_login, name="admin_login"),
    path('admin_logout', views.admin_logout, name="admin_logout"),
    path('create_user', views.create_user, name="create_user"),
    path('user_list', views.user_list, name="user_list"),
    path('edit_user/<int:user_id>/', views.edit_user, name="edit_user"),
    path('assign_labourers', views.assign_labourers, name="assign_labourers"),
    path('labourers/<int:user_id>/couples/', views.view_labourer_couples, name='view_labourer_couples'),
    path('labourer_dashboard', views.labourer_dashboard, name='labourer_dashboard'),
    path('add_note/<uuid:unique_id>/', views.add_note, name='add_note'),
    path('labourer_notes/', views.labourer_notes, name='labourer_notes'),

]