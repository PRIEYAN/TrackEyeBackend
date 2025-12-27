from flask import Blueprint
from mongoengine import get_db
from app.config import Config
from app.views.response_formatter import success_response

health_bp = Blueprint('health', __name__)


@health_bp.route('/', methods=['GET'])
def root():
    return success_response({
        "message": f"Welcome to {Config.PROJECT_NAME} API",
        "docs": "/api/docs",
        "version": Config.VERSION,
        "environment": "development" if Config.DEBUG else "production"
    })


@health_bp.route('/health', methods=['GET'])
def health_check():
    try:
        db = get_db()
        db.command('ping')
        db_status = "connected"
        status = "healthy"
        message = None
    except Exception as e:
        db_status = "disconnected"
        status = "degraded"
        message = f"Database connection failed: {str(e)}"
    
    return success_response({
        "status": status,
        "version": Config.VERSION,
        "database": db_status,
        "message": message
    })

