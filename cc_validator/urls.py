from django.urls import path

from cc_validator import views

app_name = 'cc_validator'
urlpatterns = [
    path('validate_card', views.validate_card, name='validate_card'),
    path('generate_card', views.gen_random_card_number, name='generate_card'),
]
