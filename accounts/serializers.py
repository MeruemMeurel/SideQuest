from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
    )
    password_confirm = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "bio",
            "password",
            "password_confirm",
        )
        read_only_fields = (
            "id",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm": (
                        "The two passwords do not match."
                    )
                }
            )

        temporary_user = User(
            username=attrs.get("username", ""),
            email=attrs.get("email", ""),
        )

        validate_password(
            attrs["password"],
            user=temporary_user,
        )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        standard_users_group, _ = Group.objects.get_or_create(
            name="standard_users",
        )

        user.groups.add(standard_users_group)

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "bio",
            "created_at",
            "is_active",
        )
        read_only_fields = (
            "id",
            "created_at",
            "is_active",
        )
