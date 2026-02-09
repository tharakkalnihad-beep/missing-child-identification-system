from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class User_Profile(models.Model):
    USER = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    alternative_ph_no = models.CharField(max_length=255)
    id_proof = models.FileField(upload_to='user_id_proof/', null=True, blank=True)



class Police_Station(models.Model):
    USER = models.OneToOneField(User, on_delete=models.CASCADE)
    sho_id = models.CharField(max_length=255)
    station_name = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    approval_status = models.CharField(max_length=255)




  
class Case_Report(models.Model):
    USER_PROFILE = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=255)
    age = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    hair_color = models.CharField(max_length=255)
    height = models.CharField(max_length=255)
    scar_mark = models.CharField(max_length=255)
    dress_color = models.CharField(max_length=255)
    image = models.FileField(upload_to='missing_child/', null=True, blank=True)
    missing_place = models.CharField(max_length=255)
    details = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
    time = models.CharField(max_length=255)
    status = models.CharField(max_length=255)



class Missing_Child_Data(models.Model):
    POLICE_STATION = models.ForeignKey(Police_Station, on_delete=models.CASCADE)
    CASE_REPORT = models.ForeignKey(Case_Report, on_delete=models.CASCADE)
    progress = models.CharField(max_length=255)
   

class Complaint(models.Model):
    USER_PROFILE = models.ForeignKey(User_Profile, on_delete=models.CASCADE)
    complaint = models.CharField(max_length=255)
    reply = models.CharField(max_length=255, default="pending")
    date = models.CharField(max_length=255)




class Public_Upload(models.Model):
    MISSING_CHILD_DATA = models.ForeignKey(Missing_Child_Data, on_delete=models.CASCADE)
    photo = models.FileField(upload_to='captured_image/', null=True, blank=True)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
    time = models.CharField(max_length=255)



class Awareness(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    file = models.FileField(upload_to='awareness/', null=True, blank=True)
    date = models.CharField(max_length=255)
