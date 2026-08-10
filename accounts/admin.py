from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'postal_code', 'phone_number', 'created_at')
    search_fields = ('user__username', 'user__email', 'address', 'phone_number')
