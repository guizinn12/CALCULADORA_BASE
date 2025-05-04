from app import db
import json
from datetime import datetime

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relação com configurações
    configs = db.relationship('CityConfig', backref='city', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<City {self.name}>'

class CityConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    
    # Tema
    primary_color = db.Column(db.String(20), default='#1e3a8a')
    secondary_color = db.Column(db.String(20), default='#172554')
    accent_color = db.Column(db.String(20), default='#3b82f6')
    danger_color = db.Column(db.String(20), default='#ef4444')
    success_color = db.Column(db.String(20), default='#22c55e')
    warning_color = db.Column(db.String(20), default='#f59e0b')
    text_color = db.Column(db.String(20), default='#f1f5f9')
    dark_bg = db.Column(db.String(20), default='#0f172a')
    card_bg = db.Column(db.String(20), default='#1e293b')
    border_color = db.Column(db.String(20), default='#334155')
    
    # Links do servidor
    server_name = db.Column(db.String(100))
    discord_url = db.Column(db.String(500))
    website_url = db.Column(db.String(500))
    instagram_url = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CityConfig {self.id} for City {self.city_id}>'
    
    def to_json(self):
        """Converte a configuração para o formato JSON"""
        return {
            "city": {
                "name": self.city.name,
                "logo": self.city.logo_url,
                "description": self.city.description
            },
            "theme": {
                "primary_color": self.primary_color,
                "secondary_color": self.secondary_color,
                "accent_color": self.accent_color,
                "danger_color": self.danger_color,
                "success_color": self.success_color,
                "warning_color": self.warning_color,
                "text_color": self.text_color,
                "dark_bg": self.dark_bg,
                "card_bg": self.card_bg,
                "border_color": self.border_color
            },
            "server": {
                "name": self.server_name,
                "discord_url": self.discord_url,
                "website_url": self.website_url,
                "instagram_url": self.instagram_url
            }
        }