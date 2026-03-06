from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'parent', 'order']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']
