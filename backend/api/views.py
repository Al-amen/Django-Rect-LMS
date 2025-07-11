from django.shortcuts import render, redirect
import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import models
from django.db.models.functions import ExtractMonth
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
import requests
import stripe.error


from api import models as api_models
from api import serializer as api_serializer
from userauths.models import Profile, User



from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics,status,viewsets
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, APIView

from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import stripe


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

            link = f"http://127.0.0.1:8000/password-change/?otp={user.otp}&uuidb64={uuidb64}&refresh_token={refresh_token}"

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
            if user.check_password(old_password):
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
        user_id = self.kwargs.get('user_id')
        user = self.request.user
        print(user.id, user_id)
        if str(user.id) != str(user_id):
            raise PermissionDenied("You cannot access other users' profiles.")

        return Profile.objects.get(user=user)
        


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
        from django.shortcuts import get_object_or_404

        course = get_object_or_404(api_models.Course, course_id=course_id, platform_status="Published", teacher_course_status="Published")

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
            country_object = api_models.Country.objects.filter(name=country_name).first()
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
    

class CheckoutAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = api_models.CartOrder.objects.all()
    lookup_field = 'oid'



class CouponApplyAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = api_models.CartOrder.objects.all()
    lookup_field = 'oid'

    def create(self,request, *args, **kwargs):
        order_oid = request.data['oid']
        coupon_code = request.data['coupon_code']
        order = api_models.CartOrder.objects.filter(oid=order_oid).first()
        coupon = api_models.Coupon.objects.filter(code=coupon_code).first()


        if coupon:
            order_items = api_models.CartOrderItem.objects.filter(order=order, teacher=coupon.teacher)
            for i in order_items:
                if not coupon in i.coupons.all():
                    discount = i.total * (coupon.discount / 100)

                    i.total -= discount
                    i.price -= discount
                    i.saved += discount
                    i.applied_coupons = True

                    order.coupons.add(coupon)
                    order.total -= discount
                    order.sub_total -= discount
                    order.saved += discount

                    i.save()
                    order.save()
                    coupon.used_by.add(order.student)
                    return Response({"message":"Coupon Applied Successfully","icon": "success"},status=status.HTTP_200_OK)
                else:
                    return Response({"message":"Coupon Already Applied","icon": "error"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Invalid Coupon Code","icon": "error"},status=status.HTTP_400_BAD_REQUEST)
        


class StripeCheckoutAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        
        order_oid = self.kwargs['order_oid']
        order = api_models.CartOrder.objects.get(oid=order_oid)

        if not order:
            return Response({"message":"Order Not Found"},status=status.HTTP_404_NOT_FOUND)
        
        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=order.email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': order.full_name
                            },
                            'unit_amount': int(order.total * 100)
                        },
                        'quantity': 1
                    }
                ],
                mode='payment',
                success_url=settings.FRONTEND_SITE_URL + '/payment-success/' + order.oid + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.FRONTEND_SITE_URL + '/payment-failed/'
            )
            order.stripe_session_id = checkout_session.id
            return redirect(checkout_session.url)
        except stripe.error.StripeError as e:
            return Response({"message": f"Something went wrong when trying to make payment. Error: {str(e)}"})
            



def ger_access_token(client_id,secret_key):
    token_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    data = {'grant_type': 'client_credentials'}
    auth = (client_id, secret_key)
    response = requests.post(token_url, data=data, auth=auth)

    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return access_token
    else:
        raise Exception(f"Failed to get access token: {response.status_code}")
    

class PaymentSuccessAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        order_oid = request.data['order_id']
        session_id = request.data['session_id']
        paypal_order_id = request.data['paypal_order_id']

        print("order_oid ====", order_oid)
        print("session_id ====", session_id)
        print("paypal_order_id ====", paypal_order_id)

        order = api_models.CartOrder.objects.objects.get(oid=order_oid)
        order_items = api_models.CartOrderItem.objects.filter(order=order)


        #paypal payment success

        if paypal_order_id:
            paypal_api_url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {ger_access_token(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET_ID)}'

            }
            response = requests.get(paypal_api_url, headers=headers)

            if response.status_code == 200:
               paypal_order_data = response.json()
               paypal_payment_status = paypal_order_data.get('status')

               if paypal_payment_status == 'COMPLETED':
                   if order.payment_status == "Processing":
                       order.payment_staus = "Paied"
                       order.save()
                       api_models.Notification.objects.create(user=order.student,order=order,type="Course Enrollment Completed")
                       for item in order_items:
                           api_models.Notification.objects.create(teacher=item.teacher, order=order,order_item=item,type="New Order")
                           api_models.EnrolledCourse.objects.create(
                               course=item.corse,
                               user=order.student,
                               teacher=item.teacher,
                               order_item=item
                           )
                       return Response({"message":"Payment Success","icon":"success"},status=status.HTTP_200_OK)
                   else:
                       return Response({"message":"Payment Already Completed","icon":"info"},status=status.HTTP_200_OK)
               else:
                    return Response({"message":"Payment Failed","icon":"error"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message":"Failed to verify PayPal payment","icon":"error"},status=status.HTTP_400_BAD_REQUEST)
        #stripe payment success
        if session_id:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                if order.payment_status == "Processing":
                    order.payment_status = "Paied"
                    order.save()
                    api_models.Notification.objects.create(user=order.student, order=order, type="Course Enrollment Completed")
                    for item in order_items:
                        api_models.Notification.objects.create(teacher=item.teacher, order=order, order_item=item, type="New Order")
                        api_models.EnrolledCourse.objects.create(
                            course=item.course,
                            user=order.student,
                            teacher=item.teacher,
                            order_item=item
                        )
                    return Response({"message": "Payment Success", "icon": "success"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Payment Already Completed", "icon": "info"}, status=status.HTTP_200_OK)   
            else:
                return Response({"message": "Payment Failed", "icon": "error"}, status=status.HTTP_400_BAD_REQUEST)              



                            
                       
                       
class StudentSummaryAPIView(generics.ListAPIView):
    serializer_class = api_serializer.StudentSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        total_courses = api_models.EnrolledCourse.objects.filter(user=user).count()
        completed_lessons = api_models.CompletedLesson.objects.filter(user=user).count()
        achieved_certificates = api_models.Certificate.objects.filter(user=user).count()

        return [
            {
                "total_courses" : total_courses,
                "completed_lessons":completed_lessons,
                "achieved_certificates":achieved_certificates
            }
        ]
    
    def list(self,request,*args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)

class StudentCourseListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.EnrolledCourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        return api_models.EnrolledCourse.objects.filter(user=user)
    
    class StudentCourseDetailAPIView(generics.RetrieveAPIView):
         serializer_class = api_serializer.EnrolledCourseSerializer
         permission_classes = [AllowAny]
         lookup_field = 'enrollment_id'

         def get_object(self):
             user_id = self.kwargs['user_id']
             enrollment_id = self.kwargs['enrollment_id']

             user = User.objects.get(id=user_id)

             return api_models.EnrolledCourse.objects.get(user=user,enrollment_id=enrollment_id)
         

class StudentCourseCompletedCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CompletedLessionSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        variant_item_id = request.data['variant_item_id']

        user = User.object.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        variant_item = api_models.VariantItem.objects.get(variant_item_id=variant_item_id)
        completed_lesson = api_models.CompletedLesson.objects.filter(user=user, course=course, variant_item=variant_item).first()
        if completed_lesson:
            completed_lesson.delete()
            return Response({"message":"Course marked as not completed"})
        else:
            completed_lesson = api_models.CompletedLesson.objects.create(
                user=user,
                course=course,
                variant_item=variant_item
            )
            return Response({"message":"Course marked as completed"},status=status.HTTP_201_CREATED)

class StudentNoteCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.NoteSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']
        user = User.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        return api_models.Note.objects.filter(user=user,course=enrolled.course)
    
    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        enrolment_id = request.data['enrollment_id']
        title = request.data['title']
        note = request.data['note']

        user = User.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrolment_id=enrolment_id)

        api_models.Note.objects.create(
            user=user,
            course=enrolled.course,
            title=title,
            note=note
        )
        return Response({"message":"Note Created Successfully"},status=status.HTTP_201_CREATED)
    

class StudentNoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']
        note_id = self.kwargs['note_id']

        user = User.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        note = api_models.Note.objects.get(user=user,course=enrolled.course,id=note_id)
        return note
    

class StudentRateCourseCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        rating = request.data['rating']
        review = request.data['review']

        user = user.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)

        api_models.Review.objects.create(
            user=user,
            course=course,
            review=review,
            rating=rating,
            active=True
        )
        return Response({"message":"Review Created Successfully"},status=status.HTTP_201_CREATED)



class StudentRateCourseUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]


    def get_object(self):
        user_id = self.kwargs['user_id']
        review_id = self.kwargs['review_id']
        
        user = User.objects.get(id=user_id)
        review = api_models.Review.objects.get(user=user, id=review_id)

        return review

class StudentWishListListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.WishListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        return api_models.WishList.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        wishlist = api_models.WishList.objects.filter(user=user,course=course).first()

        if wishlist:
            wishlist.delete()
            return Response({"message":"Wishlist Deleted"},status=status.HTTP_201_CREATED)
        else:
            api_models.WishList.objects.create(
                user=user,course=course
            )
            return Response({"message":"Whishlist Created"},status=status.HTTP_201_CREATED)



class QuestionAnswerListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.QuestionAnswerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = api_models.Course.objects.get(id=course_id)
        return api_models.QuestionAnswer.objects.filter(course=course)
    
    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']
        user_id = request.data['user_id']
        title = request.data['title']
        message = request.data['message']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)

        question = api_models.QuestionAnswer.objects.create(
            course=course,
            user=user,
            title=title
        )
        api_models.QuestionAnswerMessage.objects.create(
            course=course,
            user=user,
            message=message,
            question=question
        )
        return Response({"message":"Group conversation Started"}, status=status.HTTP_201_CREATED)



class QuestionAnswerMessageSendAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.QuestionAnswerMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
       course_id = request.data['course_id']
       qa_id = request.data['qa_id']
       user_id = request.data['user_id']
       message = request.data['message']

       user = User.objects.get(id=user_id)
       course = api_models.Course.objects.get(id=course_id)
       question = api_models.QuestionAnswer.objects.get(qa_id=qa_id)
       api_models.QuestionAnswerMessage.objects.create(
           course=course,
           user=user,
           message=message,
           question=question
       )

       question_serializer = api_serializer.QuestionAnswerMessageSerializer(question)

       return Response({"message":"Message sent","question":question_serializer.data})
    


class TeacherSummaryAPIView(generics.ListAPIView):
    serializer_class = api_serializer.TeacherSummarySerializer
    permission_classes =[AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        one_month_ago = datetime.today() - timedelta(days=28)

        total_courses = api_models.Course.objects.filter(teacher=teacher).count()
        total_revenue = api_models.CartOrderItem.objects.filter(teacher=teacher, order__payment_status="Paid").aggregate(total_revenue=models.Sum("price"))['total_revenue'] or 0
        monthly_revenue = api_models.CartOrderItem.objects.filter(teacher=teacher,order__payment_status='Paid', date__gte=one_month_ago).aggregate(total_revenue=models.Sum("price"))['total_revenue'] or 0
        enrolled_courses = api_models.EnrolledCourse.objects.filter(teacher=teacher)
        unique_student_ids = set()
        students = []

        for course in enrolled_courses:
            if course.user_id not in unique_student_ids:
                user = User.objects.get(id=course.user_id)

                student = {
                    "full_name":user.profile.full_name,
                    "image":user.profile.image.url,
                    "country":user.profile.country,
                    "date":course.date
                }
                students.append(student)
                unique_student_ids.add(course.user_id)
        
        return [{
            "total_courses":total_courses,
            "total_revenue":total_revenue,
            "monthly_revenue":monthly_revenue,
            "total_students":len(students),
        }]
    
    def list(self,request,*args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)

        return Response(serializer.data)
    

class TeacherCourseListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CountrySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Course.objects.filter(teacher=teacher, platform_status="Published", teacher_course_status="Published")

class TeacherReviewListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Review.objects.filter(course__teacher=teacher)

class TeacherReviewDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        teacher_id = self.kwargs['teacher_id']
        review_id = self.kwargs['review_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Review.objects.get(id=review_id, course__teacher=teacher)
    


class TeacherStudentsListAPIView(viewsets.ViewSet):

    def list(self, request, teacher_id=None):
        
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        enrolled_courses = api_models.EnrolledCourse.objects.filter(teacher=teacher)
        
        students = []
        unique_student_ids = set()

        for course in enrolled_courses:
            if course.user_id not in unique_student_ids:
                user = User.objects.get(id=course.user_id)
                student = {
                    "full_name": user.profile.full_name,
                    "image": user.profile.image.url,
                    "country": user.profile.country,
                    "date": course.date
                }
                students.append(student)
                unique_student_ids.add(course.user_id)

        return Response(students)

@api_view(['GET'])
def TeacherAllMonthEarningAPIView(request, teacher_id):
    teacher = api_models.Teacher.objects.get(id=teacher_id)
    all_month_earnings = (
        api_models.CartOrderItem.objects
        .filter(teacher=teacher,order__payment_status="Paid")
        .annotate( month=ExtractMonth("date"))
        .values('month')
        .annotate(total_earning=models.Sum('price'))
        .order_by('month')
    )
    return Response(all_month_earnings)


class TeacherBestSellingCourseAPIView(viewsets.ViewSet):
    
    def list(self,request, teacher_id=None):
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        courses_with_total_price = []
        courses = api_models.Course.objects.filter(teacher=teacher)

        for course in courses:
            revenue = course.enrolledcourse_set.aggregate(total_price=models.Sum('order_item__price'))['total_price'] or 0
            sales = course.enrolledcourse_set.count()
            courses_with_total_price.append({
                "course_image": course.image.url,
                "course_name": course.title,
                "total_revenue": revenue,
                "total_sales": sales
            })
        return Response(courses_with_total_price)
    

class TeacherCourseOrdersListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CartOrderItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.CartOrderItem.objects.filter(teacher=teacher)
    
class TeacherQuestionAnswerListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.QuestionAnswerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.QuestionAnswer.objects.filter(course__teacher=teacher)
    

class TeacherCouponListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.CouponSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Coupon.objects.filter(teacher=teacher)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class TeacherCouponDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.CouponSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        teacher_id = self.kwargs['teacher_id']
        coupon_id = self.kwargs['coupon_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Coupon.objects.get(teacher=teacher, id=coupon_id)



    