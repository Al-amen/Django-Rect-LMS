from django.contrib import admin
from django import forms

from api import models

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id','full_name', 'country')
    search_fields = ('full_name','country')
   

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['image'].required = False
        return form
admin.site.register(models.Teacher, TeacherAdmin)

admin.site.register(models.Category)
admin.site.register(models.Course)
admin.site.register(models.Variant)
admin.site.register(models.VariantItem)
admin.site.register(models.QuestionAnswer)
admin.site.register(models.QuestionAnswerMessage)
admin.site.register(models.Cart)
admin.site.register(models.CartOrder)
admin.site.register(models.CartOrderItem)
admin.site.register(models.Certificate)
admin.site.register(models.CompletedLesson)
admin.site.register(models.EnrolledCourse)
admin.site.register(models.Note)
admin.site.register(models.Review)
admin.site.register(models.Notification)
admin.site.register(models.Coupon)
admin.site.register(models.WishList)
admin.site.register(models.Country)

