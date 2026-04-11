// Main application JavaScript

let loadedJobs = [];

// Tab switching
function switchTab(tab) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(t => t.classList.remove('active'));
    document.getElementById(tab + 'Tab').classList.add('active');
}

// Add experience entry to form
function addExperience() {
    const container = document.getElementById('experienceContainer') || document.getElementById('experienceList');
    const index = container.children.length;
    
    const exp = document.createElement('div');
    exp.className = 'form-group';
    exp.innerHTML = `
        <fieldset>
            <legend>Experience ${index + 1}</legend>
            <input type="text" placeholder="Job Title" name="job_title_${index}">
            <input type="text" placeholder="Company" name="company_${index}">
            <input type="text" placeholder="Start Date" name="start_date_${index}">
            <input type="text" placeholder="End Date" name="end_date_${index}">
            <textarea placeholder="Description" rows="3" name="exp_description_${index}"></textarea>
            <button type="button" onclick="this.parentElement.remove()" class="btn btn-secondary">Remove</button>
        </fieldset>
    `;
    container.appendChild(exp);
}

// Add education entry to form
function addEducation() {
    const container = document.getElementById('educationContainer') || document.getElementById('educationList');
    const index = container.children.length;
    
    const edu = document.createElement('div');
    edu.className = 'form-group';
    edu.innerHTML = `
        <fieldset>
            <legend>Education ${index + 1}</legend>
            <input type="text" placeholder="School/University" name="school_${index}">
            <input type="text" placeholder="Degree" name="degree_${index}">
            <input type="text" placeholder="Field of Study" name="field_${index}">
            <input type="text" placeholder="Graduation Year" name="grad_year_${index}">
            <button type="button" onclick="this.parentElement.remove()" class="btn btn-secondary">Remove</button>
        </fieldset>
    `;
    container.appendChild(edu);
}

function renderJobs(jobs) {
    const jobsContainer = document.getElementById('jobsContainer');
    const noResults = document.getElementById('noResults');
    jobsContainer.innerHTML = '';

    if (!jobs || jobs.length === 0) {
        noResults.classList.remove('hidden');
        return;
    }

    noResults.classList.add('hidden');
    jobs.forEach(job => {
        const card = document.createElement('div');
        card.className = 'job-card';
        card.innerHTML = `
            <h3>${job.title}</h3>
            <div class="company">${job.company}</div>
            <div class="location">${job.location}</div>
            <div class="match-score">Match: ${job.match_score}%</div>
            <p class="description">${job.description}</p>
            <div class="salary">${job.salary}</div>
        `;

        const detailsButton = document.createElement('button');
        detailsButton.className = 'btn btn-primary';
        detailsButton.textContent = 'View Details';
        detailsButton.addEventListener('click', () => openJobModal(job));

        card.appendChild(detailsButton);
        jobsContainer.appendChild(card);
    });
}

function openJobModal(job) {
    sessionStorage.setItem('selectedJob', JSON.stringify(job));
    const modal = document.getElementById('jobModal');
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <h2>${job.title}</h2>
        <p><strong>${job.company}</strong> — ${job.location}</p>
        <p class="description">${job.description}</p>
        <p><strong>Type:</strong> ${job.salary}</p>
        <p><strong>Match Score:</strong> ${job.match_score}%</p>
        ${job.url ? `<p><a href="${job.url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">Apply / View Job</a></p>` : ''}
    `;
    modal.classList.remove('hidden');
}

function applyFilters() {
    const locationValue = document.getElementById('locationFilter')?.value.toLowerCase().trim();
    const salaryValue = document.getElementById('salaryFilter')?.value.trim();

    const filteredJobs = loadedJobs.filter(job => {
        const locationMatch = !locationValue || job.location.toLowerCase().includes(locationValue);
        const salaryMatch = !salaryValue || parseInt(job.salary.replace(/[^0-9]/g, '').slice(0, 3), 10) >= parseInt(salaryValue, 10);
        return locationMatch && salaryMatch;
    });

    renderJobs(filteredJobs);
}

async function loadJobMatches() {
    const jobsContainer = document.getElementById('jobsContainer');
    if (!jobsContainer) return;

    const loadingIndicator = document.getElementById('loadingIndicator');
    const noResults = document.getElementById('noResults');
    loadingIndicator.classList.remove('hidden');
    noResults.classList.add('hidden');
    jobsContainer.innerHTML = '';

    try {
        const response = await fetch('/api/match-jobs', { method: 'POST' });
        const data = await response.json();
        loadedJobs = data.jobs || [];
        renderJobs(loadedJobs);
    } catch (error) {
        document.getElementById('noResults').classList.remove('hidden');
    } finally {
        loadingIndicator.classList.add('hidden');
    }
}

// Handle file upload
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(uploadForm);

            try {
                await fetch('/api/parse-resume', {
                    method: 'POST',
                    body: formData
                });
                window.location.href = '/jobs';
            } catch (error) {
                alert('Error uploading resume: ' + error.message);
            }
        });
    }

    const resumeForm = document.getElementById('resumeForm');
    if (resumeForm) {
        resumeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(resumeForm);

            try {
                await fetch('/api/parse-resume', {
                    method: 'POST',
                    body: formData
                });
                window.location.href = '/jobs';
            } catch (error) {
                alert('Error creating resume: ' + error.message);
            }
        });
    }

    const textForm = document.getElementById('textForm');
    if (textForm) {
        textForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(textForm);

            try {
                await fetch('/api/parse-resume', {
                    method: 'POST',
                    body: formData
                });
                window.location.href = '/jobs';
            } catch (error) {
                alert('Error submitting resume: ' + error.message);
            }
        });
    }

    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    const locationFilter = document.getElementById('locationFilter');
    const salaryFilter = document.getElementById('salaryFilter');
    if (locationFilter) {
        locationFilter.addEventListener('input', applyFilters);
    }
    if (salaryFilter) {
        salaryFilter.addEventListener('input', applyFilters);
    }

    loadJobMatches();
});

// Close modal
function closeJobModal() {
    document.getElementById('jobModal').classList.add('hidden');
}

// Generate cover letter
function generateCoverLetter() {
    const job = JSON.parse(sessionStorage.getItem('selectedJob'));
    if (!job) {
        alert('Please select a job first.');
        return;
    }

    fetch('/api/generate-cover-letter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: job.id })
    })
    .then(r => r.json())
    .then(data => {
        alert('Cover letter generated!\n\n' + data.cover_letter);
    });
}

// Reset filters
function resetFilters() {
    const locationInput = document.getElementById('locationFilter');
    const salaryInput = document.getElementById('salaryFilter');
    if (locationInput) locationInput.value = '';
    if (salaryInput) salaryInput.value = '';
    renderJobs(loadedJobs);
}
