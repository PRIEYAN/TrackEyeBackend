from mongoengine import Document, StringField, BooleanField, DateTimeField, EmailField
from datetime import datetime
import uuid


class User(Document):
    email = EmailField(required=True, unique=True)
    hashed_password = StringField(required=True)
    name = StringField(required=True, min_length=2)
    company_name = StringField()
    phone = StringField()
    role = StringField(required=True, choices=['supplier', 'forwarder', 'buyer'])
    gstin = StringField()
    country = StringField(default='IN', max_length=2)
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'users',
        'indexes': ['email']
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'name': self.name,
            'company_name': self.company_name,
            'phone': self.phone,
            'role': self.role,
            'gstin': self.gstin,
            'country': self.country,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
