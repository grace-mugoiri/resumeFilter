"""Resume Filter Web Application

Main Flask app for resume-to-job matching with AI-powered filtering.
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
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


@app.route('/')
def home():
    """Landing page - choose resume upload or create from scratch."""
    return render_template('index.html')


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

    return resume_data


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

    # Store in session for backward compatibility, but also save to DB if user is logged in
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

    # Store matched jobs in session for cover letter generation
    session['matched_jobs'] = jobs
    session.modified = True

    return jsonify({'jobs': jobs, 'matches': [job.get('match_score', 0) for job in jobs]})


@app.route('/api/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """Generate cover letter using resume + job description."""
    data = request.get_json()
    job_id = data.get('job_id')
    resume_data = session.get('resume_data')

    if not resume_data or not job_id:
        return jsonify({'error': 'Missing resume data or job ID'}), 400

    # Get job details from the matched jobs in session
    matched_jobs = session.get('matched_jobs', [])
    job_data = None
    for job in matched_jobs:
        if str(job.get('id')) == str(job_id):
            job_data = job
            break

    # Generate cover letter
    cover_letter = generate_cover_letter_content(resume_data, job_data or {})

    # Return as downloadable file
    from flask import send_file
    import io

    # Create an in-memory file
    file_obj = io.BytesIO(cover_letter.encode('utf-8'))
    file_obj.seek(0)

    return send_file(
        file_obj,
        mimetype='text/plain',
        as_attachment=True,
        download_name=f'cover_letter_{job_id}.txt'
    )


def generate_cover_letter_content(resume_data, job_data):
    """Generate a simple cover letter based on resume and job data."""
    name = resume_data.get('name', 'Applicant')
    skills = resume_data.get('skills', [])
    if isinstance(skills, str):
        skills = [skill.strip() for skill in skills.split(',') if skill.strip()]

    # Use actual job data
    job_title = job_data.get('title', 'Software Engineer')
    company_name = job_data.get('company', 'Tech Company')

    # Simple cover letter template
    cover_letter = f"""[Your Name]
[Your Address]
[City, State, ZIP Code]
[Email Address]
[Phone Number]
[Date]

Hiring Manager
{company_name}
[Company Address]
[City, State, ZIP Code]

Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With my background in {', '.join(skills[:3]) if skills else 'various technologies'}, I am excited about the opportunity to contribute to your innovative team.

My experience includes working with {', '.join(skills) if skills else 'relevant technologies'}, and I am confident that my skills and passion for technology would make me a valuable addition to your organization.

I would welcome the opportunity to discuss how my background, skills, and enthusiasm can contribute to {company_name}'s continued success.

Thank you for considering my application. I look forward to the possibility of speaking with you soon.

Sincerely,
{name}
"""

    return cover_letter



@app.route('/api/save-job', methods=['POST'])
def save_job():
    """Save job to favorites."""
    data = request.get_json()
    job_id = data.get('job_id')
    job_title = data.get('job_title')
    company = data.get('company')
    location = data.get('location')
    salary = data.get('salary')
    description = data.get('description')
    url = data.get('url')
    source = data.get('source')

    # Get current favorites from session
    favorites = session.get('favorites', [])

    # Check if already saved
    for fav in favorites:
        if fav.get('job_id') == job_id:
            return jsonify({'status': 'already_saved'})

    # Save to session
    favorite = {
        'job_id': job_id,
        'job_title': job_title,
        'company': company,
        'location': location,
        'salary': salary,
        'description': description,
        'url': url,
        'source': source
    }
    favorites.append(favorite)
    session['favorites'] = favorites
    session.modified = True

    return jsonify({'status': 'saved'})


@app.route('/favorites')
def favorites():
    """View saved/favorite jobs."""
    favorite_jobs = session.get('favorites', [])
    return render_template('favorites.html', favorites=favorite_jobs)


if __name__ == '__main__':
    app.run(debug=True)
