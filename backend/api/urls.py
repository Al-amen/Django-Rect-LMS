from django.urls import path

from api import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    #Authentication Endpoints
    path('user/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', views.RegisterView.as_view(), name='register'),
    path('user/password-reset/<email>/',views.PasswordResetEmailVerifyAPIView.as_view()),
    path('user/password-change/',views.PasswordChangeAPIView.as_view()),
    path('user/profile/<user_id>/',views.ProfileAPIView.as_view()),
    path('user/change-password/',views.ChangePasswordAPIView.as_view()),

    #core Endpoints
    path('course/category',views.CategoryListAPIView.as_view()),



]