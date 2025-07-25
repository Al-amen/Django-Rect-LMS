from django.db import models
from userauths.models import User,Profile
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
#from moviepy.editor import VideoFileClip
from smart_selects.db_fields import ChainedForeignKey



LANGUAGE = (
    ('Arabic', 'Arabic'),
    ('Bengali', 'Bengali'),
    ('Chinese', 'Chinese'),
    ('Dutch', 'Dutch'),
    ('English', 'English'),
    ('French', 'French'),
    ('German', 'German'),
    ('Hindi', 'Hindi'),
    ('Italian', 'Italian'),
    ('Japanese', 'Japanese'),
    ('Korean', 'Korean'),
    ('Portuguese', 'Portuguese'),
    ('Russian', 'Russian'),
    ('Spanish', 'Spanish'),
    ('Turkish', 'Turkish'),
    ('Urdu', 'Urdu'),
)

LEVEL = (
    ('Beginner','Beginner'),
    ('Intemediate','Intemediate'),
    ('Advanced','Advanced'),
)

TEACHER_STATUS = (
    ('Draft','Draft'),
    ('Disabled','Disabled'),
    ('Published','Published')
)

PLATFORM_STATUS = (
    ('Review','Review'),
    ('Disabled','Disabled'),
    ('Rejected','Rejected'),
    ('Draft','Draft'),
    ('Published','Published'),
)

PAYMENT_STATUS = (
    ("Paid", "Paid"),
    ("Processing", "Processing"),
    ("Failed", "Failed"),
)

RATING = (
    (1, "1 Star"),
    (2, "2 Star"),
    (3, "3 Star"),
    (4, "4 Star"),
    (5, "5 Star"),
)


NOTI_TYPE = (
    ("New Order", "New Order"),
    ("New Review", "New Review"),
    ("New Course Question", "New Course Question"),
    ("Draft", "Draft"),
    ("Course Published", "Course Published"),
    ("Course Enrollment Completed", "Course Enrollment Completed"),
)

 

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to='course-file',  default='default-teacher.jpg', null=True, blank=True)
    full_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=500, null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name if self.full_name else self.user.full_name

    def students(self):
        return CartOrder.objects.filter(teacher=self)
    
    def course(self):
        return Course.objects.filter(teacher=self)

    def review(self):
        return Review.objects.filter(teacher=self).count()




class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to='course-file', default='category.jpg', null=True, blank=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True,null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def course_count(self):
        return Course.objects.filter(category=self).count()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)


class Course(models.Model):
    category = models.ForeignKey(Category,on_delete=models.SET_NULL, null=True,blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.CharField(max_length=1000, null=True, blank=True)
    image = models.ImageField(null=True,blank=True,upload_to='course-images')
    title = models.CharField(max_length=100,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2,default=0.00,blank=True)
    language = models.CharField(choices=LANGUAGE, default="English",max_length=100,null=True,blank=True)
    level = models.CharField(choices=LEVEL,default='Beginner', max_length=100, null=True,blank=True)
    platform_status = models.CharField(choices=PLATFORM_STATUS,default="Published",max_length=100, null=True,blank=True)
    teacher_course_status = models.CharField(choices=TEACHER_STATUS,default="Published",max_length=100)
    featured = models.BooleanField(default=False)
    course_id = ShortUUIDField(unique=True, null=True,blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True,max_length=300)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def save(self,*args, **kwargs):
            if not self.slug:
                self.slug = slugify(self.title) 
            
            super(Course,self).save(*args, **kwargs)
    
    def students(self):
        return EnrolledCourse.objects.filter(course=self)
    
    def curriculum(self):
        return Variant.objects.filter(course=self)

    def lectures(self):
        return VariantItem.objects.filter(variant__course=self)
    
    def average_rating(self):
        average_rating = Review.objects.filter(course=self,active=True).aggregate(average_rating=models.Avg('rating'))
        return average_rating.get('average_rating', 0)
    
    def rating_count(self):
        return Review.objects.filter(course=self,active=True).count()
    
    def reviews(self):
        return Review.objects.filter(course=self,active=True)

class Variant(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    variant_id = ShortUUIDField(unique=True,max_length=6, length=6, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return  self.title
    
    def variant_items(self):
        return VariantItem.objects.filter(variant=self)
    
    def items(self):
        return VariantItem.objects.filter(variant=self)



class VariantItem(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    variant = ChainedForeignKey(
        Variant,
        chained_field="course",
        chained_model_field="course",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=1000)
    description = models.TextField(null=True,blank=True)
    file = models.CharField(max_length=200,null=True, blank=True)
    duration = models.DurationField(null=True,blank=True)
    content_duration = models.CharField(max_length=1000, null=True,blank=True)
    preview = models.BooleanField(default=False)
    variant_item_id = ShortUUIDField(unique=True,max_length=20,length=6, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.variant.title} - {self.title}"
    
     # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     if self.file:
    #         clip = VideoFileClip(self.file.path)
    #         duration_seconds = clip.duration

    #         minutes, remainder = divmod(duration_seconds, 60)  

    #         minutes = math.floor(minutes)
    #         seconds = math.floor(remainder)

    #         duration_text = f"{minutes}m {seconds}s"
    #         self.content_duration = duration_text
    #         super().save(update_fields=['content_duration'])
    

class QuestionAnswer(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=1000, null=True, blank=True)
    qa_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    class Meta:
        ordering = ['-date']
    
    def message(self):
        return QuestionAnswerMessage.objects.filter(question=self)

    def profile(self):
        return Profile.objects.get(user=self.user) if self.user else None
    



class QuestionAnswerMessage(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionAnswer, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    qam_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    qa_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.user} - {self.course.title}"
    
    class Meta:
        ordering = ['-date']
    
    def profile(self):
        return Profile.objects.get(user=self.user) if self.user else None



class Cart(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    tax_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    cart_id = ShortUUIDField(length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title



class CartOrder(models.Model):
    student = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    teachers = models.ManyToManyField(Teacher, blank=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    tax_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    intial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    payment_status = models.CharField(choices=PAYMENT_STATUS, default="Processing", max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    coupons = models.ManyToManyField("api.Coupon", null=True, blank=True)
    stripe_session_id = models.CharField(max_length=1000, null=True, blank=True)
    oid = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ['date']


    def __str__(self):
        return f"Order {self.oid} by {self.student.email}" if self.student else f"Order {self.oid}"
    
    def order_items(self):
        return CartOrderItem.objects.filter(order=self)
    



class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE,related_name="orderitems")
    course = models.ForeignKey(Course, on_delete=models.CASCADE,related_name="order_item")
    teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    tax_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    coupons = models.ManyToManyField("api.Coupon", blank=True,)
    applied_coupons = models.BooleanField(default=False)
    oid = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']
    
    def order_id(self):
        return f"Order ID #{self.oid}"
    
    def payment_status(self):
        return f"{self.order.payment_status}"
    
    def __str__(self):
        return self.oid
    

class Coupon(models.Model):
    teacher = models.ForeignKey(Teacher,on_delete=models.SET_NULL, null=True, blank=True)
    used_by = models.ManyToManyField(User,blank=True)
    code = models.CharField(max_length=50)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.code
    


class WishList(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} - {self.course.title}" if self.user else self.course.title



class Country(models.Model):
    name = models.CharField(max_length=100)
    tax_rate = models.IntegerField(default=5)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name



class Certificate(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    certificate_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title


class CompletedLesson(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    variant_item = models.ForeignKey(VariantItem, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title


class EnrolledCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    enrollment_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title
    
    def lecture_count(self):
        return VariantItem.objects.filter(variant__course=self.course)
    
    def completed_lesson(self):
        return CompletedLesson.objects.filter(course=self.course, user=self.user)

    def curriculum(self):
        return Variant.objects.filter(course=self.course)
    
    def note(self):
        return Note.objects.filter(course=self.course, user=self.user)
    
    def question_answer(self):
        return QuestionAnswer.objects.filter(course=self.course)
    
    def review(self):
        return Review.objects.filter(course=self.course, user=self.user).first()
    


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    note_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        self.title

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    review = models.TextField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING, default=None)
    reply = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title
    
    def profile(self):
        return Profile.objects.get(user=self.user) if self.user else None
    



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(CartOrder, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(choices=NOTI_TYPE, max_length=100, null=True, blank=True)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.type