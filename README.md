Here is the updated `README.md` that incorporates the new frontend details, specifically highlighting the Chrome Extension architecture and the interactive features revealed in your code (like the specific analysis tabs and scoring visualizations).

---

# InternOps

**InternOps** is an intelligent, Agentic AI-powered platform designed to revolutionize the job application workflow. By bridging the gap between job descriptions and candidate profiles, it automates the analysis, optimization, and application process to maximize hiring success.

The project consists of a robust **FastAPI backend** for AI processing and a **Chrome Extension frontend** for seamless user interaction.

---

## 🚀 About The Project

InternOps acts as an AI career coach and operational assistant. It solves the problem of "resume black holes" by providing transparent feedback on why a resume might be rejected and agentically modifying it to match specific Job Descriptions (JDs).

The system utilizes advanced LLM orchestration to chat with users, analyze documents, and even automate the final application submission. The **Chrome Extension** interface allows users to upload their resume directly and get instant, scored feedback across different hiring personas.

## ✨ Key Features

* **Smart Resume Builder:** Analyzes your resume against a specific JD, provides a "Selection Percentage," and modifies the content to improve interview chances.
* **Multi-Perspective Analysis:** View results through three distinct lenses (ATS, Recruiter, Engineering Manager).
* **Visual Scoring:** Interactive circular charts and color-coded badges for quick assessment of "Match Score," "Tech Depth," and "Impact."
* **Agentic AI Chat:** A GPT-style chat interface allowing users to interact with the system for career advice.
* **Automated Application:** An agentic workflow that handles the submission of applications on the user's behalf.

### The 3 Modes of Hiring Analysis

InternOps evaluates resumes using three distinct simulation modes selected via the extension:

1. **Strict Compliance Mode (ATS Heavy):**
* *Simulates:* Enterprise ATS + HR Legal Filters.
* *Focus:* Binary eligibility checks based on explicit JD requirements.


2. **Real-World ATS Mode (Default):**
* *Simulates:* Modern ATS (Greenhouse, Lever, Ashby).
* *Focus:* Semantic skill matching and weighted relevance scoring.


3. **Brutal Signal Mode (FAANG):**
* *Simulates:* Skeptical Hiring Manager / Interviewer.
* *Focus:* Evidence-based scrutiny of claims, metrics, scope, and depth.



---

## 🛠 Tech Stack

### Backend

* **Framework:** FastAPI (with Uvicorn)
* **AI & Orchestration:** LangChain (Core, Community, Google GenAI), LangGraph
* **Database & Caching:** PostgreSQL, Redis, LangChain-Redis
* **Asynchronous Tasks:** Celery
* **Data Processing:** Pandas, PyPDF2, OpenPyXL

### Frontend (Chrome Extension)

* **Core:** HTML5, CSS3, Vanilla JavaScript (ES6+)
* **Interaction:** Dynamic DOM manipulation, Fetch API for backend communication
* **Styling:** Responsive layout with dynamic state management (loading spinners, tab transitions)

---

## 🏁 Getting Started

Follow these instructions to set up the full stack (Backend + Frontend) locally.

### Prerequisites

* **Python 3.9+**
* **Docker & Docker Compose** (Recommended for DB and Redis services)
* **Google Gemini API Key** (Required for `langchain-google-genai`)
* **Google Chrome** (For loading the extension)

### Installation

#### 1. Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/gyanprakashkushwaha/internops.git
cd internops

```


2. **Set up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

```


3. **Install Dependencies**
```bash
pip install -r requirements.txt

```


4. **Environment Configuration**
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_api_key_here
POSTGRES_URI=postgresql://postgres:password@localhost:5432/internops
REDIS_URL=redis://localhost:6379/0

```



#### 2. Frontend Setup (Chrome Extension)

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Toggle **Developer mode** in the top right corner.
3. Click **Load unpacked**.
4. Select the `frontend` (or `extension`) folder from this repository.
5. The InternOps logo should appear in your extensions toolbar.

---

## 💡 Usage

### Running the Application

1. **Start Backend Services:**
```bash
# Start Redis & Postgres
docker-compose up -d

# Start Celery Worker
celery -A app.celery_worker worker --loglevel=info

# Start FastAPI Server
uvicorn app.app:app --reload

```


*Ensure the server is running on `http://localhost:8000` as the frontend is hardcoded to this endpoint.*
2. **Using the Extension:**
* Click the InternOps extension icon.
* **Upload Resume:** Select your PDF resume file.
* **Select Strategy:** Choose between *Strict Mode*, *Real World*, or *Brutal Mode*.
* **Analyze:** Click "Analyze Resume" to start the AI agent.


3. **Interpreting Results:**
Once analysis is complete, the extension window will expand to show three tabs:
* **ATS Scan:** View Match Score, missing keywords, and formatting issues.
* **Recruiter:** Check Career Progression score and soft skills analysis.
* **Engineering:** Review Tech Depth, Impact Score, and Stack Alignment.



*(Placeholder: Include a screenshot of the Extension Popup showing the Score Card here)*

---

## 🗄 Database Management

InternOps uses PostgreSQL for persistent storage. You can access the running database container using the interactive terminal.

**Connect to the Database:**

```bash
docker exec -it internopsdb psql -U postgres -d internops

```

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Contact

**Gyan Prakash Kushwaha** - [GitHub Profile](https://github.com/gyanprakashkushwaha)

Project Link: [https://github.com/gyanprakashkushwaha/internops](https://www.google.com/search?q=https://github.com/gyanprakashkushwaha/internops)