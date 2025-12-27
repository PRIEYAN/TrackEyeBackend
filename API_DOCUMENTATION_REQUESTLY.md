# TradeFlow API Documentation for Requestly

**Base URL:** `http://localhost:8000` (ASSUMED - adjust based on your environment)

**Authentication:** JWT Bearer Token (where required)
**Token Format:** `Bearer <access_token>`

---

## Table of Contents
1. [Health & Root](#health--root)
2. [Authentication](#authentication)
3. [Users](#users)
4. [Shipments](#shipments)
5. [Carriers](#carriers)
6. [Forwarder](#forwarder)
7. [Quotes](#quotes)
8. [Tracking](#tracking)
9. [Documents](#documents)
10. [Customs](#customs)

---

## Health & Root

### 1. Root Endpoint
- **Endpoint Group:** Health
- **HTTP Method:** GET
- **Full Path:** `/`
- **Authentication Required:** No
- **Authentication Type:** None
- **Role Required:** none

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/
Headers: (none)
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "message": "Welcome to TradeFlow API",
  "docs": "/api/docs",
  "version": "1.0.0",
  "environment": "development"
}
```

**Error Responses:**
- None (always returns 200)

---

### 2. Health Check
- **Endpoint Group:** Health
- **HTTP Method:** GET
- **Full Path:** `/health`
- **Authentication Required:** No
- **Authentication Type:** None
- **Role Required:** none

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/health
Headers: (none)
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "message": null
}
```

**Error Responses:**
- **503 Service Unavailable:** Database connection failed
  ```json
  {
    "status": "degraded",
    "version": "1.0.0",
    "database": "disconnected",
    "message": "Database connection failed: <error>"
  }
  ```

---

## Authentication

### 3. Register User
- **Endpoint Group:** Auth
- **HTTP Method:** POST
- **Full Path:** `/api/auth/register`
- **Authentication Required:** No
- **Authentication Type:** None
- **Role Required:** none

**Required Headers:**
```
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "email": "string (required, valid email format, unique)",
  "password": "string (required, min 8 characters)",
  "name": "string (required, min 2 characters)",
  "phone": "string (required, valid phone format)",
  "role": "string (required, one of: 'supplier', 'forwarder', 'buyer')",
  "company_name": "string (optional)",
  "gstin": "string (optional)",
  "country": "string (optional, default: 'IN', max 2 chars)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/auth/register
Headers:
  Content-Type: application/json
Body (JSON):
{
  "email": "supplier@example.com",
  "password": "password123",
  "name": "John Supplier",
  "phone": "+1234567890",
  "role": "supplier",
  "company_name": "ABC Trading Co",
  "gstin": "29ABCDE1234F1Z5",
  "country": "IN"
}
```

**Expected Success Response (201):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "supplier@example.com",
  "name": "John Supplier",
  "company_name": "ABC Trading Co",
  "phone": "+1234567890",
  "role": "supplier",
  "gstin": "29ABCDE1234F1Z5",
  "country": "IN",
  "is_verified": false,
  "created_at": "2025-01-15T10:30:00.000000"
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
  ```json
  {
    "error": "Invalid input",
    "reason": "Request data validation failed",
    "module": "validation",
    "safe_for_demo": true,
    "errors": [
      {
        "loc": ["email"],
        "msg": "Email is required",
        "type": "value_error"
      }
    ]
  }
  ```
- **400 Bad Request:** User already exists
  ```json
  {
    "error": "Bad Request",
    "reason": "User with this email already exists",
    "module": "auth",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

### 4. Login
- **Endpoint Group:** Auth
- **HTTP Method:** POST
- **Full Path:** `/api/auth/login`
- **Authentication Required:** No
- **Authentication Type:** None
- **Role Required:** none

**Required Headers:**
```
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/auth/login
Headers:
  Content-Type: application/json
Body (JSON):
{
  "email": "supplier@example.com",
  "password": "password123"
}
```

**Expected Success Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "supplier@example.com",
    "name": "John Supplier",
    "company_name": "ABC Trading Co",
    "phone": "+1234567890",
    "role": "supplier",
    "gstin": "29ABCDE1234F1Z5",
    "country": "IN",
    "is_verified": false,
    "created_at": "2025-01-15T10:30:00.000000"
  }
}
```

**Error Responses:**
- **400 Bad Request:** Missing email/password or invalid JSON
  ```json
  {
    "error": "Invalid input",
    "reason": "Email and password are required",
    "module": "auth",
    "safe_for_demo": true
  }
  ```
- **401 Unauthorized:** Incorrect credentials
  ```json
  {
    "error": "Unauthorized",
    "reason": "Incorrect email or password",
    "module": "auth",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

## Users

### 5. Get Current User Profile
- **Endpoint Group:** Users
- **HTTP Method:** GET
- **Full Path:** `/api/me` OR `/api/my-profile`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/me
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "supplier@example.com",
  "name": "John Supplier",
  "company_name": "ABC Trading Co",
  "phone": "+1234567890",
  "role": "supplier",
  "gstin": "29ABCDE1234F1Z5",
  "country": "IN",
  "is_verified": false,
  "created_at": "2025-01-15T10:30:00.000000"
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
  ```json
  {
    "error": "Unauthorized",
    "reason": "User not found",
    "module": "auth",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

## Shipments

### 6. Create Shipment
- **Endpoint Group:** Shipments
- **HTTP Method:** POST
- **Full Path:** `/api/shipments/create` OR `/api/shipments/`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any (ASSUMED - typically supplier)

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "origin_port": "string (required)",
  "destination_port": "string (required)",
  "weight": "number (required) OR gross_weight_kg",
  "volume": "number (required) OR volume_cbm"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/shipments/create
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "origin_port": "Mumbai",
  "destination_port": "New York",
  "weight": 15000.5,
  "volume": 60.5
}
```

**Expected Success Response (201):**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "shipment_number": "SH7761CB95",
  "supplier_id": "507f1f77bcf86cd799439011",
  "buyer_id": null,
  "forwarder_id": null,
  "origin_port": "Mumbai",
  "destination_port": "New York",
  "incoterm": null,
  "cargo_type": null,
  "container_type": null,
  "container_qty": 1,
  "goods_description": null,
  "hs_code": null,
  "gross_weight_kg": 15000.5,
  "net_weight_kg": null,
  "volume_cbm": 60.5,
  "total_packages": null,
  "package_type": null,
  "preferred_etd": null,
  "preferred_eta": null,
  "actual_etd": null,
  "actual_eta": null,
  "declared_value_usd": null,
  "insurance_required": false,
  "special_instructions": null,
  "status": "draft",
  "quote_forwarder_booked": [],
  "quote_amount": null,
  "quote_time": null,
  "quote_extra": null,
  "quote_status": "pending",
  "booked_forwarder_id": null,
  "metadata": {},
  "created_at": "2025-01-15T10:30:00.000000",
  "updated_at": null
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
  ```json
  {
    "error": "Invalid input",
    "reason": "Request data validation failed",
    "module": "validation",
    "safe_for_demo": true,
    "errors": [
      {
        "loc": ["origin_port"],
        "msg": "Origin port is required",
        "type": "value_error"
      }
    ]
  }
  ```
- **401 Unauthorized:** Invalid or missing token
- **503 Service Unavailable:** Database error

---

### 7. Get Shipment by ID
- **Endpoint Group:** Shipments
- **HTTP Method:** GET
- **Full Path:** `/api/shipments/<shipment_id>`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any (must be supplier, buyer, or assigned forwarder)

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/shipments/507f1f77bcf86cd799439012
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "shipment_number": "SH7761CB95",
  "supplier_id": "507f1f77bcf86cd799439011",
  "buyer_id": null,
  "forwarder_id": null,
  "origin_port": "Mumbai",
  "destination_port": "New York",
  "status": "draft",
  ...
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
- **403 Forbidden:** Not authorized to view this shipment
  ```json
  {
    "error": "Forbidden",
    "reason": "Not authorized to view this shipment",
    "module": "shipments",
    "safe_for_demo": true
  }
  ```
- **404 Not Found:** Shipment not found
  ```json
  {
    "error": "Not Found",
    "reason": "Shipment not found",
    "module": "shipments",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

### 8. List Shipments
- **Endpoint Group:** Shipments
- **HTTP Method:** GET
- **Full Path:** `/api/shipments/list` OR `/api/shipments/show` OR `/api/shipments/show_shipments`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Query Parameters:**
- `status` (string, optional) - Filter by status: 'draft', 'pending_quote', 'pending', 'quoted', 'booked', 'in_transit', 'arrived', 'delivered', 'cancelled'

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/shipments/show_shipments?status=draft
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439012",
      "shipment_number": "SH7761CB95",
      "supplier_id": "507f1f77bcf86cd799439011",
      "status": "draft",
      ...
    }
  ]
}
```

**Note:** 
- For **suppliers**: Returns shipments where `supplier_id` matches user
- For **buyers**: Returns shipments where `buyer_id` matches user
- For **forwarders**: Returns shipments assigned to them OR without forwarder

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
- **503 Service Unavailable:** Database error

---

### 9. Show Accepted Quotes (Booked Shipments)
- **Endpoint Group:** Shipments
- **HTTP Method:** GET
- **Full Path:** `/api/shipments/showAcceptedQuotes`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** supplier (ASSUMED - filters by supplier_id)

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/shipments/showAcceptedQuotes
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439012",
      "shipment_number": "SH7761CB95",
      "status": "booked",
      "quote_status": "accepted",
      ...
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
- **503 Service Unavailable:** Database error

---

## Carriers

### 10. Create Booking
- **Endpoint Group:** Carriers
- **HTTP Method:** POST
- **Full Path:** `/api/carriers/booking/create`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "carrier": "string (required)",
  "origin": "string (required)",
  "destination": "string (required)",
  "containerType": "string (required)",
  "quantity": "integer (required, min 1)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/carriers/booking/create
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "carrier": "MAERSK",
  "origin": "Mumbai",
  "destination": "New York",
  "containerType": "40HC",
  "quantity": 2
}
```

**Expected Success Response (200):**
```json
{
  "bookingNumber": "MAE123456",
  "carrier": "MAERSK",
  "status": "CONFIRMED",
  "vessel": "MV MAERSK EXPRESS",
  "etd": "2025-01-22T10:30:00.000000"
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
- **401 Unauthorized:** Invalid or missing token

---

### 11. Get Booking Status
- **Endpoint Group:** Carriers
- **HTTP Method:** GET
- **Full Path:** `/api/carriers/booking/status/<booking_number>`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `booking_number` (string, required)

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/carriers/booking/status/MAE123456
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "bookingNumber": "MAE123456",
  "carrier": "MAERSK",
  "status": "CONFIRMED",
  "containerAllocated": true
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token

---

### 12. Search Schedule
- **Endpoint Group:** Carriers
- **HTTP Method:** GET
- **Full Path:** `/api/carriers/schedule/search`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Query Parameters:**
- `origin` (string, required)
- `destination` (string, required)

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/carriers/schedule/search?origin=Mumbai&destination=New York
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "carrier": "MAERSK",
  "vessel": "MV MAERSK EXPRESS",
  "etd": "2025-01-22T10:30:00.000000",
  "eta": "2025-02-15T10:30:00.000000",
  "transitDays": 24
}
```

**Error Responses:**
- **400 Bad Request:** Missing origin/destination
  ```json
  {
    "error": "Invalid input",
    "reason": "Origin and destination are required",
    "module": "carriers",
    "safe_for_demo": true
  }
  ```
- **401 Unauthorized:** Invalid or missing token

---

### 13. Get Rate Quote
- **Endpoint Group:** Carriers
- **HTTP Method:** POST
- **Full Path:** `/api/carriers/rates/quote`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "origin": "string (required)",
  "destination": "string (required)",
  "containerType": "string (required)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/carriers/rates/quote
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "origin": "Mumbai",
  "destination": "New York",
  "containerType": "40HC"
}
```

**Expected Success Response (200):**
```json
{
  "carrier": "MAERSK",
  "containerType": "40HC",
  "rateUSD": 3250.50,
  "currency": "USD",
  "validity": "2025-02-14T10:30:00.000000"
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
- **401 Unauthorized:** Invalid or missing token

---

### 14. Track Container
- **Endpoint Group:** Carriers
- **HTTP Method:** GET
- **Full Path:** `/api/carriers/tracking/container/<container_number>`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `container_number` (string, required)

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/carriers/tracking/container/CONTAINER123456
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "containerNumber": "CONTAINER123456",
  "carrier": "MAERSK",
  "currentLocation": "Port of Singapore",
  "status": "IN_TRANSIT",
  "lastUpdated": "2025-01-15T10:30:00.000000"
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token

---

### 15. Predict Rate (AI)
- **Endpoint Group:** Carriers
- **HTTP Method:** POST
- **Full Path:** `/api/carriers/ai/rates/predict`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "origin": "string (required)",
  "destination": "string (required)",
  "carrier": "string (required)",
  "containerType": "string (required)",
  "currentRateUSD": "number (required)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/carriers/ai/rates/predict
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "origin": "Mumbai",
  "destination": "New York",
  "carrier": "MAERSK",
  "containerType": "40HC",
  "currentRateUSD": 3000.00
}
```

**Expected Success Response (200):**
```json
{
  "predicted_rate": 3250.50,
  "confidence": 0.85,
  "factors": [...]
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
- **401 Unauthorized:** Invalid or missing token

---

### 16. Get All Quotes (Quoted Shipments)
- **Endpoint Group:** Carriers
- **HTTP Method:** POST
- **Full Path:** `/api/carriers/AllQuotes`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** supplier (ASSUMED - filters by supplier_id)

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{}  // Empty body or any valid JSON
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/carriers/AllQuotes
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{}
```

**Expected Success Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439012",
      "shipment_number": "SH7761CB95",
      "status": "quoted",
      "supplier_id": "507f1f77bcf86cd799439011",
      ...
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
- **503 Service Unavailable:** Database error

---

### 17. Accept Quote
- **Endpoint Group:** Carriers
- **HTTP Method:** POST
- **Full Path:** `/api/carriers/acceptQuote`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** supplier (ASSUMED - filters by supplier_id)

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "quote_id": "string (required, MongoDB ObjectId)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/carriers/acceptQuote
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "quote_id": "507f1f77bcf86cd799439012"
}
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "shipment_number": "SH7761CB95",
  "status": "booked",
  "quote_status": "accepted",
  "forwarder_id": "507f1f77bcf86cd799439013",
  ...
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
- **401 Unauthorized:** Invalid or missing token
- **404 Not Found:** Quote not found or not available
  ```json
  {
    "error": "Not Found",
    "reason": "Quote not found or not available",
    "module": "quotes",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

## Forwarder

### 18. Show Available Shipments
- **Endpoint Group:** Forwarder
- **HTTP Method:** GET
- **Full Path:** `/api/forwarder/show-shipments`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** forwarder

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/forwarder/show-shipments
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439012",
      "shipment_number": "SH7761CB95",
      "forwarder_id": null,
      "status": "draft",
      ...
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid token or user is not a forwarder
  ```json
  {
    "error": "Unauthorized",
    "reason": "User is not a forwarder",
    "module": "auth",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

### 19. Get Forwarder Profile
- **Endpoint Group:** Forwarder
- **HTTP Method:** GET
- **Full Path:** `/api/forwarder/my-profile`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** forwarder

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/forwarder/my-profile
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439013",
  "email": "forwarder@example.com",
  "name": "Jane Forwarder",
  "company_name": "XYZ Logistics",
  "phone": "+1234567890",
  "role": "forwarder",
  "country": "IN",
  "is_verified": false,
  "created_at": "2025-01-15T10:30:00.000000"
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid token or user is not a forwarder
- **503 Service Unavailable:** Database error

---

### 20. Accept Shipment Request (Submit Quote)
- **Endpoint Group:** Forwarder
- **HTTP Method:** PUT
- **Full Path:** `/api/forwarder/request-accept/<shipment_id>`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** forwarder

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "quote_amount": "number (required)",
  "quote_time": "string (optional, ISO 8601 datetime)",
  "quote_extra": "string (optional)"
}
```

**Requestly Configuration:**
```
Method: PUT
URL: http://localhost:8000/api/forwarder/request-accept/507f1f77bcf86cd799439012
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "quote_amount": 5000.00,
  "quote_time": "2025-12-27T12:00:00Z",
  "quote_extra": "Additional notes or conditions"
}
```

**Expected Success Response (200):**
```json
{
  "message": "Quote accepted successfully",
  "id": "507f1f77bcf86cd799439012",
  "shipment_number": "SH7761CB95",
  "quote_amount": 5000.00,
  "quote_status": "accepted",
  "status": "quoted",
  "quote_forwarder_id": "507f1f77bcf86cd799439013",
  ...
}
```

**Error Responses:**
- **400 Bad Request:** Missing quote_amount
  ```json
  {
    "error": "Bad Request",
    "reason": "quote_amount is required",
    "module": "validation",
    "safe_for_demo": true
  }
  ```
- **401 Unauthorized:** Invalid token or user is not a forwarder
- **404 Not Found:** Shipment not found or already assigned
  ```json
  {
    "error": "Not Found",
    "reason": "Shipment not found or already assigned to a forwarder",
    "module": "shipments",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

### 21. Get All Quotes (Forwarder)
- **Endpoint Group:** Forwarder
- **HTTP Method:** POST
- **Full Path:** `/api/forwarder/all-quotes`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** forwarder

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{}  // Empty body or any valid JSON
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/forwarder/all-quotes
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{}
```

**Expected Success Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439012",
      "shipment_number": "SH7761CB95",
      "quote_forwarder_id": "507f1f77bcf86cd799439013",
      "quote_status": "accepted",
      ...
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid token or user is not a forwarder
- **503 Service Unavailable:** Database error

---

### 22. Get Accepted Quotes (Forwarder)
- **Endpoint Group:** Forwarder
- **HTTP Method:** GET
- **Full Path:** `/api/forwarder/accepted-quotes`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** forwarder

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/forwarder/accepted-quotes
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439012",
      "shipment_number": "SH7761CB95",
      "status": "booked",
      "quote_status": "accepted",
      "forwarder_id": "507f1f77bcf86cd799439013",
      "supplier_details": {
        "name": "John Supplier",
        "phone": "+1234567890",
        "company_name": "ABC Trading Co"
      },
      ...
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid token or user is not a forwarder
- **503 Service Unavailable:** Database error

---

## Quotes

### 23. Get Shipment Quotes
- **Endpoint Group:** Quotes
- **HTTP Method:** GET
- **Full Path:** `/api/quotes/shipments/<shipment_id>/quotes`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/quotes/shipments/507f1f77bcf86cd799439012/quotes
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439014",
      "shipment_id": "507f1f77bcf86cd799439012",
      "forwarder_id": "507f1f77bcf86cd799439013",
      "forwarder_name": "Jane Forwarder",
      "forwarder_company": "XYZ Logistics",
      "freight_amount_usd": 4500.00,
      "total_amount_usd": 5000.00,
      "status": "pending",
      ...
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
- **404 Not Found:** Shipment not found
  ```json
  {
    "error": "Not Found",
    "reason": "Shipment not found",
    "module": "quotes",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

### 24. Accept Quote (Supplier)
- **Endpoint Group:** Quotes
- **HTTP Method:** POST
- **Full Path:** `/api/quotes/shipments/<shipment_id>/accept-quote`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** supplier

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Query Parameters:**
- `quote_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/quotes/shipments/507f1f77bcf86cd799439012/accept-quote?quote_id=507f1f77bcf86cd799439014
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439014",
  "shipment_id": "507f1f77bcf86cd799439012",
  "forwarder_id": "507f1f77bcf86cd799439013",
  "status": "accepted",
  "forwarder_name": "Jane Forwarder",
  "forwarder_company": "XYZ Logistics",
  ...
}
```

**Error Responses:**
- **400 Bad Request:** Missing quote_id or quote already processed
  ```json
  {
    "error": "Invalid input",
    "reason": "quote_id query parameter is required",
    "module": "quotes",
    "safe_for_demo": true
  }
  ```
- **403 Forbidden:** Not a supplier or not authorized
  ```json
  {
    "error": "Forbidden",
    "reason": "Only suppliers can accept quotes",
    "module": "quotes",
    "safe_for_demo": true
  }
  ```
- **404 Not Found:** Shipment or quote not found
- **500 Internal Server Error:** Server error

---

### 25. Update Quote
- **Endpoint Group:** Quotes
- **HTTP Method:** PUT
- **Full Path:** `/api/quotes/quotes/<quote_id>`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** forwarder

**Path Parameters:**
- `quote_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "status": "string (required, one of: 'pending', 'rejected')",
  "remarks": "string (optional)"
}
```

**Requestly Configuration:**
```
Method: PUT
URL: http://localhost:8000/api/quotes/quotes/507f1f77bcf86cd799439014
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "status": "rejected",
  "remarks": "Price too high"
}
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439014",
  "status": "rejected",
  "remarks": "Price too high",
  ...
}
```

**Error Responses:**
- **400 Bad Request:** Invalid status value
  ```json
  {
    "error": "Invalid input",
    "reason": "Status must be pending or rejected",
    "module": "quotes",
    "safe_for_demo": true
  }
  ```
- **403 Forbidden:** Not a forwarder or not authorized
  ```json
  {
    "error": "Forbidden",
    "reason": "Only forwarders can update quotes",
    "module": "quotes",
    "safe_for_demo": true
  }
  ```
- **404 Not Found:** Quote not found
- **500 Internal Server Error:** Server error

---

## Tracking

### 26. Get Shipment Tracking
- **Endpoint Group:** Tracking
- **HTTP Method:** GET
- **Full Path:** `/api/tracking/shipments/<shipment_id>`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/tracking/shipments/507f1f77bcf86cd799439012
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "shipment_id": "507f1f77bcf86cd799439012",
  "shipment_number": "SH7761CB95",
  "current_status": "in_transit",
  "origin_port": "Mumbai",
  "destination_port": "New York",
  "estimated_arrival": "2025-02-15T10:30:00.000000",
  "actual_arrival": null,
  "events": [
    {
      "id": "507f1f77bcf86cd799439015",
      "status": "in_transit",
      "location": "Port of Singapore",
      "description": "Vessel departed",
      "timestamp": "2025-01-20T10:30:00.000000",
      ...
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
- **404 Not Found:** Shipment not found
  ```json
  {
    "error": "Not Found",
    "reason": "Shipment not found",
    "module": "tracking",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

### 27. Create Tracking Event
- **Endpoint Group:** Tracking
- **HTTP Method:** POST
- **Full Path:** `/api/tracking/shipments/<shipment_id>/events`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** forwarder

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "status": "string (required, one of: 'booked', 'gate_in', 'vessel_departed', 'in_transit', 'port_arrival', 'gate_out', 'customs_clearance', 'delivered', 'held', 'delayed')",
  "location": "string (required, min 2 chars)",
  "description": "string (required, min 5 chars)",
  "vessel_name": "string (optional)",
  "voyage_number": "string (optional)",
  "container_number": "string (optional)",
  "remarks": "string (optional)",
  "estimated_datetime": "string (optional, ISO 8601)",
  "actual_datetime": "string (optional, ISO 8601)",
  "documents": "array (optional, array of strings)",
  "is_milestone": "boolean (optional, default: false)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/tracking/shipments/507f1f77bcf86cd799439012/events
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "status": "in_transit",
  "location": "Port of Singapore",
  "description": "Vessel departed from origin port",
  "vessel_name": "MV MAERSK EXPRESS",
  "voyage_number": "V123",
  "container_number": "CONTAINER123456",
  "remarks": "On schedule",
  "estimated_datetime": "2025-01-25T10:30:00Z",
  "actual_datetime": "2025-01-20T10:30:00Z",
  "is_milestone": true
}
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439015",
  "shipment_id": "507f1f77bcf86cd799439012",
  "created_by": "507f1f77bcf86cd799439013",
  "status": "in_transit",
  "location": "Port of Singapore",
  "description": "Vessel departed from origin port",
  "vessel_name": "MV MAERSK EXPRESS",
  "voyage_number": "V123",
  "container_number": "CONTAINER123456",
  "timestamp": "2025-01-20T10:30:00.000000",
  ...
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
  ```json
  {
    "error": "Invalid input",
    "reason": "Request data validation failed",
    "module": "validation",
    "safe_for_demo": true,
    "errors": [
      {
        "loc": ["status"],
        "msg": "Status is required",
        "type": "value_error"
      }
    ]
  }
  ```
- **403 Forbidden:** Not a forwarder
  ```json
  {
    "error": "Forbidden",
    "reason": "Only forwarders can create tracking events",
    "module": "tracking",
    "safe_for_demo": true
  }
  ```
- **404 Not Found:** Shipment not found
- **500 Internal Server Error:** Server error

---

### 28. Get Latest Tracking Event
- **Endpoint Group:** Tracking
- **HTTP Method:** GET
- **Full Path:** `/api/tracking/shipments/<shipment_id>/events/latest`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/tracking/shipments/507f1f77bcf86cd799439012/events/latest
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439015",
  "shipment_id": "507f1f77bcf86cd799439012",
  "status": "in_transit",
  "location": "Port of Singapore",
  "description": "Vessel departed from origin port",
  "timestamp": "2025-01-20T10:30:00.000000",
  ...
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
- **404 Not Found:** Shipment or events not found
  ```json
  {
    "error": "Not Found",
    "reason": "No tracking events found",
    "module": "tracking",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

## Documents

### 29. Upload Document
- **Endpoint Group:** Documents
- **HTTP Method:** POST
- **Full Path:** `/api/documents/shipments/<shipment_id>/upload`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body Schema (Form Data):**
- `file` (file, required) - PDF, PNG, JPEG, JPG (max 16MB)
- `document_type` (string, optional) - One of: 'invoice', 'packing_list', 'commercial_invoice', 'certificate_of_origin', 'bill_of_lading', 'house_bl', 'master_bl', 'telex_release', 'other' (default: 'invoice')

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/documents/shipments/507f1f77bcf86cd799439012/upload
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body (Form Data):
  file: [SELECT FILE]
  document_type: invoice
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439016",
  "shipment_id": "507f1f77bcf86cd799439012",
  "uploaded_by": "507f1f77bcf86cd799439011",
  "type": "invoice",
  "file_name": "invoice.pdf",
  "file_url": "https://storage.example.com/documents/...",
  "file_size": 102400,
  "mime_type": "application/pdf",
  "extracted_data": null,
  "confidence_score": 0.0,
  "needs_review": true,
  "created_at": "2025-01-15T10:30:00.000000"
}
```

**Error Responses:**
- **400 Bad Request:** No file provided, invalid file type, or invalid document_type
  ```json
  {
    "error": "Invalid input",
    "reason": "Invalid file type. Allowed: PDF, JPEG, PNG",
    "module": "documents",
    "safe_for_demo": true
  }
  ```
- **401 Unauthorized:** Invalid or missing token
- **404 Not Found:** Shipment not found
- **500 Internal Server Error:** Upload or processing failed

---

### 30. Get Shipment Documents
- **Endpoint Group:** Documents
- **HTTP Method:** GET
- **Full Path:** `/api/documents/shipments/<shipment_id>/documents`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/documents/shipments/507f1f77bcf86cd799439012/documents
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439016",
      "shipment_id": "507f1f77bcf86cd799439012",
      "type": "invoice",
      "file_name": "invoice.pdf",
      "file_url": "https://storage.example.com/documents/...",
      "extracted_data": {...},
      "confidence_score": 0.85,
      ...
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
- **404 Not Found:** Shipment not found
- **503 Service Unavailable:** Database error

---

### 31. Get Document by ID
- **Endpoint Group:** Documents
- **HTTP Method:** GET
- **Full Path:** `/api/documents/documents/<document_id>`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `document_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/documents/documents/507f1f77bcf86cd799439016
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439016",
  "shipment_id": "507f1f77bcf86cd799439012",
  "type": "invoice",
  "file_name": "invoice.pdf",
  "file_url": "https://storage.example.com/documents/...",
  "extracted_data": {
    "total_weight_kg": 15000.5,
    "volume_cbm": 60.5,
    ...
  },
  "confidence_score": 0.85,
  ...
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token
- **404 Not Found:** Document not found
  ```json
  {
    "error": "Not Found",
    "reason": "Document not found",
    "module": "documents",
    "safe_for_demo": true
  }
  ```
- **503 Service Unavailable:** Database error

---

### 32. Extract Document (Not Implemented)
- **Endpoint Group:** Documents
- **HTTP Method:** POST
- **Full Path:** `/api/documents/documents/<document_id>/extract`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `document_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/documents/documents/507f1f77bcf86cd799439016/extract
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Error Response (501):**
```json
{
  "error": "Not Implemented",
  "reason": "Extraction from stored files not implemented",
  "module": "documents",
  "safe_for_demo": true
}
```

---

### 33. Autofill Shipment from Document
- **Endpoint Group:** Documents
- **HTTP Method:** POST
- **Full Path:** `/api/documents/documents/<document_id>/autofill`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `document_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "fields": "array (optional, default: ['gross_weight_kg', 'net_weight_kg', 'volume_cbm', 'total_packages', 'hs_code', 'goods_description'])"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/documents/documents/507f1f77bcf86cd799439016/autofill
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "fields": ["gross_weight_kg", "volume_cbm", "hs_code"]
}
```

**Expected Success Response (200):**
```json
{
  "document_id": "507f1f77bcf86cd799439016",
  "shipment_id": "507f1f77bcf86cd799439012",
  "updated_fields": ["gross_weight_kg", "volume_cbm", "hs_code"],
  "confidence": 0.85,
  "extracted_values": {
    "gross_weight_kg": 15000.5,
    "volume_cbm": 60.5,
    "hs_code": "12345678"
  }
}
```

**Error Responses:**
- **400 Bad Request:** Document has no extracted data
  ```json
  {
    "error": "Bad Request",
    "reason": "Document has no extracted data",
    "module": "documents",
    "safe_for_demo": true
  }
  ```
- **401 Unauthorized:** Invalid or missing token
- **404 Not Found:** Document or shipment not found
- **500 Internal Server Error:** Server error

---

## Customs

### 34. Submit Export Shipping Bill
- **Endpoint Group:** Customs
- **HTTP Method:** POST
- **Full Path:** `/api/customs/export/shipping-bill`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "exporterName": "string (required)",
  "invoiceNumber": "string (required)",
  "portOfLoading": "string (required)",
  "goodsValue": "number (required)",
  "shipmentId": "string (required, MongoDB ObjectId)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/customs/export/shipping-bill
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "exporterName": "ABC Trading Co",
  "invoiceNumber": "INV-2025-001",
  "portOfLoading": "Mumbai",
  "goodsValue": 50000.00,
  "shipmentId": "507f1f77bcf86cd799439012"
}
```

**Expected Success Response (201):**
```json
{
  "message": "Export shipping bill submitted successfully",
  "referenceId": "ICEGATE-EXPORT-A1B2C3D4"
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
  ```json
  {
    "error": "Invalid input",
    "reason": "Request data validation failed",
    "module": "validation",
    "safe_for_demo": true,
    "errors": [
      {
        "loc": ["exporterName"],
        "msg": "Exporter name is required",
        "type": "value_error"
      }
    ]
  }
  ```
- **401 Unauthorized:** Invalid or missing token

---

### 35. Submit Import Bill of Entry
- **Endpoint Group:** Customs
- **HTTP Method:** POST
- **Full Path:** `/api/customs/import/bill-of-entry`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "importerName": "string (required)",
  "invoiceNumber": "string (required)",
  "portOfDischarge": "string (required)",
  "dutyAmount": "number (required)",
  "shipmentId": "string (required, MongoDB ObjectId)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/customs/import/bill-of-entry
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "importerName": "DEF Imports",
  "invoiceNumber": "INV-2025-002",
  "portOfDischarge": "New York",
  "dutyAmount": 5000.00,
  "shipmentId": "507f1f77bcf86cd799439012"
}
```

**Expected Success Response (201):**
```json
{
  "message": "Import bill of entry submitted successfully",
  "referenceId": "ICEGATE-IMPORT-E5F6G7H8"
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
- **401 Unauthorized:** Invalid or missing token

---

### 36. Get Clearance Status
- **Endpoint Group:** Customs
- **HTTP Method:** GET
- **Full Path:** `/api/customs/clearance/status/<shipment_id>`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Path Parameters:**
- `shipment_id` (string, required) - MongoDB ObjectId

**Required Headers:**
```
Authorization: Bearer <access_token>
```

**Requestly Configuration:**
```
Method: GET
URL: http://localhost:8000/api/customs/clearance/status/507f1f77bcf86cd799439012
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Body: (none)
```

**Expected Success Response (200):**
```json
{
  "shipmentId": "507f1f77bcf86cd799439012",
  "exportStatus": "CLEARED",
  "importStatus": "PENDING",
  "reason": null
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid or missing token

---

### 37. Predict Customs Delay (AI)
- **Endpoint Group:** Customs
- **HTTP Method:** POST
- **Full Path:** `/api/customs/ai/prediction`
- **Authentication Required:** Yes
- **Authentication Type:** JWT Bearer
- **Role Required:** any

**Required Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "port": "string (required)",
  "rmsExamination": "boolean (required)",
  "dutyAmount": "number (required)",
  "documentsComplete": "boolean (required)"
}
```

**Requestly Configuration:**
```
Method: POST
URL: http://localhost:8000/api/customs/ai/prediction
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
  Content-Type: application/json
Body (JSON):
{
  "port": "Mumbai",
  "rmsExamination": false,
  "dutyAmount": 5000.00,
  "documentsComplete": true
}
```

**Expected Success Response (200):**
```json
{
  "predicted_delay_days": 2,
  "confidence": 0.75,
  "factors": [...]
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors
- **401 Unauthorized:** Invalid or missing token

---

## Common Error Responses

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "reason": "User not found",
  "module": "auth",
  "safe_for_demo": true
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "reason": "Insufficient permissions",
  "module": "auth",
  "safe_for_demo": true
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "reason": "Resource not found",
  "module": "<module_name>",
  "safe_for_demo": true
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "reason": "<error_message>",
  "module": "<module_name>",
  "safe_for_demo": false
}
```

### 503 Service Unavailable
```json
{
  "error": "Service Unavailable",
  "reason": "<error_message>",
  "module": "database",
  "safe_for_demo": true
}
```

---

## Notes

1. **Base URL:** Update `http://localhost:8000` based on your environment
2. **Token Expiry:** JWT tokens expire in 30 minutes (1800 seconds)
3. **File Upload:** Maximum file size is 16MB
4. **Allowed File Types:** PDF, PNG, JPEG, JPG
5. **MongoDB ObjectIds:** Use valid MongoDB ObjectId format (24 hex characters)
6. **Date Formats:** Use ISO 8601 format for datetime fields (e.g., `2025-01-15T10:30:00Z`)
7. **Role-Based Access:** Some endpoints require specific roles (supplier, forwarder, buyer)
8. **ASSUMED Fields:** Fields marked as "ASSUMED" are inferred from code logic and may need verification

---

## Quick Reference: Authentication Flow

1. **Register:** `POST /api/auth/register` → Get user object
2. **Login:** `POST /api/auth/login` → Get `access_token`
3. **Use Token:** Include `Authorization: Bearer <access_token>` header in subsequent requests

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Generated for:** Requestly API Client


