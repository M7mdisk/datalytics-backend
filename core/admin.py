from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Dataset, Column, Technique
from .managers import UserManager
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Dataset)
class DatasetInstanceAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")
    list_display_links = ("__str__",)
    readonly_fields = ["id", "uploaded_at", "status", "test"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "owner",
                    "description",
                    "file",
                    "test",
                    "status",
                    "uploaded_at",
                )
            },
        ),
    )

    def test(self, instance):
        return format_html(instance.df.to_html())
