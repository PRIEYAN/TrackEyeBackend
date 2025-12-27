from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.shipment import Shipment
from app.models.user import User
from app.utils.auth import get_current_user
from app.views.response_formatter import success_response, error_response, validation_error_response
from datetime import datetime
import uuid
import logging


logger = logging.getLogger(__name__)

forwarder_bp = Blueprint('forwarder', __name__)

@forwarder_bp.route('/', methods=['POST', 'OPTIONS'])

@forwarder_bp.route('/forwarder/show-shipments', methods=['GET'])
@jwt_required()
def show_shipments():
    if request.method == 'OPTIONS':
        return '', 200
    
    user = get_current_user()
    checkForwarder = User.objects(id=user.id, role='forwarder').first()
    if not checkForwarder:
        return error_response("Unauthorized", "User is not a forwarder", "auth", True, status_code=401)
    
    #get all shipments withour forwarder_id
    shipments = Shipment.objects()

    return success_response([shipment.to_dict() for shipment in shipments], status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)

@forwarder_bp.route('/forwarder/my-profile', methods=['GET'])
@jwt_required()
def my_profile():
    user = get_current_user()
    checkForwarder = User.objects(id=user.id, role='forwarder').first()
    if not checkForwarder:
        return error_response("Unauthorized", "User is not a forwarder", "auth", True, status_code=401)
    
    return success_response(checkForwarder.to_dict(), status_code=200)
        except Exception as e:
            return error_response("Service Unavailable", str(e), "database", True, status_code=503)
    except Exception as e:
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)