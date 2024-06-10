from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.hashers import make_password


class UserProfileSerializer(serializers.ModelSerializer):
    # So that we dont need to input user data during form submission of new user
    # user = serializers.PrimaryKeyRelatedField(read_only=True)
    # profile_pic = serializers.Field(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('verified', 'dob', 'profile_pic')
        extra_kwargs = {'verified': {'read_only': True}}


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(many=False, read_only=True)
    dob = serializers.DateField(write_only=True)
    profile_pic = serializers.ImageField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_profile',
                  'password', 'dob', 'profile_pic', 'first_name', 'last_name')
        # So that we dont send password during user request
        extra_kwargs = {'password': {'write_only': True},
                        'first_name': {'required': True},
                        'last_name': {'required': True}}

    def create(self, validated_data):
        user_profile_data = {}
        user_profile_data['dob'] = validated_data.pop('dob')
        user_profile_data['profile_pic'] = validated_data.pop('profile_pic')
        # password is in plain text, need to change it to django encrpytion
        password = validated_data.pop('password')
        user = User.objects.create(
            **validated_data, password=make_password(password))
        UserProfile.objects.create(**user_profile_data, user=user)
        return user

    def update(self, instance, validated_data):
        user_profile_data = {}
        if 'dob' in validated_data:
            user_profile_data['dob'] = validated_data.pop('dob')
        if 'profile_pic' in validated_data:
            user_profile_data['profile_pic'] = validated_data.pop(
                'profile_pic')
        if 'password' in validated_data:
            validated_data['password'] = make_password(
                validated_data['password'])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update user profile
        user_profile = instance.user_profile

        for attr, value in user_profile_data.items():
            setattr(user_profile, attr, value)
        user_profile.save()

        return instance
