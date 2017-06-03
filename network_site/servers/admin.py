from django.contrib import admin

from .models import Router, Server


class RouterInline(admin.StackedInline):
    model = Router


class ServerAdmin(admin.ModelAdmin):
    inlines = [RouterInline,]


admin.site.register(Server, ServerAdmin)
admin.site.register(Router)
