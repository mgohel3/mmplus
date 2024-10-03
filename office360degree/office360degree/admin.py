from django.contrib import admin
from .models import Ad, AdType, AdSize, Booking

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'ad', 'contact_number', 'payment_status', 'created_at')
    list_filter = ('payment_status',)

admin.site.register(Booking, BookingAdmin)

admin.site.register(AdType)
admin.site.register(AdSize)