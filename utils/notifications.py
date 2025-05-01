from flask import current_app
from models import Notification, Influencer, Sponsor, db
from datetime import datetime

def create_notification(user_id, message, notification_type, related_id=None):
    """
    Create a new notification for a user
    
    Parameters:
    - user_id: ID of the user receiving the notification
    - message: Notification message content
    - notification_type: Type of notification (request, approval, campaign, etc.)
    - related_id: ID of the related object (campaign_id, request_id, etc.)
    
    Returns:
    - Created notification object
    """
    notification = Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type,
        related_id=related_id,
        date_created=datetime.utcnow(),
        is_read=False
    )
    
    db.session.add(notification)
    db.session.commit()
    return notification

def mark_notification_read(notification_id):
    """
    Mark a notification as read
    
    Parameters:
    - notification_id: ID of the notification to mark as read
    
    Returns:
    - True if successful, False otherwise
    """
    notification = Notification.query.get(notification_id)
    if notification:
        notification.is_read = True
        notification.date_read = datetime.utcnow()
        db.session.commit()
        return True
    return False

def mark_all_notifications_read(user_id):
    """
    Mark all notifications for a user as read
    
    Parameters:
    - user_id: ID of the user whose notifications should be marked as read
    
    Returns:
    - Number of notifications marked as read
    """
    unread_notifications = Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).all()
    
    current_time = datetime.utcnow()
    for notification in unread_notifications:
        notification.is_read = True
        notification.date_read = current_time
    
    db.session.commit()
    return len(unread_notifications)

def get_user_notifications(user_id, limit=10, include_read=False):
    """
    Get notifications for a specific user
    
    Parameters:
    - user_id: ID of the user to get notifications for
    - limit: Maximum number of notifications to return
    - include_read: Whether to include notifications that have been read
    
    Returns:
    - List of notification objects
    """
    query = Notification.query.filter_by(user_id=user_id)
    
    if not include_read:
        query = query.filter_by(is_read=False)
    
    return query.order_by(Notification.date_created.desc()).limit(limit).all()

def get_unread_notification_count(user_id):
    """
    Get the count of unread notifications for a user
    
    Parameters:
    - user_id: ID of the user to count notifications for
    
    Returns:
    - Number of unread notifications
    """
    return Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).count()

def get_unread_count(user_id, user_type):
    """
    Get the count of unread notifications for a specific user
    
    Parameters:
    - user_id: ID of the user to count notifications for
    - user_type: Type of user (admin, influencer, sponsor)
    
    Returns:
    - Number of unread notifications
    """
    # We use the same get_unread_notification_count but just need to handle user types
    return get_unread_notification_count(user_id)

def delete_notification(notification_id):
    """
    Delete a notification
    
    Parameters:
    - notification_id: ID of the notification to delete
    
    Returns:
    - True if successful, False otherwise
    """
    notification = Notification.query.get(notification_id)
    if notification:
        db.session.delete(notification)
        db.session.commit()
        return True
    return False

def delete_all_notifications(user_id):
    """
    Delete all notifications for a user
    
    Parameters:
    - user_id: ID of the user whose notifications should be deleted
    
    Returns:
    - Number of notifications deleted
    """
    notifications = Notification.query.filter_by(user_id=user_id).all()
    count = len(notifications)
    
    for notification in notifications:
        db.session.delete(notification)
    
    db.session.commit()
    return count

def create_campaign_request_notification(influencer_id, campaign_id, campaign_title):
    """
    Create notification when an influencer requests to join a campaign
    
    Parameters:
    - influencer_id: ID of the influencer making the request
    - campaign_id: ID of the campaign being requested
    - campaign_title: Title of the campaign
    """
    # Get the influencer details
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return False
    
    # Get the campaign sponsor
    from models import Campaign
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return False
    
    # Create notification for the sponsor
    message = f"{influencer.username} has requested to join your campaign: {campaign_title}"
    create_notification(
        user_id=campaign.sponsor_id,
        message=message,
        notification_type="request",
        related_id=campaign_id
    )
    
    return True

def create_request_decision_notification(request_id, approved=True):
    """
    Create notification when a sponsor approves/rejects an influencer's request
    
    Parameters:
    - request_id: ID of the request
    - approved: Whether the request was approved (True) or rejected (False)
    """
    # Use appropriate request model classes instead of generic Request
    from models import InfluencerAdRequest, SponsorRequest, Campaign
    
    # Try both request types since we don't know which one it is
    request = InfluencerAdRequest.query.get(request_id)
    if not request:
        request = SponsorRequest.query.get(request_id)
        if not request:
            return False
    
    # Get the campaign details
    campaign = Campaign.query.get(request.campaign_id)
    if not campaign:
        return False
    
    # Get the sponsor details
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    if not sponsor:
        return False
    
    # Create notification for the influencer
    action = "approved" if approved else "rejected"
    message = f"{sponsor.company_name} has {action} your request to join the campaign: {campaign.campaign_name}"
    
    create_notification(
        user_id=request.influencer_id,
        message=message,
        notification_type="request_decision",
        related_id=campaign.campaign_id
    )
    
    return True

def create_payment_notification(influencer_id, campaign_id, amount):
    """
    Create notification when a payment is made to an influencer
    
    Parameters:
    - influencer_id: ID of the influencer receiving payment
    - campaign_id: ID of the campaign
    - amount: Payment amount
    """
    from models import Campaign
    
    # Get the campaign details
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return False
    
    # Get the sponsor details
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    if not sponsor:
        return False
    
    # Create notification for the influencer
    message = f"You've received a payment of ${amount:.2f} from {sponsor.company_name} for the campaign: {campaign.campaign_name}"
    
    create_notification(
        user_id=influencer_id,
        message=message,
        notification_type="payment",
        related_id=campaign_id
    )
    
    return True

def create_campaign_complete_notification(campaign_id):
    """
    Create notifications when a campaign is marked as completed
    
    Parameters:
    - campaign_id: ID of the completed campaign
    """
    from models import Campaign, InfluencerAdRequest, SponsorRequest
    
    # Get the campaign details
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return False
    
    # Get the sponsor details
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    if not sponsor:
        return False
    
    # Get all approved influencers for this campaign
    approved_requests = InfluencerAdRequest.query.filter_by(
        campaign_id=campaign_id,
        influencer_status='Approved'  # Updated to match your schema
    ).all()
    
    # Create notification for each influencer
    for request in approved_requests:
        message = f"The campaign '{campaign.campaign_name}' by {sponsor.company_name} has been marked as completed."
        
        create_notification(
            user_id=request.influencer_id,
            message=message,
            notification_type="campaign_complete",
            related_id=campaign_id
        )
    
    return True

def create_new_campaign_notification(campaign_id):
    """
    Create notifications for relevant influencers when a new campaign is created
    
    Parameters:
    - campaign_id: ID of the new campaign
    """
    from models import Campaign, Influencer
    
    # Get the campaign details
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return False
    
    # Get the sponsor details
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    if not sponsor:
        return False
    
    # Find influencers who match the campaign requirements
    # This is a simplified matching logic - adjust based on your actual data model
    matching_influencers = Influencer.query.filter(
        Influencer.genre == campaign.finding_niche
    ).limit(20).all()  # Limiting to 20 notifications to avoid spam
    
    # Create notification for each matching influencer
    for influencer in matching_influencers:
        message = f"New campaign '{campaign.campaign_name}' by {sponsor.company_name} matches your profile."
        
        create_notification(
            user_id=influencer.influencer_id,
            message=message,
            notification_type="new_campaign",
            related_id=campaign_id
        )
    
    return True