from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Dataset
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    # comment this to remove password validation
    # def validate(self, data):
    #     password = data.get("password")
    #     errors = dict()
    #     try:
    #         validators.validate_password(password=password)
    #     except exceptions.ValidationError as e:
    #         errors["password"] = list(e.messages)
    #     if errors:
    #         raise serializers.ValidationError(errors)
    #     return super(UserSerializer, self).validate(data)
    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "email", "password"]


class DatasetSerializer(serializers.ModelSerializer):
    columns = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)
    size = serializers.IntegerField(source="file.size", read_only=True)

    class Meta:
        model = Dataset
        fields = ["file_name", "uploaded_at", "status", "size", "columns"]


class CreateDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["file"]
