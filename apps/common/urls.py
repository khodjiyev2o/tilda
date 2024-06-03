from django.urls import path
from apps.common.views import PaylovSuccessView

app_name = "common"

urlpatterns = [
    path("paylov/callback/", PaylovSuccessView.as_view(), name="paylov-success"),
]
