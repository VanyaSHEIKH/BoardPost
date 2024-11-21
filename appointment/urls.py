from django.urls import path,include
from .views import AppointmentView

app_name='appointments'
urlpatterns = [
    path('', AppointmentView.as_view(),name='make_appointment'),
]