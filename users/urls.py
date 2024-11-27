from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, UserDetailView,
    ForgotPasswordView, ResetPasswordConfirmView, ChangePasswordView,create_school_application
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView , TokenBlacklistView
from .views import RetrieveSettingsView, UpdateSettingsView, student_dashboard,change_learning_type
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),  # For logging out
    path('settings/', RetrieveSettingsView.as_view(), name='retrieve-settings'),
    path('settings/update/', UpdateSettingsView.as_view(), name='update-settings'),
    path('student-dashboard/', student_dashboard, name='student-dashboard'),
    path('change-learning-type/', change_learning_type, name='change_learning_type'),
    path('submit-application/', create_school_application, name='submit_application'),

    
]
