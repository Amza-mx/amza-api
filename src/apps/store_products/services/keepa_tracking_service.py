import json
import requests
from django.conf import settings
from apps.pricing_analysis.models import KeepaConfiguration

class KeepaTrackingService:
    BASE_URL = 'https://api.keepa.com/tracking'
    DOMAIN_US = 1
    DOMAIN_MX = 12
    NOTIFICATION_TYPE_API_INDEX = 5

    def __init__(self, api_key: str | None = None):
        self.api_key = self.get_api_key()

    def get_api_key(self) -> str | None:
        keepa_configuration = KeepaConfiguration.objects.last()
        if keepa_configuration:
            return keepa_configuration.api_key
        return None

    def _post(self, params: dict, payload: list | dict | None = None) -> dict:
        if not self.api_key:
            raise ValueError('Missing KEEPA_API_KEY for Keepa tracking.')

        params = {**params, 'key': self.api_key}
        response = requests.post(self.BASE_URL, params=params, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def _get(self, params: dict) -> dict:
        if not self.api_key:
            raise ValueError('Missing KEEPA_API_KEY for Keepa tracking.')

        params = {**params, 'key': self.api_key}
        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def set_webhook(self, url: str) -> dict:
        """
        Set the webhook URL for push notifications.

        Args:
            url: Full webhook URL (must be HTTPS and publicly accessible)

        Returns:
            Keepa API response

        Note:
            The webhook is GLOBAL for your entire Keepa account.
            All trackings will send notifications to this URL.
            You only need to set this once per deployment.
        """
        return self._post({'type': 'webhook', 'url': url})

    def get_webhook(self) -> dict:
        """
        Get current webhook configuration.

        Returns:
            Keepa API response with webhook information
        """
        return self._get({'type': 'webhook'})

    def add_tracking(
        self,
        asins: list[str],
        tracking_type: str = 'regular',
        marketplace: str = 'US',
        update_interval_hours: int = 1,
        list_name: str | None = None,
        threshold_value: int | None = None,
        csv_type: int = 0,
        is_drop: bool = True,
    ) -> dict:
        """
        Add product tracking to Keepa.

        Args:
            asins: List of ASINs to track
            tracking_type: 'regular' or 'marketplace'
            marketplace: 'US' or other Amazon marketplace
            update_interval_hours: Update interval (0-25 hours). Lower = more frequent updates.
            list_name: Optional named list for logical separation
            threshold_value: Price threshold in smallest currency unit (cents). None = track all changes.
            csv_type: Price type to track (0=Amazon, 1=New, 2=Used, etc.)
            is_drop: True to notify on price drops, False for price increases

        Returns:
            Keepa API response with trackings array
        """
        domain_id = self.DOMAIN_US if marketplace == 'US' else self.DOMAIN_MX
        params = {'type': 'add'}
        if list_name:
            params['list'] = list_name

        def build_payload() -> list[dict]:
            payload = []
            for asin in asins:
                # NotificationType array: only enable API notifications (index 5)
                # Array must have 8 elements according to Keepa API documentation
                notification_type = [False] * 8
                notification_type[self.NOTIFICATION_TYPE_API_INDEX] = True

                # Build tracking creation object
                item = {
                    'asin': asin,
                    'mainDomainId': domain_id,
                    'ttl': 0,  # Never expires
                    'expireNotify': True,  # Notify if tracking expires
                    'desiredPricesInMainCurrency': True,
                    'updateInterval': max(0, min(25, int(update_interval_hours))),  # REQUIRED: 0-25
                    'notificationType': notification_type,
                    'individualNotificationInterval': -1,  # Use default rearm timer
                }

                # Add tracking criteria based on type and threshold
                if threshold_value is not None:
                    # Track specific price threshold
                    item['thresholdValues'] = [{
                        'thresholdValue': threshold_value,
                        'domain': domain_id,
                        'csvType': csv_type,
                        'isDrop': is_drop,
                    }]
                else:
                    # Track stock status changes (no specific price threshold)
                    item['notifyIf'] = [
                        {
                            'domain': domain_id,
                            'csvType': csv_type,
                            'notifyIfType': 1,  # BACK_IN_STOCK
                        }
                    ]

                # Add metadata for identification
                item['metaData'] = f'StoreProduct_{asin}_{tracking_type}'

                payload.append(item)
            return payload

        def post_or_get(payload: list[dict]):
            try:
                return self._post(params, payload)
            except requests.HTTPError as exc:
                response = exc.response
                if response is not None and response.status_code == 400:
                    tracking_param = json.dumps(payload, separators=(',', ':'))
                    params_with_tracking = {**params, 'tracking': tracking_param}
                    return self._get(params_with_tracking)
                raise

        return post_or_get(build_payload())

    def get_tracking(self, asin: str, list_name: str | None = None) -> dict:
        params = {'type': 'get', 'asin': asin}
        if list_name:
            params['list'] = list_name
        return self._get(params)
