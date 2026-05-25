<p align="center">
  <h1 align="center">🤖 ReviewMind AI</h1>
  <p align="center">
    <strong>AI-Powered Pull Request Code Review Bot</strong><br>
    Automated code review using Google Gemini AI — posts detailed, organized review comments directly on your GitHub Pull Requests.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109-green?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Gemini_AI-2.5_Flash-orange?logo=google&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

---

## ✨ What It Does

When a Pull Request is **opened**, **updated**, or **reopened** on your GitHub repository, ReviewMind AI automatically:

1. 🔍 **Fetches the PR diff** from GitHub
2. 🧠 **Analyzes the code** using Google Gemini AI across 4 categories:
   - 🔒 **Security** — SQL injection, XSS, secret leakage, insecure auth
   - ⚡ **Performance** — blocking calls, memory leaks, inefficient queries
   - 🏗️ **Architecture** — code smells, missing error handling, poor abstractions
   - 🐛 **Bugs** — logical errors, race conditions, edge cases
3. 📝 **Posts a structured review comment** directly on the PR with:
   - Overall risk level & verdict
   - Issues table with severity & category
   - 🚀 Future enhancement suggestions
   - 🛠️ Major bugs with fix instructions

---

## 📋 Sample Review Output

The bot posts a comment like this on your PR:

> ### 🤖 ReviewMind AI Code Review
> **Overall Risk Level:** 🔴 Critical  
> **Verdict:** This PR contains multiple critical security vulnerabilities...
>
> | # | Severity | Category | File | Line | Issue |
> |---|----------|----------|------|------|-------|
> | 1 | 🔴 Critical | 🔒 Security | `auth.py` | 8 | SQL Injection in login query |
> | 2 | 🟠 High | ⚡ Performance | `main.py` | 13 | Blocking loop with 10M iterations |
>
> ### 🚀 Future Enhancements
> | # | Priority | File | Enhancement |
> |---|----------|------|-------------|
> | 1 | 🔵 Strongly Recommended | `auth.py` | Use parameterized queries |
>
> ### 🛠️ Major Bugs & How to Fix Them
> **💡 Fix:** Use parameterized queries: `cursor.execute("SELECT * FROM users WHERE username=?", (username,))`

---

## 🏗️ Architecture

```
GitHub Webhook → FastAPI Server → Google Gemini AI → GitHub PR Comment
```

```
GithubPRanalysis/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── github.py      # Webhook handler + review pipeline
│   │       ├── review.py      # Manual review endpoint
│   │       └── health.py      # Health check
│   ├── core/
│   │   ├── config.py          # Settings (from .env)
│   │   └── celery_app.py      # Celery config (optional)
│   ├── services/
│   │   ├── ai_service.py      # Gemini AI integration
│   │   └── github_service.py  # GitHub API (PyGithub)
│   ├── tasks/
│   │   └── review_tasks.py    # Celery tasks (optional)
│   └── main.py                # FastAPI app
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **GitHub Account** with a repository
- **Google Gemini API Key** (free tier available)
- **ngrok** (to expose your local server to GitHub)

### 1. Clone the Repository

```bash
git clone https://github.com/naitikraj9112-max/ReviewMind-AI.git
cd ReviewMind-AI
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install google-genai
```

### 4. Get Your API Keys

#### 🔑 Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

#### 🔑 GitHub Personal Access Token (PAT)

1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens](https://github.com/settings/personal-access-tokens/new)
2. Click **"Generate new token"**
3. Set a name (e.g., `ReviewMind Bot`)
4. Under **Repository access**, select the repos you want to review
5. Under **Repository permissions**, enable:
   - **Pull Requests**: Read & Write
   - **Issues**: Read & Write
   - **Contents**: Read-only
6. Click **Generate token** and copy it (starts with `github_pat_...` or `ghp_...`)

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
GITHUB_WEBHOOK_SECRET=any_secret_string_you_choose
GITHUB_PAT=ghp_your_token_here
GEMINI_API_KEY=AIzaSy_your_key_here
REDIS_URL=redis://127.0.0.1:6379/0
```

### 6. Start the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 7. Expose with ngrok

In a **new terminal**:

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

### 8. Set Up GitHub Webhook

1. Go to your GitHub repository → **Settings** → **Webhooks** → **Add webhook**
2. Configure:
   | Field | Value |
   |-------|-------|
   | **Payload URL** | `https://your-ngrok-url.ngrok-free.app/webhook/github` |
   | **Content type** | `application/json` |
   | **Secret** | The same value you set in `GITHUB_WEBHOOK_SECRET` |
   | **Events** | Select **"Let me select individual events"** → check **Pull requests** |
3. Click **Add webhook**

### 9. Test It!

Create or reopen a Pull Request on your repository. Within ~15 seconds, ReviewMind AI will post a detailed review comment! 🎉

---

## 🐳 Docker Setup (Optional)

If you prefer Docker with Redis:

```bash
# Start all services
docker-compose up --build

# The API will be available at http://localhost:8000
```

> **Note:** When using Docker, the `REDIS_URL` in `.env` should be `redis://redis:6379/0` (internal Docker network).

---

## ⚙️ Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key from AI Studio |
| `GITHUB_PAT` | ✅ | GitHub Personal Access Token with PR write access |
| `GITHUB_WEBHOOK_SECRET` | ✅ | Secret string to verify webhook authenticity |
| `REDIS_URL` | ❌ | Redis URL (only needed for Celery worker mode) |
| `GCP_PROJECT_ID` | ❌ | GCP Project ID (only if using Vertex AI instead of API key) |
| `GCP_LOCATION` | ❌ | GCP region (default: `us-central1`) |

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/webhook/github` | GitHub webhook receiver |
| `POST` | `/api/review` | Manual review trigger |
| `GET` | `/health` | Health check |

---

## 🛡️ Security Notes

- **Never commit your `.env` file** — it contains secrets
- Use a **strong webhook secret** to prevent unauthorized triggers
- The GitHub PAT should have **minimum required permissions**
- Consider using a **Fine-grained PAT** scoped to specific repositories

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  <sub>Built with ❤️ using FastAPI + Google Gemini AI</sub>
</p>
