from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.shipment import Shipment
from app.models.user import User
from app.utils.auth import get_current_user
from app.views.response_formatter import success_response, error_response
from mongoengine import Q
import logging

logger = logging.getLogger(__name__)

forwarder_bp = Blueprint('forwarder', __name__)


@forwarder_bp.route('/show-shipments', methods=['GET', 'OPTIONS'])
@jwt_required()
def show_shipments():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        checkForwarder = User.objects(id=user.id, role='forwarder').first()
        if not checkForwarder:
            return error_response("Unauthorized", "User is not a forwarder", "auth", True, status_code=401)
        
        # Get all shipments without forwarder_id (available for bidding)
        shipments = Shipment.objects(Q(forwarder_id__exists=False) | Q(forwarder_id=None))
        
        return success_response([shipment.to_dict() for shipment in shipments], status_code=200)
    except Exception as e:
        logger.error(f"Error in show_shipments: {str(e)}", exc_info=True)
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)


@forwarder_bp.route('/my-profile', methods=['GET', 'OPTIONS'])
@jwt_required()
def my_profile():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        checkForwarder = User.objects(id=user.id, role='forwarder').first()
        if not checkForwarder:
            return error_response("Unauthorized", "User is not a forwarder", "auth", True, status_code=401)
        
        return success_response(checkForwarder.to_dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error in my_profile: {str(e)}", exc_info=True)
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)


@forwarder_bp.route('/request-accept/<shipment_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
def request_accept(shipment_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        checkForwarder = User.objects(id=user.id, role='forwarder').first()
        if not checkForwarder:
            return error_response("Unauthorized", "User is not a forwarder", "auth", True, status_code=401)
        
        # Parse request data
        if request.is_json:
            data = request.get_json()
        elif request.data:
            import json
            data = json.loads(request.data)
        else:
            data = {}
        
        # Update quoteDetails in shipment Document
        shipment = Shipment.objects(id=shipment_id, forwarder_id=None).first()
        if not shipment:
            return error_response("Not Found", "Shipment not found or already assigned to a forwarder", "shipments", True, status_code=404)
        
        # Validate required fields
        quote_amount = data.get('quote_amount')
        if quote_amount is None:
            return error_response("Bad Request", "quote_amount is required", "validation", True, status_code=400)
        
        # Set quote details
        shipment.quote_amount = float(quote_amount)
        shipment.quote_forwarder_id = user  # ReferenceField expects User object
        shipment.quote_status = 'accepted'
        shipment.quote_extra = data.get('quote_extra', '')
        
        # Parse quote_time if provided
        quote_time = data.get('quote_time')
        if quote_time:
            try:
                if isinstance(quote_time, str):
                    from datetime import datetime
                    shipment.quote_time = datetime.fromisoformat(quote_time.replace('Z', '+00:00'))
                else:
                    shipment.quote_time = quote_time
            except Exception as e:
                logger.warning(f"Could not parse quote_time: {e}")
        
        shipment.save()
        
        return success_response( "Quote accepted successfully", shipment.to_dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error in request_accept: {str(e)}", exc_info=True)
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)