from django.shortcuts import render
import random

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.hashers import check_password

from api import models as api_models
from api import serializer as api_serializer
from userauths.models import Profile, User

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics,status,viewsets
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response


from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer

def generate_random_otp():
    otp = ''.join(str(random.randint(0,9)))
    return otp

class PasswordResetEmailVerifyAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs['email']

        user = User.objects.filter(email=email).first()

        if user:
            uuidb64 = user.pk
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh.access_token)
            user.refresh_token = refresh_token

            user.otp = generate_random_otp()
            user.save()

            link = f"http://127.0.0.1:8000/create-new-password/?otp={user.otp}&uuidb64={uuidb64}&refresh_token={refresh_token}"

            context = {
                "link":link,
                "username":user.username
            }

            subject = "Password Reset Email"
            text_body = render_to_string("email/password_reset.txt",context)
            html_body = render_to_string("email/password_reset.html", context)

            mgs = EmailMultiAlternatives(
                subject=subject,
                from_email=settings.FROM_EMAIL,
                to = [user.email],
                body=text_body
            )

            mgs.attach_alternative(html_body,"text/html")
            mgs.send()



class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer


    def create(self,request,*args, **kwargs):
        otp = request.data['otp']
        uuidb64 = request.data['uuidb64']
        password = request.data['password']

        user = User.objects.get(id=uuidb64,otp=otp)

        if user:
            user.set_password(password)
            user.save()

            return Response({"message":"Password Changed Successfully"},status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"User Does Not Exists"},status=status.HTTP_404_NOT_FOUND)
        

class ChangePasswordAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = api_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        
        user = User.objects.get(id=user_id)

        if user:
            if check_password(old_password,new_password):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password changed successfully","icon":"success"})
            else:
                return Response({"message":"Old Password is incorrect", "icon":"waring"})
        else:
            return Response({"message":"User does not exists","icon":"error"})
        




class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            user_id = self.kwargs['user_id']
            user = User.objects.get(id=user_id)
            return Profile.objects.get(user=user)
        except:
            return None
        


class CategoryListAPIView(generics.ListAPIView):
    queryset = api_models.Category.objects.filter(active=True)
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]






