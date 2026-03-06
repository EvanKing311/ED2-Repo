from django.contrib import admin
from .models import Command, SensorData, Message

admin.site.register(Command)
admin.site.register(SensorData)
admin.site.register(Message)

