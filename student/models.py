from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)  # Links to Django's built-in User model
    profile_pic= models.ImageField(upload_to='profile_pic/Student/',null=True,blank=True)  # Stores student's profile picture
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name  # Returns student's full name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name