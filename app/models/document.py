from mongoengine import Document, StringField, IntField, FloatField, BooleanField, DateTimeField, ReferenceField, DictField
from datetime import datetime
from app.models.shipment import Shipment
from app.models.user import User


class DocumentModel(Document):
    shipment_id = ReferenceField(Shipment, required=True)
    uploaded_by = ReferenceField(User, required=True)
    type = StringField(required=True, choices=['invoice', 'packing_list', 'commercial_invoice', 
                                               'certificate_of_origin', 'bill_of_lading', 'house_bl', 
                                               'master_bl', 'telex_release', 'other'])
    file_name = StringField(required=True)
    file_url = StringField(required=True)
    file_size = IntField()
    mime_type = StringField()
    extracted_data = DictField()
    confidence_score = FloatField(default=0.0)
    extraction_method = StringField()
    needs_review = BooleanField(default=True)
    metadata = DictField(default=dict)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'documents',
        'indexes': ['shipment_id', 'uploaded_by', 'type']
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'shipment_id': str(self.shipment_id.id) if self.shipment_id else None,
            'uploaded_by': str(self.uploaded_by.id) if self.uploaded_by else None,
            'type': self.type,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'extracted_data': self.extracted_data,
            'confidence_score': self.confidence_score,
            'extraction_method': self.extraction_method,
            'needs_review': self.needs_review,
            'metadata': self.metadata if hasattr(self, 'metadata') else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExtractionJob(Document):
    document_id = ReferenceField(DocumentModel, required=True, unique=True)
    status = StringField(default='pending', choices=['pending', 'processing', 'completed', 'failed'])
    model_used = StringField()
    processing_time_ms = IntField()
    error_message = StringField()
    attempts = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'extraction_jobs',
        'indexes': ['document_id', 'status']
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'document_id': str(self.document_id.id) if self.document_id else None,
            'status': self.status,
            'model_used': self.model_used,
            'processing_time_ms': self.processing_time_ms,
            'error_message': self.error_message,
            'attempts': self.attempts,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
