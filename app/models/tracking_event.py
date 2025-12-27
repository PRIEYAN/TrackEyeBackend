from mongoengine import Document, StringField, BooleanField, DateTimeField, ReferenceField, ListField
from datetime import datetime
from app.models.shipment import Shipment
from app.models.user import User


class TrackingEvent(Document):
    shipment_id = ReferenceField(Shipment, required=True)
    created_by = ReferenceField(User)
    status = StringField(required=True, choices=['booked', 'gate_in', 'vessel_departed', 'in_transit', 
                                                  'port_arrival', 'gate_out', 'customs_clearance', 
                                                  'delivered', 'held', 'delayed'])
    location = StringField(required=True)
    vessel_name = StringField()
    voyage_number = StringField()
    container_number = StringField()
    description = StringField(required=True)
    remarks = StringField()
    estimated_datetime = DateTimeField()
    actual_datetime = DateTimeField()
    documents = ListField(StringField(), default=list)
    is_milestone = BooleanField(default=False)
    verified = BooleanField(default=False)
    timestamp = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'tracking_events',
        'indexes': ['shipment_id', 'created_by', 'status', 'timestamp']
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'shipment_id': str(self.shipment_id.id) if self.shipment_id else None,
            'created_by': str(self.created_by.id) if self.created_by else None,
            'status': self.status,
            'location': self.location,
            'vessel_name': self.vessel_name,
            'voyage_number': self.voyage_number,
            'container_number': self.container_number,
            'description': self.description,
            'remarks': self.remarks,
            'estimated_datetime': self.estimated_datetime.isoformat() if self.estimated_datetime else None,
            'actual_datetime': self.actual_datetime.isoformat() if self.actual_datetime else None,
            'documents': self.documents if self.documents else [],
            'is_milestone': self.is_milestone,
            'verified': self.verified,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
