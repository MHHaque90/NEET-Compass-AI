# API Specification

> **Base URL:** `https://api.neetcompass.in/v1`
> **OpenAPI:** Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)
> **Version:** v1 (locked)

---

## Authentication

All endpoints except health checks require a valid JWT access token in
the `Authorization: Bearer <token>` header.

### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "email": "aspirant@example.com",
  "password": "Str0ngP@ss!",
  "full_name": "Aspirant User"
}
```

**Response:** `201 Created`
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "aspirant@example.com",
  "full_name": "Aspirant User",
  "created_at": "2026-08-10T12:00:00Z"
}
```

### POST /auth/login

Authenticate and receive access + refresh tokens.

**Request:**
```json
{
  "email": "aspirant@example.com",
  "password": "Str0ngP@ss!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g...",
  "expires_in": 900
}
```

### POST /auth/refresh

Exchange a refresh token for a new access token.

**Request:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 900
}
```

### POST /auth/logout

Revoke the current access and refresh tokens.

**Response:** `204 No Content`

---

## Colleges

### GET /colleges

List colleges with optional filtering.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `state` | string | — | Filter by state name |
| `course` | string | — | Filter by course (MBBS/BDS) |
| `category` | string | — | Filter by category (general/obc/sc/st) |
| `quota` | string | — | Filter by quota (aiq/deemed/management) |
| `cursor` | string | null | Pagination cursor |
| `limit` | int | 20 | Page size (max 100) |
| `sort_by` | string | name | Sort field (name, fee, rank) |
| `sort_order` | string | asc | asc or desc |

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "code": "MAM001",
      "name": "Maulana Azad Medical College",
      "state": "Delhi",
      "city": "New Delhi",
      "course": "MBBS",
      "ownership": "GOVERNMENT",
      "annual_fee_inr": 0,
      "total_seats": 250,
      "aiq_seats": 15,
      "cutoff_min_rank": 850,
      "cutoff_max_rank": 5200
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6Ij...",
    "has_more": true
  }
}
```

### GET /colleges/{college_id}

Get detailed information about a specific college.

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "MAM001",
  "name": "Maulana Azad Medical College",
  "state": "Delhi",
  "city": "New Delhi",
  "course": "MBBS",
  "ownership": "GOVERNMENT",
  "annual_fee_inr": 0,
  "total_seats": 250,
  "aiq_seats": 15,
  "seat_matrix": [
    {
      "category": "GENERAL",
      "quota_type": "AIQ",
      "seats": 15,
      "opening_rank": 850,
      "closing_rank": 5200
    }
  ],
  "cutoffs": [
    {
      "year": 2023,
      "category": "GENERAL",
      "quota_type": "AIQ",
      "round": 1,
      "opening_rank": 850,
      "closing_rank": 5200
    }
  ],
  "fee_history": [
    {
      "year": 2023,
      "annual_fee_inr": 0,
      "hostel_fee_inr": 90000
    }
  ]
}
```

---

## Predictions

### POST /predictions

Generate college recommendations based on rank and preferences.

**Request:**
```json
{
  "rank": 25000,
  "category": "GENERAL",
  "quota_type": "AIQ",
  "course": "MBBS",
  "state": "Maharashtra",
  "gender": "NEUTRAL",
  "is_pwd": false,
  "preferences": ["MUM001", "MUM002", "PUN001"]
}
```

**Response:** `200 OK`
```json
{
  "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
  "rank": 25000,
  "recommendations": [
    {
      "college_id": "550e8400-e29b-41d4-a716-446655440000",
      "college_code": "MAM001",
      "college_name": "Maulana Azad Medical College",
      "confidence_score": 0.87,
      "reasoning": [
        "Rank within historical range (850-5200 for 2023)",
        "AIQ quota matches your selection",
        "Preference #1 in your list"
      ],
      "cutoff_info": {
        "year": 2023,
        "opening_rank": 850,
        "closing_rank": 5200,
        "category": "GENERAL"
      }
    }
  ],
  "model_version": "cutoff-predictor-v1.2.0"
}
```

### POST /predictions/batch

Generate recommendations for multiple rank scenarios.

**Request:**
```json
{
  "predictions": [
    {
      "rank": 25000,
      "category": "GENERAL",
      ...
    },
    {
      "rank": 50000,
      "category": "OBC",
      ...
    }
  ],
  "webhook_url": "https://example.com/webhook"
}
```

**Response:** `202 Accepted`
```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "QUEUED",
  "poll_url": "/predictions/batch/550e8400-..."
}
```

### GET /predictions/batch/{batch_id}

Check batch prediction status.

**Response:** `200 OK`
```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "COMPLETED",
  "results_url": "/predictions/batch/550e8400-.../results"
}
```

---

## Admins

All endpoints in this section require `ADMIN` or `SUPERADMIN` role.

### GET /admin/features

List all feature flags.

### PATCH /admin/features/{key}

Update a feature flag's current value.

### GET /admin/etl-runs

List ETL run history with status, row counts, and error summaries.

### POST /admin/etl-runs/{run_id}/retry

Retry a failed ETL run from its last successful stage.

### GET /admin/models

List model versions with performance metrics and promotion status.

### POST /admin/models/{model_name}/train

Trigger a new model training run with specified parameters.

---

## Rate Limits

| Endpoint | Authenticated | Unauthenticated |
|---|---|---|
| All except /health | 100 req/min | 10 req/min |
| /predictions | 10 req/min | — (auth required) |
| /predictions/batch | 2 req/min | — (auth required) |

Rate-limited responses return `429 Too Many Requests` with a
`Retry-After` header.

---

## Error Responses

All errors follow a consistent JSON format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {"field": "email", "issue": "Invalid email format"}
    ]
  }
}
```

| Code | HTTP Status | Description |
|---|---|---|
| VALIDATION_ERROR | 400 | Request body failed schema validation |
| AUTHENTICATION_ERROR | 401 | Missing or invalid token |
| AUTHORIZATION_ERROR | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource does not exist |
| CONFLICT | 409 | Duplicate resource or state conflict |
| TOO_MANY_REQUESTS | 429 | Rate limit exceeded |
| INTERNAL_ERROR | 500 | Unexpected server error |
