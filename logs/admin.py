from django.contrib import admin
from .models import *

# Register your models here.


class LogAdmin(admin.ModelAdmin):
    list_display = ["created_by", "id", "date_created", 'total']


class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "log_id", "amount"]


admin.site.register(Item, ItemAdmin)
admin.site.register(Log, LogAdmin)
