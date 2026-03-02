import json
import time
import requests
from django.conf import settings
from apps.pricing_analysis.models import KeepaConfiguration, KeepaAPILog

class KeepaTrackingService:
    BASE_URL = 'https://api.keepa.com/tracking'
    DOMAIN_US = 1
    DOMAIN_MX = 11  # Amazon Mexico domain ID (not 12, which is Brazil)
    NOTIFICATION_TYPE_API_INDEX = 5

    def __init__(self, api_key: str | None = None):
        self.api_key = self.get_api_key()

    def get_api_key(self) -> str | None:
        keepa_configuration = KeepaConfiguration.objects.last()
        if keepa_configuration:
            return keepa_configuration.api_key
        return None

    def _log(self, method: str, params: dict, payload, response, elapsed_ms: int, error: str = ''):
        """Persist request/response to KeepaAPILog for debugging."""
        safe_params = {k: v for k, v in params.items() if k != 'key'}
        request_data = {'method': method, 'params': safe_params}
        if payload is not None:
            request_data['body'] = payload

        try:
            response_data = response.json() if response is not None else {}
        except Exception:
            response_data = {'raw': response.text[:2000]} if response is not None else {}

        tokens = 0
        if isinstance(response_data, dict):
            tokens = response_data.get('tokensConsumed', 0)

        KeepaAPILog.objects.create(
            endpoint=f'tracking/{safe_params.get("type", "")}',
            request_params=request_data,
            response_status=response.status_code if response is not None else None,
            response_data=response_data,
            tokens_consumed=tokens,
            error_message=error,
            execution_time_ms=elapsed_ms,
        )

    def _post(self, params: dict, payload: list | dict | None = None) -> dict:
        if not self.api_key:
            raise ValueError('Missing KEEPA_API_KEY for Keepa tracking.')

        params = {**params, 'key': self.api_key}
        response = None
        start = time.monotonic()
        try:
            response = requests.post(self.BASE_URL, params=params, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            self._log('POST', params, payload, response, int((time.monotonic() - start) * 1000))
            return data
        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            self._log('POST', params, payload, response, elapsed, error=str(exc))
            raise

    def _get(self, params: dict) -> dict:
        if not self.api_key:
            raise ValueError('Missing KEEPA_API_KEY for Keepa tracking.')

        params = {**params, 'key': self.api_key}
        response = None
        start = time.monotonic()
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            self._log('GET', params, None, response, int((time.monotonic() - start) * 1000))
            return data
        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            self._log('GET', params, None, response, elapsed, error=str(exc))
            raise

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

                # thresholdValues is REQUIRED by Keepa API for price notifications.
                # When no specific threshold is given, use a permissive value
                # ($999,999 in cents) so any real price triggers the notification.
                effective_threshold = threshold_value if threshold_value is not None else 99999900
                item['thresholdValues'] = [{
                    'thresholdValue': effective_threshold,
                    'domain': domain_id,
                    'csvType': csv_type,
                    'isDrop': is_drop,
                }]

                # Also monitor stock availability changes
                item['notifyIf'] = [
                    {
                        'domain': domain_id,
                        'csvType': csv_type,
                        'notifyIfType': 0,  # OUT_OF_STOCK
                    },
                    {
                        'domain': domain_id,
                        'csvType': csv_type,
                        'notifyIfType': 1,  # BACK_IN_STOCK
                    },
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
