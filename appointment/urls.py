from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('appointment/', views.book_appointment, name='appointment'),
    path('nurse-lizan/', views.doctor_detail, name="doctor_detail"),
]