"""Job matching and filtering utilities."""

import requests


def fetch_jobs_from_api(criteria):
    """
    Fetch live job listings from a public job API.

    Args:
        criteria: dict with keywords, preferred_location, and optional salary.

    Returns:
        list of normalized job objects
    """
    search_terms = criteria.get('search') or criteria.get('keywords') or criteria.get('query') or ''
    if isinstance(search_terms, list):
        search_terms = ' '.join(search_terms)
    search_terms = search_terms.strip() or 'developer'

    try:
        response = requests.get(
            'https://www.arbeitnow.com/api/job-board-api',
            params={'search': search_terms},
            timeout=12,
        )
        response.raise_for_status()
        raw_jobs = response.json().get('data', [])
    except requests.RequestException:
        raw_jobs = []

    jobs = []
    for index, raw in enumerate(raw_jobs):
        job_types = raw.get('job_types') or []
        salary = ', '.join(job_types) if job_types else ('Remote' if raw.get('remote') else 'N/A')
        description = raw.get('description', '') or ''
        description = description.replace('\n', ' ').strip()
        if len(description) > 320:
            description = description[:317].rstrip() + '...'

        jobs.append({
            'id': raw.get('slug') or f'job-{index}',
            'title': raw.get('title', 'Unknown Title'),
            'company': raw.get('company_name', 'Unknown Company'),
            'location': raw.get('location', 'Remote') or ('Remote' if raw.get('remote') else 'Unknown'),
            'salary': salary,
            'description': description,
            'url': raw.get('url'),
            'tags': raw.get('tags', []),
            'remote': raw.get('remote', False),
            'created_at': raw.get('created_at', ''),
        })

    return jobs


def match_resume_to_jobs(resume_data, jobs, top_n=15):
    """
    Rank live jobs based on resume data.

    Returns:
        Ranked list of jobs with a match_score field.
    """
    skills = resume_data.get('skills', []) or []
    if isinstance(skills, str):
        skills = [skill.strip() for skill in skills.split(',') if skill.strip()]

    text_fields = ' '.join(
        str(resume_data.get(key, '') or '')
        for key in ['content', 'summary', 'name', 'location']
    ).lower()
    preferred_location = (resume_data.get('preferred_location') or resume_data.get('location') or '').lower()
    skill_set = {skill.lower() for skill in skills if skill.strip()}

    if not skill_set:
        skill_set = set(text_fields.split())

    for job in jobs:
        score = 50
        title = (job.get('title') or '').lower()
        description = (job.get('description') or '').lower()
        tags = ' '.join(job.get('tags', [])).lower()

        for term in skill_set:
            if not term:
                continue
            if term in title or term in description or term in tags:
                score += 8

        if preferred_location and preferred_location in job.get('location', '').lower():
            score += 15
        if job.get('remote') and 'remote' in preferred_location:
            score += 10

        job['match_score'] = min(score, 100)

    jobs = sorted(jobs, key=lambda item: item.get('match_score', 0), reverse=True)
    return jobs[:top_n]


def filter_by_location(jobs, preferred_locations=None):
    """Filter jobs by location preference."""
    if not preferred_locations:
        return jobs
    filtered = []
    preferred_set = {loc.strip().lower() for loc in preferred_locations if loc}
    for job in jobs:
        if any(loc in job.get('location', '').lower() for loc in preferred_set):
            filtered.append(job)
    return filtered


def filter_by_salary(jobs, min_salary=None, max_salary=None):
    """Filter jobs by salary range."""
    if not min_salary and not max_salary:
        return jobs
    filtered = []
    for job in jobs:
        salary_text = job.get('salary', '')
        filtered.append(job)
    return filtered
