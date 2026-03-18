from django.contrib import admin

from users.models import CustomUser

@admin.register(CustomUser)
class AuthorAdmin(admin.ModelAdmin):
    exclude = ('password',)
