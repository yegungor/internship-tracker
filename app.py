from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from models import db, Application, Contact, Update, AnalysisHistory
from datetime import datetime, date
import csv
import io
import re
import json
from collections import Counter
import PyPDF2  # pip install PyPDF2
import os
import anthropic  # pip install anthropic

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

def extract_text_from_pdf(pdf_file):
    """Extract text content from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.lower()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""


def extract_text_from_pdf(pdf_file):
    """Extract text content from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.lower()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""


def extract_skills_from_text(text):
    """Extract potential skills/keywords from text."""
    # Common tech/business skills to look for
    skill_patterns = [
        # Programming languages
        r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\btypescript\b', r'\bc\+\+\b',
        r'\bc#\b', r'\bruby\b', r'\bgo\b', r'\brust\b', r'\bswift\b', r'\bkotlin\b',
        r'\bphp\b', r'\br\b', r'\bscala\b', r'\bmatlab\b', r'\bjulia\b', r'\bsas\b',
        r'\bstata\b', r'\bspss\b',
        
        # Data & ML
        r'\bsql\b', r'\bnosql\b', r'\bmongodb\b', r'\bpostgresql\b', r'\bmysql\b',
        r'\bpandas\b', r'\bnumpy\b', r'\bscikit-learn\b', r'\btensorflow\b', r'\bpytorch\b',
        r'\bkeras\b', r'\bmachine learning\b', r'\bdeep learning\b', r'\bdata analysis\b',
        r'\bdata science\b', r'\bstatistics\b', r'\beconometrics\b', r'\bcausal inference\b',
        r'\ba/b testing\b', r'\bexperimentation\b', r'\bregression\b', r'\bforecasting\b',
        r'\btime series\b', r'\bnlp\b', r'\bnatural language\b', r'\bcomputer vision\b',
        
        # Cloud & DevOps
        r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bgoogle cloud\b', r'\bdocker\b',
        r'\bkubernetes\b', r'\bci/cd\b', r'\bgit\b', r'\blinux\b', r'\bterraform\b',
        
        # Web & Frameworks
        r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bnode\.js\b', r'\bdjango\b',
        r'\bflask\b', r'\bfastapi\b', r'\bspring\b', r'\brest api\b', r'\bgraphql\b',
        
        # Business & Analytics
        r'\bexcel\b', r'\btableau\b', r'\bpower bi\b', r'\blooker\b', r'\bfinancial modeling\b',
        r'\bfinancial analysis\b', r'\bvaluation\b', r'\baccounting\b', r'\bbudgeting\b',
        r'\bproject management\b', r'\bagile\b', r'\bscrum\b', r'\bjira\b',
        
        # Soft skills
        r'\bcommunication\b', r'\bleadership\b', r'\bteamwork\b', r'\bpresentation\b',
        r'\bproblem solving\b', r'\bcritical thinking\b', r'\banalytical\b',
        
        # Economics specific
        r'\bmicroeconomics\b', r'\bmacroeconomics\b', r'\beconometrics\b',
        r'\bgame theory\b', r'\bbehavioral economics\b', r'\bmarket research\b',
        r'\bpricing\b', r'\bstrategy\b', r'\bconsulting\b',
        
        # Engineering
        r'\bcad\b', r'\bautocad\b', r'\bsolidworks\b', r'\bsimulation\b',
        r'\boptimization\b', r'\boperations research\b', r'\bsupply chain\b',
        r'\blogistics\b', r'\bmanufacturing\b', r'\bquality\b', r'\blean\b',
        r'\bsix sigma\b',
    ]
    
    found_skills = set()
    text_lower = text.lower()
    
    for pattern in skill_patterns:
        if re.search(pattern, text_lower):
            # Clean up the skill name
            skill = pattern.replace(r'\b', '').replace('\\', '')
            skill = skill.replace('+', ' plus').replace('.', ' ')
            found_skills.add(skill.strip())
    
    return found_skills


def tokenize_text(text):
    """Simple tokenization for word frequency."""
    # Remove special characters, keep alphanumeric
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    words = text.split()
    
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'what', 'which', 'who', 'whom', 'where', 'when', 'why',
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'not', 'only', 'own', 'same', 'so', 'than',
        'too', 'very', 'just', 'also', 'now', 'here', 'there', 'then',
        'about', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'between', 'under', 'again', 'further', 'once', 'our',
        'your', 'their', 'its', 'any', 'etc', 'eg', 'ie', 'vs', 'via',
        'ability', 'able', 'experience', 'work', 'working', 'job', 'role',
        'team', 'company', 'position', 'candidate', 'required', 'requirements',
        'including', 'include', 'includes', 'preferred', 'plus', 'strong',
        'excellent', 'good', 'great', 'best', 'new', 'well', 'years', 'year'
    }
    
    return [w for w in words if len(w) > 2 and w not in stop_words]


def calculate_match_score(resume_skills, job_skills):
    """Calculate percentage match between resume and job skills."""
    if not job_skills:
        return 0, [], []
    
    matched = resume_skills.intersection(job_skills)
    missing = job_skills - resume_skills
    
    score = int(len(matched) / len(job_skills) * 100) if job_skills else 0
    
    return score, list(matched), list(missing)
    
def analyze_with_llm(resume_text, jobs_data):
    """
    Use Claude to analyze resume against jobs.
    Returns detailed analysis with semantic matching.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return None, "ANTHROPIC_API_KEY environment variable not set"
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Build job descriptions summary
    jobs_summary = ""
    for i, job in enumerate(jobs_data, 1):
        jobs_summary += f"""
### Job {i}: {job['company']} - {job['job_title']}
Requirements: {job['requirements']}
Tags: {job['tags']}
---
"""
    
    prompt = f"""You are an expert career advisor and ATS (Applicant Tracking System) analyst. 
Analyze how well this resume matches the following job positions.

## RESUME:
{resume_text[:8000]}

## JOB POSITIONS TO ANALYZE:
{jobs_summary}

## YOUR TASK:
Provide a comprehensive analysis in the following JSON format (respond ONLY with valid JSON, no markdown):

{{
    "overall_summary": "2-3 sentence overview of the candidate's fit across all positions",
    "resume_strengths": ["strength1", "strength2", "strength3"],
    "resume_weaknesses": ["weakness1", "weakness2"],
    "top_skills_from_resume": ["skill1", "skill2", "skill3", "skill4", "skill5"],
    "job_analyses": [
        {{
            "company": "Company Name",
            "job_title": "Job Title",
            "match_score": 75,
            "match_level": "Strong Match",
            "matched_skills": ["skill1", "skill2"],
            "missing_skills": ["skill1", "skill2"],
            "transferable_skills": ["skill from resume that applies but wasn't explicitly listed"],
            "recommendations": "Specific advice to improve match for this role",
            "key_insight": "One unique observation about fit"
        }}
    ],
    "general_recommendations": [
        "Actionable advice 1 to improve resume",
        "Actionable advice 2",
        "Actionable advice 3"
    ],
    "skills_to_learn": ["High-priority skill 1", "Skill 2", "Skill 3"],
    "strongest_match": {{
        "company": "Best matching company",
        "job_title": "Best matching job",
        "why": "Brief explanation"
    }}
}}

IMPORTANT:
- Match scores should be 0-100 based on realistic ATS scoring
- Be specific and actionable in recommendations
- Identify transferable skills the ATS might miss
- Consider both hard skills and soft skills
- Match level should be: "Excellent Match" (80+), "Strong Match" (60-79), "Moderate Match" (40-59), "Weak Match" (<40)
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            temperature=0.5,  # (lower = more consistent)
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON response
        import json
        # Clean up response if needed
        response_text = response_text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        analysis = json.loads(response_text)
        return analysis, None
        
    except anthropic.APIError as e:
        return None, f"API Error: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"Failed to parse response: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"

    
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

@app.route('/analysis')
def analysis():
    """Analysis page for resume matching."""
    return render_template('analysis.html')


@app.route('/api/jobs')
def api_jobs():
    """Return list of all jobs for selection."""
    apps = Application.query.order_by(Application.updated_at.desc()).all()
    return jsonify([{
        'id': app.id,
        'company': app.company,
        'job_title': app.job_title,
        'status': app.status
    } for app in apps])


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze resume against selected job applications."""
    try:
        # Get uploaded resume
        resume_file = request.files.get('resume')
        cover_letter_file = request.files.get('cover_letter')
        job_ids_json = request.form.get('job_ids', '[]')
        
        if not resume_file:
            return jsonify({'success': False, 'error': 'No resume uploaded'})
        
        # Parse job IDs
        try:
            job_ids = json.loads(job_ids_json)
        except:
            job_ids = []
        
        # Extract text from resume
        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text:
            return jsonify({'success': False, 'error': 'Could not extract text from resume'})
        
        # Extract text from cover letter if provided
        cover_letter_text = ""
        if cover_letter_file:
            cover_letter_text = extract_text_from_pdf(cover_letter_file)
        
        # Combine resume and cover letter for analysis
        combined_text = resume_text + " " + cover_letter_text
        
        # Extract skills from resume
        resume_skills = extract_skills_from_text(combined_text)
        
        # Get selected applications
        if job_ids:
            apps = Application.query.filter(Application.id.in_(job_ids)).all()
        else:
            apps = Application.query.all()
        
        if not apps:
            return jsonify({
                'success': False, 
                'error': 'No applications found'
            })
        
        # Analyze each job
        job_results = []
        all_job_skills = Counter()
        all_matched_skills = set()
        all_missing_skills = set()
        total_score = 0
        
        all_job_words = []
        
        for app_entry in apps:
            # Combine job requirements and notes for analysis
            job_text = f"{app_entry.requirements or ''} {app_entry.job_title or ''} {app_entry.tags or ''}"
            job_skills = extract_skills_from_text(job_text)
            
            # Count skill frequency across all jobs
            for skill in job_skills:
                all_job_skills[skill] += 1
            
            # Calculate match
            score, matched, missing = calculate_match_score(resume_skills, job_skills)
            total_score += score
            
            all_matched_skills.update(matched)
            all_missing_skills.update(missing)
            
            # Tokenize for word cloud
            all_job_words.extend(tokenize_text(job_text))
            
            job_results.append({
                'id': app_entry.id,
                'company': app_entry.company,
                'job_title': app_entry.job_title,
                'match_score': score,
                'matched_keywords': matched,
                'missing_keywords': missing
            })
        
        # Sort by match score (highest first)
        job_results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Calculate averages
        avg_match = int(total_score / len(apps)) if apps else 0
        
        # Get top skills (most requested)
        top_skills = []
        max_count = max(all_job_skills.values()) if all_job_skills else 1
        for skill, count in all_job_skills.most_common(15):
            top_skills.append({
                'name': skill,
                'count': count,
                'percentage': int(count / max_count * 100)
            })
        
        # Word frequency for word cloud
        word_counts = Counter(all_job_words)
        word_frequency = [
            {'word': word, 'count': count}
            for word, count in word_counts.most_common(40)
        ]
        
        return jsonify({
            'success': True,
            'jobs_analyzed': len(apps),
            'avg_match_score': avg_match,
            'total_skills_matched': len(all_matched_skills),
            'total_skills_missing': len(all_missing_skills - all_matched_skills),
            'top_skills': top_skills,
            'matched_skills': list(all_matched_skills),
            'missing_skills': list(all_missing_skills - all_matched_skills)[:20],
            'job_results': job_results,
            'word_frequency': word_frequency
        })
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check-llm')
def check_llm_available():
    """Check if LLM API key is configured."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    return jsonify({
        'available': bool(api_key),
        'message': 'API key configured' if api_key else 'Set ANTHROPIC_API_KEY environment variable'
    })


@app.route('/api/analyze-llm', methods=['POST'])
def api_analyze_llm():
    """Analyze resume using Claude LLM for semantic matching."""
    try:
        # Check API key
        if not os.environ.get('ANTHROPIC_API_KEY'):
            return jsonify({
                'success': False, 
                'error': 'ANTHROPIC_API_KEY not configured. Set it in your environment variables.'
            })
        
        # Get uploaded resume
        resume_file = request.files.get('resume')
        cover_letter_file = request.files.get('cover_letter')
        job_ids_json = request.form.get('job_ids', '[]')
        
        if not resume_file:
            return jsonify({'success': False, 'error': 'No resume uploaded'})
        
        # Parse job IDs
        try:
            job_ids = json.loads(job_ids_json)
        except:
            job_ids = []
        
        # Extract text from resume
        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text:
            return jsonify({'success': False, 'error': 'Could not extract text from resume'})
        
        # Add cover letter if provided
        if cover_letter_file:
            cover_letter_text = extract_text_from_pdf(cover_letter_file)
            resume_text += "\n\nCOVER LETTER:\n" + cover_letter_text
        
        # Get selected applications
        if job_ids:
            apps = Application.query.filter(Application.id.in_(job_ids)).all()
        else:
            apps = Application.query.all()
        
        if not apps:
            return jsonify({'success': False, 'error': 'No applications found'})
        
        # Prepare jobs data
        jobs_data = [{
            'id': app.id,
            'company': app.company,
            'job_title': app.job_title,
            'requirements': app.requirements or '',
            'tags': app.tags or ''
        } for app in apps]
        
        # Run LLM analysis
        analysis, error = analyze_with_llm(resume_text, jobs_data)
        
        if error:
            return jsonify({'success': False, 'error': error})
        
        # Add job IDs to analysis results
        for i, job_analysis in enumerate(analysis.get('job_analyses', [])):
            if i < len(apps):
                job_analysis['id'] = apps[i].id
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'jobs_analyzed': len(apps)
        })
        
    except Exception as e:
        print(f"LLM Analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/history')
def analysis_history():
    """View analysis history."""
    analyses = AnalysisHistory.query.order_by(AnalysisHistory.created_at.desc()).all()
    return render_template('history.html', analyses=analyses)


@app.route('/history/<int:id>')
def view_analysis(id):
    """View a specific past analysis."""
    analysis = AnalysisHistory.query.get_or_404(id)
    results = json.loads(analysis.full_results) if analysis.full_results else {}
    job_ids = json.loads(analysis.job_ids) if analysis.job_ids else []
    
    # Get the jobs that were analyzed
    jobs = Application.query.filter(Application.id.in_(job_ids)).all() if job_ids else []
    
    return render_template('view_analysis.html', analysis=analysis, results=results, jobs=jobs)


@app.route('/history/<int:id>/delete', methods=['POST'])
def delete_analysis(id):
    """Delete an analysis from history."""
    analysis = AnalysisHistory.query.get_or_404(id)
    db.session.delete(analysis)
    db.session.commit()
    flash('Analysis deleted.', 'info')
    return redirect(url_for('analysis_history'))


@app.route('/api/save-analysis', methods=['POST'])
def save_analysis():
    """Save analysis results to history."""
    try:
        data = request.json
        
        analysis = AnalysisHistory(
            resume_name=data.get('resume_name', 'Unknown'),
            cover_letter_name=data.get('cover_letter_name'),
            analysis_type=data.get('analysis_type', 'ats'),
            jobs_analyzed=data.get('jobs_analyzed', 0),
            job_ids=json.dumps(data.get('job_ids', [])),
            avg_match_score=data.get('avg_match_score', 0),
            total_skills_matched=data.get('total_skills_matched', 0),
            total_skills_missing=data.get('total_skills_missing', 0),
            full_results=json.dumps(data.get('full_results', {})),
            overall_summary=data.get('overall_summary'),
            best_match_company=data.get('best_match_company'),
            best_match_title=data.get('best_match_title')
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({'success': True, 'id': analysis.id})
    except Exception as e:
        print(f"Save analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/compare-analyses', methods=['POST'])
def compare_analyses():
    """Compare two analyses."""
    try:
        data = request.json
        id1 = data.get('id1')
        id2 = data.get('id2')
        
        analysis1 = AnalysisHistory.query.get_or_404(id1)
        analysis2 = AnalysisHistory.query.get_or_404(id2)
        
        results1 = json.loads(analysis1.full_results) if analysis1.full_results else {}
        results2 = json.loads(analysis2.full_results) if analysis2.full_results else {}
        
        # Calculate improvements
        score_change = analysis2.avg_match_score - analysis1.avg_match_score
        skills_change = analysis2.total_skills_matched - analysis1.total_skills_matched
        
        return jsonify({
            'success': True,
            'comparison': {
                'analysis1': {
                    'id': analysis1.id,
                    'date': analysis1.created_at.isoformat(),
                    'resume_name': analysis1.resume_name,
                    'avg_score': analysis1.avg_match_score,
                    'skills_matched': analysis1.total_skills_matched
                },
                'analysis2': {
                    'id': analysis2.id,
                    'date': analysis2.created_at.isoformat(),
                    'resume_name': analysis2.resume_name,
                    'avg_score': analysis2.avg_match_score,
                    'skills_matched': analysis2.total_skills_matched
                },
                'score_change': score_change,
                'skills_change': skills_change,
                'improved': score_change > 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


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
