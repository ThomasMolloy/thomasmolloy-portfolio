from django.urls import path
from . import views
from . import dash_app_code

urlpatterns = [
    path("", views.dash_app, name="dash_app")
]