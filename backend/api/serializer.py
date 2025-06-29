from api import models as api_models
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from userauths.models import Profile, User
from django.contrib.auth.password_validation import validate_password

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.full_name
        token['email'] = user.email
        token['username'] = user.username
        try:
            token['teacher_id'] = user.teacher.id
        except:
            token['teacher_id'] = 0

        return token
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True,validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password2']
    
    def validate(self, attr):
        if attr['password'] != attr['password2']:
            raise serializers.ValidationError("password","Password fields didn't match.")
        return attr
    
    def create(self, validated_data):
        full_name = validated_data['full_name']
        email = validated_data['email']
        password = validated_data['password']
        

        user = User.objects.create(full_name=full_name,email=email)

        email_username,_ = user.email.split("@")
        user.username = email_username
        user.set_password(password)
        user.save()

        return user
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__al__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Category
        fields = ['id','title','image','slug','course_count']

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Teacher
        fields = ['user','image','full_name','bio','facebook','twitter','linkedin','about','country','students','courses','review']


class VariantItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.VariantItem
        fields = "__al__"
    
    def __init__(self, *args, **kwargs):
        super(VariantItemSerializer,self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method =="POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

class QuestionAnswerMessageSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        model = api_models.QuestionAnswerMessage
        fields = '__all__'

class QuestionAnswerSerializer(serializers.ModelSerializer):
    message = QuestionAnswerMessageSerializer(many=True)
    profile  = ProfileSerializer(many=False)
 
    class Meta:
        model = api_models.QuestionAnswer
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Cart
        fields = '__all__'
    
    
    def __init__(self, *args, **kwargs):
        super(CartSerializer,self).__init__(args, **kwargs)
        request = self.context.get("request")

        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class CartOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.CartOrderItem
        fields = '__al__'

    
    
    def __init__(self, *args, **kwargs):
        super(CartOrderItemSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and request.method == "POST":
            self.Meta.depth = 0
        
        else:
            self.Meta.depth = 3


class CartOrderSerializer(serializers.ModelSerializer):
    order_items = CartOrderItemSerializer(many=True)

    class Meta:
        model = api_models.CartOrder
    
    
    def __init__(self, *args, **kwargs):
        super(CartOrderSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        
        else:
            self.Meta.depth = 3

class CertiFicateSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Certificate
        fields = '__all__'


class CompletedLessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.CompletedLesson
        fields = '__al__'

    
    def __init__(self, *args, **kwargs):
        super(CartOrderSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        
        else:
            self.Meta.depth = 3


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Note
        fields = '__all__'



class ReviewSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        model = api_models.Review
        fields = '__al__'

    def __init__(self, *args, **kwargs):
        super(ReviewSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

    
    







class CourseSerializer(serializers.ModelSerializer):
    pass