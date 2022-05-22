from django.contrib import admin

from .models import Question
from .models import Map

admin.site.register(Question)
admin.site.register(Map)
