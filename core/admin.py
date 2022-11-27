from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Dataset, Column
from .managers import UserManager


@admin.register(User)
class UserAdmni(admin.ModelAdmin):
    pass


admin.site.register(Dataset)
# admin.site.register(Column)
