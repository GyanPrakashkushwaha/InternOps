# InternOps

**InternOps** is an intelligent, Agentic AI-powered platform designed to revolutionize the job application workflow. By bridging the gap between job descriptions and candidate profiles, it automates the analysis, optimization, and application process to maximize hiring success.

The project ecosystem consists of three core components:

1. **FastAPI Backend:** The brain handling AI processing, resume analysis, and orchestration.
2. **Chrome Extension:** A browser-based tool for instant resume scoring and optimization while browsing job boards.
3. **Web Dashboard:** A modern Vue 3 application for managing user profiles, application history, and deep-dive analytics.
---

## 🚀 About The Project

InternOps acts as an AI career coach and operational assistant. It solves the problem of "resume black holes" by providing transparent feedback on why a resume might be rejected and agentically modifying it to match specific Job Descriptions (JDs).

### The 3 Modes of Hiring Analysis (Extension)

The Chrome Extension evaluates resumes using three distinct simulation modes:

1. **Strict Compliance Mode:** Simulates Enterprise ATS + HR Legal Filters (Binary eligibility checks).
2. **Real-World ATS Mode (Default):** Simulates modern ATS (Greenhouse, Lever) with semantic skill matching.
3. **Brutal Signal Mode:** Simulates a skeptical Engineering Manager looking for proof of work and depth.

---

## ✨ Key Features

* **Smart Resume Builder:** Analyzes your resume against a specific JD, provides a "Selection Percentage," and modifies the content to improve interview chances.
* **Multi-Perspective Analysis:** View results through three distinct lenses (ATS, Recruiter, Engineering Manager).
* **Agentic AI Chat:** A GPT-style chat interface allowing users to interact with the system for career advice.
* **Full Observability:** Integrated with **LangSmith** to trace agent workflows, debug complex LLM chains, and evaluate the quality of AI outputs in real-time.
* **Automated Application:** An agentic workflow that handles the submission of applications on the user's behalf.

---

## 🛠 Tech Stack

### 🧠 Backend (AI & Logic)

* **Framework:** FastAPI (with Uvicorn)
* **AI & Orchestration:** LangChain (Core, Community, Google GenAI), LangGraph
* **Observability & Eval:** **LangSmith**
* **Database & Caching:** PostgreSQL, Redis, LangChain-Redis
* **Asynchronous Tasks:** Celery
* **Data Processing:** Pandas, PyPDF2, OpenPyXL

### 🧩 Chrome Extension (Browser Integration)

* **Core:** Manifest V3, Service Workers
* **Stack:** Vanilla JavaScript (ES6+), HTML5, CSS3
* **Permissions:** `activeTab` (for reading current page content)

### 💻 Web Dashboard (User Interface)

* **Framework:** Vue.js 3 (Script Setup)
* **Build Tool:** Vite
* **Styling:** Tailwind CSS

---

## 🏁 Getting Started

Follow these instructions to set up the full stack locally.

### 1. Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/gyanprakashkushwaha/internops.git
cd internops

```


2. **Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```


3. **Environment Configuration**
Create a `.env` file in the root directory. **Note the addition of LangSmith credentials for observability.**
```env
# AI Providers
GOOGLE_API_KEY=your_google_api_key

# Database & Cache
POSTGRES_URI=postgresql://postgres:password@localhost:5432/internops
REDIS_URL=redis://localhost:6379/0

# LangSmith Observability
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT="internops-dev"

```


4. **Start Services (Docker)**
```bash
docker-compose up -d  # Starts Postgres & Redis

```


5. **Run the Server**
```bash
# Start Celery Worker
celery -A app.celery_worker worker --loglevel=info

# Start FastAPI
uvicorn app.app:app --reload

```



### 2. Chrome Extension Setup

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Toggle **Developer mode** in the top right corner.
3. Click **Load unpacked**.
4. Select the `internops-frontend/extension` folder.
5. The InternOps logo should appear in your toolbar.

### 3. Web Dashboard Setup

1. Navigate to the web directory:
```bash
cd internops-frontend/web

```


2. Install Node dependencies:
```bash
npm install

```


3. Start the development server:
```bash
npm run dev

```



---

## 💡 Usage

### Using the Chrome Extension

1. Navigate to a job posting or open the extension popup.
2. **Upload Resume:** Select your PDF resume file.
3. **Select Strategy:** Choose between *Strict Mode*, *Real World*, or *Brutal Mode*.
4. **Analyze:** Click "Analyze Resume." The extension communicates with the FastAPI backend to generate a scored report.

### Monitoring with LangSmith

* Once the backend is running with `LANGCHAIN_TRACING_V2=true`, all agent steps, LLM calls, and tool usages will be logged to your LangSmith project.
* Use the LangSmith dashboard to debug failed chains, view token usage, and evaluate the "reasoning" quality of the agents.

---

## 🗄 Database Management

InternOps uses PostgreSQL for persistent storage. You can access the running database container using the interactive terminal.

```bash
docker exec -it internopsdb psql -U postgres -d internops

```

---

## 🗺 Roadmap

* [x] **Core AI Analysis:** Resume parsing and multi-mode evaluation logic.
* [x] **Chrome Extension:** Functional popup with file upload and result visualization.
* [x] **Observability:** Full integration with LangSmith for traces and evals.
* [ ] **Dashboard Features:** Build out the Vue components for "Application History" and "Detailed Analytics."
* [ ] **Auth Integration:** Unified login between Extension and Web Dashboard.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Contact

**Gyan Prakash Kushwaha** - [Linkedin Profile](https://www.linkedin.com/in/gyanprakashkushwaha/)
