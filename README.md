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

## 🛠 Tech Stack

### 🧠 Backend (AI & Logic)

* **Framework:** FastAPI (with Uvicorn)
* **AI & Orchestration:** LangChain (Core, Community, Google GenAI), LangGraph
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
* **Package Manager:** NPM

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


3. **Start Services (Docker)**
```bash
docker-compose up -d  # Starts Postgres & Redis

```


4. **Run the Server**
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


4. Open the link provided (usually `http://localhost:5173`) to view the dashboard.

---

## 💡 Usage

### Using the Chrome Extension

1. Navigate to a job posting or open the extension popup.
2. **Upload Resume:** Select your PDF resume file.
3. **Select Strategy:** Choose between *Strict Mode*, *Real World*, or *Brutal Mode*.
4. **Analyze:** Click "Analyze Resume." The extension communicates with the FastAPI backend to generate a scored report.
5. **View Results:** See your "Match Score," missing keywords, and specific feedback for formatting and content.

### Using the Web Dashboard

* *Current State:* The dashboard is initialized with Vue 3 and Tailwind CSS. It is designed to serve as the central hub for tracking past analyses and managing user settings.
* Access it via your browser at the local Vite address.

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
* [x] **Web Infrastructure:** Vue 3 + Vite + Tailwind project structure initialized.
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

**Gyan Prakash Kushwaha** - [GitHub Profile](https://github.com/gyanprakashkushwaha)

Project Link: [https://github.com/gyanprakashkushwaha/internops](https://www.google.com/search?q=https://github.com/gyanprakashkushwaha/internops)
