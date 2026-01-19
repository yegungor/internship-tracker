from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from models import db, Application, Contact, Update
from datetime import datetime, date
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables on first run
with app.app_context():
    db.create_all()


# ============== HELPER FUNCTIONS ==============

def get_statistics():
    """Calculate dashboard statistics."""
    total = Application.query.count()
    saved = Application.query.filter_by(status='saved').count()
    applied = Application.query.filter_by(status='applied').count()
    interviewing = Application.query.filter_by(status='interviewing').count()
    offers = Application.query.filter_by(status='offer').count()
    rejected = Application.query.filter_by(status='rejected').count()
    
    # Response rate (interviews / applied)
    total_applied = applied + interviewing + offers + rejected
    response_rate = round((interviewing + offers) / total_applied * 100, 1) if total_applied > 0 else 0
    
    return {
        'total': total,
        'saved': saved,
        'applied': applied,
        'interviewing': interviewing,
        'offers': offers,
        'rejected': rejected,
        'response_rate': response_rate
    }


# ============== ROUTES ==============

@app.route('/')
def index():
    """Dashboard with statistics and recent applications."""
    stats = get_statistics()
    recent = Application.query.order_by(Application.updated_at.desc()).limit(5).all()
    
    # Get upcoming deadlines
    today = date.today()
    upcoming_deadlines = Application.query.filter(
        Application.deadline >= today,
        Application.status.in_(['saved', 'applied'])
    ).order_by(Application.deadline).limit(5).all()
    
    return render_template('index.html', 
                         stats=stats, 
                         recent=recent,
                         upcoming_deadlines=upcoming_deadlines)


@app.route('/applications')
def applications():
    """List all applications with filtering."""
    # Get filter parameters
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'updated_at')
    sort_order = request.args.get('order', 'desc')
    
    # Build query
    query = Application.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search_query:
        search = f'%{search_query}%'
        query = query.filter(
            db.or_(
                Application.company.ilike(search),
                Application.job_title.ilike(search),
                Application.tags.ilike(search)
            )
        )
    
    # Sort
    sort_column = getattr(Application, sort_by, Application.updated_at)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    apps = query.all()
    
    return render_template('applications.html', 
                         applications=apps,
                         status_filter=status_filter,
                         search_query=search_query,
                         sort_by=sort_by,
                         sort_order=sort_order)


@app.route('/application/add', methods=['GET', 'POST'])
def add_application():
    """Add a new application."""
    if request.method == 'POST':
        # Parse deadline if provided
        deadline = None
        if request.form.get('deadline'):
            deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
        
        # Parse date_applied if provided
        date_applied = None
        if request.form.get('date_applied'):
            date_applied = datetime.strptime(request.form['date_applied'], '%Y-%m-%d').date()
        
        app_entry = Application(
            company=request.form['company'],
            company_website=request.form.get('company_website', ''),
            location=request.form.get('location', ''),
            job_title=request.form['job_title'],
            position_level=request.form.get('position_level', 'Intern'),
            job_type=request.form.get('job_type', 'Full-time'),
            work_mode=request.form.get('work_mode', 'On-site'),
            requirements=request.form.get('requirements', ''),
            job_posting_url=request.form.get('job_posting_url', ''),
            salary_range=request.form.get('salary_range', ''),
            deadline=deadline,
            date_applied=date_applied,
            status=request.form.get('status', 'saved'),
            tags=request.form.get('tags', ''),
            notes=request.form.get('notes', '')
        )
        
        db.session.add(app_entry)
        db.session.commit()
        
        flash('Application added successfully!', 'success')
        return redirect(url_for('view_application', id=app_entry.id))
    
    return render_template('add.html')


@app.route('/application/<int:id>')
def view_application(id):
    """View a single application with all details."""
    app_entry = Application.query.get_or_404(id)
    return render_template('view.html', app=app_entry)


@app.route('/application/<int:id>/edit', methods=['GET', 'POST'])
def edit_application(id):
    """Edit an existing application."""
    app_entry = Application.query.get_or_404(id)
    
    if request.method == 'POST':
        app_entry.company = request.form['company']
        app_entry.company_website = request.form.get('company_website', '')
        app_entry.location = request.form.get('location', '')
        app_entry.job_title = request.form['job_title']
        app_entry.position_level = request.form.get('position_level', 'Intern')
        app_entry.job_type = request.form.get('job_type', 'Full-time')
        app_entry.work_mode = request.form.get('work_mode', 'On-site')
        app_entry.requirements = request.form.get('requirements', '')
        app_entry.job_posting_url = request.form.get('job_posting_url', '')
        app_entry.salary_range = request.form.get('salary_range', '')
        app_entry.status = request.form.get('status', 'saved')
        app_entry.tags = request.form.get('tags', '')
        app_entry.notes = request.form.get('notes', '')
        
        if request.form.get('deadline'):
            app_entry.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
        else:
            app_entry.deadline = None
            
        if request.form.get('date_applied'):
            app_entry.date_applied = datetime.strptime(request.form['date_applied'], '%Y-%m-%d').date()
        else:
            app_entry.date_applied = None
        
        db.session.commit()
        flash('Application updated successfully!', 'success')
        return redirect(url_for('view_application', id=id))
    
    return render_template('edit.html', app=app_entry)


@app.route('/application/<int:id>/delete', methods=['POST'])
def delete_application(id):
    """Delete an application."""
    app_entry = Application.query.get_or_404(id)
    db.session.delete(app_entry)
    db.session.commit()
    flash('Application deleted.', 'info')
    return redirect(url_for('applications'))


@app.route('/application/<int:id>/status', methods=['POST'])
def update_status(id):
    """Quick status update via AJAX."""
    app_entry = Application.query.get_or_404(id)
    new_status = request.json.get('status')
    
    if new_status in ['saved', 'applied', 'interviewing', 'offer', 'rejected', 'withdrawn']:
        app_entry.status = new_status
        
        # Auto-set date_applied when status changes to applied
        if new_status == 'applied' and not app_entry.date_applied:
            app_entry.date_applied = date.today()
        
        db.session.commit()
        return jsonify({'success': True, 'status': new_status})
    
    return jsonify({'success': False, 'error': 'Invalid status'}), 400


# ============== CONTACTS ==============

@app.route('/application/<int:id>/contact/add', methods=['POST'])
def add_contact(id):
    """Add a contact to an application."""
    app_entry = Application.query.get_or_404(id)
    
    contact = Contact(
        application_id=id,
        name=request.form['name'],
        title=request.form.get('title', ''),
        email=request.form.get('email', ''),
        linkedin_url=request.form.get('linkedin_url', ''),
        phone=request.form.get('phone', ''),
        notes=request.form.get('notes', '')
    )
    
    db.session.add(contact)
    db.session.commit()
    flash('Contact added!', 'success')
    return redirect(url_for('view_application', id=id))


@app.route('/contact/<int:id>/toggle', methods=['POST'])
def toggle_contact(id):
    """Toggle contacted status."""
    contact = Contact.query.get_or_404(id)
    contact.contacted = not contact.contacted
    if contact.contacted:
        contact.contacted_date = date.today()
    else:
        contact.contacted_date = None
    db.session.commit()
    return jsonify({'success': True, 'contacted': contact.contacted})


@app.route('/contact/<int:id>/delete', methods=['POST'])
def delete_contact(id):
    """Delete a contact."""
    contact = Contact.query.get_or_404(id)
    app_id = contact.application_id
    db.session.delete(contact)
    db.session.commit()
    flash('Contact removed.', 'info')
    return redirect(url_for('view_application', id=app_id))


# ============== UPDATES ==============

@app.route('/application/<int:id>/update/add', methods=['POST'])
def add_update(id):
    """Add an update to an application."""
    app_entry = Application.query.get_or_404(id)
    
    update = Update(
        application_id=id,
        title=request.form['title'],
        content=request.form.get('content', ''),
        update_type=request.form.get('update_type', 'note')
    )
    
    db.session.add(update)
    db.session.commit()
    flash('Update added!', 'success')
    return redirect(url_for('view_application', id=id))


@app.route('/update/<int:id>/delete', methods=['POST'])
def delete_update(id):
    """Delete an update."""
    update = Update.query.get_or_404(id)
    app_id = update.application_id
    db.session.delete(update)
    db.session.commit()
    flash('Update removed.', 'info')
    return redirect(url_for('view_application', id=app_id))


# ============== EXPORT ==============

@app.route('/export/csv')
def export_csv():
    """Export all applications to CSV."""
    applications = Application.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow([
        'Company', 'Job Title', 'Position Level', 'Location', 'Work Mode',
        'Status', 'Date Applied', 'Deadline', 'Requirements', 'Tags', 'Notes',
        'Job URL', 'Salary Range', 'Created', 'Updated'
    ])
    
    # Data rows
    for app in applications:
        writer.writerow([
            app.company,
            app.job_title,
            app.position_level,
            app.location,
            app.work_mode,
            app.status,
            app.date_applied.isoformat() if app.date_applied else '',
            app.deadline.isoformat() if app.deadline else '',
            app.requirements,
            app.tags,
            app.notes,
            app.job_posting_url,
            app.salary_range,
            app.created_at.isoformat(),
            app.updated_at.isoformat()
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=applications_export.csv'}
    )


# ============== API FOR CHARTS ==============

@app.route('/api/stats')
def api_stats():
    """Return statistics for charts."""
    stats = get_statistics()
    
    # Monthly application counts (last 6 months)
    # This is a simplified version - could be expanded
    
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True, port = 1453)
