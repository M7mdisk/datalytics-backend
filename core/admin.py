from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Dataset, MLModel
from .managers import UserManager
from django.utils.html import format_html


@admin.register(MLModel)
class MLModelInstanceAdmin(admin.ModelAdmin):
    readonly_fields = [
        "id",
        "created_at",
        "status",
    ]
    fields = (
        "id",
        "name",
        "created_at",
        "status",
        "dataset",
        "target",
        "features",
    )

    def get_status(self, obj):
        return obj.get_status_display()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Dataset)
class DatasetInstanceAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")
    list_display_links = ("__str__",)
    readonly_fields = ["id", "uploaded_at", "status", "df"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "owner",
                    "description",
                    "file",
                    "df",
                    "status",
                    "uploaded_at",
                )
            },
        ),
    )

    def get_status(self, obj):
        return obj.get_status_display()

    @admin.display(description="Table")
    def df(self, instance):
        if instance.file:
            return format_html(instance.df.head(10).to_html())
        return ""
