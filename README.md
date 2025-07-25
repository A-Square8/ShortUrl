# URL Shortener

## Project Overview: How It Works

This Flask-based URL shortener provides a lightweight service that converts a long URL into a short, shareable link. It supports redirection to the original URL and offers analytics like number of clicks and creation timestamp.

**Core Functionalities:**
- **Shorten URL**: Client sends a long URL, receives a unique short code and shortened URL
- **Redirect**: Accessing the short URL redirects the user to the original long URL
- **Analytics**: Retrieve data on the short URL including click counts and creation time

The entire application stores mappings in an in-memory data structure, meaning all URL mappings and click counts reset when the app restarts.

## Code Explanation: Module-by-Module

### app/models.py — Data Storage & Thread Safety
**Purpose**: Manages the in-memory storage for URL mappings (short_code → original URL, clicks, and timestamp).

**Key aspects:**
- Uses a Python dictionary `_url_store` to keep mappings
- `threading.RLock()` provides thread-safe access so concurrent requests don't corrupt data

**Functions:**
- `create_mapping(short_code, original_url)`: Adds a new shortened URL entry
- `get_mapping(short_code)`: Retrieves stored data by short code
- `increment_click(short_code)`: Increments the click counter when the short URL is used
- `short_code_exists(short_code)`: Checks whether a short code already exists to avoid collisions

### app/utils.py — Helper Utilities
**Purpose**: Contains helper functions for common tasks.

**Functions:**
- `generate_short_code(length=6)`: Creates a random 6-character alphanumeric string as the short code
- `is_valid_url(url)`: Validates that the URL has a proper schema (http or https) and domain using Python's urlparse

### app/main.py — Flask Application and Routes
**Purpose**: The main Flask app exposing HTTP endpoints for client interaction.

**Endpoints:**

**`/` (GET):**
- Health check to ensure the app is running
- Responds with JSON `{"status": "healthy", "service": "URL Shortener API"}`

**`/api/shorten` (POST):**
- Accepts a JSON payload like `{"url": "<long_url>"}`
- Validates the URL; returns an error if invalid
- Generates a unique 6-character short code
- Stores the mapping in the in-memory store
- Responds with JSON: `{"short_code": "...", "short_url": "http://<host>/<short_code>"}`

**`/<short_code>` (GET):**
- Redirects the user to the original URL
- Increments the click count
- Returns a 404 error if the code is not found

**`/api/stats/<short_code>` (GET):**
- Returns analytics about the short URL
- JSON response includes the original URL, the number of clicks, and creation timestamp
- 404 error if short code does not exist

### tests/test_basic.py — Automated Test Suite
Uses pytest framework.

**Tests cover:**
- Health check endpoint
- Shortening valid URLs, redirection correctness
- Handling invalid URLs gracefully
- Redirecting for unknown codes returns 404
- Analytics data correctness after usage

## Detailed Overall Working

### Client Request to Shorten URL:
The client sends a POST request to `/api/shorten` with a JSON body containing the long URL. The server validates the URL. If valid, it generates a short code (6 random alphanumeric characters), checks for uniqueness (retrying if necessary), and stores the mapping with metadata (click count initialized to 0, creation timestamp).

### Short URL Generated:
The server responds with a JSON object containing the short code and the full short URL (protocol + host + / + short code).

### User Redirects via Short URL:
When someone visits the short URL (e.g., `http://localhost:5000/abc123`), the server:
- Looks up the original URL based on the short code
- If found, increments the click count
- Sends a HTTP 302 redirect to the client pointing to the original URL
- If not found, returns a 404 JSON error response

### Retrieving Analytics:
A client can query `/api/stats/<short_code>` to get usage stats. The server fetches and returns the original URL, how many times it has been visited via the short URL, and when it was created.

### In-Memory Data:
All mappings and statistics reside in an in-memory Python dictionary protected by a threading lock for concurrency safety. This data is lost once the app stops.

### Error Handling:
The application returns clear, appropriate HTTP status codes and JSON messages for invalid inputs or missing short codes, ensuring a clean developer/user experience.

## Best Practices Followed

**RESTful API Design:**
Clear endpoints correspond to discrete resources and actions, using appropriate HTTP verbs.

**Thread Safety:**
Use of a reentrant lock (`threading.RLock`) in models to prevent data race conditions under concurrent access.

**URL Validation:**
The URL validator ensures only valid http/https URLs are accepted, reducing errors and abuse.

**Modular Code Structure:**
Separation between model/storage (models.py), utility functions (utils.py), and routing/controller logic (main.py) improves maintainability.

**Clear Error Handling:**
Returns explicit error messages and HTTP status codes (400 for bad request, 404 for missing data, 500 for internal issues).

**Automated Testing:**
Uses pytest to validate core functionality and common edge cases, speeding up development and reducing regressions.

**Documentation & Readability:**
Well-named functions and variables, clear comments, and logical organization aid comprehension and extensibility.

**Avoiding External Dependencies:**
Only Flask and pytest are required, achieving simplicity and ease of setup.

## How to Run Locally

### Prerequisites
- Python 3.8+ installed
- pip and optionally virtual environment tools (recommended)

### Step 1: Clone Code and Navigate to Project Root
```bash
git clone <your-repo-url>
cd url-shortener
```

### Step 2: Create and Activate Virtual Environment (Optional but recommended)
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# OR
venv\Scripts\activate      # Windows Command Prompt
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Flask App Environment Variable
**Linux/macOS:**
```bash
export FLASK_APP=app.main
```

**Windows Command Prompt:**
```
set FLASK_APP=app.main
```

### Step 5: Run the Application
```bash
python -m flask run
```
By default runs on `http://localhost:5000`. The app logs will indicate startup success.

### Step 6: Test the Endpoints
Use curl, Postman, or browser:

**Health Check:**
```bash
curl http://localhost:5000/
```

**Shorten URL:**
```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Redirect:**
Visit `http://localhost:5000/<short_code>` returned by the above.

**Analytics:**
```bash
curl http://localhost:5000/api/stats/<short_code>
```

### Step 7: Run Automated Tests
Ensure you are at the project root, then run:
```bash
pytest
```
