from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (                      # new fieldset added on to the bottom
            "Custom Properties",  # group heading of your choice; set to None for a blank space instead of a header
            {
                'fields': (
                    'is_admin',
                    'find_count'
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Geocache)
admin.site.register(Find)
admin.site.register(Comment)