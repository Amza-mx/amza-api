# API Documentation

## Overview
This API provides a RESTful interface for managing marketplaces, sales orders, and prep centers.

## Versioning
The API is versioned using URL-based versioning (e.g., `/api/v1/`). This allows for:
- Maintaining backward compatibility
- Introducing breaking changes in new versions
- Supporting multiple versions simultaneously

## Authentication
All endpoints require authentication using JWT (JSON Web Tokens).
- Obtain a token using the `/api/v1/auth/token/` endpoint
- Include the token in the Authorization header: `Authorization: Bearer <token>`

## Rate Limiting
- Default rate limit: 100 requests per minute per user
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Available Endpoints

### Marketplaces
- `GET /api/v1/marketplaces/` - List all marketplaces
- `POST /api/v1/marketplaces/` - Create a new marketplace
- `GET /api/v1/marketplaces/{id}/` - Retrieve a specific marketplace
- `PUT /api/v1/marketplaces/{id}/` - Update a marketplace
- `DELETE /api/v1/marketplaces/{id}/` - Delete a marketplace

### Sales Orders
- `GET /api/v1/sales-orders/` - List all sales orders
- `POST /api/v1/sales-orders/` - Create a new sales order
- `GET /api/v1/sales-orders/{id}/` - Retrieve a specific sales order
- `PUT /api/v1/sales-orders/{id}/` - Update a sales order
- `DELETE /api/v1/sales-orders/{id}/` - Delete a sales order

### Prep Centers
- `GET /api/v1/prep-centers/` - List all prep centers
- `POST /api/v1/prep-centers/` - Create a new prep center
- `GET /api/v1/prep-centers/{id}/` - Retrieve a specific prep center
- `PUT /api/v1/prep-centers/{id}/` - Update a prep center
- `DELETE /api/v1/prep-centers/{id}/` - Delete a prep center

## Error Responses
The API follows Django REST Framework's standard error response format:

### Validation Errors (400 Bad Request)
```json
{
    "field_name": [
        "Error message for this field"
    ],
    "non_field_errors": [
        "Error message not related to a specific field"
    ]
}
```

### Authentication Errors (401 Unauthorized)
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Permission Errors (403 Forbidden)
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### Not Found Errors (404 Not Found)
```json
{
    "detail": "Not found."
}
```

### Method Not Allowed (405 Method Not Allowed)
```json
{
    "detail": "Method 'POST' not allowed."
}
```

### Throttling Errors (429 Too Many Requests)
```json
{
    "detail": "Request was throttled. Expected available in [time] seconds."
}
```

The API uses standard HTTP status codes to indicate the type of error:
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `405 Method Not Allowed`: HTTP method not supported
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error

## Development
To add new endpoints:
1. Create a new module in `/api/v1/`
2. Implement views, serializers, and URLs
3. Add the module's URLs to `/api/v1/urls.py`
4. Add tests in the module's `tests/` directory
5. Update this documentation 