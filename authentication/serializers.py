from django.contrib.auth import get_user_model
from rest_framework import serializers, validators, exceptions
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    # comment this to remove password validation
    # def validate(self, data):
    #     password = data.get("password")
    #     errors = dict()
    #     try:
    #         validate_password(password=password)
    #     except exceptions.ValidationError as e:
    #         errors["password"] = list(e.messages)
    #     if errors:
    #         raise serializers.ValidationError(errors)
    #     return super(UserSerializer, self).validate(data)

    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
