from flask import Blueprint, jsonify, request, session
from models import Influencer, Sponsor, Campaign, InfluencerAdRequest, SponsorRequest, db
from utils.notifications import get_user_notifications, mark_notification_read, mark_all_notifications_read, get_unread_count
from utils.security import get_current_user, is_authenticated, get_user_type
from utils.analytics import get_influencer_analytics, get_sponsor_analytics
import json

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for the current user"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
        
    user = get_current_user()
    user_type = get_user_type()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user ID based on type
    if user_type == 'admin':
        user_id = user.admin_id
    elif user_type == 'influencer':
        user_id = user.influencer_id
    elif user_type == 'sponsor':
        user_id = user.sponsor_id
    else:
        return jsonify({'error': 'Invalid user type'}), 400
    
    # Get notifications
    limit = request.args.get('limit', 10, type=int)
    include_read = request.args.get('include_read', 'false').lower() == 'true'
    
    notifications = get_user_notifications(user_id, limit, include_read)
    
    return jsonify({
        'notifications': [notification.to_dict() for notification in notifications],
        'unread_count': get_unread_count(user_id, user_type)
    })

@api_bp.route('/notifications/read/<int:notification_id>', methods=['POST'])
def read_notification(notification_id):
    """Mark a notification as read"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    success = mark_notification_read(notification_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Notification marked as read'})
    else:
        return jsonify({'error': 'Notification not found'}), 404

@api_bp.route('/notifications/read-all', methods=['POST'])
def read_all_notifications():
    """Mark all notifications as read"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = get_current_user()
    user_type = get_user_type()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user ID based on type
    if user_type == 'admin':
        user_id = user.admin_id
    elif user_type == 'influencer':
        user_id = user.influencer_id
    elif user_type == 'sponsor':
        user_id = user.sponsor_id
    else:
        return jsonify({'error': 'Invalid user type'}), 400
    
    # Call with just user_id, as the function doesn't use user_type
    count = mark_all_notifications_read(user_id)
    
    return jsonify({
        'success': True,
        'message': f'Marked {count} notifications as read'
    })

@api_bp.route('/influencer/analytics/<int:influencer_id>', methods=['GET'])
def influencer_analytics(influencer_id):
    """Get analytics for a specific influencer"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_type = get_user_type()
    user = get_current_user()
    
    # Authorization check - only the influencer themselves or an admin can view
    if user_type == 'influencer' and user.influencer_id != influencer_id:
        return jsonify({'error': 'Unauthorized'}), 403
    elif user_type == 'sponsor':
        return jsonify({'error': 'Unauthorized'}), 403
    
    analytics = get_influencer_analytics(influencer_id)
    
    return jsonify(analytics)

@api_bp.route('/sponsor/analytics/<int:sponsor_id>', methods=['GET'])
def sponsor_analytics(sponsor_id):
    """Get analytics for a specific sponsor"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_type = get_user_type()
    user = get_current_user()
    
    # Authorization check - only the sponsor themselves or an admin can view
    if user_type == 'sponsor' and user.sponsor_id != sponsor_id:
        return jsonify({'error': 'Unauthorized'}), 403
    elif user_type == 'influencer':
        return jsonify({'error': 'Unauthorized'}), 403
    
    analytics = get_sponsor_analytics(sponsor_id)
    
    return jsonify(analytics)

@api_bp.route('/campaigns/search', methods=['GET'])
def search_campaigns():
    """Search campaigns based on various filters"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get search parameters
    search_term = request.args.get('query', '')
    genre = request.args.get('genre', '')
    status = request.args.get('status', '')
    
    # Start with base query
    query = db.session.query(Campaign)
    
    # Apply filters
    if search_term:
        query = query.filter(
            Campaign.campaign_name.ilike(f'%{search_term}%') | 
            Campaign.description.ilike(f'%{search_term}%')
        )
    
    if genre:
        query = query.filter(Campaign.finding_niche == genre)
    
    if status:
        query = query.filter(Campaign.status == status)
    
    # Only show public campaigns for influencers or all for admins
    user_type = get_user_type()
    if user_type == 'influencer':
        query = query.filter(Campaign.visibility == 'Public')
    
    campaigns = query.all()
    
    # Format response
    result = []
    for campaign in campaigns:
        sponsor = Sponsor.query.get(campaign.sponsor_id)
        
        result.append({
            'campaign_id': campaign.campaign_id,
            'campaign_name': campaign.campaign_name,
            'description': campaign.description,
            'sponsor_name': sponsor.username if sponsor else 'Unknown',
            'start_date': campaign.start_date.strftime('%Y-%m-%d'),
            'end_date': campaign.end_date.strftime('%Y-%m-%d'),
            'status': campaign.status,
            'budget': campaign.budget,
            'genre': campaign.finding_niche
        })
    
    return jsonify(result)

@api_bp.route('/influencers/search', methods=['GET'])
def search_influencers():
    """Search influencers based on various filters"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get search parameters
    search_term = request.args.get('query', '')
    platform = request.args.get('platform', '')
    genre = request.args.get('genre', '')
    popularity = request.args.get('popularity', '')
    
    # Start with base query
    query = db.session.query(Influencer)
    
    # Apply filters
    if search_term:
        query = query.filter(
            Influencer.username.ilike(f'%{search_term}%') | 
            Influencer.bio.ilike(f'%{search_term}%')
        )
    
    if platform:
        query = query.filter(Influencer.platform == platform)
    
    if genre:
        query = query.filter(Influencer.genre == genre)
    
    if popularity:
        query = query.filter(Influencer.popularity == popularity)
    
    # Don't show flagged influencers
    query = query.filter(Influencer.flag == 'no')
    
    influencers = query.all()
    
    # Format response
    result = []
    for influencer in influencers:
        result.append({
            'influencer_id': influencer.influencer_id,
            'username': influencer.username,
            'platform': influencer.platform,
            'genre': influencer.genre,
            'popularity': influencer.popularity,
            'bio': influencer.bio
        })
    
    return jsonify(result)

@api_bp.route('/campaign/requests/<int:campaign_id>', methods=['GET'])
def campaign_requests(campaign_id):
    """Get all influencer requests for a campaign"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_type = get_user_type()
    user = get_current_user()
    
    # Get campaign
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    # Authorization check - only the campaign owner or admin can view
    if user_type == 'sponsor' and user.sponsor_id != campaign.sponsor_id:
        return jsonify({'error': 'Unauthorized'}), 403
    elif user_type == 'influencer':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get requests
    requests = InfluencerAdRequest.query.filter_by(campaign_id=campaign_id).all()
    
    result = []
    for req in requests:
        influencer = Influencer.query.get(req.influencer_id)
        
        result.append({
            'request_id': req.influencer_request_id,
            'influencer_id': req.influencer_id,
            'influencer_username': influencer.username if influencer else 'Unknown',
            'platform': influencer.platform if influencer else 'Unknown',
            'genre': influencer.genre if influencer else 'Unknown',
            'message': req.message,
            'amount': req.amount,
            'status': req.influencer_status,
            'date': req.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result)

def register_api_routes(app):
    """Register API routes with the Flask app"""
    app.register_blueprint(api_bp)