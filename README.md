# LinkedIn Voyager Profile Scraper API

A high-performance, asynchronous REST API built with FastAPI that extracts comprehensive LinkedIn profile data by reverse-engineering LinkedIn’s internal Voyager REST API.

Unlike traditional browser-automation scrapers (such as Selenium or Puppeteer), this service communicates directly with LinkedIn's internal endpoints using authenticated HTTP requests. This eliminates the heavy CPU and RAM overhead of running a headless browser, executing requests in milliseconds rather than tens of seconds.

---

---

## 🔗 Live Interactive Demo

The API is deployed on the Render free tier. You can test it immediately using the interactive documentation interfaces:

* 🟢 **Swagger UI:** [https://tross-linkedin-api-e6y1.onrender.com/docs](https://tross-linkedin-api-e6y1.onrender.com/docs)
* 🔵 **ReDoc UI:** [https://tross-linkedin-api-e6y1.onrender.com/redoc](https://tross-linkedin-api-e6y1.onrender.com/redoc)

**🧪 Sample Test URL:**
Copy and paste this URL into the Swagger UI `url` parameter to test the payload extraction:
`https://www.linkedin.com/in/shivam-sagar-002263209/`

---

## ✨ Key Features & Engineering Highlights

* ⚡ **Asynchronous Networking:** Built on `httpx.AsyncClient` with non-blocking I/O for concurrent request handling.
* 🧱 **Modular Clean Architecture:** Strict separation between network ingestion (`services.py`), data modeling (`schemas.py`), domain constants (`constants.py`), and entity normalization (`ProfileParser.py`).
* 🛡️ **Built-in Rate Limiting:** Implements IP-based sliding window rate-limiting via `slowapi` to protect the API from DDoS attacks or runaway scripts, safely enforcing a threshold of **10 requests per minute** per client.
* 🧬 **Entity URN Resolution:** Automatically builds in-memory relational lookup tables to resolve LinkedIn URN hashes (such as Company IDs and Skill URNs) to human-readable strings.
* 📸 **Asset Extraction:** Extracts resume documents, portfolio PDF links, LeetCode profiles, and high-resolution CDN images (profile and banner).
* 🐳 **Container Ready:** Fully Dockerized with dynamic port binding for seamless cloud deployment.

---

## 📂 Project Structure

```text
tross-linkedin-api/
│
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI application entry point, routes, middleware, and logging
│   ├── schemas.py            # Pydantic data models defining the structured output schema
│   ├── services.py           # Handles HTTP networking, headers, and upstream Voyager calls
│   ├── ProfileParser.py      # Normalizes raw nested Voyager JSON graph into clean data models
│   └── constants.py          # Centralized LinkedIn Voyager entity types and namespaces
│
├── .dockerignore             # Excludes local caches, logs, and sensitive files from Docker
├── .gitignore                # Prevents committing virtual environments and secret keys
├── Dockerfile                # Production multi-stage Docker build configuration
├── README.md                 # Complete system documentation
└── requirements.txt          # Production dependencies and pinned versions
```

---

## Input Validation & Error Handling

The API implements defensive error handling to prevent runtime crashes and provide descriptive HTTP status codes:

| Scenario | HTTP Status | Response Detail |
| :--- | :--- | :--- |
| Missing `.env` credentials | `400 Bad Request` | `"LinkedIn credentials are missing. Please set LINKEDIN_LI_AT and LINKEDIN_JSESSIONID..."` |
| Invalid protocol (e.g. `htt://`) | `400 Bad Request` | `"Invalid URL protocol. Ensure the URL starts with http:// or https://"` |
| Non-LinkedIn domain | `400 Bad Request` | `"Invalid domain. Please provide a valid LinkedIn URL."` |
| Missing `/in/` username path | `400 Bad Request` | `"Invalid profile URL. Could not locate a valid username in the '/in/' path."` |
| Expired / Revoked Session Cookie | `401 Unauthorized` | `"The provided LinkedIn credentials are not valid or have expired..."` |
| Profile not found or private | `404 Not Found` | `"LinkedIn profile not found or is set to private."` |
| Unhandled server exceptions | `500 Server Error` | Logs full stack trace to terminal and returns structured error payload |

---

## Local Setup & Installation

### 1. Prerequisites
* Python 3.11 or higher
* Git

### 2. Clone the Repository
```bash
git clone [https://github.com/your-username/tross-linkedin-api.git](https://github.com/your-username/tross-linkedin-api.git)
cd tross-linkedin-api
```

### 3. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Environment Configuration

The API requires authentication cookies extracted from an active LinkedIn browser session.

### Extracting Required Cookies:
1. Open Google Chrome and log in to [LinkedIn](https://www.linkedin.com).
2. Press `F12` (or right-click anywhere and select **Inspect**) to open Developer Tools.
3. Navigate to the **Application** tab (top bar) $\rightarrow$ Expand **Cookies** (left sidebar) $\rightarrow$ Click `https://www.linkedin.com`.
4. Locate and copy the following two keys:
   * **`li_at`**: A long alphanumeric session token string.
   * **`JSESSIONID`**: A string formatted like `"ajax:1234567890123456789"`.
5. Close the browser tab. **Do not click "Sign Out"**, as logging out immediately invalidates the tokens on LinkedIn's backend.

### Setting up `.env`:
Create a `.env` file in the root directory:

```env
LINKEDIN_LI_AT=your_copied_li_at_cookie_value_here
LINKEDIN_JSESSIONID="ajax:your_copied_jsessionid_value_here"
```

---

## Running the Application

Start the local development server with auto-reload:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running:
* **Interactive Swagger UI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alternative ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Running with Docker

You can build and run the entire application inside an isolated Docker container:

```bash
# 1. Build the Docker image
docker build -t linkedin-scraper-api .

# 2. Run the container passing your environment variables
docker run -p 8000:8000 --env-file .env linkedin-scraper-api
```

The API will be accessible at `http://localhost:8000/docs`.

---

## API Reference

### `GET /api/profile`
Fetches and structures public data from any valid LinkedIn personal profile.

#### Query Parameters:
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `url` | `string` | **Yes** | The full LinkedIn profile URL (e.g., `https://www.linkedin.com/in/username/`) |

#### Example Request:
```bash
curl -X GET "[http://127.0.0.1:8000/api/profile?url=https://www.linkedin.com/in/shivam-sagar-002263209/](http://127.0.0.1:8000/api/profile?url=https://www.linkedin.com/in/shivam-sagar-002263209/)" \
     -H "accept: application/json"
```

#### Example JSON Output:
```json
{
  "public_identifier": "shivam-sagar-002263209",
  "profile_urn": "urn:li:fsd_profile:ACoAADTlokIBH8xiCbEnxXBUF7d1QwWamQTWPmU",
  "industry": "Information Technology & Services",
  "full_name": "Shivam Sagar",
  "headline": "Software Developer | ASP.NET | C# | Python | Machine Learning",
  "about": "I’m a Software Developer with professional experience building enterprise web applications...",
  "location": "Pune District, Maharashtra, India",
  "profile_picture_url": "[https://media.licdn.com/dms/image/v2/.../crop_800_800/](https://media.licdn.com/dms/image/v2/.../crop_800_800/)...",
  "background_picture_url": "[https://media.licdn.com/dms/image/v2/.../350_1400/](https://media.licdn.com/dms/image/v2/.../350_1400/)...",
  "featured_media": [
    {
      "title": "Resume",
      "description": "Software Developer with experience building enterprise web applications...",
      "url": "[https://media.licdn.com/dms/document/media/v2/.../profile-treasury-document-sanitized-pdf/](https://media.licdn.com/dms/document/media/v2/.../profile-treasury-document-sanitized-pdf/)...",
      "media_type": "Document",
      "thumbnail_url": "[https://media.licdn.com/dms/image/v2/.../1920/](https://media.licdn.com/dms/image/v2/.../1920/)..."
    },
    {
      "title": "s_shivam04 - LeetCode Profile",
      "description": null,
      "url": "[https://leetcode.com/u/s_shivam04/](https://leetcode.com/u/s_shivam04/)",
      "media_type": "Link",
      "thumbnail_url": "[https://media.licdn.com/dms/image/sync/v2/.../1280_800/](https://media.licdn.com/dms/image/sync/v2/.../1280_800/)..."
    }
  ],
  "experiences": [
    {
      "start_date": "10/2024",
      "end_date": "07/2026",
      "title": "Software Developer",
      "company_name": "Aloha Technology",
      "location": "Pune City",
      "description": "- Developed and maintained web applications using ASP.NET MVC, C#, and SQL Server.\n- Designed and implemented scheduled tasks to automate business processes..."
    }
  ],
  "educations": [
    {
      "start_date": "08/2023",
      "end_date": "05/2025",
      "school_name": "Indira College of Engineering and Management, Pune",
      "degree_name": "Masters Of Computer Application(MCA)",
      "field_of_study": "Computer Science",
      "grade": "CGPA: 8.09"
    }
  ],
  "projects": [
    {
      "start_date": "11/2025",
      "end_date": "12/2025",
      "title": "High-Concurrency Ticketing API",
      "description": "An enterprise-grade .NET 8 Web API built to handle extreme traffic loads and prevent data corruption...",
      "url": null
    }
  ],
  "certifications": [
    {
      "start_date": "03/2026",
      "end_date": null,
      "name": "Model Context Protocol: Advanced Topics",
      "authority": "Anthropic",
      "url": "[https://verify.skilljar.com/c/wwekp9tbo78f](https://verify.skilljar.com/c/wwekp9tbo78f)",
      "license_number": "wwekp9tbo78f"
    }
  ],
  "skills": [
    "ASP.NET",
    "Model Context Protocol(MCP): Advanced Topics",
    "Java",
    "Bootstrap (Framework)",
    "MySQL",
    ".NET 8",
    "Amazon Web Services (AWS)",
    "Clean Architecture (N-Tier)",
    "REST APIs",
    "Entity Framework (EF) Core",
    "Python (Programming Language)"
  ],
  "languages": [
    "English",
    "Hindi"
  ]
}
```

---

## Cloud Deployment (Render / Railway)

1. Push your code to a GitHub repository (ensure `.env` is **not** committed).
2. Create a new **Web Service** on [Render](https://render.com) or [Railway](https://railway.app) and connect your repository.
3. Configure the build parameters:
   * **Runtime:** `Python 3` (or choose `Docker`)
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables** in your cloud hosting dashboard:
   * `LINKEDIN_LI_AT` = `<your_li_at_value>`
   * `LINKEDIN_JSESSIONID` = `<your_jsessionid_value>`
5. Deploy the application. Once complete, your public API will be live over HTTPS.

---

## Technical Constraints & Design Decisions

* **Hierarchical Schema over Flat CSV:** Instead of flattening job titles and schools into repetitive top-level properties (e.g., `previousSchoolDegree1`, `previousSchoolDegree2`), data is organized into clean, nested arrays (`experiences`, `educations`). This structure matches REST API standards and simplifies frontend integration.
* **Network Efficiency vs. Network Count:** Connection counts and follower totals reside in separate Voyager network endpoints (`/networkinfo`). To keep profile fetching atomic and preserve single-request latency, this endpoint focuses entirely on complete entity resolution (`FullProfileWithEntities-103`).
* **Privacy Controls:** Personal email addresses and phone numbers are strictly protected by LinkedIn's first-degree privacy settings and are omitted unless authorized by the authenticated account.
