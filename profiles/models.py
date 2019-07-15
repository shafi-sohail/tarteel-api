from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    # Gender Choices
    MALE = 'male'
    FEMALE = 'female'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]
    # Recitation Choices
    HAFS = 'hafs'
    WARSH = 'warsh'
    OTHER = 'other'
    RECITATION_CHOICES = [
        (HAFS, 'Hafss'),
        (WARSH, 'Warsh'),
        (OTHER, 'Other'),
    ]
    # Fields
    session_id = models.CharField(max_length=32, blank=True)
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='DOB')
    ethnicity = models.CharField(max_length=32, blank=True, null=True)
    gender = models.CharField(max_length=32, choices=GENDER_CHOICES, default=MALE)
    recitation = models.CharField(max_length=32, choices=RECITATION_CHOICES, default=HAFS)
