from django.shortcuts import render
import random
from decimal import Decimal

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

def generate_random_otp(length=7):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
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


class CourseListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CourseSerializer
    queryset = api_models.Course.objects.filter(platform_status="Published",teacher_course_status="Published")
    permission_classes = [AllowAny]


class SearchCourseAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.GET.get('query')
        # learn lms
        return api_models.Course.objects.filter(title__icontains=query, platform_status="Published", teacher_course_status="Published")


class TeacherCourseDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]
    queryset = api_models.Course.objects.filter(platform_status="Published", teacher_course_status="Published")

    def get_object(self):
        course_id = self.kwargs['course_id']
        course = api_models.Course.get(course_id=course_id,platform_status="Published", teacher_course_status="Published")
        return course
    



class CartAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    queryset = api_models.Cart.objects.all()


    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']
        user_id = request.data['user_id']
        price = request.data['price']
        country_name = request.data['country_name']
        cart_id = request.data['cart_id']
       
        course = api_models.Course.objects.filter(id=course_id).first()

        if user_id != "undefined":
            user = User.objects.filter(id=user_id).first()
        else:
            user = None

        try:
            country_object = api_models.Country.objects.filter(name=country_name)
            country = country_object.name
        
        except:
            country_object = None
            country = "Bangladesh"

        if country_object:
            tax_rate = country_object.tax_rate / 100
        
        else:
            tax_rate = 0
        
        cart = api_models.Cart.objects.filter(cart_id=cart_id,course=course).first()

        if cart:
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_fee = Decimal(price) * Decimal(tax_rate)
            cart.country = country
            cart_id = cart_id
            cart.total = Decimal(cart.price) + Decimal(cart.tax_fee)
            cart.save()

            return Response({"message":"Cart Updated Sucessfully"},status=status.HTTP_200_OK)
        
        else:
            cart = api_models.Cart()
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_fee = Decimal(price) * Decimal(tax_rate)
            cart.country = country
            cart_id = cart_id
            cart.total = Decimal(cart.price) + Decimal(cart.tax_fee)
            cart.save()

            return Response({"message": "Cart Created Successfully"}, status=status.HTTP_201_CREATED)



class CartListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset =  api_models.Cart.objects.filter(cart_id=cart_id)

        return queryset
    

class CartItemDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']
        cart_item = api_models.Cart.objects.filter(cart_id=cart_id, id=item_id).first()

        if cart_item:
            return cart_item
        else:
            return None
    

class CartStatsAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    lookup_field = 'cart_id'

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = api_models.Cart.objects.filter(cart_id=cart_id)
        return queryset
    
    def get(self,request,*args, **kwargs):
        queryset = self.get_queryset()

        total_price  = 0.00
        total_tax = 0.00
        total_total = 0.00

        for cart_item in queryset:
            total_price += float(self.calculate_price(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            total_total += float(self.calculate_total((cart_item)),2)
        
        data = {
            "price":total_total,
            "tax":total_tax,
            "total":total_total,
        }

        return Response(data)
    

    def calculate_price(self,cart_item):
        return cart_item.price
    
    def calculate_tax(self,cart_item):
        return cart_item.tax_fee
    
    def calculate_total(self,cart_item):
        return cart_item.total


class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print(request.headers.get('Authorization'))
        full_name = request.data['full_name']
        email = request.data['email']
        country = request.data['country']
        cart_id = request.data['cart_id']
        user_id = request.user.id
        
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            user = None
        
        cart_items = api_models.Cart.objects.filter(cart_id=cart_id)

        total_price = Decimal(0.00)
        total_tax = Decimal(0.00)
        total_initial_total = Decimal(0.00)
        total_total = Decimal(0.00)

        order = api_models.CartOrder.objects.create(
            full_name=full_name,
            email=email,
            country=country,
            student=user
        )

        for c in cart_items:
            api_models.CartOrderItem.objects.create(
                order=order,
                course=c.course,
                price=c.price,
                tax_fee=c.tax_fee,
                total=c.total,
                initial_total=c.total,
                teacher=c.course.teacher

            )
            total_price += Decimal(c.price)
            total_tax += Decimal(c.tax_fee)
            total_initial_total += Decimal(c.total)
            total_total += Decimal(c.total)

            order.teacher.add(c.course.teacher)

        order.sub_total = total_price
        order.tax_fee = total_tax
        order.intial_total = total_initial_total
        order.total = total_total
        order.save()

        return Response({"message":"Order Created Successfully","order_oid":order.oid},status=status.HTTP_201_CREATED)




   





