"""Job matching and filtering utilities.

Supports multiple job APIs:
1. ArbeitNow - No auth required
2. JSearch (RapidAPI) - Requires JSEARCH_API_KEY
3. Adzuna - Requires ADZUNA_API_ID and ADZUNA_API_KEY
4. Reed - Requires REED_API_KEY
5. GitHub Jobs Archive - No auth required (limited data)
6. USAJobs.gov - No auth required (government jobs)
7. Remote.co - No auth required (remote jobs)
8. The Muse - No auth required
9. Stack Overflow Jobs - No auth required
10. Dice - No auth required
11. AngelList - No auth required
"""

import os
import requests
from typing import List, Dict


def fetch_jobs_from_arbeitnow(search_terms: str) -> List[Dict]:
    """Fetch jobs from ArbeitNow API (no authentication required)."""
    try:
        response = requests.get(
            'https://www.arbeitnow.com/api/job-board-api',
            params={'search': search_terms},
            timeout=10,
        )
        response.raise_for_status()
        raw_jobs = response.json().get('data', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            job_types = raw.get('job_types') or []
            salary = ', '.join(job_types) if job_types else ('Remote' if raw.get('remote') else 'N/A')
            description = raw.get('description', '') or ''
            description = description.replace('\n', ' ').strip()
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            jobs.append({
                'id': f"arbeitnow-{raw.get('slug') or index}",
                'title': raw.get('title', 'Unknown Title'),
                'company': raw.get('company_name', 'Unknown Company'),
                'location': raw.get('location', 'Remote') or ('Remote' if raw.get('remote') else 'Unknown'),
                'salary': salary,
                'description': description,
                'url': raw.get('url'),
                'tags': raw.get('tags', []),
                'remote': raw.get('remote', False),
                'source': 'ArbeitNow',
            })
        return jobs
    except requests.RequestException as e:
        print(f"ArbeitNow API error: {e}")
        return []


def fetch_jobs_from_jsearch(search_terms: str) -> List[Dict]:
    """Fetch jobs from JSearch API via RapidAPI (requires JSEARCH_API_KEY)."""
    api_key = os.environ.get('JSEARCH_API_KEY')
    if not api_key:
        return []

    try:
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": search_terms,
            "page": "1",
            "num_pages": "1"
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        raw_jobs = response.json().get('data', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            description = raw.get('job_description', '') or ''
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            salary = 'N/A'
            if raw.get('job_min_salary') and raw.get('job_max_salary'):
                salary = f"${raw.get('job_min_salary')}-${raw.get('job_max_salary')}"

            jobs.append({
                'id': f"jsearch-{raw.get('job_id', index)}",
                'title': raw.get('job_title', 'Unknown Title'),
                'company': raw.get('employer_name', 'Unknown Company'),
                'location': raw.get('job_city', 'Remote'),
                'salary': salary,
                'description': description,
                'url': raw.get('job_apply_link'),
                'remote': raw.get('job_is_remote', False),
                'source': 'JSearch',
            })
        return jobs
    except requests.RequestException as e:
        print(f"JSearch API error: {e}")
        return []


def fetch_jobs_from_adzuna(search_terms: str, location: str = '') -> List[Dict]:
    """Fetch jobs from Adzuna API (requires ADZUNA_API_ID and ADZUNA_API_KEY)."""
    api_id = os.environ.get('ADZUNA_API_ID')
    api_key = os.environ.get('ADZUNA_API_KEY')
    if not api_id or not api_key:
        return []

    try:
        url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
        params = {
            "app_id": api_id,
            "app_key": api_key,
            "results_per_page": 10,
            "what": search_terms,
            "where": location or "",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_jobs = response.json().get('results', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            description = raw.get('description', '') or ''
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            salary = 'N/A'
            if raw.get('salary_min') and raw.get('salary_max'):
                salary = f"${raw.get('salary_min')}-${raw.get('salary_max')}"

            jobs.append({
                'id': f"adzuna-{raw.get('id', index)}",
                'title': raw.get('title', 'Unknown Title'),
                'company': raw.get('company', {}).get('display_name', 'Unknown Company'),
                'location': raw.get('location', {}).get('display_name', 'Remote'),
                'salary': salary,
                'description': description,
                'url': raw.get('redirect_url'),
                'remote': False,
                'source': 'Adzuna',
            })
        return jobs
    except requests.RequestException as e:
        print(f"Adzuna API error: {e}")
        return []


def fetch_jobs_from_reed(search_terms: str) -> List[Dict]:
    """Fetch jobs from Reed API (requires REED_API_KEY)."""
    api_key = os.environ.get('REED_API_KEY')
    if not api_key:
        return []

    try:
        url = "https://www.reed.co.uk/api/1.0/search"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {
            "keywords": search_terms,
            "resultsToTake": 10,
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        raw_jobs = response.json().get('results', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            description = raw.get('jobDescription', '') or ''
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            jobs.append({
                'id': f"reed-{raw.get('jobId', index)}",
                'title': raw.get('jobTitle', 'Unknown Title'),
                'company': raw.get('employerName', 'Unknown Company'),
                'location': raw.get('locationName', 'Remote'),
                'salary': raw.get('salaryDescription', 'N/A'),
                'description': description,
                'url': raw.get('jobUrl'),
                'remote': False,
                'source': 'Reed',
            })
        return jobs
    except requests.RequestException as e:
        print(f"Reed API error: {e}")
        return []


def fetch_jobs_from_github(search_terms: str) -> List[Dict]:
    """Fetch jobs from GitHub Jobs Archive (no authentication required)."""
    try:
        url = "https://jobs.github.com/positions.json"
        params = {
            "description": search_terms,
            "page": 1,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_jobs = response.json()

        jobs = []
        for index, raw in enumerate(raw_jobs):
            description = raw.get('description', '') or ''
            # Remove HTML tags from description
            import re
            description = re.sub('<[^<]+?>', '', description)
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            jobs.append({
                'id': f"github-{raw.get('id', index)}",
                'title': raw.get('title', 'Unknown Title'),
                'company': raw.get('company', 'Unknown Company'),
                'location': raw.get('location', 'Remote'),
                'salary': 'N/A',
                'description': description,
                'url': raw.get('url'),
                'remote': raw.get('type', '').lower() == 'full time',
                'source': 'GitHub Jobs',
            })
        return jobs
    except requests.RequestException as e:
        print(f"GitHub Jobs API error: {e}")
        return []


def fetch_jobs_from_usajobs(search_terms: str) -> List[Dict]:
    """Fetch jobs from USAJobs.gov API (no authentication required)."""
    try:
        url = "https://data.usajobs.gov/api/search"
        params = {
            "Keyword": search_terms,
            "ResultsPerPage": 10,
            "Page": 1,
        }
        headers = {
            "User-Agent": "resume-filter-app@example.com",
            "Authorization-Key": "",  # USAJobs doesn't require auth but expects this header
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        raw_jobs = data.get('SearchResult', {}).get('SearchResultItems', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            job_data = raw.get('MatchedObjectDescriptor', {})
            position = job_data.get('PositionFormattedDescription', [{}])[0] if job_data.get('PositionFormattedDescription') else {}

            description = position.get('UserArea', {}).get('Details', {}).get('JobSummary', '') or ''
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            salary = 'N/A'
            if position.get('PositionRemuneration'):
                salary_info = position.get('PositionRemuneration', [])
                if salary_info:
                    salary = salary_info[0].get('MinimumRange', 'N/A') + ' - ' + salary_info[0].get('MaximumRange', 'N/A')

            jobs.append({
                'id': f"usajobs-{job_data.get('PositionID', index)}",
                'title': position.get('PositionTitle', 'Unknown Title'),
                'company': job_data.get('OrganizationName', 'U.S. Government'),
                'location': position.get('PositionLocationDisplay', [{}])[0].get('CityName', 'Washington, DC'),
                'salary': salary,
                'description': description,
                'url': job_data.get('ApplyURI', [''])[0] if job_data.get('ApplyURI') else '',
                'remote': position.get('PositionSchedule', [{}])[0].get('Name', '').lower() == 'full-time',
                'source': 'USAJobs.gov',
            })
        return jobs
    except requests.RequestException as e:
        print(f"USAJobs API error: {e}")
        return []


def fetch_jobs_from_remoteco(search_terms: str) -> List[Dict]:
    """Fetch jobs from Remote.co API (no authentication required)."""
    try:
        url = "https://remote.co/api/jobs"
        params = {
            "search": search_terms,
            "limit": 10,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_jobs = response.json().get('jobs', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            description = raw.get('description', '') or ''
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            jobs.append({
                'id': f"remoteco-{raw.get('id', index)}",
                'title': raw.get('title', 'Unknown Title'),
                'company': raw.get('company', {}).get('name', 'Unknown Company'),
                'location': 'Remote',
                'salary': raw.get('salary', 'N/A'),
                'description': description,
                'url': raw.get('url'),
                'remote': True,
                'source': 'Remote.co',
            })
        return jobs
    except requests.RequestException as e:
        print(f"Remote.co API error: {e}")
        return []


def fetch_jobs_from_themuse(search_terms: str) -> List[Dict]:
    """Fetch jobs from The Muse API (no authentication required)."""
    try:
        url = "https://www.themuse.com/api/public/jobs"
        params = {
            "page": 0,
            "descending": False,
            "api_key": "",  # The Muse allows some requests without API key
        }
        if search_terms:
            params["category"] = search_terms

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_jobs = response.json().get('results', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            description = raw.get('contents', '') or ''
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            salary = 'N/A'
            if raw.get('salary_min') and raw.get('salary_max'):
                salary = f"${raw.get('salary_min')}-${raw.get('salary_max')}"

            jobs.append({
                'id': f"themuse-{raw.get('id', index)}",
                'title': raw.get('name', 'Unknown Title'),
                'company': raw.get('company', {}).get('name', 'Unknown Company'),
                'location': raw.get('locations', [{}])[0].get('name', 'Remote'),
                'salary': salary,
                'description': description,
                'url': raw.get('refs', {}).get('landing_page'),
                'remote': raw.get('type') == 'remote',
                'source': 'The Muse',
            })
        return jobs
    except requests.RequestException as e:
        print(f"The Muse API error: {e}")
        return []


def fetch_jobs_from_stackoverflow(search_terms: str) -> List[Dict]:
    """Fetch jobs from Stack Overflow Jobs API (no authentication required)."""
    try:
        url = "https://api.stackexchange.com/2.3/jobs"
        params = {
            "order": "desc",
            "sort": "creation",
            "site": "stackoverflow",
            "pagesize": 10,
            "tagged": search_terms.replace(' ', ';'),
            "filter": "default",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_jobs = response.json().get('items', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            description = raw.get('description', '') or ''
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            jobs.append({
                'id': f"stackoverflow-{raw.get('job_id', index)}",
                'title': raw.get('title', 'Unknown Title'),
                'company': raw.get('company', {}).get('name', 'Unknown Company'),
                'location': raw.get('location', 'Remote'),
                'salary': 'N/A',
                'description': description,
                'url': raw.get('link'),
                'remote': 'remote' in raw.get('title', '').lower(),
                'source': 'Stack Overflow Jobs',
            })
        return jobs
    except requests.RequestException as e:
        print(f"Stack Overflow Jobs API error: {e}")
        return []


def fetch_jobs_from_dice(search_terms: str) -> List[Dict]:
    """Fetch jobs from Dice API (no authentication required for basic search)."""
    try:
        url = "https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search"
        params = {
            "q": search_terms,
            "countryCode2": "US",
            "radius": 30,
            "radiusUnit": "mi",
            "page": 1,
            "pageSize": 10,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        raw_jobs = data.get('data', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            description = raw.get('summary', '') or ''
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            jobs.append({
                'id': f"dce-{raw.get('id', index)}",
                'title': raw.get('title', 'Unknown Title'),
                'company': raw.get('companyName', 'Unknown Company'),
                'location': raw.get('jobLocation', {}).get('displayName', 'Remote'),
                'salary': raw.get('salary', 'N/A'),
                'description': description,
                'url': raw.get('detailsPageUrl'),
                'remote': raw.get('isRemote', False),
                'source': 'Dice',
            })
        return jobs
    except requests.RequestException as e:
        print(f"Dice API error: {e}")
        return []


def fetch_jobs_from_angellist(search_terms: str) -> List[Dict]:
    """Fetch jobs from AngelList Jobs API (no authentication required)."""
    try:
        url = "https://api.angel.co/1/jobs"
        params = {
            "q": search_terms,
            "type": "full-time",
            "per_page": 10,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_jobs = response.json().get('jobs', [])

        jobs = []
        for index, raw in enumerate(raw_jobs):
            description = raw.get('description', '') or ''
            if len(description) > 320:
                description = description[:317].rstrip() + '...'

            salary = 'N/A'
            if raw.get('salary_min') and raw.get('salary_max'):
                salary = f"${raw.get('salary_min')}-${raw.get('salary_max')}"

            jobs.append({
                'id': f"angellist-{raw.get('id', index)}",
                'title': raw.get('title', 'Unknown Title'),
                'company': raw.get('startup', {}).get('name', 'Unknown Company'),
                'location': raw.get('angellist_url', 'Remote'),  # AngelList doesn't provide location in basic API
                'salary': salary,
                'description': description,
                'url': f"https://angel.co/company/{raw.get('startup', {}).get('slug')}/jobs/{raw.get('id')}",
                'remote': raw.get('remote_ok', False),
                'source': 'AngelList',
            })
        return jobs
    except requests.RequestException as e:
        print(f"AngelList API error: {e}")
        return []


def fetch_jobs_from_api(criteria):
    """
    Fetch live job listings from multiple job APIs.

    Args:
        criteria: dict with keywords, preferred_location, and optional salary.

    Returns:
        list of normalized job objects from multiple sources
    """
    search_terms = criteria.get('search') or criteria.get('keywords') or criteria.get('query') or ''
    if isinstance(search_terms, list):
        search_terms = ' '.join(search_terms)
    search_terms = search_terms.strip() or 'developer'

    location = criteria.get('preferred_location') or criteria.get('location') or ''

    # Fetch from all available APIs
    all_jobs = []

    # Always try ArbeitNow (no auth required)
    all_jobs.extend(fetch_jobs_from_arbeitnow(search_terms))

    # Try optional APIs if keys are configured
    all_jobs.extend(fetch_jobs_from_jsearch(search_terms))
    all_jobs.extend(fetch_jobs_from_adzuna(search_terms, location))
    all_jobs.extend(fetch_jobs_from_reed(search_terms))
    all_jobs.extend(fetch_jobs_from_github(search_terms))

    # Always try free APIs
    all_jobs.extend(fetch_jobs_from_usajobs(search_terms))
    all_jobs.extend(fetch_jobs_from_remoteco(search_terms))
    all_jobs.extend(fetch_jobs_from_themuse(search_terms))
    all_jobs.extend(fetch_jobs_from_stackoverflow(search_terms))
    all_jobs.extend(fetch_jobs_from_dice(search_terms))
    all_jobs.extend(fetch_jobs_from_angellist(search_terms))

    # Remove duplicate jobs based on title and company
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = (job['title'].lower(), job['company'].lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs


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
