from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Dataset, Column
from django.utils.translation import gettext_lazy as _
from .models import User
import json
import pandas as pd


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

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CreateDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["file"]


class DatasetSerializer(serializers.ModelSerializer):
    columns = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)
    size = serializers.IntegerField(source="file.size", read_only=True)

    class Meta:
        model = Dataset
        fields = ["id", "file_name", "uploaded_at", "status", "size", "columns"]


class ColumnSerializer(serializers.ModelSerializer):

    applied_techniques = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        read_only=True,
    )

    class Meta:
        model = Column
        fields = ["name", "applied_techniques"]


class DetailsDatasetSerializer(serializers.ModelSerializer):
    size = serializers.IntegerField(source="file.size", read_only=True)
    columns = ColumnSerializer(many=True, read_only=True)
    data = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = ["file_name", "uploaded_at", "status", "size", "columns", "data"]

    def get_data(self, dataframe):
        df = dataframe.df
        percent_missing = df.isnull().sum() * 100 / len(df)
        missing_value_df = pd.DataFrame(
            {"column_name": df.columns, "percent_missing": percent_missing}
        )
        missing_values_json = missing_value_df.to_json(orient="records")

        data = df.head(10).to_json(orient="records")
        return {"data": json.loads(data), "columns": json.loads(missing_values_json)}
