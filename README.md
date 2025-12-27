# TradeFlow AI - Flask Backend

Flask MVC backend for TradeFlow AI - A comprehensive trade and logistics management system.

## Features

- User authentication and authorization (JWT)
- Shipment management
- Document upload and AI-powered extraction (Google Gemini)
- Quote management
- Tracking events
- Carrier integrations
- Customs integrations
- Supabase Storage integration

## Technology Stack

- **Framework**: Flask 3.0.0
- **Database**: MongoDB Atlas
- **ORM**: MongoEngine 0.27.0
- **Database Driver**: pymongo 4.6.1
- **Authentication**: Flask-JWT-Extended
- **AI**: Google Generative AI (Gemini)
- **Storage**: Supabase Storage (optional - can be switched to GridFS)

## Project Structure

```
backend-express/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── shipment.py
│   │   ├── document.py
│   │   ├── quote.py
│   │   └── tracking_event.py
│   ├── controllers/         # Route handlers (MVC Controllers)
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   ├── carrier_controller.py
│   │   ├── customs_controller.py
│   │   ├── document_controller.py
│   │   ├── quote_controller.py
│   │   ├── tracking_controller.py
│   │   └── health_controller.py
│   ├── services/            # Business logic services
│   │   ├── storage_service.py
│   │   └── ai_service.py
│   ├── utils/               # Utilities
│   │   ├── auth.py
│   │   ├── error_handler.py
│   │   └── validators.py
│   └── views/               # Response formatters (MVC Views)
│       └── response_formatter.py
├── migrations/              # Database migrations
├── uploads/                 # Temporary file uploads
├── requirements.txt
├── .env.example
├── run.py
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `MONGODB_URI`: MongoDB Atlas connection string (default provided)
- `MONGODB_DB_NAME`: Database name (default: 'tradeflow')
- `SECRET_KEY`: Secret key for Flask sessions
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `SUPABASE_URL`: Supabase project URL (for file storage)
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key
- `STORAGE_BUCKET`: Supabase storage bucket name
- `GEMINI_API_KEY`: Google Gemini API key

### 3. Database Setup

MongoDB collections are created automatically when you first use the models. No migrations needed!

### 4. Run the Application

```bash
python run.py
```

Or using Flask CLI:

```bash
flask run --host=0.0.0.0 --port=8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### User
- `GET /api/me` - Get current user info

### Carriers
- `POST /api/carriers/booking/create` - Create booking
- `GET /api/carriers/booking/status/<booking_number>` - Get booking status
- `GET /api/carriers/schedule/search` - Search vessel schedules
- `POST /api/carriers/rates/quote` - Get rate quote
- `GET /api/carriers/tracking/container/<container_number>` - Track container
- `POST /api/carriers/ai/rates/predict` - AI rate prediction

### Customs
- `POST /api/customs/export/shipping-bill` - Submit export shipping bill
- `POST /api/customs/import/bill-of-entry` - Submit import bill of entry
- `GET /api/customs/clearance/status/<shipment_id>` - Get clearance status
- `POST /api/customs/ai/prediction` - AI delay prediction

### Documents
- `POST /api/documents/shipments/<shipment_id>/upload` - Upload document
- `GET /api/documents/shipments/<shipment_id>/documents` - Get shipment documents
- `GET /api/documents/documents/<document_id>` - Get document details
- `POST /api/documents/documents/<document_id>/extract` - Trigger extraction
- `POST /api/documents/documents/<document_id>/autofill` - Auto-fill shipment from document

### Quotes
- `GET /api/quotes/shipments/<shipment_id>/quotes` - Get shipment quotes
- `POST /api/quotes/shipments/<shipment_id>/accept-quote` - Accept quote
- `PUT /api/quotes/quotes/<quote_id>` - Update quote

### Tracking
- `GET /api/tracking/shipments/<shipment_id>` - Get tracking history
- `POST /api/tracking/shipments/<shipment_id>/events` - Create tracking event
- `GET /api/tracking/shipments/<shipment_id>/events/latest` - Get latest event

### Health
- `GET /` - Root endpoint
- `GET /health` - Health check

## Authentication

All endpoints except `/api/auth/*`, `/`, and `/health` require JWT authentication.

Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Database Models (MongoDB Collections)

- **users**: User accounts (supplier, forwarder, buyer)
- **shipments**: Shipment records
- **documents**: Uploaded documents with extracted data
- **extraction_jobs**: AI extraction job tracking
- **quotes**: Forwarder quotes for shipments
- **tracking_events**: Shipment tracking events

All models use MongoEngine Document classes. Collections are created automatically on first use.

## Development

### MongoDB Notes

- No migrations needed - MongoDB is schema-less
- Indexes are defined in model meta classes
- Use MongoDB Compass or Atlas UI to view/manage data

### Code Formatting

```bash
black app/
isort app/
```

## License

Proprietary - TradeFlow AI

