from flask import Blueprint, render_template, url_for, redirect, flash, request, session, Response
from models import Admin, Influencer, Sponsor, Campaign, InfluencerAdRequest, SponsorRequest, Img, Notification
# Import db directly from db.py instead of models
from db import db, bcrypt
import sqlalchemy as sa
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import config
from functools import wraps

# Create blueprints for different sections of the application
main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
influencer_bp = Blueprint('influencer', __name__, url_prefix='/influencer')
sponsor_bp = Blueprint('sponsor', __name__, url_prefix='/sponsor')

def register_routes(app):
    """Register all blueprints to the app"""
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(influencer_bp)
    app.register_blueprint(sponsor_bp)

# Admin login required decorator
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login to access the admin dashboard.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# Main routes
@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('main.index'))

# Admin routes
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.admin_id
            session['admin_name'] = admin.username  # Store both for compatibility
            flash('Login successful!', 'success')
            return redirect(url_for('admin.home'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    
    return render_template('admin_login.html')

@admin_bp.route('/home')
@admin_login_required
def home():
    # Get view parameter for different sections of admin panel
    view = request.args.get('view', 'dashboard')
    
    # Load common data needed across views
    influencers = Influencer.query.all()
    sponsors = Sponsor.query.all()
    campaigns = Campaign.query.all()
    active_campaign_count = Campaign.query.filter_by(status='Active').count()
    
    # Handle notification count safely - to prevent ROLLBACK errors
    notification_count = 0
    try:
        # Try to run the notification query in a separate transaction
        from sqlalchemy.orm import Session
        from db import engine

        # Create a new session just for this query to isolate it
        with Session(engine) as separate_session:
            # Get notification count
            notification_count = separate_session.query(sa.func.count()).select_from(Notification).filter(
                Notification.user_id == session.get('admin_id'),
                Notification.is_read == False
            ).scalar() or 0
    except Exception as e:
        # Log the error but continue with the page load
        print(f"Error getting notification count: {e}")
        notification_count = 0
    
    # Handle different views based on query parameter
    if view == 'users':
        return render_template('admin_home.html', 
                                influencers=influencers, 
                                sponsors=sponsors, 
                                view=view,
                                notification_count=notification_count,
                                title="User Management")

    elif view == 'campaigns':
        # Format campaign data for the campaign management view
        formatted_campaigns = []
        
        for campaign in campaigns:
            sponsor = Sponsor.query.get(campaign.sponsor_id)
            # Count unique influencers associated with this campaign through sponsor requests
            try:
                # Count distinct influencers that have been requested for this campaign
                influencer_count = db.session.query(db.func.count(db.distinct(SponsorRequest.influencer_id))).filter(
                    SponsorRequest.campaign_id == campaign.campaign_id
                ).scalar() or 0
                
            except Exception as e:
                # Fallback to zero if there's an error with the query
                print(f"Error counting influencers for campaign {campaign.campaign_id}: {e}")
                influencer_count = 0
            
            formatted_campaigns.append({
                'campaign_id': campaign.campaign_id,
                'title': campaign.campaign_name,
                'sponsor_id': campaign.sponsor_id,
                'sponsor_username': sponsor.username if sponsor else 'Unknown',
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'budget': campaign.budget,
                'influencer_count': influencer_count,
                'status': campaign.status
            })
            
        return render_template('admin_home.html', 
                               influencers=influencers, 
                               sponsors=sponsors, 
                               campaigns=formatted_campaigns,
                               active_campaign_count=active_campaign_count,
                               notification_count=notification_count,
                               view=view,
                               title="Campaign Management")

    elif view == 'reports':
        # Get analytics data
        total_influencers = len(influencers)
        total_sponsors = len(sponsors)
        total_campaigns = len(campaigns)
        
        return render_template('admin_home.html', 
                                influencers=influencers, 
                                sponsors=sponsors,
                                campaigns=campaigns,
                                total_influencers=total_influencers,
                                total_sponsors=total_sponsors,
                                total_campaigns=total_campaigns,
                                active_campaign_count=active_campaign_count,
                                notification_count=notification_count,
                                view=view,
                                title="Analytics & Reports")

    elif view == 'settings':
        return render_template('admin_home.html', 
                                view=view,
                                notification_count=notification_count,
                                title="Platform Settings")
    
    # Default dashboard view
    admin_count = Admin.query.count()
    sponsor_count = len(sponsors)
    influencer_count = len(influencers)
    total_earnings = 0  # This would be calculated from actual data
    
    return render_template('admin_home.html', 
                          influencers=influencers, 
                          sponsors=sponsors,
                          campaigns=campaigns,
                          active_campaign_count=active_campaign_count,
                          admin_count=admin_count,
                          sponsor_count=sponsor_count,
                          influencer_count=influencer_count,
                          total_earnings=total_earnings,
                          notification_count=notification_count,
                          view='dashboard',
                          title="Dashboard Overview")

@admin_bp.route('/actions', methods=['POST'])
@admin_login_required
def admin_actions():
    # Flag an influencer
    if 'flag' in request.form and 'influencer_id' in request.form:
        influencer_id = request.form.get('influencer_id')
        flag_value = request.form.get('flag')
        
        influencer = Influencer.query.get(influencer_id)
        if influencer:
            influencer.flag = flag_value
            db.session.commit()
            flash(f'Influencer {influencer.username} has been {"flagged" if flag_value=="yes" else "unflagged"}.', 'success')
    
    # Delete an influencer
    elif 'delete' in request.form and 'influencer_id' in request.form:
        influencer_id = request.form.get('influencer_id')
        influencer = Influencer.query.get(influencer_id)
        
        if influencer:
            db.session.delete(influencer)
            db.session.commit()
            flash(f'Influencer {influencer.username} has been deleted.', 'success')
    
    # Flag a sponsor
    elif 'flag_sponsor' in request.form and 'sponsor_id' in request.form:
        sponsor_id = request.form.get('sponsor_id')
        flag_value = request.form.get('flag_sponsor')
        
        sponsor = Sponsor.query.get(sponsor_id)
        if sponsor:
            sponsor.flag = flag_value
            db.session.commit()
            flash(f'Sponsor {sponsor.username} has been {"flagged" if flag_value=="yes" else "unflagged"}.', 'success')
    
    # Delete a sponsor
    elif 'delete_sponsor' in request.form and 'sponsor_id' in request.form:
        sponsor_id = request.form.get('sponsor_id')
        sponsor = Sponsor.query.get(sponsor_id)
        
        if sponsor:
            db.session.delete(sponsor)
            db.session.commit()
            flash(f'Sponsor {sponsor.username} has been deleted.', 'success')
    
    # Campaign management actions
    elif 'campaign_action' in request.form and 'campaign_id' in request.form:
        campaign_id = request.form.get('campaign_id')
        action = request.form.get('campaign_action')
        
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            if action == 'approve':
                campaign.status = 'active'
                flash(f'Campaign "{campaign.campaign_name}" has been approved.', 'success')
            elif action == 'pause':
                campaign.status = 'paused'
                flash(f'Campaign "{campaign.campaign_name}" has been paused.', 'success')
            elif action == 'complete':
                campaign.status = 'completed'
                flash(f'Campaign "{campaign.campaign_name}" has been marked as completed.', 'success')
            elif action == 'delete':
                db.session.delete(campaign)
                flash(f'Campaign "{campaign.campaign_name}" has been deleted.', 'success')
            elif action == 'flag':
                campaign.flag = 'yes'
                flash(f'Campaign "{campaign.campaign_name}" has been flagged.', 'success')
            elif action == 'unflag':
                campaign.flag = 'no'
                flash(f'Campaign "{campaign.campaign_name}" has been unflagged.', 'success')
                
            db.session.commit()
    
    # Redirect back to the same view
    view = request.args.get('view', 'dashboard')
    return redirect(url_for('admin.home', view=view))

@admin_bp.route("/logout")
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Successfully logged out', 'success')
    return redirect(url_for("main.index"))

@admin_bp.route("/influencer/stats")
@admin_login_required
def influencer_stats():
    """Statistical data about influencers"""
    # Query the database to get the count of each genre
    niche_results = db.session.query(
        Influencer.genre, 
        db.func.count(Influencer.influencer_id)
    ).group_by(Influencer.genre).all()
    
    niche_count_list = [(genre, count) for genre, count in niche_results]
    labels = [genre for genre, count in niche_results]
    data = [count for genre, count in niche_results]
    
    # Query the database to get the count of each platform
    platform_result = db.session.query(
        Influencer.platform, 
        db.func.count(Influencer.influencer_id)
    ).group_by(Influencer.platform).all()
    
    platform_count_list = [(platform, count) for platform, count in platform_result]
    labels2 = [platform for platform, count in platform_result]
    data2 = [count for platform, count in platform_result]
    
    # Query by flagged condition
    results = db.session.query(
        db.func.count().filter(Influencer.flag == 'yes').label('Flagged'),
        db.func.count().filter(Influencer.flag == 'no').label('Ethical')
    ).all()
    
    flag_count_list = [('yes', results[0][0]), ('no', results[0][1])]

    labels3 = ['yes', 'no']
    data3 = [results[0][0], results[0][1]]
    
    # Information of influencer
    influencer_count = db.session.query(db.func.count(Influencer.influencer_id)).scalar()
    
    subquery = db.session.query(Influencer.genre).distinct().subquery()
    unique_genre_count = db.session.query(db.func.count()).select_from(subquery).scalar()
    
    subquery2 = db.session.query(Influencer.platform).distinct().subquery()
    unique_platform_count = db.session.query(db.func.count()).select_from(subquery2).scalar()
    
    flag_count = db.session.query(db.func.count(Influencer.influencer_id)).filter(Influencer.flag == 'yes').scalar()
    unflag_count = db.session.query(db.func.count(Influencer.influencer_id)).filter(Influencer.flag == 'no').scalar()
    
    influencer_request_count = db.session.query(db.func.count(InfluencerAdRequest.influencer_request_id)).scalar()
    
    info_influencer = [
        influencer_count,
        unique_genre_count,
        unique_platform_count,
        flag_count,
        unflag_count,
        influencer_request_count
    ]
    
    return render_template(
        'influencer_stats.html',
        labels=labels,
        data=data,
        labels2=labels2,
        data2=data2,
        labels3=labels3,
        data3=data3,
        influencer=info_influencer
    )

@admin_bp.route("/sponsor/stats")
@admin_login_required
def sponsor_stats():
    """Statistical data about sponsors"""
    # Query for count of campaigns per industry
    results = db.session.query(
        Sponsor.industry, 
        db.func.count(Sponsor.sponsor_id)
    ).group_by(Sponsor.industry).all()
    
    industry_count_list = [(industry, count) for industry, count in results]
    labels = [industry for industry, count in results]
    data = [count for industry, count in results]
    
    # Query for count of campaigns per user
    results = db.session.query(
        Sponsor.sponsor_id, 
        Sponsor.username, 
        db.func.count(Campaign.campaign_id)
    ).outerjoin(
        Campaign, 
        Sponsor.sponsor_id == Campaign.sponsor_id
    ).group_by(
        Sponsor.sponsor_id, 
        Sponsor.username
    ).all()
    
    sponsor_campaign_list = [(sponsor_id, sponsor_name, count) for sponsor_id, sponsor_name, count in results]
    labels2 = [sponsor_name for sponsor_id, sponsor_name, count in results]
    data2 = [count for sponsor_id, sponsor_name, count in results]
    
    # Query by sponsor flagged condition
    results = db.session.query(
        db.func.count().filter(Sponsor.flag == 'yes').label('Flagged'),
        db.func.count().filter(Sponsor.flag == 'no').label('Ethical')
    ).all()
    
    flag_count_list = [('yes', results[0][0]), ('no', results[0][1])]
    labels3 = ['yes', 'no']
    data3 = [results[0][0], results[0][1]]
    
    # Information of sponsor
    sponsor_count = db.session.query(db.func.count(Sponsor.sponsor_id)).scalar()
    
    subquery = db.session.query(Sponsor.industry).distinct().subquery()
    unique_industry_count = db.session.query(db.func.count()).select_from(subquery).scalar()
    
    flag_count = db.session.query(db.func.count(Sponsor.sponsor_id)).filter(Sponsor.flag == 'yes').scalar()
    unflag_count = db.session.query(db.func.count(Sponsor.sponsor_id)).filter(Sponsor.flag == 'no').scalar()
    
    sponsor_request_count = db.session.query(db.func.count(SponsorRequest.sponsor_request_id)).scalar()
    
    info_sponsor = [
        sponsor_count,
        unique_industry_count,
        flag_count,
        unflag_count,
        sponsor_request_count
    ]
    
    return render_template(
        'sponsor_stats.html',
        labels=labels,
        data=data,
        labels2=labels2,
        data2=data2,
        labels3=labels3,
        data3=data3,
        sponsor=info_sponsor
    )

@admin_bp.route("/campaign/stats", methods=['GET', 'POST'])
@admin_login_required
def campaign_stats():
    """Campaign statistics and management"""
    if request.method == 'POST':
        if 'flag' in request.form:
            campaign_id = request.form['campaign_id']
            flag = request.form['flag']
            campaign_obj = Campaign.query.filter_by(campaign_id=campaign_id).first()
            campaign_obj.flag = flag
            db.session.commit()
            flash(f"Campaign '{campaign_obj.campaign_name}' flag updated", 'success')
            return redirect(url_for("admin.campaign_stats"))
    
    # Join sponsor and campaign tables
    campaigns = db.session.query(Sponsor, Campaign).join(Campaign).all()
    
    # Visibility count of campaigns [public, private]
    results = db.session.query(
        Campaign.visibility, 
        db.func.count(Campaign.campaign_id)
    ).group_by(Campaign.visibility).all()
    
    campaign_count_list = [(campaign_type, count) for campaign_type, count in results]
    labels = [campaign_type for campaign_type, count in results]
    data = [count for campaign_type, count in results]

    # Niche of campaign when campaign is private
    results = db.session.query(
        Campaign.finding_niche, 
        db.func.count(Campaign.campaign_id)
    ).filter(Campaign.visibility == 'Private').group_by(Campaign.finding_niche).all()
    
    niche_campaign_list = [(niche, count) for niche, count in results]
    labels2 = [niche for niche, count in results]
    data2 = [count for niche, count in results]
    
    # Campaign count per sponsor
    results = db.session.query(
        Sponsor.sponsor_id, 
        Sponsor.username, 
        db.func.count(Campaign.campaign_id)
    ).outerjoin(
        Campaign, 
        Sponsor.sponsor_id == Campaign.sponsor_id
    ).group_by(
        Sponsor.sponsor_id, 
        Sponsor.username
    ).all()
    
    sponsor_campaign_list = [(sponsor_id, sponsor_name, count) for sponsor_id, sponsor_name, count in results]
    labels3 = [sponsor_name for sponsor_id, sponsor_name, count in results]
    data3 = [count for sponsor_id, sponsor_name, count in results]
    
    return render_template(
        'campaign_stats.html',
        campaigns=campaigns,
        labels=labels,
        data=data,
        labels2=labels2,
        data2=data2,
        labels3=labels3,
        data3=data3
    )

@main_bp.route("/view_campaign")
def view_campaign():
    """View details of a specific campaign"""
    campaign_id = int(request.args.get('campaign_id'))
    campaigns = db.session.query(Sponsor, Campaign).join(Campaign).filter(Campaign.campaign_id == campaign_id).all()
    return render_template('view_campaign.html', campaign=campaigns)

# Influencer routes
@influencer_bp.route("/login", methods=['GET', 'POST'])
def login():
    """Influencer login page"""
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        found_user = Influencer.query.filter_by(username=name).first()
        
        if not found_user:
            flash('User does not exist', 'danger')
            return redirect(url_for("influencer.login"))
            
        if found_user.flag == 'yes':
            flash('Your account has been flagged by administrators', 'danger')
            return redirect(url_for("influencer.login"))
            
        # Use bcrypt to check password instead of the model's check_password method
        if bcrypt.check_password_hash(found_user.password, password):
            session['influencer_name'] = name
            found_user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Login successful', 'success')
            return redirect(url_for("influencer.home"))
        else:
            flash('Incorrect password', 'danger')
            return redirect(url_for("influencer.login"))
            
    return render_template('influencer_login.html')

@influencer_bp.route("/register", methods=['GET', 'POST'])
def register():
    """Influencer registration page"""
    if request.method == 'POST':
        username = request.form.get('name')  # Using 'name' as in the form
        email = request.form.get('email')
        password = request.form.get('password')
        genre = request.form.get('genre')
        platform = request.form.get('platform')
        follower_count = request.form.get('follower')  # Using 'follower' as in the form
        short_description = request.form.get('bio')  # Using 'bio' as in the form
        
        # Validation
        if not all([username, email, password, genre, platform, follower_count]):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('influencer.register'))
            
        # Check if user already exists
        existing_user = Influencer.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return redirect(url_for('influencer.register'))
            
        existing_email = Influencer.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered', 'danger')
            return redirect(url_for('influencer.register'))
        
        # Create new influencer
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_influencer = Influencer(
            username=username,
            email=email,
            password=hashed_password,
            genre=genre,
            platform=platform,
            popularity=follower_count,  # Map to the correct field name in the model
            bio=short_description,      # Using 'bio' as in the model
            flag='no',                  # Default not flagged
            created_at=datetime.utcnow()
        )
        
        # Handle profile image if uploaded
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                new_influencer.profile_image = filename
        
        # Save influencer to database
        db.session.add(new_influencer)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('influencer.login'))
        
    return render_template('influencer_register.html')

@influencer_bp.route("/home")
def home():
    """Influencer home page"""
    if 'influencer_name' not in session:
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('influencer.login'))
        
    username = session['influencer_name']
    founduser = Influencer.query.filter_by(username=username).first()
    
    # Get active campaigns that might be relevant to this influencer
    active_campaigns = Campaign.query.filter_by(status='Active').limit(5).all()
    
    # Get profile image
    profile = Img.query.filter_by(influencer_id=founduser.influencer_id).first()
    profile = profile if profile else 'none'
    
    # Get influencer's requests with campaign and sponsor details
    influencer_request_data = db.session.query(
        InfluencerAdRequest, Campaign, Sponsor
    ).join(
        Campaign, InfluencerAdRequest.campaign_id == Campaign.campaign_id
    ).join(
        Sponsor, InfluencerAdRequest.sponsor_id == Sponsor.sponsor_id
    ).filter(
        InfluencerAdRequest.influencer_id == founduser.influencer_id
    ).all()
    
    # Get sponsor requests with campaign and sponsor details
    sponsor_request_data = db.session.query(
        SponsorRequest, Campaign, Sponsor
    ).join(
        Campaign, SponsorRequest.campaign_id == Campaign.campaign_id
    ).join(
        Sponsor, SponsorRequest.sponsor_id == Sponsor.sponsor_id
    ).filter(
        SponsorRequest.influencer_id == founduser.influencer_id
    ).all()
    
    return render_template(
        'influencer_home.html', 
        founduser=founduser, 
        active_campaigns=active_campaigns,
        profile=profile,
        influencer_requests=influencer_request_data,
        sponsor_requests=sponsor_request_data
    )

@influencer_bp.route("/profile/edit", methods=['GET', 'POST'])
def profile_edit():
    """Edit influencer profile page"""
    if 'influencer_name' not in session:
        flash('Please login to access your profile.', 'warning')
        return redirect(url_for('influencer.login'))
        
    username = session['influencer_name']
    influencer = Influencer.query.filter_by(username=username).first()
    
    # Get current profile image
    profile_image = Img.query.filter_by(influencer_id=influencer.influencer_id).first()
    
    if request.method == 'POST':
        # Update profile information
        influencer.username = request.form.get('username', influencer.username)
        influencer.email = request.form.get('email', influencer.email)
        influencer.genre = request.form.get('genre', influencer.genre)
        influencer.platform = request.form.get('platform', influencer.platform)
        influencer.popularity = request.form.get('follower_count', influencer.popularity)
        influencer.bio = request.form.get('bio', influencer.bio)
        
        # Handle profile image update if provided
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # If already has profile image, update it
                if profile_image:
                    profile_image.name = filename
                    profile_image.filepath = file_path
                    profile_image.mimetype = file.mimetype
                else:
                    # Create new profile image record
                    new_image = Img(
                        name=filename,
                        filepath=file_path,
                        mimetype=file.mimetype,
                        influencer_id=influencer.influencer_id
                    )
                    db.session.add(new_image)
        
        # Handle password update if provided
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password == confirm_password:
                influencer.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                flash('Password updated successfully!', 'success')
            else:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('influencer.profile_edit'))
        
        # Save all changes
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('influencer.home'))
    
    return render_template(
        'influencer_profile_edit.html', 
        influencer=influencer,
        profile_image=profile_image
    )

# Sponsor routes
@sponsor_bp.route("/login", methods=['GET', 'POST'])
def login():
    """Sponsor login page"""
    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')
        
        sponsor = Sponsor.query.filter_by(username=username).first()
        
        if sponsor and bcrypt.check_password_hash(sponsor.password, password):
            session['sponsor_id'] = sponsor.sponsor_id
            session['sponsor_username'] = sponsor.username
            flash(f'Welcome back, {sponsor.username}!', 'success')
            return redirect(url_for('sponsor.home'))
        else:
            flash('Login failed! Please check your username and password.', 'danger')
    
    return render_template('sponsor_login.html')

@sponsor_bp.route("/register", methods=['GET', 'POST'])
def register():
    """Sponsor registration page"""
    if request.method == 'POST':
        username = request.form.get('name')  # Changed from 'username' to 'name' to match the form
        email = request.form.get('email')
        password = request.form.get('password')
        company_name = request.form.get('company_name')
        industry = request.form.get('industry')
        website = request.form.get('website')  # Added website field from the form
        
        # Validation
        if not all([username, email, password, company_name, industry]):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('sponsor.register'))
            
        # Check if username or email already exists
        existing_user = Sponsor.query.filter((Sponsor.username == username) | (Sponsor.email == email)).first()
        if existing_user:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('sponsor.register'))
        
        # Hash password
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new sponsor
        new_sponsor = Sponsor(
            username=username,
            email=email,
            password=hashed_pw,
            company_name=company_name,
            industry=industry,
            website=website,  # Added website field
            flag='no',  # Default to not flagged
            created_at=datetime.utcnow()  # Added creation timestamp
        )
        
        db.session.add(new_sponsor)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('sponsor.login'))
        
    return render_template('sponsor_register.html')

@sponsor_bp.route("/home")
def home():
    """Sponsor home page"""
    if 'sponsor_id' not in session:
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('sponsor.login'))
        
    sponsor_id = session['sponsor_id']
    sponsor = Sponsor.query.get(sponsor_id)
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
    
    return render_template('sponsor_home.html', sponsor=sponsor, campaigns=campaigns)

# More routes for influencer and sponsor management would be placed here

# Function to check if file upload is allowed
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

