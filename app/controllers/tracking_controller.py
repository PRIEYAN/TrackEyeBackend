from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.tracking_event import TrackingEvent
from app.models.shipment import Shipment
from app.utils.auth import get_current_user, require_role
from app.utils.validators import validate_request_json
from app.views.response_formatter import success_response, error_response, validation_error_response
from datetime import datetime

tracking_bp = Blueprint('tracking', __name__)


@tracking_bp.route('/shipments/<shipment_id>', methods=['GET'])
@jwt_required()
def get_shipment_tracking(shipment_id):
    try:
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "tracking", True, status_code=404)
        
        events = TrackingEvent.objects(shipment_id=shipment).order_by('-timestamp').all()
        
        latest_event = events[0] if events else None
        current_status = latest_event.status if latest_event else shipment.status
        
        return success_response({
            "shipment_id": str(shipment.id),
            "shipment_number": shipment.shipment_number,
            "current_status": current_status,
            "origin_port": shipment.origin_port,
            "destination_port": shipment.destination_port,
            "estimated_arrival": shipment.preferred_eta.isoformat() if shipment.preferred_eta else None,
            "actual_arrival": shipment.actual_eta.isoformat() if shipment.actual_eta else None,
            "events": [event.to_dict() for event in events]
        }, status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", f"Database error: {str(e)}", "database", True, status_code=503)


@tracking_bp.route('/shipments/<shipment_id>/events', methods=['POST'])
@jwt_required()
def create_tracking_event(shipment_id):
    try:
        user = get_current_user()
        if not user or user.role != 'forwarder':
            return error_response("Forbidden", "Only forwarders can create tracking events", "tracking", True, status_code=403)
        
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "tracking", True, status_code=404)
        
        data, error_response_obj, status = validate_request_json()
        if error_response_obj:
            return error_response_obj, status
        
        errors = []
        status_value = data.get('status')
        location = data.get('location')
        description = data.get('description')
        
        valid_statuses = ['booked', 'gate_in', 'vessel_departed', 'in_transit', 'port_arrival', 
                         'gate_out', 'customs_clearance', 'delivered', 'held', 'delayed']
        
        if not status_value:
            errors.append({"loc": ["status"], "msg": "Status is required", "type": "value_error"})
        elif status_value not in valid_statuses:
            errors.append({"loc": ["status"], "msg": f"Status must be one of: {', '.join(valid_statuses)}", "type": "value_error"})
        
        if not location:
            errors.append({"loc": ["location"], "msg": "Location is required", "type": "value_error"})
        elif len(location) < 2:
            errors.append({"loc": ["location"], "msg": "Location must be at least 2 characters", "type": "value_error"})
        
        if not description:
            errors.append({"loc": ["description"], "msg": "Description is required", "type": "value_error"})
        elif len(description) < 5:
            errors.append({"loc": ["description"], "msg": "Description must be at least 5 characters", "type": "value_error"})
        
        if errors:
            return validation_error_response(errors)
        
        estimated_datetime = None
        if data.get('estimated_datetime'):
            try:
                estimated_datetime = datetime.fromisoformat(data['estimated_datetime'].replace('Z', '+00:00'))
            except:
                pass
        
        actual_datetime = None
        if data.get('actual_datetime'):
            try:
                actual_datetime = datetime.fromisoformat(data['actual_datetime'].replace('Z', '+00:00'))
            except:
                pass
        
        event = TrackingEvent(
            shipment_id=shipment,
            created_by=user,
            status=status_value,
            location=location,
            vessel_name=data.get('vessel_name'),
            voyage_number=data.get('voyage_number'),
            container_number=data.get('container_number'),
            description=description,
            remarks=data.get('remarks'),
            estimated_datetime=estimated_datetime,
            actual_datetime=actual_datetime,
            documents=data.get('documents', []),
            is_milestone=data.get('is_milestone', False)
        )
        
        event.save()
        shipment.status = status_value
        shipment.save()
        
        return success_response(event.to_dict(), status_code=200)
    except Exception as e:
        return error_response("Internal Server Error", str(e), "tracking", False, status_code=500)


@tracking_bp.route('/shipments/<shipment_id>/events/latest', methods=['GET'])
@jwt_required()
def get_latest_tracking_event(shipment_id):
    try:
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "tracking", True, status_code=404)
        
        event = TrackingEvent.objects(shipment_id=shipment).order_by('-timestamp').first()
        
        if not event:
            return error_response("Not Found", "No tracking events found", "tracking", True, status_code=404)
        
        return success_response(event.to_dict(), status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", f"Database error: {str(e)}", "database", True, status_code=503)
