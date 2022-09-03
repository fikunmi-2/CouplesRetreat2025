from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('viewregistered', views.registered, name="view-registered"),
    path('register', views.register, name="register"),
    path('show_registee/<registered_id>', views.show_registee, name='show_registee'),
    path('search_record', views.search_record, name="search_record"),
    path('update_registee/<registered_id>', views.update_registee, name='update_registee'),
    path('delete_registee/<registered_id>', views.delete_registee, name='delete_registee'),
    path('pdf_registee/<registered_id>', views.pdf_registee, name='pdf_registee'),
]
