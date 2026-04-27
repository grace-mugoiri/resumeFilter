# Job API Integration Setup Guide

This Resume Filter application integrates with 5 different job APIs to provide a comprehensive job matching experience. Below is a guide to set up each API.

## Available APIs

### 1. **ArbeitNow** ✅ (No Setup Required)
- **Status**: Already working, no authentication needed
- **URL**: https://www.arbeitnow.com/api/job-board-api
- **Features**: Entry-level job listings, tags, remote support
- **Rate Limit**: Generous free tier

### 2. **JSearch (RapidAPI)**
- **Status**: Optional, requires API key
- **URL**: https://rapidapi.com/laimoon/api/jsearch
- **Setup Steps**:
  1. Go to https://rapidapi.com/laimoon/api/jsearch
  2. Sign up for a free RapidAPI account
  3. Subscribe to the free tier (1000 requests/month)
  4. Copy your API key
  5. Add to `.env`: `JSEARCH_API_KEY=your-key-here`
- **Features**: Comprehensive job data, salary ranges, location details

### 3. **Adzuna**
- **Status**: Optional, requires API key
- **URL**: https://developer.adzuna.com/
- **Setup Steps**:
  1. Go to https://developer.adzuna.com/
  2. Sign up for a free account
  3. Create an application to get App ID and API Key
  4. Free tier includes 1000 requests/day
  5. Add to `.env`:
     ```
     ADZUNA_API_ID=your-app-id
     ADZUNA_API_KEY=your-api-key
     ```
- **Features**: Multiple countries, salary data, advanced filtering

### 4. **Reed** 
- **Status**: Optional, requires API key
- **URL**: https://www.reed.co.uk/api
- **Setup Steps**:
  1. Go to https://www.reed.co.uk/api
  2. Sign up for a free developer account
  3. Get your API key from the dashboard
  4. Free tier includes 4 requests/hour
  5. Add to `.env`: `REED_API_KEY=your-api-key`
- **Features**: UK job market focus, quality listings

### 5. **GitHub Jobs Archive** ✅ (No Setup Required)
- **Status**: Working without authentication
- **URL**: https://jobs.github.com/positions.json
- **Features**: Tech-focused jobs, remote opportunities
- **Note**: Archive API (limited new listings, but stable)

## Configuration Steps

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Add API keys to `.env`** (only for APIs you want to enable):
   ```env
   JSEARCH_API_KEY=your-jsearch-key
   ADZUNA_API_ID=your-adzuna-id
   ADZUNA_API_KEY=your-adzuna-key
   REED_API_KEY=your-reed-key
   ```

3. **Restart the Flask application** to load the new environment variables

## How It Works

- The application queries all configured APIs simultaneously
- Results are aggregated and deduplicated by title and company
- Jobs are ranked by match score based on your resume
- Each job displays which API it came from (the badge next to the title)

## Troubleshooting

**API keys not working?**
- Verify the `.env` file is in the project root
- Restart Flask after updating `.env`
- Check API console logs for error messages

**Missing jobs from a specific API?**
- Ensure the API key is valid and has requests remaining
- Check your API subscription tier (free tiers may have limits)
- Some APIs may return empty results for specific keywords

**Getting lots of duplicate jobs?**
- This is normal initially as multiple APIs may have the same listings
- The system automatically removes near-duplicates

## Free Tier Limits Summary

| API | Free Tier | Reset Period |
|-----|-----------|--------------|
| ArbeitNow | Unlimited | - |
| JSearch | 1,000 requests | Month |
| Adzuna | 1,000 requests | Day |
| Reed | 4 requests | Hour |
| GitHub Jobs | Unlimited (limited data) | - |

## Future Enhancements

Consider adding these APIs:
- Indeed (requires partnership)
- LinkedIn (enterprise only)
- Stack Overflow Jobs (API available)
- RemoteOK (public API)
- WeWorkRemotely (public API)
