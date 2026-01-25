import json
import requests
from django.conf import settings


class KeepaTrackingService:
    BASE_URL = 'https://api.keepa.com/tracking'
    DOMAIN_US = 1
    NOTIFICATION_TYPE_API_INDEX = 5

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.KEEPA_API_KEY

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
        return self._post({'type': 'webhook', 'url': url})

    def add_tracking(
        self,
        asins: list[str],
        tracking_type: str = 'regular',
        marketplace: str = 'US',
        update_interval_hours: int | None = 0,
        list_name: str | None = None,
    ) -> dict:
        domain_id = self.DOMAIN_US if marketplace == 'US' else self.DOMAIN_US
        params = {'type': 'add'}
        if list_name:
            params['list'] = list_name

        def build_payload() -> list[dict]:
            payload = []
            for asin in asins:
                notification_type = [False] * 7
                notification_type[self.NOTIFICATION_TYPE_API_INDEX] = True
                item = {
                    'asin': asin,
                    'mainDomainId': domain_id,
                    'ttl': 0,
                    'expireNotify': True,
                    'desiredPricesInMainCurrency': True,
                    'notificationType': notification_type,
                    'individualNotificationInterval': -1,
                }
                if update_interval_hours is not None:
                    item['updateInterval'] = max(0, min(25, int(update_interval_hours)))
                if list_name:
                    item['trackingListName'] = list_name
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
