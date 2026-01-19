from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Application(db.Model):
    """Main application model storing job/internship applications."""
    
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Company Info
    company = db.Column(db.String(200), nullable=False)
    company_website = db.Column(db.String(500))
    location = db.Column(db.String(200))
    
    # Position Info
    job_title = db.Column(db.String(200), nullable=False)
    position_level = db.Column(db.String(100), default='Intern')  # Intern, Junior, Mid, Senior
    job_type = db.Column(db.String(50), default='Full-time')  # Full-time, Part-time, Contract
    work_mode = db.Column(db.String(50), default='On-site')  # Remote, Hybrid, On-site
    
    # Requirements
    requirements = db.Column(db.Text)  # Skills and qualifications needed
    
    # Application Details
    job_posting_url = db.Column(db.String(500))
    salary_range = db.Column(db.String(100))
    deadline = db.Column(db.Date)
    date_applied = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(50), default='saved')  # saved, applied, interviewing, offer, rejected, withdrawn
    
    # Tags (stored as comma-separated string)
    tags = db.Column(db.String(500))
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contacts = db.relationship('Contact', backref='application', lazy=True, cascade='all, delete-orphan')
    updates = db.relationship('Update', backref='application', lazy=True, cascade='all, delete-orphan', order_by='desc(Update.created_at)')
    
    def get_tags_list(self):
        """Return tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_list(self, tags_list):
        """Set tags from a list."""
        self.tags = ', '.join(tags_list)
    
    def __repr__(self):
        return f'<Application {self.company} - {self.job_title}>'


class Contact(db.Model):
    """People to connect with for each application."""
    
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200))  # Their job title
    email = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(500))
    phone = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    # Track if you've reached out
    contacted = db.Column(db.Boolean, default=False)
    contacted_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name}>'


class Update(db.Model):
    """Timeline updates for each application."""
    
    __tablename__ = 'updates'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)  # e.g., "Phone Screen Scheduled"
    content = db.Column(db.Text)  # Details about the update
    update_type = db.Column(db.String(50), default='note')  # note, interview, offer, rejection, follow-up
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Update {self.title}>'
