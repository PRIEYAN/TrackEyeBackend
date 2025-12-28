import google.generativeai as genai
from app.config import Config
from typing import Optional, Dict, Any
import time
import base64
import os


class AIService:
    def __init__(self):
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.enabled = Config.ENABLE_AI_EXTRACTION
        else:
            self.enabled = False
    
    def _get_model(self, preferred_model='gemini-1.5-flash'):
        """Get a Gemini model with fallback options"""
        models_to_try = [preferred_model, 'gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro']
        for model_name in models_to_try:
            try:
                return genai.GenerativeModel(model_name), model_name
            except Exception:
                continue
        raise Exception("No available Gemini model found")
    
    def extract_document_data(self, file_path: str, document_type: str) -> tuple[Optional[Dict[str, Any]], float, str]:
        if not self.enabled:
            return None, 0.0, "ai_disabled"
        
        try:
            start_time = time.time()
            
            model, model_name = self._get_model('gemini-1.5-flash')
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            mime_type = self._get_mime_type(file_path)
            
            prompt = self._get_extraction_prompt(document_type)
            
            file_part = {
                "mime_type": mime_type,
                "data": file_data
            }
            
            response = model.generate_content([prompt, file_part])
            
            processing_time = int((time.time() - start_time) * 1000)
            
            response_text = response.text if hasattr(response, 'text') else str(response)
            print(f"AI Response (first 500 chars): {response_text[:500]}")
            
            extracted_data = self._parse_response(response_text)
            print(f"Parsed extracted_data keys: {list(extracted_data.keys()) if extracted_data else 'None'}")
            
            confidence = self._calculate_confidence(extracted_data)
            
            return extracted_data, confidence, model_name
        except Exception as e:
            print(f"AI extraction error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, 0.0, "error"
    
    def detect_document_type(self, file_path: str) -> tuple[str, float]:
        if not self.enabled:
            return "other", 0.0
        
        try:
            model, _ = self._get_model('gemini-1.5-flash')
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            mime_type = self._get_mime_type(file_path)
            
            prompt = """Analyze this document and determine its type. 
            Return only one of: invoice, packing_list, commercial_invoice, certificate_of_origin, 
            bill_of_lading, house_bl, master_bl, telex_release, or other.
            Response format: TYPE|CONFIDENCE (0.0-1.0)"""
            
            file_part = {
                "mime_type": mime_type,
                "data": file_data
            }
            
            response = model.generate_content([prompt, file_part])
            result = response.text.strip().split('|')
            
            if len(result) == 2:
                doc_type = result[0].strip().lower()
                confidence = float(result[1].strip())
                return doc_type, confidence
            
            return "other", 0.5
        except Exception:
            return "other", 0.0
    
    def predict_customs_delay(self, port: str, rms_examination: bool, duty_amount: float, 
                             documents_complete: bool) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "delayRisk": "MEDIUM",
                "predictedDelayDays": 3,
                "confidenceScore": 0.5,
                "reasons": ["AI service not available"],
                "recommendation": "Please ensure all documents are complete"
            }
        
        try:
            model, _ = self._get_model('gemini-1.5-flash')
            
            prompt = f"""Analyze customs clearance delay risk for:
            Port: {port}
            RMS Examination: {rms_examination}
            Duty Amount: ${duty_amount}
            Documents Complete: {documents_complete}
            
            Return JSON format:
            {{
                "delayRisk": "LOW|MEDIUM|HIGH",
                "predictedDelayDays": <integer>,
                "confidenceScore": <float 0.0-1.0>,
                "reasons": ["reason1", "reason2"],
                "recommendation": "string"
            }}"""
            
            response = model.generate_content(prompt)
            import json
            return json.loads(response.text)
        except Exception:
            return {
                "delayRisk": "MEDIUM",
                "predictedDelayDays": 3,
                "confidenceScore": 0.5,
                "reasons": ["Analysis unavailable"],
                "recommendation": "Please ensure all documents are complete"
            }
    
    def predict_rate(self, origin: str, destination: str, carrier: str, 
                     container_type: str, current_rate: float) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "predictedRateUSD": current_rate,
                "trend": "STABLE",
                "confidenceScore": 0.5,
                "recommendation": "AI service not available"
            }
        
        try:
            model, _ = self._get_model('gemini-1.5-flash')
            
            prompt = f"""Predict freight rate trend for:
            Origin: {origin}
            Destination: {destination}
            Carrier: {carrier}
            Container Type: {container_type}
            Current Rate: ${current_rate}
            
            Return JSON format:
            {{
                "predictedRateUSD": <float>,
                "trend": "UP|DOWN|STABLE",
                "confidenceScore": <float 0.0-1.0>,
                "recommendation": "string"
            }}"""
            
            response = model.generate_content(prompt)
            import json
            return json.loads(response.text)
        except Exception:
            return {
                "predictedRateUSD": current_rate,
                "trend": "STABLE",
                "confidenceScore": 0.5,
                "recommendation": "Analysis unavailable"
            }
    
    def _get_mime_type(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _get_extraction_prompt(self, document_type: str) -> str:
        base_prompt = """Extract structured data from this invoice document. You must return ONLY valid JSON format, no other text. The JSON must include all available fields from the document."""
        
        prompts = {
            "invoice": base_prompt + """
Extract ALL fields from this invoice document and return as valid JSON. Be thorough and extract every available field.

Required JSON structure:
{
  "invoice_number": "extract invoice number/invoice no (e.g., INV-2024-001, 51109338)",
  "invoiceNumber": "same as invoice_number",
  "date": "extract date of issue/invoice date in YYYY-MM-DD format (convert from MM/DD/YYYY or DD/MM/YYYY)",
  "invoice_date": "same as date",
  "amount": extract total gross amount as number (remove currency symbols, commas),
  "total_amount": extract total gross amount as number,
  "total": extract total gross amount as number,
  "gross_worth": extract gross total as number,
  "net_worth": extract net total as number (before tax),
  "currency": "extract currency (USD, EUR, INR, etc.) or infer from symbol ($=USD, €=EUR, ₹=INR)",
  "buyer_name": "extract buyer/client/customer company name",
  "buyerName": "same as buyer_name",
  "buyer": "same as buyer_name",
  "client_name": "extract client name if different from buyer",
  "seller_name": "extract seller/vendor/company name",
  "sellerName": "same as seller_name",
  "seller": "same as seller_name",
  "company_name": "extract seller company name",
  "exporter": "extract exporter name if present",
  "tax_amount": extract total tax/VAT/GST amount as number (remove currency symbols),
  "taxAmount": "same as tax_amount",
  "vat": extract VAT amount as number,
  "gst": extract GST amount as number,
  "tax_percentage": extract tax percentage as number (e.g., 10, 18),
  "payment_terms": "extract payment terms (e.g., Net 30, Due on Receipt, Payment Due)",
  "paymentTerms": "same as payment_terms",
  "due_date": "extract due date if mentioned (convert to YYYY-MM-DD)",
  "dueDate": "same as due_date",
  "po_number": "extract purchase order number/PO number if present",
  "poNumber": "same as po_number",
  "purchase_order": "same as po_number",
  "summary": "brief summary describing what this invoice is for",
  "notes": "any additional notes, terms, or conditions",
  "seller_address": "extract seller address",
  "buyer_address": "extract buyer/client address",
  "seller_tax_id": "extract seller tax ID/GSTIN/VAT number",
  "buyer_tax_id": "extract buyer tax ID if present",
  "iban": "extract IBAN or bank account if present",
  "items": [
    {
      "description": "item/product description",
      "quantity": extract quantity as number,
      "unit_price": extract unit price per item as number,
      "net_price": "same as unit_price",
      "total": extract line total as number,
      "net_worth": "line net total",
      "gross_worth": "line gross total",
      "vat_percentage": extract VAT percentage for this item,
      "hs_code": "extract HSN/HS code if present",
      "hsn_code": "same as hs_code"
    }
  ]
}

IMPORTANT:
- Extract ALL numbers without currency symbols or commas
- Convert dates to YYYY-MM-DD format
- Include ALL items from the invoice table
- Extract seller and buyer names exactly as written
- If currency symbol is $, set currency to "USD"
- If currency symbol is €, set currency to "EUR"  
- If currency symbol is ₹, set currency to "INR"
- Extract tax/VAT amounts separately from totals
- Return ONLY valid JSON, no markdown formatting, no code blocks, no explanations""",
            "packing_list": base_prompt + """ Fields: packing_list_number, date, total_packages, total_weight_kg, total_volume_cbm, items (array with description, quantity, weight_kg, volume_cbm, hs_code).""",
            "commercial_invoice": base_prompt + """ Fields: invoice_number, date, exporter, importer, items (array with description, quantity, unit_price, total, hs_code), total_amount, currency, incoterm.""",
            "certificate_of_origin": base_prompt + """ Fields: certificate_number, issue_date, exporter, importer, origin_country, items (array with description, hs_code).""",
            "bill_of_lading": base_prompt + """ Fields: bl_number, shipper, consignee, notify_party, vessel_name, voyage_number, port_of_loading, port_of_discharge, container_numbers (array), packages, weight_kg, volume_cbm.""",
        }
        
        return prompts.get(document_type, base_prompt)
    
    def _parse_response(self, text: str) -> Dict[str, Any]:
        import json
        import re
        
        if not text:
            return {}
        
        try:
            # Try to find JSON in markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except:
            pass
        
        try:
            # Try to find JSON object directly
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                # Try to fix common JSON issues
                json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Text snippet: {text[:500]}")
        except Exception as e:
            print(f"Parse error: {e}")
        
        return {}
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        if not extracted_data:
            return 0.0
        required_fields = ['invoice_number', 'date', 'amount']
        found_fields = sum(1 for field in required_fields if field in extracted_data)
        return min(found_fields / len(required_fields), 0.95)

