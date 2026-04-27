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
    console.log('Rendering', jobs.length, 'jobs');
    jobs.forEach((job, index) => {
        console.log('Rendering job', index, job.title);
        const card = document.createElement('div');
        card.className = 'job-card';
        card.innerHTML = `
            <div class="job-header">
                <h3>${job.title}</h3>
                ${job.source ? `<span class="job-source">${job.source}</span>` : ''}
            </div>
            <div class="company">${job.company}</div>
            <div class="location">${job.location}</div>
            <div class="match-score">Match: ${job.match_score}%</div>
            <p class="description">${job.description}</p>
            <div class="salary">${job.salary}</div>
        `;

        const detailsButton = document.createElement('button');
        detailsButton.className = 'btn btn-primary';
        detailsButton.textContent = 'View Details';
        detailsButton.addEventListener('click', () => {
            console.log('Button clicked for job:', job.title);
            openJobModal(job);
        });

        card.appendChild(detailsButton);
        jobsContainer.appendChild(card);
    });
}

function openJobModal(job) {
    console.log('Opening modal for job:', job);
    sessionStorage.setItem('selectedJob', JSON.stringify(job));
    const modal = document.getElementById('jobModal');
    const modalBody = document.getElementById('modalBody');
    console.log('Modal element:', modal);
    console.log('Modal body element:', modalBody);
    modalBody.innerHTML = `
        <h2>${job.title}</h2>
        <p><strong>${job.company}</strong> — ${job.location}</p>
        <p class="description">${job.description}</p>
        <p><strong>Type:</strong> ${job.salary}</p>
        <p><strong>Match Score:</strong> ${job.match_score}%</p>
        ${job.url ? `<p><a href="${job.url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">Apply / View Job</a></p>` : ''}
    `;
    modal.classList.remove('hidden');
    console.log('Modal should now be visible');
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

function saveJob() {
    const job = JSON.parse(sessionStorage.getItem('selectedJob'));
    if (!job) {
        alert('Please select a job first.');
        return;
    }

    fetch('/api/save-job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            job_id: job.id,
            job_title: job.title,
            company: job.company,
            location: job.location,
            salary: job.salary,
            description: job.description,
            url: job.url,
            source: job.source
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'saved') {
                alert('Job saved to favorites!');
            } else if (data.status === 'already_saved') {
                alert('Job is already in your favorites.');
            } else {
                alert('Error saving job.');
            }
        })
        .catch(error => {
            console.error('Error saving job:', error);
            alert('Error saving job: ' + error.message);
        });
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
        console.log('Loading job matches...');
        const response = await fetch('/api/match-jobs', { method: 'POST' });
        const data = await response.json();
        console.log('Job data received:', data);
        loadedJobs = data.jobs || [];
        console.log('Loaded jobs:', loadedJobs.length);
        renderJobs(loadedJobs);
    } catch (error) {
        console.error('Error loading jobs:', error);
        document.getElementById('noResults').classList.remove('hidden');
    } finally {
        loadingIndicator.classList.add('hidden');
    }
}

// Handle file upload
document.addEventListener('DOMContentLoaded', function () {
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

    // Handle file selection display
    const fileInput = document.getElementById('fileInput');
    const selectedFileDisplay = document.getElementById('selectedFile');
    const uploadArea = document.querySelector('.upload-area');

    if (fileInput && selectedFileDisplay) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                selectedFileDisplay.textContent = `Selected: ${file.name}`;
                selectedFileDisplay.style.color = '#667eea';
            } else {
                selectedFileDisplay.textContent = 'No file selected';
                selectedFileDisplay.style.color = '#999';
            }
        });
    }

    // Handle drag and drop
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('dragover', function (e) {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#f0f0ff';
            uploadArea.style.borderColor = '#764ba2';
        });

        uploadArea.addEventListener('dragleave', function (e) {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#f8f9ff';
            uploadArea.style.borderColor = '#667eea';
        });

        uploadArea.addEventListener('drop', function (e) {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#f8f9ff';
            uploadArea.style.borderColor = '#667eea';

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                const file = files[0];
                selectedFileDisplay.textContent = `Selected: ${file.name}`;
                selectedFileDisplay.style.color = '#667eea';
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
        btn.addEventListener('click', function () {
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

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('jobModal');
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeJobModal();
            }
        });
    }
});

// Preview cover letter
function previewCoverLetter() {
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
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to generate cover letter');
            }
            return response.text();
        })
        .then(coverLetterText => {
            // Show preview in a new modal or alert
            const previewModal = document.createElement('div');
            previewModal.className = 'modal';
            previewModal.innerHTML = `
            <div class="modal-content" style="max-width: 800px;">
                <span class="close-btn" onclick="this.parentElement.parentElement.remove()">&times;</span>
                <h2>Cover Letter Preview</h2>
                <pre style="white-space: pre-wrap; font-family: monospace; background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; max-height: 400px; overflow-y: auto;">${coverLetterText}</pre>
                <div class="modal-actions">
                    <button class="btn btn-secondary" onclick="this.parentElement.parentElement.remove()">Close</button>
                    <button class="btn btn-primary" onclick="downloadCoverLetter('${job.id}')">Download</button>
                </div>
            </div>
        `;
            document.body.appendChild(previewModal);
        })
        .catch(error => {
            console.error('Error generating cover letter:', error);
            alert('Error generating cover letter: ' + error.message);
        });
}

// Generate cover letter (now downloads directly)
function generateCoverLetter() {
    const job = JSON.parse(sessionStorage.getItem('selectedJob'));
    if (!job) {
        alert('Please select a job first.');
        return;
    }

    downloadCoverLetter(job.id);
}

// Download cover letter as file
function downloadCoverLetter(jobId) {
    fetch('/api/generate-cover-letter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to generate cover letter');
            }
            return response.blob();
        })
        .then(blob => {
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `cover_letter_${jobId}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            alert('Cover letter downloaded successfully!');
        })
        .catch(error => {
            console.error('Error downloading cover letter:', error);
            alert('Error downloading cover letter: ' + error.message);
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
