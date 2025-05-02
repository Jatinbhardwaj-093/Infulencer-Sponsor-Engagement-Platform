from flask import Flask, render_template, request, redirect
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# Import db from our centralized db.py file
from db import db
import sqlalchemy as sa

class Admin(db.Model):
    """Admin user model for platform administration"""
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.username}>'
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Influencer(db.Model):
    """Influencer model representing content creators"""
    __tablename__ = 'influencer'
    influencer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Make password column nullable=False - security fix
    password = db.Column(db.String(128), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    popularity = db.Column(db.String(20), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text)
    flag = db.Column(db.String(3), default='no')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    profile_images = db.relationship('Img', backref='influencer', lazy=True)
    influencer_ad_requests = db.relationship('InfluencerAdRequest', backref='influencer', lazy=True,
                                          cascade="all, delete-orphan")
    sponsor_requests = db.relationship('SponsorRequest', backref='influencer', lazy=True,
                                      cascade="all, delete-orphan")
    campaigns = db.relationship('Campaign', backref='assigned_influencer', lazy=True)
    
    def __repr__(self):
        return f'<Influencer {self.username}>'
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Sponsor(db.Model):
    """Sponsor model representing brands/companies"""
    __tablename__ = 'sponsor'
    sponsor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(100))
    website = db.Column(db.String(200))
    email = db.Column(db.String(120), unique=True, nullable=False)
    flag = db.Column(db.String(3), default='no')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    influencer_ad_requests = db.relationship('InfluencerAdRequest', backref='sponsor', lazy=True,
                                          cascade="all, delete-orphan")
    sponsor_requests = db.relationship('SponsorRequest', backref='sponsor', lazy=True,
                                      cascade="all, delete-orphan")
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True,
                               cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Sponsor {self.username}>'
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Campaign(db.Model):
    """Campaign model representing marketing campaigns"""
    __tablename__ = 'campaign'
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    campaign_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    goals = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.String(20), nullable=False)
    visibility = db.Column(db.String(10), nullable=False)
    finding_niche = db.Column(db.String(50))
    flag = db.Column(db.String(3), default='no')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Active')
    
    # Relationships
    influencer_ad_requests = db.relationship('InfluencerAdRequest', backref='campaign', lazy=True,
                                          cascade="all, delete-orphan")
    sponsor_requests = db.relationship('SponsorRequest', backref='campaign', lazy=True,
                                      cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Campaign {self.campaign_name}>'
    
    def is_active(self):
        today = datetime.now().date()
        return self.start_date <= today <= self.end_date and self.status == 'Active'

class InfluencerAdRequest(db.Model):
    """Requests from influencers to participate in campaigns"""
    __tablename__ = 'influencer_ad_request'
    influencer_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    influencer_status = db.Column(db.String(20), default='Pending')
    message = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    sponsor_call = db.Column(db.String(20))
    status_complete_influencer = db.Column(db.String(20), default='Pending')
    status_complete_sponsor = db.Column(db.String(20), default='Pending')
    payment_sponsor = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<InfluencerAdRequest {self.influencer_request_id}>'

class SponsorRequest(db.Model):
    """Requests from sponsors to influencers for campaign participation"""
    __tablename__ = 'sponsor_request'
    sponsor_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    influencer_call = db.Column(db.String(20))
    sponsor_status = db.Column(db.String(20), default='Pending')
    status_complete_influencer = db.Column(db.String(20), default='Pending')
    status_complete_sponsor = db.Column(db.String(20), default='Pending')
    payment_sponsor = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SponsorRequest {self.sponsor_request_id}>'

class Img(db.Model):
    """Image model for storing profile and campaign images"""
    __tablename__ = 'img'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Img {self.name}>'

class Notification(db.Model):
    """Notification model for user notifications"""
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Generic user ID
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    related_id = db.Column(db.Integer)  # ID related to the notification (campaign, request, etc.)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_read = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Notification {self.id} for user {self.user_id}>'
        
    def to_dict(self):
        """Convert notification to dictionary for API responses"""
        return {
            'id': self.id,
            'message': self.message,
            'notification_type': self.notification_type,
            'related_id': self.related_id,
            'date_created': self.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'date_read': self.date_read.strftime('%Y-%m-%d %H:%M:%S') if self.date_read else None,
            'is_read': self.is_read
        }