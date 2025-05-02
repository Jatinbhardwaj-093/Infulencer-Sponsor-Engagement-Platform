import sys
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from db import db
from models import Influencer, Sponsor, Campaign, InfluencerAdRequest, SponsorRequest, Admin

def create_dummy_data():
    """
    Create dummy data for influencers, sponsors, and campaigns
    """
    print("Creating dummy data...")
    
    # Check if data already exists to prevent duplicates
    if Influencer.query.count() > 0 or Sponsor.query.count() > 0 or Campaign.query.count() > 0:
        confirmation = input("Database already contains data. Do you want to continue? (y/n): ")
        if confirmation.lower() != 'y':
            print("Operation cancelled.")
            return

    # Create admin user
    if Admin.query.filter_by(username='admin-user').first() is None:
        admin = Admin(
            username='admin-user',
            password=generate_password_hash('adminuser123'),
            email='admin@influconnect.com',
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")

    # Create dummy influencers
    influencers = [
        {
            'username': 'emma-watson', 
            'password': 'emmawatson123', 
            'email': 'emma@example.com', 
            'genre': 'Fashion', 
            'platform': 'Instagram', 
            'popularity': 'High',
            'bio': 'Fashion and lifestyle influencer with a passion for sustainable fashion.'
        },
        {
            'username': 'tech-mike', 
            'password': 'techmike123', 
            'email': 'mike@techblog.com', 
            'genre': 'Technology', 
            'platform': 'YouTube', 
            'popularity': 'Medium',
            'bio': 'Tech reviewer and gadget enthusiast covering the latest in consumer electronics.'
        },
        {
            'username': 'fitness-sarah', 
            'password': 'fitnesssarah123', 
            'email': 'sarah@fitness.com', 
            'genre': 'Fitness', 
            'platform': 'TikTok', 
            'popularity': 'High',
            'bio': 'Certified fitness trainer sharing workout tips and healthy lifestyle advice.'
        },
        {
            'username': 'food-jamie', 
            'password': 'foodjamie123', 
            'email': 'jamie@foodie.com', 
            'genre': 'Food', 
            'platform': 'Instagram', 
            'popularity': 'Medium',
            'bio': 'Food blogger and home chef sharing easy-to-make recipes and restaurant reviews.'
        },
        {
            'username': 'travel-alex', 
            'password': 'travelalex123', 
            'email': 'alex@travelblog.com', 
            'genre': 'Travel', 
            'platform': 'YouTube', 
            'popularity': 'Medium',
            'bio': 'Adventure seeker documenting travels around the world with budget-friendly tips.'
        },
        {
            'username': 'gaming-max', 
            'password': 'gamingmax123', 
            'email': 'max@gaming.com', 
            'genre': 'Gaming', 
            'platform': 'Twitch', 
            'popularity': 'High',
            'bio': 'Professional gamer and live streamer covering AAA titles and indie games.'
        },
        {
            'username': 'beauty-lisa', 
            'password': 'beautylisa123', 
            'email': 'lisa@beauty.com', 
            'genre': 'Beauty', 
            'platform': 'Instagram', 
            'popularity': 'Medium',
            'bio': 'Makeup artist and skincare enthusiast sharing beauty tips and product reviews.'
        }
    ]
    
    # Create dummy sponsors
    sponsors = [
        {
            'username': 'nike-brand', 
            'password': 'nikebrand123', 
            'email': 'marketing@nike.com', 
            'industry': 'Sports', 
            'company_name': 'Nike', 
            'website': 'www.nike.com'
        },
        {
            'username': 'apple-tech', 
            'password': 'appletech123', 
            'email': 'partnerships@apple.com', 
            'industry': 'Technology', 
            'company_name': 'Apple Inc.', 
            'website': 'www.apple.com'
        },
        {
            'username': 'loreal-beauty', 
            'password': 'lorealbeauty123', 
            'email': 'influencers@loreal.com', 
            'industry': 'Beauty', 
            'company_name': 'L\'Oreal', 
            'website': 'www.loreal.com'
        },
        {
            'username': 'tesla-motors', 
            'password': 'teslamotors123', 
            'email': 'marketing@tesla.com', 
            'industry': 'Automotive', 
            'company_name': 'Tesla Motors', 
            'website': 'www.tesla.com'
        },
        {
            'username': 'airbnb-travel', 
            'password': 'airbnbtravel123', 
            'email': 'creators@airbnb.com', 
            'industry': 'Travel', 
            'company_name': 'Airbnb', 
            'website': 'www.airbnb.com'
        }
    ]
    
    # Add influencers to database
    for influencer_data in influencers:
        influencer = Influencer(
            username=influencer_data['username'],
            password=generate_password_hash(influencer_data['password']),
            email=influencer_data['email'],
            genre=influencer_data['genre'],
            platform=influencer_data['platform'],
            popularity=influencer_data['popularity'],
            bio=influencer_data['bio'],
            created_at=datetime.utcnow()
        )
        db.session.add(influencer)
    
    # Add sponsors to database
    for sponsor_data in sponsors:
        sponsor = Sponsor(
            username=sponsor_data['username'],
            password=generate_password_hash(sponsor_data['password']),
            email=sponsor_data['email'],
            industry=sponsor_data['industry'],
            company_name=sponsor_data['company_name'],
            website=sponsor_data['website'],
            created_at=datetime.utcnow()
        )
        db.session.add(sponsor)
    
    # Commit changes to get IDs for the next step
    db.session.commit()
    
    # Get all influencers and sponsors from the database
    influencers_db = Influencer.query.all()
    sponsors_db = Sponsor.query.all()
    
    # Create dummy campaigns
    campaigns = [
        {
            'sponsor_id': sponsors_db[0].sponsor_id,  # Nike
            'campaign_name': 'Summer Sports Collection',
            'description': 'Promote our new summer sports collection featuring lightweight and breathable sportswear.',
            'goals': 'Increase brand awareness, drive traffic to the website, and boost sales of the new collection.',
            'budget': '10000-20000',
            'visibility': 'Public',
            'finding_niche': 'Fitness'
        },
        {
            'sponsor_id': sponsors_db[1].sponsor_id,  # Apple
            'campaign_name': 'iPhone Pro Launch',
            'description': 'Highlight the features and capabilities of the new iPhone Pro through creative content.',
            'goals': 'Generate buzz around the new iPhone launch and showcase its unique features.',
            'budget': '50000-100000',
            'visibility': 'Public',
            'finding_niche': 'Technology'
        },
        {
            'sponsor_id': sponsors_db[2].sponsor_id,  # L'Oreal
            'campaign_name': 'Natural Beauty Movement',
            'description': 'Promote our new line of natural and sustainable beauty products for all skin types.',
            'goals': 'Establish L\'Oreal as a leader in natural beauty products and reach environmentally conscious consumers.',
            'budget': '15000-25000',
            'visibility': 'Public',
            'finding_niche': 'Beauty'
        },
        {
            'sponsor_id': sponsors_db[3].sponsor_id,  # Tesla
            'campaign_name': 'Electric Future',
            'description': 'Educational campaign about electric vehicles and their impact on reducing carbon emissions.',
            'goals': 'Increase awareness about electric vehicles and highlight Tesla\'s commitment to sustainability.',
            'budget': '30000-60000',
            'visibility': 'Public',
            'finding_niche': 'Automotive, Technology'
        },
        {
            'sponsor_id': sponsors_db[4].sponsor_id,  # Airbnb
            'campaign_name': 'Hidden Gems Travel Series',
            'description': 'Showcase unique and off-the-beaten-path Airbnb listings around the world.',
            'goals': 'Inspire travel to lesser-known destinations and highlight unique Airbnb experiences.',
            'budget': '20000-40000',
            'visibility': 'Public',
            'finding_niche': 'Travel'
        },
        {
            'sponsor_id': sponsors_db[0].sponsor_id,  # Nike
            'campaign_name': 'Winter Sports Challenge',
            'description': 'Engage with winter sports enthusiasts and promote our new line of cold weather gear.',
            'goals': 'Build community around winter sports and drive sales of our winter collection.',
            'budget': '15000-30000',
            'visibility': 'Public',
            'finding_niche': 'Sports'
        },
        {
            'sponsor_id': sponsors_db[2].sponsor_id,  # L'Oreal
            'campaign_name': 'Summer Skincare Essentials',
            'description': 'Promote our SPF and summer skincare line with tips for skin protection.',
            'goals': 'Educate consumers about the importance of sun protection and drive sales of our SPF products.',
            'budget': '10000-20000',
            'visibility': 'Public',
            'finding_niche': 'Beauty, Health'
        }
    ]
    
    # Add campaigns to database with dynamic dates
    today = datetime.utcnow().date()
    for idx, campaign_data in enumerate(campaigns):
        # Vary the start and end dates
        start_offset = (idx * 5) % 30  # Starts staggered between now and 30 days from now
        duration = 30 + (idx * 10) % 60  # Campaigns last between 30 and 90 days
        
        start_date = today + timedelta(days=start_offset)
        end_date = start_date + timedelta(days=duration)
        
        # Assign an influencer to some campaigns
        influencer_id = None
        if idx % 2 == 0:  # Assign an influencer to every other campaign
            # Try to match genre with finding_niche if possible
            matching_influencer = None
            for inf in influencers_db:
                if inf.genre.lower() in campaign_data['finding_niche'].lower():
                    matching_influencer = inf
                    break
            
            if matching_influencer:
                influencer_id = matching_influencer.influencer_id
            else:
                # Pick an influencer based on the campaign index if no genre match
                influencer_id = influencers_db[idx % len(influencers_db)].influencer_id
        
        campaign = Campaign(
            sponsor_id=campaign_data['sponsor_id'],
            influencer_id=influencer_id,
            campaign_name=campaign_data['campaign_name'],
            description=campaign_data['description'],
            goals=campaign_data['goals'],
            start_date=start_date,
            end_date=end_date,
            budget=campaign_data['budget'],
            visibility=campaign_data['visibility'],
            finding_niche=campaign_data['finding_niche'],
            created_at=datetime.utcnow(),
            status='Active'
        )
        db.session.add(campaign)
    
    # Commit all changes
    db.session.commit()
    
    # Create some influencer requests for campaigns
    campaigns_db = Campaign.query.all()
    for idx, campaign in enumerate(campaigns_db):
        if not campaign.influencer_id:  # Only create requests for campaigns without assigned influencers
            # Pick two influencers to make requests for this campaign
            for i in range(2):
                influencer = influencers_db[(idx + i) % len(influencers_db)]
                
                # Check if this influencer is already assigned to this campaign
                if campaign.influencer_id != influencer.influencer_id:
                    request = InfluencerAdRequest(
                        campaign_id=campaign.campaign_id,
                        influencer_id=influencer.influencer_id,
                        sponsor_id=campaign.sponsor_id,
                        message=f"I'm interested in promoting your {campaign.campaign_name} campaign. My content aligns well with your goals.",
                        amount=int(campaign.budget.split('-')[0]) + 1000,  # Requested amount is slightly more than minimum budget
                        created_at=datetime.utcnow()
                    )
                    db.session.add(request)
    
    # Create some sponsor requests to influencers
    for idx, campaign in enumerate(campaigns_db):
        if not campaign.influencer_id:  # Only create requests for campaigns without assigned influencers
            # Pick an influencer to send a request to
            influencer = influencers_db[(idx + len(influencers_db) - 1) % len(influencers_db)]
            
            # Check if this influencer is already assigned to this campaign
            if campaign.influencer_id != influencer.influencer_id:
                request = SponsorRequest(
                    campaign_id=campaign.campaign_id,
                    influencer_id=influencer.influencer_id,
                    sponsor_id=campaign.sponsor_id,
                    message=f"We think you'd be a perfect fit for our {campaign.campaign_name} campaign. Would you be interested in collaborating?",
                    amount=int(campaign.budget.split('-')[0]),  # Offered amount is minimum budget
                    created_at=datetime.utcnow()
                )
                db.session.add(request)
    
    # Commit all changes
    db.session.commit()
    
    print(f"Successfully created {len(influencers)} influencers, {len(sponsors)} sponsors, and {len(campaigns)} campaigns!")
    print("\nAdmin login credentials:")
    print("Username: admin-user, Password: adminuser123")
    
    print("\nInfluencer login credentials:")
    for inf in influencers:
        print(f"Username: {inf['username']}, Password: {inf['password']}")
    
    print("\nSponsor login credentials:")
    for spo in sponsors:
        print(f"Username: {spo['username']}, Password: {spo['password']}")
    
    print("\nDummy data created successfully!")

if __name__ == "__main__":
    with app.app_context():
        create_dummy_data()