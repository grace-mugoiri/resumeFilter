# Resume Filter

AI-powered web application for resume analysis and job matching.

## Features

- 📄 **Resume Upload** - Upload existing resume (PDF, DOCX, TXT)
- ✏️ **Resume Builder** - Create resume from scratch with form or free text editor
- 🤖 **AI Matching** - Use LLM to intelligently match resumes to job listings
- 🌍 **Job Board Integration** - Pull jobs from Indeed, LinkedIn, and other APIs
- 📍 **Location Filtering** - Filter by location (including remote)
- 💾 **Save Favorites** - Save and manage favorite job listings
- 📝 **Cover Letter Generation** - AI-generated, personalized cover letters

## Project Structure

```
resumeFilter/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── templates/            # HTML templates
│   ├── index.html        # Home page
│   ├── upload.html       # Resume upload page
│   ├── create.html       # Resume creation page
│   ├── jobs.html         # Job listings page
│   └── favorites.html    # Saved jobs page
├── static/               # Static assets
│   ├── style.css         # Main stylesheet
│   └── script.js         # JavaScript functionality
└── utils/                # Utility modules
    ├── resume_parser.py  # Resume parsing & text extraction
    ├── job_matcher.py    # Job matching & filtering
    └── cover_letter_generator.py # Cover letter generation
```

## Setup

1. **Clone and setup:**
   ```bash
   git clone <repo>
   cd resumeFilter
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

Visit `http://localhost:5000` in your browser.

## API Integrations Needed

- **Indeed API** - Job listings
- **LinkedIn API** - Job data (optional)
- **OpenAI API** - Resume analysis and cover letter generation

## TODO

- [ ] Implement resume parsing (PDF/DOCX extraction)
- [ ] Integrate job board APIs
- [ ] Build LLM matching logic
- [ ] Add cover letter generation
- [ ] Implement session-based job favorites
- [ ] Add user authentication (optional future)
- [ ] Deploy to production

## Development

Currently on the `feature/resume-filter` branch for active development.

## License

MIT
