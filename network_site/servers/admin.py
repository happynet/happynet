from datetime import date

from django.contrib import admin

from .models import Router, Server


class YearListFilter(admin.SimpleListFilter):
    title = 'year created'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        return (
            ('2017', '2017'),
            ('2018', '2018'),
        )

    def queryset(self, request, queryset):
        if self.value() == '2017':
            return queryset.filter(created_at__gte=date(2017, 1, 1),
                                   created_at__lte=date(2017, 12, 31))
        if self.value() == '2018':
            return queryset.filter(created_at__gte=date(2018, 1, 1),
                                   created_at__lte=date(2018, 12, 31))


class RouterInline(admin.StackedInline):
    model = Router


class ServerAdmin(admin.ModelAdmin):
    inlines = [RouterInline,]
    # fields = ['name', 'notes', 'is_active']
    search_fields = ['name', 'notes',]
    list_filter = ['created_at', YearListFilter,]
    list_display = ['name', 'created_at', 'is_active',]
    fieldsets = (
        (None, {
            'fields': ('name',)}),
        ('Optional', {
            'fields': ('notes', 'is_active',),
            'classes': ('collapse',),
        }),
    )

    class Media:
        js = ('js/vendor/markdown.js', 'js/preview.js')
        css = {
            'all': ('css/preview.css',),
        }


class RouterAdmin(admin.ModelAdmin):
    # fields = ['server', 'name', 'notes', 'content', 'is_active', 'order',]
    search_fields = ['name', 'notes', 'content',]
    list_filter = ['created_at', YearListFilter,]
    list_display = ['name', 'created_at', 'is_active', 'server',]
    list_editable = ['server',]
    fieldsets = (
        (None, {
            'fields': ('server', 'name',)}),
        ('Optional', {
            'fields': ('notes', 'content', 'is_active', 'order',),
            'classes': ('collapse',),
        }),
    )
    # radio_fields = {'server': admin.HORIZONTAL}


admin.site.register(Server, ServerAdmin)
admin.site.register(Router, RouterAdmin)
