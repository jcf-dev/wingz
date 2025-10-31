from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        validators=[validate_password],
        allow_blank=False,
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        allow_blank=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "role",
            "first_name",
            "last_name",
            "phone_number",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "phone_number": {"required": True, "allow_blank": False},
            "username": {"max_length": 150},
            "email": {"max_length": 255},
        }

    def validate_username(self, value):
        """Validate username uniqueness"""
        if self.instance:
            if (
                User.objects.exclude(id=self.instance.id)
                .filter(username=value)
                .exists()
            ):
                raise serializers.ValidationError(
                    "A user with this username already exists."
                )
        else:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError(
                    "A user with this username already exists."
                )
        return value

    def validate_email(self, value):
        """Validate email uniqueness (case-insensitive)"""
        normalized_email = value.lower()

        if self.instance:
            if (
                User.objects.exclude(id=self.instance.id)
                .filter(email__iexact=normalized_email)
                .exists()
            ):
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )
        else:
            if User.objects.filter(email__iexact=normalized_email).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )
        return normalized_email

    def validate(self, attrs):
        """Validate password confirmation and other fields"""
        if not self.instance and "password" not in attrs:
            raise serializers.ValidationError(
                {"password": "Password is required for user creation."}
            )

        if "password" in attrs:
            if "password_confirm" not in attrs:
                raise serializers.ValidationError(
                    {"password_confirm": "Password confirmation is required."}
                )
            if attrs["password"] != attrs["password_confirm"]:
                raise serializers.ValidationError(
                    {"password_confirm": "Password fields didn't match."}
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create user with hashed password in atomic transaction"""
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update user in atomic transaction, handling password separately if provided"""
        instance = User.objects.select_for_update().get(pk=instance.pk)

        password = validated_data.pop("password", None)
        validated_data.pop("password_confirm", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
