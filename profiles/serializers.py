from rest_framework import serializers
from profiles.models import UserAyah, UserSurah, UserSession


class UserAyahListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAyah
        fields = ['ayah', 'count', 'created_at', 'updated_at']


class UserAyahDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAyah
        fields = ['user', 'ayah', 'count']


class UserSurahSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSurah
        fields = ['user' 'surah', 'count']


class UserSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSession
        fields = ['user', 'surahs', 'ayahs']
        depth = 1
