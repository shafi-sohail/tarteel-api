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


class UserAyahSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAyah
        exclude = ['user']


class UserSurahSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSurah
        exclude = ['user']


class UserSessionSerializer(serializers.ModelSerializer):
    surahs = UserSurahSerializer(many=True)
    ayahs = UserAyahSerializer(many=True)

    class Meta:
        model = UserSession
        exclude = ['user']
        depth = 1
