from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    """
    Base admin class that provides common functionality for all model admins.
    
    This class automatically adds timestamp fields (created_at, updated_at) to the
    list display and readonly fields of all model admins that inherit from it.
    """
    
    timestamps = ('created_at', 'updated_at')

    def get_list_display(self, request):
        """
        Returns the list of fields to display in the admin list view.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            tuple: A tuple containing the model's list_display fields plus timestamp fields.
        """
        return self.list_display + self.timestamps

    def get_readonly_fields(self, request, obj=None):
        """
        Returns the list of readonly fields for the admin form.
        
        Args:
            request: The HTTP request object.
            obj: The model instance being edited, or None if creating a new instance.
            
        Returns:
            tuple: A tuple containing the model's readonly fields plus timestamp fields.
        """
        return self.readonly_fields + self.timestamps


class AdminSite(admin.AdminSite):
    """
    Custom admin site configuration for the Amza application.
    
    This class customizes the admin interface with specific branding and titles.
    """
    
    site_header = 'Amza Admin'
    site_title = 'Amza Admin Portal'
    index_title = 'Welcome to Amza Admin Portal'


admin_site = AdminSite()
