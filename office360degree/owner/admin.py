from django.contrib import admin
from .models import CustomUser, Company, SBU, ContactPage, Zone, Schedule

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Company)
admin.site.register(SBU)
admin.site.register(ContactPage)
admin.site.register(Zone)
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['paper_code', 'publish_date', 'day_of_week', 'zone']