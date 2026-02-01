import csv
import io
import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseNotAllowed

from .forms import StoreProductUploadForm, StoreProductAddForm
from .models import StoreProduct, KeepaNotification
from .services.keepa_tracking_service import KeepaTrackingService


def _decode_upload(file_obj):
    raw = file_obj.read()
    for encoding in ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def _parse_decimal(value: str | None) -> Decimal | None:
    if value is None:
        return None
    cleaned = value.strip().replace(',', '')
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    return normalized in {'1', 'true', 'yes', 'si', 'on', 'active', 'activo'}


class StoreProductListView(LoginRequiredMixin, View):
    template_name = 'store_products/list.html'
    login_url = '/admin/login/'

    def get(self, request):
        products = StoreProduct.objects.order_by('asin')
        notifications = KeepaNotification.objects.order_by('-created_at')[:50]
        unread_count = KeepaNotification.objects.filter(is_read=False).count()

        context = {
            'products': products,
            'upload_form': StoreProductUploadForm(),
            'add_form': StoreProductAddForm(),
            'notifications': notifications,
            'unread_count': unread_count,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        action = request.POST.get('action', '')
        if action == 'add_single':
            form = StoreProductAddForm(request.POST)
            if not form.is_valid():
                return render(request, self.template_name, {
                    'products': StoreProduct.objects.order_by('asin'),
                    'upload_form': StoreProductUploadForm(),
                    'add_form': form,
                    'notifications': KeepaNotification.objects.order_by('-created_at')[:50],
                    'unread_count': KeepaNotification.objects.filter(is_read=False).count(),
                    'error': 'Formulario invalido.',
                })

            asin = form.cleaned_data['asin'].strip().upper()
            sku = form.cleaned_data.get('sku', '').strip()
            price_mxn = form.cleaned_data.get('price_mxn')
            tracking_type = form.cleaned_data['tracking_type']
            tracking_enabled = bool(form.cleaned_data.get('tracking_enabled'))
            is_active = bool(form.cleaned_data.get('is_active'))

            store_product, created = StoreProduct.objects.update_or_create(
                asin=asin,
                defaults={
                    'sku': sku,
                    'price_mxn': price_mxn,
                    'is_active': is_active,
                    'tracking_type': tracking_type,
                    'tracking_enabled': tracking_enabled,
                    'keepa_marketplace': 'US',
                },
            )

            keepa_error = ''
            if tracking_enabled:
                try:
                    service = KeepaTrackingService()
                    # Note: Webhook URL should be configured once using the management command:
                    # python manage.py setup_keepa_webhook https://yourdomain.com/api/v1/webhooks/keepa
                    response = service.add_tracking(
                        [asin],
                        tracking_type=tracking_type,
                        marketplace='US',
                        update_interval_hours=1,
                    )
                    if response.get('error'):
                        keepa_error = response['error']
                    trackings = response.get('trackings', [])
                    for tracking in trackings:
                        tracking_asin = (tracking.get('asin') or '').strip().upper()
                        tracking_id = tracking.get('trackingId') or tracking.get('id') or ''
                        if tracking_asin == asin and tracking_id:
                            StoreProduct.objects.filter(asin=asin).update(
                                keepa_tracking_id=tracking_id
                            )
                            break
                except Exception as exc:
                    keepa_error = str(exc)

            notifications = KeepaNotification.objects.order_by('-created_at')[:50]
            unread_count = KeepaNotification.objects.filter(is_read=False).count()
            return render(request, self.template_name, {
                'products': StoreProduct.objects.order_by('asin'),
                'upload_form': StoreProductUploadForm(),
                'add_form': StoreProductAddForm(),
                'notifications': notifications,
                'unread_count': unread_count,
                'success': 'Producto agregado correctamente.',
                'keepa_error': keepa_error,
            })

        if action == 'verify_tracking':
            asin = request.POST.get('asin', '').strip().upper()
            keepa_error = ''
            keepa_status = ''
            if asin:
                try:
                    service = KeepaTrackingService()
                    response = service.get_tracking(asin)
                    if response.get('error'):
                        keepa_error = response['error']
                    else:
                        trackings = response.get('trackings', [])
                        keepa_status = 'Activo' if trackings else 'No registrado'
                except Exception as exc:
                    keepa_error = str(exc)

            notifications = KeepaNotification.objects.order_by('-created_at')[:50]
            unread_count = KeepaNotification.objects.filter(is_read=False).count()
            return render(request, self.template_name, {
                'products': StoreProduct.objects.order_by('asin'),
                'upload_form': StoreProductUploadForm(),
                'add_form': StoreProductAddForm(),
                'notifications': notifications,
                'unread_count': unread_count,
                'keepa_status': keepa_status,
                'keepa_error': keepa_error,
            })

        if action == 'upload':
            form = StoreProductUploadForm(request.POST, request.FILES)
            if not form.is_valid():
                return render(request, self.template_name, {
                    'products': StoreProduct.objects.order_by('asin'),
                    'upload_form': form,
                    'add_form': StoreProductAddForm(),
                    'notifications': KeepaNotification.objects.order_by('-created_at')[:50],
                    'unread_count': KeepaNotification.objects.filter(is_read=False).count(),
                    'error': 'Formulario invalido.',
                })

            file = form.cleaned_data['file']
            tracking_type = form.cleaned_data['tracking_type']
            tracking_enabled = bool(form.cleaned_data.get('tracking_enabled'))
            is_active = bool(form.cleaned_data.get('is_active'))

            decoded = _decode_upload(file)
            if decoded is None:
                return render(request, self.template_name, {
                    'products': StoreProduct.objects.order_by('asin'),
                    'upload_form': form,
                    'add_form': StoreProductAddForm(),
                    'notifications': KeepaNotification.objects.order_by('-created_at')[:50],
                    'unread_count': KeepaNotification.objects.filter(is_read=False).count(),
                    'error': 'No se pudo leer el archivo CSV.',
                })

            stream = io.StringIO(decoded)
            reader = csv.reader(stream)
            rows = list(reader)
            if not rows:
                return redirect(request.path)

            header = [c.strip().lower() for c in rows[0]]
            has_header = 'asin' in header

            if has_header:
                stream.seek(0)
                dict_reader = csv.DictReader(stream)
                rows_iter = dict_reader
            else:
                rows_iter = rows

            created_count = 0
            updated_count = 0
            tracked_asins = []

            for row in rows_iter:
                if has_header:
                    asin = (row.get('asin') or '').strip().upper()
                    sku = (row.get('sku') or '').strip()
                    price_mxn = _parse_decimal(row.get('price_mxn') or row.get('price'))
                    row_active = _parse_bool(row.get('is_active') or row.get('active'), default=is_active)
                else:
                    if not row:
                        continue
                    asin = (row[0] or '').strip().upper()
                    sku = (row[1] or '').strip() if len(row) > 1 else ''
                    price_mxn = _parse_decimal(row[2]) if len(row) > 2 else None
                    row_active = is_active

                if not asin:
                    continue

                store_product, created = StoreProduct.objects.update_or_create(
                    asin=asin,
                    defaults={
                        'sku': sku,
                        'price_mxn': price_mxn,
                        'is_active': row_active,
                        'tracking_type': tracking_type,
                        'tracking_enabled': tracking_enabled,
                        'keepa_marketplace': 'US',
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

                if tracking_enabled:
                    tracked_asins.append(asin)

            keepa_error = ''
            if tracking_enabled and tracked_asins:
                try:
                    service = KeepaTrackingService()
                    # Note: Webhook URL should be configured once using the management command:
                    # python manage.py setup_keepa_webhook https://yourdomain.com/api/v1/webhooks/keepa
                    response = service.add_tracking(
                        tracked_asins,
                        tracking_type=tracking_type,
                        marketplace='US',
                        update_interval_hours=1,
                    )
                    if response.get('error'):
                        keepa_error = response['error']
                    trackings = response.get('trackings', [])
                    for tracking in trackings:
                        tracking_asin = (tracking.get('asin') or '').strip().upper()
                        tracking_id = tracking.get('trackingId') or tracking.get('id') or ''
                        if tracking_asin and tracking_id:
                            StoreProduct.objects.filter(asin=tracking_asin).update(
                                keepa_tracking_id=tracking_id
                            )
                except Exception as exc:
                    keepa_error = str(exc)

            notifications = KeepaNotification.objects.order_by('-created_at')[:50]
            unread_count = KeepaNotification.objects.filter(is_read=False).count()
            return render(request, self.template_name, {
                'products': StoreProduct.objects.order_by('asin'),
                'upload_form': StoreProductUploadForm(),
                'add_form': StoreProductAddForm(),
                'notifications': notifications,
                'unread_count': unread_count,
                'success': f'Creados: {created_count} | Actualizados: {updated_count}',
                'keepa_error': keepa_error,
            })

        if action == 'mark_all_read':
            KeepaNotification.objects.filter(is_read=False).update(is_read=True)
            return redirect(request.path)

        return redirect(request.path)
