from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)  # Links to Django's built-in User model
    profile_pic= models.ImageField(upload_to='profile_pic/Teacher/',null=True,blank=True)  # Stores teacher's profile picture
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    status= models.BooleanField(default=False)  # Tracks if teacher is approved by admin
    salary=models.PositiveIntegerField(null=True)  # Teacher's salary set by admin
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name  # Returns teacher's full name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name