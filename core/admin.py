
from django.contrib import admin
from .models import *



admin.site.register(Manager)
admin.site.register(Agent)
admin.site.register(Transaction)
admin.site.register(AgentBalance)