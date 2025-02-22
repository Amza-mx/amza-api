from django.db import models


class BaseModel(models.Model):
    """
    BaseModel is an abstract class that provides automatic timestamp fields for model instances.
    Attributes:
        created_at (DateTimeField): Automatically set to the current date and time when a record is created.
        updated_at (DateTimeField): Automatically updated to the current date and time whenever a record is modified.
    Meta Attributes:
        abstract (bool): Indicates that this class is abstract and should not create a corresponding database table.
        ordering (tuple): Specifies the default ordering of objects, sorted by the creation timestamp in descending order.

    How to Implement:
    To use BaseModel, simply subclass it in your Django model. For example:

        class YourModel(BaseModel):
            # Add your custom fields
            name = models.CharField(max_length=255)
            description = models.TextField()

    This way, YourModel automatically inherits the created_at and updated_at fields and their behaviors.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)
