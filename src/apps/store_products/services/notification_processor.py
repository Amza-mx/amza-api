CSV_TYPE_NAMES = {
    0: 'Amazon',
    1: 'New (terceros)',
    2: 'Used',
    4: 'List Price',
    7: 'New FBM + envio',
    18: 'Buy Box',
}

NOTIFICATION_CAUSES = {
    0: 'EXPIRED',
    1: 'DESIRED_PRICE',
    2: 'PRICE_CHANGE',
    3: 'PRICE_CHANGE_AFTER_DESIRED',
    4: 'OUT_STOCK',
    5: 'IN_STOCK',
    6: 'DESIRED_PRICE_AGAIN',
}

PRICE_CHANGE_CAUSES = {1, 2, 3, 6}


def process_keepa_notification(payload: dict) -> tuple[str, str]:
    """
    Procesa un payload de notificacion Keepa y retorna (summary, recommendation).
    """
    cause = payload.get('trackingNotificationCause')
    csv_type = payload.get('csvType', 0)
    is_drop = payload.get('isDrop', False)
    current_prices = payload.get('currentPrices', [])

    type_name = CSV_TYPE_NAMES.get(csv_type, f'Tipo {csv_type}')

    if cause in PRICE_CHANGE_CAUSES:
        price_cents = current_prices[csv_type] if csv_type < len(current_prices) else -1
        if price_cents and price_cents > 0:
            price = price_cents / 100
            price_str = f'${price:,.2f} USD'
        else:
            price_str = 'no disponible'

        if is_drop:
            summary = f'Precio {type_name} bajo a {price_str}'
            recommendation = (
                'Tu costo de adquisicion bajo. '
                'Puedes bajar tu precio en MX para ser mas competitivo y vender mas rapido.'
            )
        else:
            summary = f'Precio {type_name} subio a {price_str}'
            recommendation = (
                'Tu costo de adquisicion subio. '
                'Sube tu precio en MX para mantener un margen de ganancia sano.'
            )

    elif cause == 4:  # OUT_STOCK
        summary = f'Producto sin stock en USA ({type_name})'
        recommendation = (
            'No hay inventario disponible en USA. '
            'Quita este producto de tu inventario en MX.'
        )

    elif cause == 5:  # IN_STOCK
        summary = f'Producto disponible de nuevo en USA ({type_name})'
        recommendation = (
            'El producto volvio a estar disponible en USA. '
            'Vuelve a darlo de alta en tu inventario en MX.'
        )

    elif cause == 0:  # EXPIRED
        summary = 'Tracking expirado'
        recommendation = (
            'El tracking expiro. '
            'Vuelve a registrar el producto para seguir monitoreando.'
        )

    else:
        cause_name = NOTIFICATION_CAUSES.get(cause, str(cause))
        summary = f'Notificacion Keepa: {cause_name}'
        recommendation = ''

    return summary, recommendation
