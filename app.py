"""Resume Filter Web Application

Main Flask app for resume-to-job matching with AI-powered filtering.
"""
from flask import Flask, render_template, request, jsonify, session, redirect
from werkzeug.utils import secure_filename
import os
from datetime import timedelta

from utils.job_matcher import fetch_jobs_from_api, match_resume_to_jobs

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def build_resume_data(form):
    """Build a normalized resume payload from submitted form data."""
    resume_text = form.get('resume_text', '').strip()
    if resume_text:
        skills = form.get('skills', '')
        return {
            'source': 'text',
            'content': resume_text,
            'skills': [skill.strip() for skill in skills.split(',') if skill.strip()]
        }

    skills = [skill.strip() for skill in form.get('skills', '').split(',') if skill.strip()]
    return {
        'source': 'form',
        'name': form.get('full_name', '').strip(),
        'email': form.get('email', '').strip(),
        'phone': form.get('phone', '').strip(),
        'location': form.get('location', '').strip(),
        'summary': form.get('summary', '').strip(),
        'skills': skills,
        'preferred_location': form.get('pref_location', '').strip() or form.get('preferredLocation', '').strip(),
        'minimum_salary': form.get('min_salary', '').strip(),
    }


def generate_job_matches(resume_data):
    """Build a simple job feed based on resume keywords."""
    jobs = [
        {
            'id': 1,
            'title': 'Python Software Engineer',
            'company': 'TechWave',
            'location': 'Remote',
            'salary': '$110k - $130k',
            'description': 'Build scalable backend services using Python, APIs, and cloud best practices.',
        },
        {
            'id': 2,
            'title': 'Frontend Engineer',
            'company': 'BrightUI',
            'location': 'San Francisco, CA',
            'salary': '$95k - $115k',
            'description': 'Create responsive web experiences with React and modern frontend tooling.',
        },
        {
            'id': 3,
            'title': 'Data Analyst',
            'company': 'InsightWorks',
            'location': 'New York, NY',
            'salary': '$85k - $105k',
            'description': 'Analyze business metrics and generate insights using SQL and Python.',
        },
        {
            'id': 4,
            'title': 'Product Manager',
            'company': 'GoLaunch',
            'location': 'Remote',
            'salary': '$100k - $125k',
            'description': 'Define product priorities and collaborate with engineering, design, and marketing teams.',
        },
    ]

    skills = resume_data.get('skills', []) or []
    if isinstance(skills, str):
        skills = [skill.strip() for skill in skills.split(',') if skill.strip()]
    skill_set = {skill.lower() for skill in skills}

    for job in jobs:
        score = 60
        title = job['title'].lower()
        if 'python' in skill_set and 'python' in title:
            score += 20
        if 'react' in skill_set and 'frontend' in title:
            score += 15
        if 'data' in skill_set and 'data' in title:
            score += 15
        if 'product' in skill_set and 'product' in title:
            score += 15
        if 'remote' in resume_data.get('preferred_location', '').lower() and 'remote' in job['location'].lower():
            score += 5
        job['match_score'] = min(score, 100)

    return sorted(jobs, key=lambda item: item['match_score'], reverse=True)


@app.route('/')
def home():
    """Landing page - choose resume upload or create from scratch."""
    return render_template('index.html')


@app.route('/upload')
def upload():
    """Upload existing resume page."""
    return render_template('upload.html')


@app.route('/create')
def create():
    """Create resume from scratch page."""
    return render_template('create.html')


@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    """Parse uploaded resume or created resume data."""
    resume_data = {}

    if 'resume' in request.files and request.files['resume'].filename:
        resume_file = request.files['resume']
        filename = secure_filename(resume_file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(save_path)
        resume_data = {
            'source': 'file',
            'filename': filename,
            'content': f'Uploaded resume file: {filename}',
            'skills': []
        }
    else:
        resume_data = build_resume_data(request.form)

    session['resume_data'] = resume_data
    session.modified = True
    return jsonify({'status': 'ok', 'resume_data': resume_data})


@app.route('/jobs')
def jobs():
    """Display filtered job listings based on resume."""
    if 'resume_data' not in session:
        return redirect('/')
    return render_template('jobs.html')


@app.route('/api/match-jobs', methods=['POST'])
def match_jobs():
    """Use live API data to match resume against job listings."""
    resume_data = session.get('resume_data')
    if not resume_data:
        return jsonify({'jobs': [], 'matches': []})

    criteria = {
        'keywords': resume_data.get('skills', []),
        'preferred_location': resume_data.get('preferred_location') or resume_data.get('location') or '',
    }
    jobs = fetch_jobs_from_api(criteria)
    jobs = match_resume_to_jobs(resume_data, jobs)
    return jsonify({'jobs': jobs, 'matches': [job.get('match_score', 0) for job in jobs]})


@app.route('/api/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """Generate cover letter using resume + job description."""
    # TODO: AI-powered cover letter generation
    return jsonify({'cover_letter': ''})


@app.route('/api/save-job', methods=['POST'])
def save_job():
    """Save job to favorites."""
    # TODO: Store in session-based favorites
    return jsonify({'status': 'saved'})


@app.route('/favorites')
def favorites():
    """View saved/favorite jobs."""
    return render_template('favorites.html')


if __name__ == '__main__':
    app.run(debug=True)
