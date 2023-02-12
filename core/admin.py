from django.contrib import admin
from .models import Dataset, Column
from django.utils.html import format_html

admin.site.register(Dataset)


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")
    list_display_links = ("__str__",)
