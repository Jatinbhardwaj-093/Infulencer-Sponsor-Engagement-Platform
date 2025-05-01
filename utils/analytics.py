from flask import current_app, jsonify
from models import Influencer, Sponsor, Campaign, InfluencerAdRequest, SponsorRequest, db
from sqlalchemy import func, extract, desc, and_, or_
from datetime import datetime, timedelta
import calendar
import json

def get_platform_growth_data(days=30):
    """
    Get growth data for the platform (new influencers and sponsors over time)
    Returns data suitable for a line chart
    """
    today = datetime.utcnow()
    start_date = today - timedelta(days=days)
    
    # Query for influencers registered per day
    influencer_data = db.session.query(
        func.date(Influencer.date_registered).label('date'),
        func.count(Influencer.id).label('count')
    ).filter(
        Influencer.date_registered >= start_date
    ).group_by(
        func.date(Influencer.date_registered)
    ).all()
    
    # Query for sponsors registered per day
    sponsor_data = db.session.query(
        func.date(Sponsor.date_registered).label('date'),
        func.count(Sponsor.id).label('count')
    ).filter(
        Sponsor.date_registered >= start_date
    ).group_by(
        func.date(Sponsor.date_registered)
    ).all()
    
    # Convert to dictionaries for easier lookup
    influencer_dict = {str(item.date): item.count for item in influencer_data}
    sponsor_dict = {str(item.date): item.count for item in sponsor_data}
    
    # Generate date range for the past N days
    date_range = []
    for i in range(days, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        date_range.append(date_str)
    
    # Format for chart.js
    influencer_counts = [influencer_dict.get(date, 0) for date in date_range]
    sponsor_counts = [sponsor_dict.get(date, 0) for date in date_range]
    
    # Format x-axis labels (dates) to be more readable
    labels = [datetime.strptime(date, '%Y-%m-%d').strftime('%b %d') for date in date_range]
    
    return {
        'labels': labels,
        'influencer_data': influencer_counts,
        'sponsor_data': sponsor_counts
    }

def get_genre_distribution():
    """
    Get distribution of influencers by genre/niche
    Returns data suitable for a pie or doughnut chart
    """
    genre_data = db.session.query(
        Influencer.genre,  # Changed from content_category to genre
        func.count(Influencer.influencer_id).label('count')  # Changed from id to influencer_id
    ).group_by(
        Influencer.genre
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    # Handle empty or None values
    labels = []
    counts = []
    
    for item in genre_data:
        genre = item.genre or 'Other'  # Changed from content_category to genre
        labels.append(genre)
        counts.append(item.count)
    
    # If we have fewer than 10 genres, add an "Other" category
    if len(genre_data) < 10:
        other_count = db.session.query(func.count(Influencer.influencer_id)).filter(  # Changed from id to influencer_id
            Influencer.genre.notin_(labels) | Influencer.genre.is_(None)  # Changed from content_category to genre
        ).scalar()
        
        if other_count > 0:
            labels.append('Other')
            counts.append(other_count)
    
    return {
        'labels': labels,
        'data': counts
    }

def get_platform_distribution():
    """
    Get distribution of influencers by social media platform
    Returns data suitable for a pie chart
    """
    platform_data = db.session.query(
        Influencer.platform,  # Changed from platform_name to platform
        func.count(Influencer.influencer_id).label('count')  # Changed from id to influencer_id
    ).group_by(
        Influencer.platform
    ).order_by(
        desc('count')
    ).all()
    
    # Handle empty or None values
    labels = []
    counts = []
    
    for item in platform_data:
        platform = item.platform or 'Other'  # Changed from platform_name to platform
        labels.append(platform)
        counts.append(item.count)
    
    return {
        'labels': labels,
        'data': counts
    }

def get_campaign_timeline(days=30):
    """
    Get campaign creation timeline
    Returns data suitable for a bar chart
    """
    today = datetime.utcnow()
    start_date = today - timedelta(days=days)
    
    campaign_data = db.session.query(
        func.date(Campaign.date_created).label('date'),
        func.count(Campaign.id).label('count')
    ).filter(
        Campaign.date_created >= start_date
    ).group_by(
        func.date(Campaign.date_created)
    ).all()
    
    # Convert to dictionary for easier lookup
    campaign_dict = {str(item.date): item.count for item in campaign_data}
    
    # Generate date range for the past N days
    date_range = []
    for i in range(days, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        date_range.append(date_str)
    
    # Format for chart.js
    counts = [campaign_dict.get(date, 0) for date in date_range]
    
    # Format x-axis labels (dates) to be more readable
    labels = [datetime.strptime(date, '%Y-%m-%d').strftime('%b %d') for date in date_range]
    
    return {
        'labels': labels,
        'data': counts
    }

def get_campaign_success_rate():
    """
    Calculate campaign success rates based on completion status
    Returns data suitable for a pie chart
    """
    total_completed = db.session.query(func.count(Campaign.id)).filter(
        Campaign.status == 'completed'
    ).scalar() or 0
    
    total_active = db.session.query(func.count(Campaign.id)).filter(
        Campaign.status == 'active'
    ).scalar() or 0
    
    total_cancelled = db.session.query(func.count(Campaign.id)).filter(
        Campaign.status == 'cancelled'
    ).scalar() or 0
    
    total_pending = db.session.query(func.count(Campaign.id)).filter(
        Campaign.status == 'pending'
    ).scalar() or 0
    
    labels = ['Completed', 'Active', 'Cancelled', 'Pending']
    data = [total_completed, total_active, total_cancelled, total_pending]
    
    return {
        'labels': labels,
        'data': data
    }

def get_request_acceptance_rate():
    """
    Calculate percentage of approved vs. rejected campaign requests
    Returns data suitable for a pie chart
    """
    total_approved = db.session.query(func.count(InfluencerAdRequest.id)).filter(
        InfluencerAdRequest.status == 'approved'
    ).scalar() or 0
    
    total_rejected = db.session.query(func.count(InfluencerAdRequest.id)).filter(
        InfluencerAdRequest.status == 'rejected'
    ).scalar() or 0
    
    total_pending = db.session.query(func.count(InfluencerAdRequest.id)).filter(
        InfluencerAdRequest.status == 'pending'
    ).scalar() or 0
    
    labels = ['Approved', 'Rejected', 'Pending']
    data = [total_approved, total_rejected, total_pending]
    
    return {
        'labels': labels,
        'data': data
    }

def get_top_influencers(limit=5):
    """
    Get top influencers based on completed campaign count
    Returns data for a leaderboard
    """
    top_influencers = db.session.query(
        Influencer.id,
        Influencer.username,
        Influencer.profile_picture,
        Influencer.content_category,
        Influencer.platform_name,
        func.count(InfluencerAdRequest.id).label('campaign_count')
    ).join(
        InfluencerAdRequest, InfluencerAdRequest.influencer_id == Influencer.id
    ).filter(
        InfluencerAdRequest.status == 'approved'
    ).group_by(
        Influencer.id,
        Influencer.username,
        Influencer.profile_picture,
        Influencer.content_category,
        Influencer.platform_name
    ).order_by(
        desc('campaign_count')
    ).limit(limit).all()
    
    result = []
    
    for influencer in top_influencers:
        result.append({
            'id': influencer.id,
            'username': influencer.username,
            'profile_picture': influencer.profile_picture,
            'genre': influencer.content_category,
            'platform': influencer.platform_name,
            'campaign_count': influencer.campaign_count
        })
    
    return result

def get_top_sponsors(limit=5):
    """
    Get top sponsors based on campaign count
    Returns data for a leaderboard
    """
    top_sponsors = db.session.query(
        Sponsor.id,
        Sponsor.company_name,
        Sponsor.logo,
        func.count(Campaign.id).label('campaign_count')
    ).join(
        Campaign, Campaign.sponsor_id == Sponsor.id
    ).group_by(
        Sponsor.id,
        Sponsor.company_name,
        Sponsor.logo
    ).order_by(
        desc('campaign_count')
    ).limit(limit).all()
    
    result = []
    
    for sponsor in top_sponsors:
        result.append({
            'id': sponsor.id,
            'company_name': sponsor.company_name,
            'logo': sponsor.logo,
            'campaign_count': sponsor.campaign_count
        })
    
    return result

def get_monthly_revenue(year=None):
    """
    Calculate monthly revenue from completed campaigns
    Returns data suitable for a bar chart
    """
    if year is None:
        year = datetime.utcnow().year
    
    monthly_revenue = []
    months = []
    
    for month in range(1, 13):
        month_name = calendar.month_abbr[month]
        months.append(month_name)
        
        # Sum the budget of all completed campaigns for this month
        revenue = db.session.query(
            func.sum(Campaign.budget)
        ).filter(
            Campaign.status == 'completed',
            extract('year', Campaign.date_created) == year,
            extract('month', Campaign.date_created) == month
        ).scalar() or 0
        
        monthly_revenue.append(float(revenue))
    
    return {
        'labels': months,
        'data': monthly_revenue
    }

def get_influencer_stats(influencer_id):
    """
    Get comprehensive stats for a specific influencer
    Returns dictionary with multiple data points
    """
    # Get influencer details
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return {'error': 'Influencer not found'}
    
    # Total requests made by the influencer
    total_requests = db.session.query(
        func.count(InfluencerAdRequest.id)
    ).filter(
        InfluencerAdRequest.influencer_id == influencer_id
    ).scalar() or 0
    
    # Approved requests
    approved_requests = db.session.query(
        func.count(InfluencerAdRequest.id)
    ).filter(
        InfluencerAdRequest.influencer_id == influencer_id,
        InfluencerAdRequest.status == 'approved'
    ).scalar() or 0
    
    # Rejected requests
    rejected_requests = db.session.query(
        func.count(InfluencerAdRequest.id)
    ).filter(
        InfluencerAdRequest.influencer_id == influencer_id,
        InfluencerAdRequest.status == 'rejected'
    ).scalar() or 0
    
    # Pending requests
    pending_requests = db.session.query(
        func.count(InfluencerAdRequest.id)
    ).filter(
        InfluencerAdRequest.influencer_id == influencer_id,
        InfluencerAdRequest.status == 'pending'
    ).scalar() or 0
    
    # Calculate acceptance rate
    acceptance_rate = (approved_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Total earnings
    earnings = db.session.query(
        func.sum(Campaign.budget)
    ).join(
        InfluencerAdRequest, InfluencerAdRequest.campaign_id == Campaign.id
    ).filter(
        InfluencerAdRequest.influencer_id == influencer_id,
        InfluencerAdRequest.status == 'approved',
        Campaign.status == 'completed'
    ).scalar() or 0
    
    # Monthly campaign activity for the past year
    today = datetime.utcnow()
    start_date = today - timedelta(days=365)
    
    monthly_activity = db.session.query(
        func.date_trunc('month', InfluencerAdRequest.date_created).label('month'),
        func.count(InfluencerAdRequest.id).label('count')
    ).filter(
        InfluencerAdRequest.influencer_id == influencer_id,
        InfluencerAdRequest.date_created >= start_date,
        InfluencerAdRequest.status == 'approved'
    ).group_by(
        'month'
    ).order_by(
        'month'
    ).all()
    
    # Format for chart.js
    activity_months = [item.month.strftime('%b %Y') for item in monthly_activity]
    activity_counts = [item.count for item in monthly_activity]
    
    return {
        'total_campaigns': total_requests,
        'approved_campaigns': approved_requests,
        'rejected_campaigns': rejected_requests,
        'pending_campaigns': pending_requests,
        'acceptance_rate': round(acceptance_rate, 2),
        'total_earnings': float(earnings),
        'activity_chart': {
            'labels': activity_months,
            'data': activity_counts
        },
        'request_status': {
            'labels': ['Approved', 'Rejected', 'Pending'],
            'data': [approved_requests, rejected_requests, pending_requests]
        }
    }

def get_sponsor_stats(sponsor_id):
    """
    Get comprehensive stats for a specific sponsor
    Returns dictionary with multiple data points
    """
    # Get sponsor details
    sponsor = Sponsor.query.get(sponsor_id)
    if not sponsor:
        return {'error': 'Sponsor not found'}
    
    # Total campaigns created by the sponsor
    total_campaigns = db.session.query(
        func.count(Campaign.id)
    ).filter(
        Campaign.sponsor_id == sponsor_id
    ).scalar() or 0
    
    # Active campaigns
    active_campaigns = db.session.query(
        func.count(Campaign.id)
    ).filter(
        Campaign.sponsor_id == sponsor_id,
        Campaign.status == 'active'
    ).scalar() or 0
    
    # Completed campaigns
    completed_campaigns = db.session.query(
        func.count(Campaign.id)
    ).filter(
        Campaign.sponsor_id == sponsor_id,
        Campaign.status == 'completed'
    ).scalar() or 0
    
    # Pending campaigns
    pending_campaigns = db.session.query(
        func.count(Campaign.id)
    ).filter(
        Campaign.sponsor_id == sponsor_id,
        Campaign.status == 'pending'
    ).scalar() or 0
    
    # Cancelled campaigns
    cancelled_campaigns = db.session.query(
        func.count(Campaign.id)
    ).filter(
        Campaign.sponsor_id == sponsor_id,
        Campaign.status == 'cancelled'
    ).scalar() or 0
    
    # Total requests received across all campaigns
    total_requests = db.session.query(
        func.count(SponsorRequest.id)
    ).join(
        Campaign, SponsorRequest.campaign_id == Campaign.id
    ).filter(
        Campaign.sponsor_id == sponsor_id
    ).scalar() or 0
    
    # Total approved requests
    approved_requests = db.session.query(
        func.count(SponsorRequest.id)
    ).join(
        Campaign, SponsorRequest.campaign_id == Campaign.id
    ).filter(
        Campaign.sponsor_id == sponsor_id,
        SponsorRequest.status == 'approved'
    ).scalar() or 0
    
    # Total budget spent
    total_spent = db.session.query(
        func.sum(Campaign.budget)
    ).filter(
        Campaign.sponsor_id == sponsor_id,
        Campaign.status.in_(['active', 'completed'])
    ).scalar() or 0
    
    # Monthly campaign creation for the past year
    today = datetime.utcnow()
    start_date = today - timedelta(days=365)
    
    monthly_campaigns = db.session.query(
        func.date_trunc('month', Campaign.date_created).label('month'),
        func.count(Campaign.id).label('count')
    ).filter(
        Campaign.sponsor_id == sponsor_id,
        Campaign.date_created >= start_date
    ).group_by(
        'month'
    ).order_by(
        'month'
    ).all()
    
    # Format for chart.js
    campaign_months = [item.month.strftime('%b %Y') for item in monthly_campaigns]
    campaign_counts = [item.count for item in monthly_campaigns]
    
    return {
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'completed_campaigns': completed_campaigns,
        'pending_campaigns': pending_campaigns,
        'cancelled_campaigns': cancelled_campaigns,
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'approval_rate': round((approved_requests / total_requests * 100) if total_requests > 0 else 0, 2),
        'total_spent': float(total_spent),
        'campaign_chart': {
            'labels': campaign_months,
            'data': campaign_counts
        },
        'campaign_status': {
            'labels': ['Active', 'Completed', 'Pending', 'Cancelled'],
            'data': [active_campaigns, completed_campaigns, pending_campaigns, cancelled_campaigns]
        }
    }

def get_admin_dashboard_stats():
    """
    Get comprehensive stats for the admin dashboard
    Returns dictionary with multiple data points
    """
    # Total users
    total_influencers = db.session.query(func.count(Influencer.id)).scalar() or 0
    total_sponsors = db.session.query(func.count(Sponsor.id)).scalar() or 0
    total_users = total_influencers + total_sponsors
    
    # Total campaigns
    total_campaigns = db.session.query(func.count(Campaign.id)).scalar() or 0
    
    # Campaigns by status
    active_campaigns = db.session.query(func.count(Campaign.id)).filter(Campaign.status == 'active').scalar() or 0
    completed_campaigns = db.session.query(func.count(Campaign.id)).filter(Campaign.status == 'completed').scalar() or 0
    pending_campaigns = db.session.query(func.count(Campaign.id)).filter(Campaign.status == 'pending').scalar() or 0
    cancelled_campaigns = db.session.query(func.count(Campaign.id)).filter(Campaign.status == 'cancelled').scalar() or 0
    
    # Total requests
    total_requests = db.session.query(func.count(InfluencerAdRequest.id)).scalar() or 0
    
    # Requests by status
    approved_requests = db.session.query(func.count(InfluencerAdRequest.id)).filter(InfluencerAdRequest.status == 'approved').scalar() or 0
    rejected_requests = db.session.query(func.count(InfluencerAdRequest.id)).filter(InfluencerAdRequest.status == 'rejected').scalar() or 0
    pending_requests = db.session.query(func.count(InfluencerAdRequest.id)).filter(InfluencerAdRequest.status == 'pending').scalar() or 0
    
    # Total platform value
    total_value = db.session.query(func.sum(Campaign.budget)).filter(
        Campaign.status.in_(['active', 'completed'])
    ).scalar() or 0
    
    # New user registrations (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    new_influencers = db.session.query(func.count(Influencer.id)).filter(
        Influencer.date_registered >= week_ago
    ).scalar() or 0
    
    new_sponsors = db.session.query(func.count(Sponsor.id)).filter(
        Sponsor.date_registered >= week_ago
    ).scalar() or 0
    
    # New campaigns (last 7 days)
    new_campaigns = db.session.query(func.count(Campaign.id)).filter(
        Campaign.date_created >= week_ago
    ).scalar() or 0
    
    # Platform growth data
    growth_data = get_platform_growth_data(days=30)
    
    # Campaign success rate
    campaign_success = get_campaign_success_rate()
    
    # Genre distribution
    genre_data = get_genre_distribution()
    
    # Platform distribution
    platform_data = get_platform_distribution()
    
    # Top influencers and sponsors
    top_influencers = get_top_influencers(limit=5)
    top_sponsors = get_top_sponsors(limit=5)
    
    return {
        'total_users': total_users,
        'total_influencers': total_influencers,
        'total_sponsors': total_sponsors,
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'completed_campaigns': completed_campaigns,
        'pending_campaigns': pending_campaigns,
        'cancelled_campaigns': cancelled_campaigns,
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'pending_requests': pending_requests,
        'total_value': float(total_value),
        'new_users': new_influencers + new_sponsors,
        'new_campaigns': new_campaigns,
        'growth_data': growth_data,
        'campaign_status': campaign_success,
        'genre_distribution': genre_data,
        'platform_distribution': platform_data,
        'top_influencers': top_influencers,
        'top_sponsors': top_sponsors
    }

def prepare_chart_data(data):
    """
    Convert data dictionary to JSON string for embedding in HTML data attributes
    """
    return json.dumps(data)

# Add alias functions to match the imports in api.py
def get_influencer_analytics(influencer_id):
    """Alias for get_influencer_stats to match API imports"""
    return get_influencer_stats(influencer_id)

def get_sponsor_analytics(sponsor_id):
    """Alias for get_sponsor_stats to match API imports"""
    return get_sponsor_stats(sponsor_id)