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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Username: {}, Email: {}, Created: {}".format(
            self.get_username(), self.email, self.created_at)


class UserAyah(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    ayah = models.ForeignKey('quran.Ayah', on_delete=models.PROTECT)
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSurah(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    surah = models.ForeignKey('quran.Surah', on_delete=models.PROTECT)
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
