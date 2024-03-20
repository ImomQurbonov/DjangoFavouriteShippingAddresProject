from django.urls import path
from accounts.views import RegisterAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='token_refresh'),
]