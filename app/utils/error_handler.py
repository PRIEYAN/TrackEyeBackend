from flask import jsonify
from werkzeug.exceptions import HTTPException
from mongoengine.errors import ValidationError, DoesNotExist, OperationError
import traceback


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "reason": str(error.description) if hasattr(error, 'description') else "Invalid request",
            "module": "unknown",
            "safe_for_demo": True
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "error": "Unauthorized",
            "reason": "Invalid or missing authentication token",
            "module": "auth",
            "safe_for_demo": True
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "error": "Forbidden",
            "reason": "Insufficient permissions",
            "module": "auth",
            "safe_for_demo": True
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "reason": str(error.description) if hasattr(error, 'description') else "Resource not found",
            "module": "unknown",
            "safe_for_demo": True
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal Server Error",
            "reason": "An unexpected error occurred",
            "module": "unknown",
            "safe_for_demo": False
        }), 500
    
    @app.errorhandler(501)
    def not_implemented(error):
        return jsonify({
            "error": "Not Implemented",
            "reason": str(error.description) if hasattr(error, 'description') else "Feature not implemented",
            "module": "unknown",
            "safe_for_demo": True
        }), 501
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({
            "error": "Service Unavailable",
            "reason": str(error.description) if hasattr(error, 'description') else "Service temporarily unavailable",
            "module": "unknown",
            "safe_for_demo": True
        }), 503
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        app.logger.error(f"Validation error: {str(error)}")
        return jsonify({
            "error": "Invalid input",
            "reason": str(error),
            "module": "database",
            "safe_for_demo": True
        }), 400
    
    @app.errorhandler(DoesNotExist)
    def handle_not_found(error):
        app.logger.error(f"Not found error: {str(error)}")
        return jsonify({
            "error": "Not Found",
            "reason": "Resource not found",
            "module": "database",
            "safe_for_demo": True
        }), 404
    
    @app.errorhandler(OperationError)
    def handle_db_error(error):
        app.logger.error(f"Database error: {str(error)}")
        return jsonify({
            "error": "Service Unavailable",
            "reason": "Database connection error",
            "module": "database",
            "safe_for_demo": True
        }), 503
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        app.logger.error(f"Unhandled error: {str(error)}\n{traceback.format_exc()}")
        return jsonify({
            "error": "Internal Server Error",
            "reason": "An unexpected error occurred",
            "module": "unknown",
            "safe_for_demo": False
        }), 500

