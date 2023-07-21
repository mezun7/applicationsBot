from django.urls import path

from telegramBot import views

app_name = 'telegramBot'


urlpatterns = [
    path('', views.home, name='home'),
]