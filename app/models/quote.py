from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ReferenceField, DictField
from datetime import datetime
from app.models.shipment import Shipment
from app.models.user import User


class Quote(Document):
    shipment_id = ReferenceField(Shipment, required=True)
    forwarder_id = ReferenceField(User, required=True)
    freight_amount_usd = FloatField(required=True)
    fuel_surcharge = FloatField(default=0.0)
    thc_charges = FloatField(default=0.0)
    documentation_charges = FloatField(default=0.0)
    other_charges = FloatField(default=0.0)
    total_amount_usd = FloatField(required=True)
    validity_date = DateTimeField()
    transit_time_days = IntField()
    free_days_at_destination = IntField(default=7)
    routing = StringField()
    vessel_name = StringField()
    voyage_number = StringField()
    container_type = StringField()
    container_quantity = IntField()
    status = StringField(default='pending', choices=['pending', 'accepted', 'rejected', 'expired'])
    remarks = StringField()
    terms_and_conditions = StringField()
    metadata = DictField(default=dict)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField()
    
    meta = {
        'collection': 'quotes',
        'indexes': ['shipment_id', 'forwarder_id', 'status']
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self, include_forwarder_info=False):
        data = {
            'id': str(self.id),
            'shipment_id': str(self.shipment_id.id) if self.shipment_id else None,
            'forwarder_id': str(self.forwarder_id.id) if self.forwarder_id else None,
            'freight_amount_usd': self.freight_amount_usd,
            'fuel_surcharge': self.fuel_surcharge,
            'thc_charges': self.thc_charges,
            'documentation_charges': self.documentation_charges,
            'other_charges': self.other_charges,
            'total_amount_usd': self.total_amount_usd,
            'validity_date': self.validity_date.isoformat() if self.validity_date else None,
            'transit_time_days': self.transit_time_days,
            'free_days_at_destination': self.free_days_at_destination,
            'routing': self.routing,
            'vessel_name': self.vessel_name,
            'voyage_number': self.voyage_number,
            'container_type': self.container_type,
            'container_quantity': self.container_quantity,
            'status': self.status,
            'remarks': self.remarks,
            'terms_and_conditions': self.terms_and_conditions,
            'metadata': self.metadata if hasattr(self, 'metadata') else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_forwarder_info and self.forwarder_id:
            forwarder = User.objects(id=self.forwarder_id.id).first()
            if forwarder:
                data['forwarder_name'] = forwarder.name
                data['forwarder_company'] = forwarder.company_name
        
        return data
