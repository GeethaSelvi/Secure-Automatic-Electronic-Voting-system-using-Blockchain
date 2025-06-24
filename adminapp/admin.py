from django.contrib import admin
from .models import Candidate, AdminUser, Schedule

# Register the Candidate model with the admin site
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'party_name', 'state', 'district', 'region', 'election_place', 'pincode']
    search_fields = ['name', 'party_name']
    list_filter = ['state', 'district', 'region']
    fieldsets = [
        ('Personal Information', {'fields': ['name', 'date_of_birth']}),
        ('Party Information', {'fields': ['party_name']}),
        ('Location Information', {'fields': ['state', 'district', 'region', 'election_place', 'pincode']}),
        ('Images', {'fields': ['image', 'symbol_image']}),  # Removed duplicate `symbol_image`
    ]


admin.site.register(AdminUser)
admin.site.register(Schedule)