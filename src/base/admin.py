from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    timestamps = ('created_at', 'updated_at')

    def get_list_display(self, request):
        return self.list_display + self.timestamps

    def get_readonly_fields(self, request, obj=None):
        """
        Hook for specifying custom readonly fields.
        """
        return self.readonly_fields + self.timestamps


class AdminSite(admin.AdminSite):
    site_header = 'Amza Admin'
    site_title = 'Amza Admin Portal'
    index_title = 'Welcome to Amza Admin Portal'


admin_site = AdminSite()
