from django.contrib import admin
from .models import product

class productAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'is_available', 'category', 'created_date', 'modified_date')
    prepopulated_fields = {'slug':('product_name',)}

# Register your models here.
admin.site.register(product, productAdmin)
