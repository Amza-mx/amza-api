from django.db.models import TextChoices


class StatusChoices(TextChoices):
    PENDING = 'PENDING', 'Pending'
    BOUGHT = 'BOUGHT', 'Bought'
    IN_WAREHOUSE = 'IN_WAREHOUSE', 'In warehouse'
    DELIVERY_PROCESS = 'DELIVERY_PROCESS', 'Delivery process'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'
    RETURNED = 'RETURNED', 'Returned'


class SalesOrderStatusChoices(TextChoices):
    PENDING = 'PENDING', 'Pending'
    BOUGHT = 'BOUGHT', 'Bought'
    IN_WAREHOUSE = 'IN_WAREHOUSE', 'In warehouse'
    DELIVERY_PROCESS = 'DELIVERY_PROCESS', 'Delivery process'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'
    RETURNED = 'RETURNED', 'Returned'


class PurchaseOrderStatusChoices(TextChoices):
    PENDING = 'PENDING', 'Pending'
    BOUGHT = 'BOUGHT', 'Bought'
    IN_WAREHOUSE = 'IN_WAREHOUSE', 'In warehouse'
    DELIVERY_PROCESS = 'DELIVERY_PROCESS', 'Delivery process'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'
    RETURNED = 'RETURNED', 'Returned'


class ShipmentStatusChoices(TextChoices):
    PENDING = 'PENDING', 'Pending'
    DISPATCHED = 'DISPATCHED', 'Dispatched'
    IN_TRANSIT = 'IN_TRANSIT', 'In transit'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'


class CourierChoices(TextChoices):
    DHL = 'DHL', 'DHL'
    UPS = 'UPS', 'UPS'
    FEDEX = 'FEDEX', 'FedEx'
    ESTAFETA = 'ESTAFETA', 'Estafeta'
    OTHER = 'OTHER', 'Other'
