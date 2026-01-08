from django.urls import path
from .views import SignupView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='login'),  # This line is crucial
]