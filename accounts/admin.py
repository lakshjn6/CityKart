from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

# Register your models here.
class accountAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_admin', 'is_active', 'date_joined', 'last_login')
    list_display_links = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account , accountAdmin)