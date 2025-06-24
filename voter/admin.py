from django.contrib import admin
from .models import Voter

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile_number', 'aadhaar_no', 'region', 'state')
    list_filter = ('state', 'region', 'district')
    search_fields = ('name', 'email', 'mobile_number', 'aadhaar_no')
    readonly_fields = ('aadhaar_no', 'password')  # Prevent editing of these fields
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'date_of_birth', 'mobile_number', 'email')
        }),
        ('Address Details', {
            'fields': ('address', 'pincode', 'region', 'state', 'district', 'current_place')
        }),
        ('System Generated', {
            'fields': ('aadhaar_no', 'password'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
