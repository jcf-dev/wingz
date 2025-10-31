from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "first_name",
            "last_name",
            "phone_number",
        ]
        read_only_fields = ["id"]

    def validate_username(self, value):
        """Validate username uniqueness"""
        if self.instance:
            # Update case - exclude current instance
            if (
                User.objects.exclude(id=self.instance.id)
                .filter(username=value)
                .exists()
            ):
                raise serializers.ValidationError(
                    "A user with this username already exists."
                )
        else:
            # Create case
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError(
                    "A user with this username already exists."
                )
        return value

    def validate_email(self, value):
        """Validate email uniqueness"""
        if self.instance:
            # Update case - exclude current instance
            if User.objects.exclude(id=self.instance.id).filter(email=value).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )
        else:
            # Create case
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )
        return value
