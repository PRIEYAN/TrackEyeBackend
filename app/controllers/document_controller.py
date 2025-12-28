from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from bson import ObjectId
from app.models.document import DocumentModel, ExtractionJob
from app.models.shipment import Shipment
from app.utils.auth import get_current_user
from app.services.storage_service import StorageService
from app.services.ai_service import AIService
from app.views.response_formatter import success_response, error_response
import os
import uuid
import requests
import base64
import re
from datetime import datetime

document_bp = Blueprint('document', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
ALLOWED_MIME_TYPES = {'application/pdf', 'image/png', 'image/jpeg', 'image/jpg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_invoice_date(date_str):
    """Parse various date formats and convert to YYYY-MM-DD"""
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # Try parsing MM/DD/YYYY format (e.g., 04/13/2013)
    mmddyyyy_match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if mmddyyyy_match:
        month, day, year = mmddyyyy_match.groups()
        try:
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
    
    # Try parsing DD/MM/YYYY format
    ddmmyyyy_match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if ddmmyyyy_match:
        day, month, year = ddmmyyyy_match.groups()
        try:
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
    
    # Try parsing YYYY-MM-DD format (already correct)
    yyyymmdd_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if yyyymmdd_match:
        return date_str
    
    # Try parsing ISO format
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        pass
    
    return date_str  # Return as-is if can't parse


def clean_numeric_value(value):
    """Clean numeric values by removing currency symbols, commas, and whitespace"""
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    value_str = str(value).strip()
    
    # Remove currency symbols
    value_str = re.sub(r'[$€₹£]', '', value_str)
    
    # Remove commas
    value_str = value_str.replace(',', '')
    
    # Remove whitespace
    value_str = value_str.strip()
    
    try:
        return float(value_str)
    except (ValueError, TypeError):
        return None

    
@document_bp.route('/uploadInvoice', methods=['POST'])
@jwt_required()
def upload_invoice():
    temp_path = None
    try:
        shipment_id = request.form.get("shipment_id")
        if not shipment_id:
            return error_response("Missing field", "shipment_id is required", "documents", True, 400)

        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "documents", True, 404)

        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, 401)

        file = request.files.get("file")
        if not file:
            return error_response("Missing file", "Invoice file is required", "documents", True, 400)

        if file.filename == '':
            return error_response("Invalid input", "No file selected", "documents", True, 400)

        if not allowed_file(file.filename):
            return error_response("Invalid input", "Invalid file type. Allowed: PDF, JPEG, PNG", "documents", True, 400)

        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
        os.makedirs(upload_folder, exist_ok=True)
        temp_path = os.path.join(upload_folder, f"{uuid.uuid4()}_{filename}")
        file.save(temp_path)

        mime_type = file.content_type or 'application/octet-stream'
        
        with open(temp_path, 'rb') as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        storage_service = StorageService()
        storage_path = storage_service.generate_document_path(shipment_id, filename)
        file_url = storage_service.upload_file(temp_path, storage_path)

        if not file_url:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return error_response("Internal Server Error", "Failed to upload file to storage", "documents", False, 500)

        ai_service = AIService()
        extracted_data, confidence, method = ai_service.extract_document_data(temp_path, "invoice")
        
        if not extracted_data:
            current_app.logger.warning("No data extracted from invoice")
        else:
            current_app.logger.debug(f"Extracted data keys: {list(extracted_data.keys())}")

        # Helper function to get value with multiple fallbacks
        def get_field(*keys, default=None):
            if not extracted_data:
                return default
            for key in keys:
                value = extracted_data.get(key)
                if value is not None and value != "":
                    return value
            return default
        
        # Extract with comprehensive fallbacks for different field names
        invoice_number = get_field("invoice_number", "invoiceNumber", "invoice_no", "invoiceNo")
        invoice_date_raw = get_field("date", "invoice_date", "invoiceDate", "date_of_issue")
        invoice_date = parse_invoice_date(invoice_date_raw) if invoice_date_raw else None
        buyer_name = get_field("buyer_name", "buyerName", "buyer", "client_name", "clientName", "importer", "customer")
        seller_name = get_field("seller_name", "sellerName", "seller", "vendor", "exporter", "company_name", "companyName")
        company_name = get_field("company_name", "companyName", "seller_name", "sellerName", "seller")
        
        # Amount extraction - prioritize gross_worth, then total_amount, then amount
        total_amount_raw = get_field("gross_worth", "grossWorth", "total_amount", "totalAmount", "total", "amount")
        total_amount = clean_numeric_value(total_amount_raw)
        
        net_amount_raw = get_field("net_worth", "netWorth", "net_amount", "netAmount", "subtotal")
        net_amount = clean_numeric_value(net_amount_raw)
        
        # Tax extraction
        tax_amount_raw = get_field("tax_amount", "taxAmount", "vat", "VAT", "gst", "GST", "tax")
        tax_amount = clean_numeric_value(tax_amount_raw)
        
        tax_percentage_raw = get_field("tax_percentage", "taxPercentage", "vat_percentage", "vatPercentage")
        tax_percentage = clean_numeric_value(tax_percentage_raw)
        
        # Currency detection
        currency = get_field("currency", "Currency")
        if not currency:
            # Try to infer from extracted data
            currency_str = str(extracted_data) if extracted_data else ""
            if "$" in currency_str or "USD" in currency_str.upper():
                currency = "USD"
            elif "€" in currency_str or "EUR" in currency_str.upper():
                currency = "EUR"
            elif "₹" in currency_str or "INR" in currency_str.upper():
                currency = "INR"
        
        invoice_data = {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "buyer_name": buyer_name,
            "seller_name": seller_name,
            "hsn_code": get_field("hs_code", "hsn_code", "hsnCode", "hsCode"),
            "total_amount": total_amount,
            "net_amount": net_amount,
            "currency": currency or "USD",
            "tax_amount": tax_amount,
            "tax_percentage": tax_percentage,
            "extracted_raw": extracted_data
        }

        # Build comprehensive invoice details
        items = get_field("items", "Items", default=[])
        if items and isinstance(items, list):
            # Ensure items are properly formatted
            formatted_items = []
            for item in items:
                if isinstance(item, dict):
                    formatted_items.append({
                        "description": item.get("description") or item.get("Description") or "",
                        "quantity": clean_numeric_value(item.get("quantity") or item.get("Qty") or item.get("qty") or 0),
                        "unit_price": clean_numeric_value(item.get("unit_price") or item.get("net_price") or item.get("Net price") or item.get("unitPrice") or 0),
                        "total": clean_numeric_value(item.get("total") or item.get("net_worth") or item.get("gross_worth") or item.get("netWorth") or item.get("grossWorth") or 0),
                        "hs_code": item.get("hs_code") or item.get("hsn_code") or item.get("hsCode") or None,
                        "vat_percentage": clean_numeric_value(item.get("vat_percentage") or item.get("VAT [%]") or item.get("vatPercentage") or None),
                    })
            items = formatted_items

        due_date_raw = get_field("due_date", "dueDate", "Due Date")
        due_date = parse_invoice_date(due_date_raw) if due_date_raw else None
        
        invoice_details = {
            "unique_invoice_number": invoice_number,
            "company_name": company_name or seller_name,
            "buyer_company_name": buyer_name,
            "seller_company_name": seller_name,
            "seller_address": get_field("seller_address", "sellerAddress"),
            "buyer_address": get_field("buyer_address", "buyerAddress", "client_address"),
            "seller_tax_id": get_field("seller_tax_id", "sellerTaxId", "tax_id", "Tax Id"),
            "buyer_tax_id": get_field("buyer_tax_id", "buyerTaxId"),
            "iban": get_field("iban", "IBAN"),
            "summary": get_field("summary", "Summary") or (f"Invoice {invoice_number} from {seller_name} to {buyer_name}" if invoice_number and seller_name and buyer_name else None),
            "date_of_invoice": invoice_date,
            "payment_terms": get_field("payment_terms", "paymentTerms", "Payment Terms"),
            "due_date": due_date,
            "po_number": get_field("po_number", "poNumber", "po_no", "purchase_order", "PO Number"),
            "total_amount": total_amount,
            "net_amount": net_amount,
            "currency": currency or "USD",
            "tax_amount": tax_amount,
            "tax_percentage": tax_percentage,
            "items": items if items else None,
            "notes": get_field("notes", "Notes", "remarks", "terms"),
            "extracted_at": datetime.utcnow().isoformat(),
            "confidence": confidence
        }
        
        # Log extracted invoice details for debugging
        current_app.logger.info(f"Invoice extracted - Number: {invoice_number}, Seller: {seller_name}, Buyer: {buyer_name}, Total: {total_amount}, Items: {len(items) if items else 0}")

        if not shipment.metadata:
            shipment.metadata = {}
        shipment.metadata['invoice_details'] = invoice_details
        shipment.metadata['invoice_image_base64'] = image_base64
        shipment.metadata['invoice_image_mime_type'] = mime_type
        shipment.save()

        file_size = os.path.getsize(temp_path)

        document_metadata = {
            'base64_image': image_base64,
            'base64_mime_type': mime_type
        }

        document = DocumentModel(
            shipment_id=shipment,
            uploaded_by=user,
            type="invoice",
            file_name=filename,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            extracted_data=invoice_data,
            confidence_score=confidence,
            extraction_method=method,
            needs_review=confidence < 0.8,
            metadata=document_metadata
        )
        document.save()

        extraction_job = ExtractionJob(
            document_id=document,
            status='completed' if extracted_data else 'failed'
        )
        extraction_job.save()

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        print(invoice_data)
        print(invoice_details)

        return success_response(
            "Invoice uploaded and processed",
            {
                "file_url": file_url,
                "extracted_data": invoice_data,
                "invoice_details": invoice_details,
                "confidence": confidence,
                "document_id": str(document.id),
                "shipment_id": str(shipment.id)
            }
        )
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return error_response("Internal Server Error", str(e), "documents", False, 500)

@document_bp.route('/shipments/<shipment_id>/upload', methods=['POST'])
@jwt_required()
def upload_document(shipment_id):
    temp_path = None
    try:
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "documents", True, status_code=404)
        
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        if 'file' not in request.files:
            return error_response("Invalid input", "No file provided", "documents", True, status_code=400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response("Invalid input", "No file selected", "documents", True, status_code=400)
        
        if not allowed_file(file.filename):
            return error_response("Invalid input", "Invalid file type. Allowed: PDF, JPEG, PNG", "documents", True, status_code=400)
        
        document_type = request.form.get('document_type', 'invoice')
        valid_types = ['invoice', 'packing_list', 'commercial_invoice', 'certificate_of_origin', 
                      'bill_of_lading', 'house_bl', 'master_bl', 'telex_release', 'other']
        if document_type not in valid_types:
            document_type = 'invoice'
        
        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
        os.makedirs(upload_folder, exist_ok=True)
        temp_path = os.path.join(upload_folder, f"{uuid.uuid4()}_{filename}")
        file.save(temp_path)
        
        storage_service = StorageService()
        storage_path = storage_service.generate_document_path(shipment_id, filename)
        file_url = storage_service.upload_file(temp_path, storage_path)
        
        if not file_url:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return error_response("Internal Server Error", "Failed to upload file to storage", "documents", False, status_code=500)
        
        mime_type = file.content_type or 'application/octet-stream'
        file_size = os.path.getsize(temp_path)
        
        document = DocumentModel(
            shipment_id=shipment,
            uploaded_by=user,
            type=document_type,
            file_name=filename,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type
        )
        document.save()
        
        extraction_job = ExtractionJob(
            document_id=document,
            status='pending'
        )
        extraction_job.save()
        
        from threading import Thread
        thread = Thread(target=process_document_extraction, args=(str(document.id), temp_path))
        thread.start()
        
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        
        return success_response(document.to_dict(), status_code=200)
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return error_response("Internal Server Error", str(e), "documents", False, status_code=500)


def process_document_extraction(document_id: str, file_path: str):
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            document = DocumentModel.objects(id=document_id).first()
            if not document:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                return
            
            ai_service = AIService()
            extracted_data, confidence, method = ai_service.extract_document_data(file_path, document.type)
            
            document.extracted_data = extracted_data
            document.confidence_score = confidence
            document.extraction_method = method
            document.needs_review = confidence < 0.8
            document.save()
            
            extraction_job = ExtractionJob.objects(document_id=document).first()
            if extraction_job:
                extraction_job.status = 'completed' if extracted_data else 'failed'
                extraction_job.save()
        except Exception as e:
            try:
                document = DocumentModel.objects(id=document_id).first()
                if document:
                    extraction_job = ExtractionJob.objects(document_id=document).first()
                    if extraction_job:
                        extraction_job.status = 'failed'
                        extraction_job.error_message = str(e)
                        extraction_job.save()
            except:
                pass
        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)


@document_bp.route('/shipments/<shipment_id>/list', methods=['GET'])
@jwt_required()
def get_shipment_documents(shipment_id):
    try:
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "documents", True, status_code=404)
        
        documents = DocumentModel.objects(shipment_id=shipment).all()
        documents_list = []
        for doc in documents:
            doc_dict = doc.to_dict()
            # Include base64 image if available
            if doc.metadata and 'base64_image' in doc.metadata:
                doc_dict['metadata'] = doc.metadata
            documents_list.append(doc_dict)
        
        return success_response(documents_list, status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", f"Database error: {str(e)}", "database", True, status_code=503)


@document_bp.route('/shipments/<shipment_id>/invoice', methods=['GET'])
@jwt_required()
def get_shipment_invoice(shipment_id):
    try:
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "documents", True, status_code=404)
        
        invoice_document = DocumentModel.objects(shipment_id=shipment, type="invoice").first()
        
        if not invoice_document:
            return error_response("Not Found", "No invoice found for this shipment", "documents", True, status_code=404)
        
        invoice_data = invoice_document.to_dict()
        
        # Get invoice details from shipment metadata
        invoice_details = None
        invoice_image_base64 = None
        invoice_image_mime_type = None
        
        if shipment.metadata:
            invoice_details = shipment.metadata.get('invoice_details')
            invoice_image_base64 = shipment.metadata.get('invoice_image_base64')
            invoice_image_mime_type = shipment.metadata.get('invoice_image_mime_type')
        
        # Also check document metadata for base64 image
        if not invoice_image_base64 and invoice_document.metadata:
            invoice_image_base64 = invoice_document.metadata.get('base64_image')
            invoice_image_mime_type = invoice_document.metadata.get('base64_mime_type')
        
        response_data = {
            'document': invoice_data,
            'invoice_details': invoice_details,
            'invoice_image_base64': invoice_image_base64,
            'invoice_image_mime_type': invoice_image_mime_type,
            'file_url': invoice_document.file_url,
            'extracted_data': invoice_document.extracted_data,
            'confidence_score': invoice_document.confidence_score,
        }
        
        return success_response(response_data, status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", f"Database error: {str(e)}", "database", True, status_code=503)


@document_bp.route('/<document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    try:
        document = DocumentModel.objects(id=document_id).first()
        if not document:
            return error_response("Not Found", "Document not found", "documents", True, status_code=404)
        
        return success_response(document.to_dict(), status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", f"Database error: {str(e)}", "database", True, status_code=503)


@document_bp.route('/<document_id>/extract', methods=['POST'])
@jwt_required()
def extract_document(document_id):
    return error_response("Not Implemented", "Extraction from stored files not implemented", "documents", True, status_code=501)


@document_bp.route('/<document_id>/autofill', methods=['POST'])
@jwt_required()
def autofill_shipment(document_id):
    try:
        document = DocumentModel.objects(id=document_id).first()
        if not document:
            return error_response("Not Found", "Document not found", "documents", True, status_code=404)
        
        if not document.extracted_data:
            return error_response("Bad Request", "Document has no extracted data", "documents", True, status_code=400)
        
        shipment = document.shipment_id
        if not shipment:
            return error_response("Not Found", "Shipment not found", "documents", True, status_code=404)
        
        data = request.get_json() or {}
        fields = data.get('fields', ['gross_weight_kg', 'net_weight_kg', 'volume_cbm', 
                                     'total_packages', 'hs_code', 'goods_description'])
        
        extracted = document.extracted_data
        updated_fields = []
        extracted_values = {}
        
        field_mapping = {
            'gross_weight_kg': ['total_weight_kg', 'gross_weight', 'weight_kg'],
            'net_weight_kg': ['net_weight', 'net_weight_kg'],
            'volume_cbm': ['volume_cbm', 'volume', 'total_volume'],
            'total_packages': ['total_packages', 'packages', 'quantity'],
            'hs_code': ['hs_code', 'hscode', 'harmonized_code'],
            'goods_description': ['description', 'goods_description', 'item_description']
        }
        
        for field in fields:
            if field in field_mapping:
                for key in field_mapping[field]:
                    if key in extracted:
                        value = extracted[key]
                        if value:
                            setattr(shipment, field, value)
                            updated_fields.append(field)
                            extracted_values[field] = value
                            break
        
        shipment.save()
        
        return success_response({
            "document_id": str(document.id),
            "shipment_id": str(shipment.id),
            "updated_fields": updated_fields,
            "confidence": document.confidence_score,
            "extracted_values": extracted_values
        }, status_code=200)
    except Exception as e:
        return error_response("Internal Server Error", str(e), "documents", False, status_code=500)
