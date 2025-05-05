# InfluConnect: Influencer Engagement and Sponsorship Platform 🚀

InfluConnect is a comprehensive web application that bridges the gap between influencers and sponsors, enabling efficient collaboration for marketing campaigns across various social media platforms.

![InfluConnect Homepage](static/Images/home.png)

## 📋 Overview

This platform facilitates seamless connections between content creators and brands, streamlining the process of campaign creation, negotiation, and performance tracking. The application serves three distinct user roles: Influencers, Sponsors, and Administrators.

## ✨ Key Features

### 🎬 For Influencers
- **Profile Management**: Create and customize your professional profile with portfolio showcases
- **Campaign Discovery**: Browse and filter available sponsorship opportunities
- **Direct Requests**: Submit applications to participate in brand campaigns
- **Campaign Management**: Track active campaigns, submission status, and payment information
- **Analytics Dashboard**: Monitor performance metrics and audience engagement statistics

### 💼 For Sponsors
- **Brand Profile**: Establish your company identity and sponsorship objectives
- **Campaign Creation**: Design and launch customized marketing campaigns
- **Influencer Discovery**: Search and filter influencers by platform, niche, and audience metrics
- **Request Management**: Review influencer applications and send direct collaboration invitations
- **Performance Tracking**: Access real-time analytics on campaign performance and ROI

### 🔧 For Administrators
- **Platform Oversight**: Monitor and manage all platform activities
- **User Management**: Review and approve user registrations and handle flags
- **Content Moderation**: Ensure all content adheres to platform guidelines
- **Analytics**: Access comprehensive platform usage statistics

## 🛠️ Technical Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML, CSS, JavaScript (with Chart.js for analytics)
- **Authentication**: Flask-Bcrypt for password hashing
- **Form Handling**: Flask-WTF
- **API Support**: Flask-RESTful and Flask-Cors
- **File Uploads**: Werkzeug and Pillow for image processing

## 📦 Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/influencer-engagement-platform.git
   cd influencer-engagement-platform
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   python init_new_db.py
   ```

5. Create an admin user:
   ```
   python create_admin.py
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Access the application in your web browser at `http://localhost:5000`

## 📂 Project Structure

```
influencer-engagement-platform/
├── app.py                 # Main application entry point
├── models.py              # Database models
├── routes.py              # Web routes and view functions
├── api.py                 # API endpoints
├── db.py                  # Database configuration
├── config.py              # Application configuration
├── requirements.txt       # Project dependencies
├── static/                # CSS, JavaScript, and image files
├── templates/             # HTML templates
├── utils/                 # Utility functions
│   ├── analytics.py       # Analytics processing
│   ├── notifications.py   # Notification system
│   └── security.py        # Authentication and authorization
├── instance/              # Instance-specific configuration
└── logs/                  # Application logs
```

## 👥 User Roles and Workflows

### 🎬 Influencer Workflow
1. Register and create a profile
2. Browse available campaigns
3. Submit requests to participate in campaigns
4. Manage active campaigns and track earnings
5. Monitor performance analytics

### 💼 Sponsor Workflow
1. Register and create company profile
2. Create and publish campaigns
3. Review influencer applications
4. Send direct collaboration requests
5. Monitor campaign performance and ROI

### 🔧 Admin Workflow
1. Manage user registrations and flags
2. Oversee campaign approvals
3. Monitor platform usage and analytics
4. Manage system settings and configurations

## 🔒 Security Features

- Password hashing with bcrypt
- CSRF protection
- Secure session management
- Role-based access control
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, email support@influconnect.com or open an issue in the GitHub repository.
