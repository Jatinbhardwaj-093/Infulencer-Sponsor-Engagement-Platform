import sys
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from db import db
from models import Influencer, Sponsor, Campaign, InfluencerAdRequest, SponsorRequest

def add_more_dummy_data():
    """
    Add additional dummy data for influencers, sponsors, and campaigns
    to an existing database without affecting existing records
    """
    print("Adding more dummy data...")
    
    # Check if database is accessible
    try:
        existing_influencers = Influencer.query.count()
        existing_sponsors = Sponsor.query.count()
        existing_campaigns = Campaign.query.count()
        print(f"Current database has: {existing_influencers} influencers, {existing_sponsors} sponsors, {existing_campaigns} campaigns")
    except Exception as e:
        print(f"Error accessing database: {e}")
        return
    
    # Create additional influencers
    new_influencers = [
        {
            'username': 'mommy-blogger', 
            'password': 'mommyblogger123', 
            'email': 'jane@mommyblog.com', 
            'genre': 'Parenting', 
            'platform': 'Instagram', 
            'popularity': 'Medium',
            'bio': 'Sharing real stories about motherhood and parenting tips for busy moms.'
        },
        {
            'username': 'finance-guru', 
            'password': 'financeguru123', 
            'email': 'finance@moneymatters.com', 
            'genre': 'Finance', 
            'platform': 'YouTube', 
            'popularity': 'High',
            'bio': 'Financial advisor helping young professionals achieve financial independence.'
        },
        {
            'username': 'DIY-queen', 
            'password': 'diyqueen123', 
            'email': 'diy@crafts.com', 
            'genre': 'DIY & Crafts', 
            'platform': 'Instagram', 
            'popularity': 'Medium',
            'bio': 'Transforming ordinary homes with budget-friendly DIY projects and upcycling ideas.'
        },
        {
            'username': 'bookworm', 
            'password': 'bookworm123', 
            'email': 'books@reader.com', 
            'genre': 'Literature', 
            'platform': 'TikTok', 
            'popularity': 'Medium',
            'bio': 'Book lover sharing reviews, recommendations, and literary insights.'
        },
        {
            'username': 'music-maestro', 
            'password': 'musicmaestro123', 
            'email': 'musician@soundcloud.com', 
            'genre': 'Music', 
            'platform': 'YouTube', 
            'popularity': 'High',
            'bio': 'Musician and producer sharing original content and music production tips.'
        },
        {
            'username': 'pet-whisperer', 
            'password': 'petwhisperer123', 
            'email': 'pets@animalcare.com', 
            'genre': 'Pets', 
            'platform': 'Instagram', 
            'popularity': 'Medium',
            'bio': 'Animal behavior specialist sharing pet care advice and cute animal content.'
        },
        {
            'username': 'wellness-guru', 
            'password': 'wellnessguru123', 
            'email': 'health@wellness.com', 
            'genre': 'Wellness', 
            'platform': 'Instagram', 
            'popularity': 'High',
            'bio': 'Holistic health practitioner sharing wellness tips for mind, body, and soul.'
        },
        {
            'username': 'science-nerd', 
            'password': 'sciencenerd123', 
            'email': 'scientist@discovery.com', 
            'genre': 'Science', 
            'platform': 'YouTube', 
            'popularity': 'Medium',
            'bio': 'Making complex scientific concepts accessible and fun for everyone.'
        },
        {
            'username': 'comedy-central', 
            'password': 'comedycentral123', 
            'email': 'comedy@laughs.com', 
            'genre': 'Comedy', 
            'platform': 'TikTok', 
            'popularity': 'High',
            'bio': 'Sharing laughs through skits, standup clips, and daily humor.'
        },
        {
            'username': 'sustainable-living', 
            'password': 'sustainable123', 
            'email': 'eco@greenlife.com', 
            'genre': 'Sustainability', 
            'platform': 'Instagram', 
            'popularity': 'Medium',
            'bio': 'Advocating for eco-friendly lifestyle choices and sustainable practices.'
        },
        {
            'username': 'fashion-forward', 
            'password': 'fashionforward123', 
            'email': 'style@fashion.com', 
            'genre': 'Fashion', 
            'platform': 'Instagram', 
            'popularity': 'High',
            'bio': 'Fashion stylist showcasing the latest trends and sustainable fashion choices.'
        },
        {
            'username': 'crypto-king', 
            'password': 'cryptoking123', 
            'email': 'crypto@blockchain.com', 
            'genre': 'Cryptocurrency', 
            'platform': 'YouTube', 
            'popularity': 'Medium',
            'bio': 'Demystifying blockchain and cryptocurrency for beginners and experts alike.'
        }
    ]
    
    # Create additional sponsors
    new_sponsors = [
        {
            'username': 'sony-electronics', 
            'password': 'sonyelectronics123', 
            'email': 'marketing@sony.com', 
            'industry': 'Electronics', 
            'company_name': 'Sony', 
            'website': 'www.sony.com'
        },
        {
            'username': 'starbucks-coffee', 
            'password': 'starbuckscoffee123', 
            'email': 'creators@starbucks.com', 
            'industry': 'Food & Beverage', 
            'company_name': 'Starbucks', 
            'website': 'www.starbucks.com'
        },
        {
            'username': 'adidas-sports', 
            'password': 'adidassports123', 
            'email': 'influencers@adidas.com', 
            'industry': 'Sports', 
            'company_name': 'Adidas', 
            'website': 'www.adidas.com'
        },
        {
            'username': 'samsung-tech', 
            'password': 'samsungtech123', 
            'email': 'partnerships@samsung.com', 
            'industry': 'Technology', 
            'company_name': 'Samsung', 
            'website': 'www.samsung.com'
        },
        {
            'username': 'bmw-motors', 
            'password': 'bmwmotors123', 
            'email': 'marketing@bmw.com', 
            'industry': 'Automotive', 
            'company_name': 'BMW', 
            'website': 'www.bmw.com'
        },
        {
            'username': 'spotify-music', 
            'password': 'spotifymusic123', 
            'email': 'artists@spotify.com', 
            'industry': 'Music', 
            'company_name': 'Spotify', 
            'website': 'www.spotify.com'
        },
        {
            'username': 'amazon-retail', 
            'password': 'amazonretail123', 
            'email': 'influencers@amazon.com', 
            'industry': 'E-commerce', 
            'company_name': 'Amazon', 
            'website': 'www.amazon.com'
        },
        {
            'username': 'disney-entertainment', 
            'password': 'disneyent123', 
            'email': 'creators@disney.com', 
            'industry': 'Entertainment', 
            'company_name': 'Disney', 
            'website': 'www.disney.com'
        }
    ]
    
    # Add influencers to database
    new_influencer_objects = []
    for influencer_data in new_influencers:
        # Check if username or email already exists
        if Influencer.query.filter_by(username=influencer_data['username']).first() or Influencer.query.filter_by(email=influencer_data['email']).first():
            print(f"Skipping influencer {influencer_data['username']} - already exists")
            continue
            
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
        new_influencer_objects.append(influencer)
    
    # Add sponsors to database
    new_sponsor_objects = []
    for sponsor_data in new_sponsors:
        # Check if username or email already exists
        if Sponsor.query.filter_by(username=sponsor_data['username']).first() or Sponsor.query.filter_by(email=sponsor_data['email']).first():
            print(f"Skipping sponsor {sponsor_data['username']} - already exists")
            continue
            
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
        new_sponsor_objects.append(sponsor)
    
    # Commit changes to get IDs for the next step
    db.session.commit()
    
    # Get all sponsors from the database for creating campaigns
    all_sponsors = Sponsor.query.all()
    
    # Create additional campaigns with a mix of new and existing sponsors
    new_campaigns = [
        {
            'campaign_name': 'Back to School Essentials',
            'description': 'Promote our range of back-to-school products including backpacks, stationery, and tech gadgets.',
            'goals': 'Target parents and students during the back-to-school shopping season.',
            'budget': '15000-25000',
            'visibility': 'Public',
            'finding_niche': 'Parenting, Education'
        },
        {
            'campaign_name': 'Home Office Setup',
            'description': 'Showcase our premium home office furniture and accessories for the modern remote worker.',
            'goals': 'Highlight the importance of a comfortable and productive home workspace.',
            'budget': '20000-30000',
            'visibility': 'Public',
            'finding_niche': 'Lifestyle, Technology'
        },
        {
            'campaign_name': 'Smart Home Revolution',
            'description': 'Demonstrate how our smart home devices can transform everyday living through connectivity and automation.',
            'goals': 'Educate consumers about the benefits of smart home technology.',
            'budget': '30000-50000',
            'visibility': 'Public',
            'finding_niche': 'Technology, Home Improvement'
        },
        {
            'campaign_name': 'Sustainable Fashion Collection',
            'description': 'Highlight our eco-friendly clothing line made from recycled materials and sustainable practices.',
            'goals': 'Appeal to environmentally conscious consumers and promote sustainable fashion choices.',
            'budget': '25000-40000',
            'visibility': 'Public',
            'finding_niche': 'Fashion, Sustainability'
        },
        {
            'campaign_name': 'Summer Reading Challenge',
            'description': 'Encourage reading with our summer reading challenge featuring recommended books and reading activities.',
            'goals': 'Promote literacy and engage with book lovers during the summer season.',
            'budget': '10000-20000',
            'visibility': 'Public',
            'finding_niche': 'Literature, Education'
        },
        {
            'campaign_name': 'Fitness Transformation',
            'description': 'Share success stories and showcase our fitness equipment and workout programs for all levels.',
            'goals': 'Inspire fitness journeys and drive sales of our home gym equipment.',
            'budget': '20000-35000',
            'visibility': 'Public',
            'finding_niche': 'Fitness, Health'
        },
        {
            'campaign_name': 'Gourmet Cooking Series',
            'description': 'Feature our premium cookware and ingredients in gourmet cooking tutorials and recipes.',
            'goals': 'Appeal to home chefs and cooking enthusiasts.',
            'budget': '15000-30000',
            'visibility': 'Public',
            'finding_niche': 'Food, Lifestyle'
        },
        {
            'campaign_name': 'Gaming Legends Tournament',
            'description': 'Promote our latest gaming hardware through an online tournament with popular gaming influencers.',
            'goals': 'Engage with the gaming community and showcase our products\' performance.',
            'budget': '40000-60000',
            'visibility': 'Public',
            'finding_niche': 'Gaming, Technology'
        },
        {
            'campaign_name': 'Music Production Masterclass',
            'description': 'Collaborate with musicians to demonstrate our audio equipment and production software.',
            'goals': 'Reach aspiring musicians and producers.',
            'budget': '25000-45000',
            'visibility': 'Public',
            'finding_niche': 'Music, Technology'
        },
        {
            'campaign_name': 'Pet Care Awareness',
            'description': 'Educate pet owners about proper care and nutrition while featuring our premium pet products.',
            'goals': 'Position our brand as a leader in pet wellness and care.',
            'budget': '15000-25000',
            'visibility': 'Public',
            'finding_niche': 'Pets, Health'
        },
        {
            'campaign_name': 'Travel Photography Challenge',
            'description': 'Launch a travel photography challenge featuring our camera equipment in stunning destinations.',
            'goals': 'Showcase the quality and capabilities of our photography gear.',
            'budget': '30000-50000',
            'visibility': 'Public',
            'finding_niche': 'Travel, Photography'
        },
        {
            'campaign_name': 'Wellness Retreat Experience',
            'description': 'Highlight our wellness products and services through immersive retreat experiences.',
            'goals': 'Promote holistic wellness and self-care practices.',
            'budget': '20000-40000',
            'visibility': 'Public',
            'finding_niche': 'Wellness, Health'
        },
        {
            'campaign_name': 'Kids Educational Apps',
            'description': 'Promote our suite of educational apps for children through engaging content and demonstrations.',
            'goals': 'Reach parents looking for quality educational content for their children.',
            'budget': '15000-30000',
            'visibility': 'Public',
            'finding_niche': 'Education, Parenting'
        },
        {
            'campaign_name': 'DIY Home Makeover',
            'description': 'Showcase home improvement projects using our tools and materials with before-and-after transformations.',
            'goals': 'Inspire DIY enthusiasts and weekend warriors to tackle home projects.',
            'budget': '20000-35000',
            'visibility': 'Public',
            'finding_niche': 'Home Improvement, DIY'
        },
        {
            'campaign_name': 'Virtual Reality Experiences',
            'description': 'Demonstrate the immersive capabilities of our VR headsets through exciting content and applications.',
            'goals': 'Generate excitement about virtual reality and showcase our technology.',
            'budget': '35000-55000',
            'visibility': 'Public',
            'finding_niche': 'Technology, Gaming'
        }
    ]
    
    # Add campaigns to database with dynamic dates
    today = datetime.utcnow().date()
    campaign_count = 0
    
    for idx, campaign_data in enumerate(new_campaigns):
        # Select a sponsor for this campaign - alternate between existing and new sponsors
        if idx % 2 == 0 and new_sponsor_objects:
            # Use a new sponsor 
            sponsor = new_sponsor_objects[idx % len(new_sponsor_objects)]
        else:
            # Use an existing sponsor
            sponsor = all_sponsors[idx % len(all_sponsors)]
        
        # Create varied start and end dates
        start_offset = (idx * 3) % 20  # Starts spread over the next 20 days
        duration = 30 + (idx * 5) % 60  # Campaigns last between 30 and 90 days
        
        start_date = today + timedelta(days=start_offset)
        end_date = start_date + timedelta(days=duration)
        
        # Determine status based on dates
        status = 'Active'
        if start_date > today:
            status = 'Pending'
        elif end_date < today:
            status = 'Completed'
            
        campaign = Campaign(
            sponsor_id=sponsor.sponsor_id,
            influencer_id=None,  # Will assign influencers later
            campaign_name=campaign_data['campaign_name'],
            description=campaign_data['description'],
            goals=campaign_data['goals'],
            start_date=start_date,
            end_date=end_date,
            budget=campaign_data['budget'],
            visibility=campaign_data['visibility'],
            finding_niche=campaign_data['finding_niche'],
            created_at=datetime.utcnow(),
            status=status
        )
        db.session.add(campaign)
        campaign_count += 1
    
    # Commit all changes
    db.session.commit()
    
    # Get the newly created campaigns and influencers
    new_campaigns_db = Campaign.query.filter(Campaign.influencer_id.is_(None)).order_by(Campaign.created_at.desc()).limit(campaign_count).all()
    all_influencers = Influencer.query.all()
    
    # Create some influencer requests for campaigns
    for idx, campaign in enumerate(new_campaigns_db):
        # Pick two influencers to make requests for this campaign
        for i in range(2):
            influencer = all_influencers[(idx + i) % len(all_influencers)]
            
            # Check if this influencer is already assigned to this campaign
            existing_request = InfluencerAdRequest.query.filter_by(
                campaign_id=campaign.campaign_id, 
                influencer_id=influencer.influencer_id
            ).first()
            
            if not existing_request:
                request = InfluencerAdRequest(
                    campaign_id=campaign.campaign_id,
                    influencer_id=influencer.influencer_id,
                    sponsor_id=campaign.sponsor_id,
                    message=f"I'm interested in promoting your {campaign.campaign_name} campaign and believe my audience would respond well to it.",
                    amount=int(campaign.budget.split('-')[0]) + 2000,  # Requested amount is more than minimum budget
                    created_at=datetime.utcnow()
                )
                db.session.add(request)
    
    # Create some sponsor requests to influencers
    for idx, campaign in enumerate(new_campaigns_db):
        # Pick an influencer to send a request to
        influencer = all_influencers[(idx + len(all_influencers) - 1) % len(all_influencers)]
        
        # Check if this influencer already has a request for this campaign
        existing_request = SponsorRequest.query.filter_by(
            campaign_id=campaign.campaign_id, 
            influencer_id=influencer.influencer_id
        ).first()
        
        if not existing_request:
            request = SponsorRequest(
                campaign_id=campaign.campaign_id,
                influencer_id=influencer.influencer_id,
                sponsor_id=campaign.sponsor_id,
                message=f"Your content aligns perfectly with our {campaign.campaign_name} campaign. We'd love to have you on board!",
                amount=int(campaign.budget.split('-')[0]),  # Offered amount is minimum budget
                created_at=datetime.utcnow()
            )
            db.session.add(request)
    
    # Assign influencers to some campaigns
    for idx, campaign in enumerate(new_campaigns_db):
        if idx % 3 == 0:  # Assign an influencer to every third campaign
            influencer = all_influencers[idx % len(all_influencers)]
            campaign.influencer_id = influencer.influencer_id
    
    # Commit all changes
    db.session.commit()
    
    # Count the newly added data
    added_influencers = len([i for i in new_influencer_objects if i.influencer_id])
    added_sponsors = len([s for s in new_sponsor_objects if s.sponsor_id])
    
    print(f"Successfully added {added_influencers} new influencers, {added_sponsors} new sponsors, and {campaign_count} new campaigns!")
    
    print("\nNew influencer login credentials:")
    for inf in new_influencers:
        if Influencer.query.filter_by(username=inf['username']).first():
            print(f"Username: {inf['username']}, Password: {inf['password']}")
    
    print("\nNew sponsor login credentials:")
    for spo in new_sponsors:
        if Sponsor.query.filter_by(username=spo['username']).first():
            print(f"Username: {spo['username']}, Password: {spo['password']}")
    
    print("\nAdditional dummy data created successfully!")

if __name__ == "__main__":
    with app.app_context():
        add_more_dummy_data()