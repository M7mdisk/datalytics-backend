from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Dataset, Column

admin.site.register(User, UserAdmin)
admin.site.register(Dataset)
# admin.site.register(Column)
