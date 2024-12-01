from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from app import app ,db
from flask_migrate import Migrate

migrate = Migrate(app, db, render_as_batch=True) 




class admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username= db.Column(db.String, nullable=False)
    passaword= db.Column(db.String, nullable=False)

class influencer(db.Model):
    __tablename__ = 'influencer'
    influencer_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username= db.Column(db.String, nullable=False)
    passaword= db.Column(db.String, nullable=False)
    genre= db.Column(db.String, nullable=False)
    email= db.Column(db.String, nullable=False)
    popularity= db.Column(db.String, nullable=False)
    platform= db.Column(db.String, nullable=False)
    flag = db.Column(db.String, default='no')
    influencer_ad_request = db.relationship('influencer_ad_request')
    sponsor_ad_request = db.relationship('sponsor_request')

class sponsor(db.Model):
    __tablename__ = 'sponsor'
    sponsor_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username= db.Column(db.String, nullable=False)
    passaword= db.Column(db.String, nullable=False)
    industry= db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    flag = db.Column(db.String, default='no')
    influencer_ad_request = db.relationship('influencer_ad_request',backref='sponsor')
    sponsor_ad_request = db.relationship('sponsor_request')
    campaign = db.relationship('campaign')
    
class campaign(db.Model):
    __tablename__ = 'campaign'
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    campaign_name = db.Column(db.String,  nullable=False)  
    description = db.Column(db.String(500),  nullable=False)  
    goals = db.Column(db.String(500),  nullable=False)  
    start_date = db.Column(db.Date, nullable=False)  
    end_date = db.Column(db.Date, nullable=False)  
    budget = db.Column(db.String,  nullable=False)  
    visiblity = db.Column(db.String,  nullable=False)  
    finding_niche = db.Column(db.String)
    flag = db.Column(db.String, default='no')
    influencer_ad_request = db.relationship('influencer_ad_request')
    sponsor_request = db.relationship('sponsor_request')

class influencer_ad_request(db.Model):
    __tablename__ = 'influencer_ad_request'
    influencer_request_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))  
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'))  
    influencer_status= db.Column(db.String,  default='Pending') 
    message = db.Column(db.String(500),  nullable=False) 
    amount= db.Column(db.Integer ,nullable=False)  
    sponsor_call= db.Column(db.String)
    status_complete_influencer = db.Column(db.String, default='Pending')
    status_complete_sponsor = db.Column(db.String, default='Pending')
    payment_sponsor = db.Column(db.String, default='Pending')

class sponsor_request(db.Model):
    __tablename__ = 'sponsor_request'
    sponsor_request_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))  
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id')) 
    message = db.Column(db.String(500),  nullable=False) 
    amount= db.Column(db.Integer ,nullable=False)  
    influencer_call= db.Column(db.String)  
    sponsor_status= db.Column(db.String,  default='Pending')
    status_complete_influencer = db.Column(db.String,  default='Pending')
    status_complete_sponsor = db.Column(db.String, default='Pending')
    payment_sponsor = db.Column(db.String,default='Pending')

    
    
class Img(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))  
    

with app.app_context():
    db.create_all() 