from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.utils.validators import validate_request_json
from app.views.response_formatter import success_response, error_response, validation_error_response
import uuid

customs_bp = Blueprint('customs', __name__)


@customs_bp.route('/export/shipping-bill', methods=['POST'])
@jwt_required()
def submit_export_shipping_bill():
    data, error_response_obj, status = validate_request_json()
    if error_response_obj:
        return error_response_obj, status
    
    errors = []
    exporter_name = data.get('exporterName')
    invoice_number = data.get('invoiceNumber')
    port_of_loading = data.get('portOfLoading')
    goods_value = data.get('goodsValue')
    shipment_id = data.get('shipmentId')
    
    if not exporter_name:
        errors.append({"loc": ["exporterName"], "msg": "Exporter name is required", "type": "value_error"})
    if not invoice_number:
        errors.append({"loc": ["invoiceNumber"], "msg": "Invoice number is required", "type": "value_error"})
    if not port_of_loading:
        errors.append({"loc": ["portOfLoading"], "msg": "Port of loading is required", "type": "value_error"})
    if goods_value is None or not isinstance(goods_value, (int, float)):
        errors.append({"loc": ["goodsValue"], "msg": "Goods value is required and must be a number", "type": "value_error"})
    if not shipment_id:
        errors.append({"loc": ["shipmentId"], "msg": "Shipment ID is required", "type": "value_error"})
    
    if errors:
        return validation_error_response(errors)
    
    reference_id = f"ICEGATE-EXPORT-{uuid.uuid4().hex[:8].upper()}"
    
    return success_response({
        "message": "Export shipping bill submitted successfully",
        "referenceId": reference_id
    }, status_code=201)


@customs_bp.route('/import/bill-of-entry', methods=['POST'])
@jwt_required()
def submit_import_bill_of_entry():
    data, error_response_obj, status = validate_request_json()
    if error_response_obj:
        return error_response_obj, status
    
    errors = []
    importer_name = data.get('importerName')
    invoice_number = data.get('invoiceNumber')
    port_of_discharge = data.get('portOfDischarge')
    duty_amount = data.get('dutyAmount')
    shipment_id = data.get('shipmentId')
    
    if not importer_name:
        errors.append({"loc": ["importerName"], "msg": "Importer name is required", "type": "value_error"})
    if not invoice_number:
        errors.append({"loc": ["invoiceNumber"], "msg": "Invoice number is required", "type": "value_error"})
    if not port_of_discharge:
        errors.append({"loc": ["portOfDischarge"], "msg": "Port of discharge is required", "type": "value_error"})
    if duty_amount is None or not isinstance(duty_amount, (int, float)):
        errors.append({"loc": ["dutyAmount"], "msg": "Duty amount is required and must be a number", "type": "value_error"})
    if not shipment_id:
        errors.append({"loc": ["shipmentId"], "msg": "Shipment ID is required", "type": "value_error"})
    
    if errors:
        return validation_error_response(errors)
    
    reference_id = f"ICEGATE-IMPORT-{uuid.uuid4().hex[:8].upper()}"
    
    return success_response({
        "message": "Import bill of entry submitted successfully",
        "referenceId": reference_id
    }, status_code=201)


@customs_bp.route('/clearance/status/<shipment_id>', methods=['GET'])
@jwt_required()
def get_clearance_status(shipment_id):
    return success_response({
        "shipmentId": shipment_id,
        "exportStatus": "CLEARED",
        "importStatus": "PENDING",
        "reason": None
    })


@customs_bp.route('/ai/prediction', methods=['POST'])
@jwt_required()
def predict_delay():
    data, error_response_obj, status = validate_request_json()
    if error_response_obj:
        return error_response_obj, status
    
    errors = []
    port = data.get('port')
    rms_examination = data.get('rmsExamination')
    duty_amount = data.get('dutyAmount')
    documents_complete = data.get('documentsComplete')
    
    if not port:
        errors.append({"loc": ["port"], "msg": "Port is required", "type": "value_error"})
    if rms_examination is None:
        errors.append({"loc": ["rmsExamination"], "msg": "RMS examination status is required", "type": "value_error"})
    if duty_amount is None or not isinstance(duty_amount, (int, float)):
        errors.append({"loc": ["dutyAmount"], "msg": "Duty amount is required and must be a number", "type": "value_error"})
    if documents_complete is None:
        errors.append({"loc": ["documentsComplete"], "msg": "Documents complete status is required", "type": "value_error"})
    
    if errors:
        return validation_error_response(errors)
    
    from app.services.ai_service import AIService
    ai_service = AIService()
    prediction = ai_service.predict_customs_delay(port, rms_examination, duty_amount, documents_complete)
    
    return success_response(prediction)

