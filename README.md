# InternOps

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D.svg)
![Vite](https://img.shields.io/badge/Vite-Enabled-646CFF.svg)
![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC.svg)
![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-Manifest_V3-yellow.svg)

**An intelligent, agentic AI platform that simulates the entire recruitment lifecycle—from ATS filtering to Hiring Manager review—to help candidates optimize their resumes and land interviews.**

> **Note:** This repository contains the **Backend logic** (Agents, Database, API). It serves as the intelligence engine for the [InternOps Frontend](https://github.com/gyanprakashkushwaha/internops-frontend) and Chrome Extension.

---

## 📖 Overview

**InternOps** is an MVP (Minimum Viable Product) designed to bridge the gap between job seekers and the complex, often opaque hiring process. By leveraging **LangGraph** and multi-agent workflows, the system simulates real-world recruitment scenarios.

It doesn't just "check keywords"; it emulates the specific personalities and strictness levels of different gatekeepers in the hiring chain: the **Applicant Tracking System (ATS)**, the **Recruiter**, and the **Hiring Manager (HM)**.

### Why InternOps?
Job seekers often fly blind. InternOps provides transparency by running resumes through a **3x3 Matrix of Hiring Modes**, offering detailed feedback on why a candidate might be rejected at specific stages—whether it's a formatting error caught by a strict ATS or a "job hopping" red flag raised by a cynical recruiter.

---

## 🚀 Key Features

### 🧠 The 3x3 Hiring Matrix
The core of InternOps is its ability to switch "modes," changing the personality and strictness of the AI agents:

1.  **Strict Compliance Mode ("The Bureaucratic Gatekeeper")**
    * **ATS:** Regex-like filter. Rejects for exact keyword misses or formatting violations.
    * **Recruiter:** Flags gaps >6 months or frequent job changes.
    * **HM:** Demands exact matches between "Skills" and "Experience" sections.

2.  **Real-World ATS Mode ("The Modern Tech Standard")**
    * **ATS:** Uses semantic matching (vector logic) to rank relevance (0-100).
    * **Recruiter:** Looks for career trajectory and soft skills; contextualizes gaps.
    * **HM:** Focuses on complexity, impact, and learning curve.

3.  **Brutal Signal Mode ("The Elite/MAANG Headhunter")**
    * **ATS:** 99% rejection rate. Demands "signals of excellence" and prestige.
    * **Recruiter:** Judges "velocity" (speed to Senior roles). Ignores low-signal verbs like "worked on."
    * **HM:** Skeptical architect who flags inflated metrics and demands deep low-level knowledge.

### 🤖 Agentic Workflow
* **Multi-Agent Architecture:** A directed graph workflow (`ATS -> Recruiter -> HM`) using **LangGraph**.
* **Resume Optimizer:** Analyzes JDs and Resumes to provide selection percentages, gap analysis, and specific improvement suggestions.
* **Memory & Persistence:** Uses checkpointers to maintain state across agent interactions.

---

## 🛠️ Tech Stack

* **Backend Framework:** Python, FastAPI, Uvicorn
* **AI & LLMs:** LangChain (Community, Core, Google GenAI), LangGraph
* **Database:** PostgreSQL (with `psycopg2` support)
* **Task Queue & Caching:** Celery, Redis
* **Containerization:** Docker, Docker Compose

---

## 🏁 Getting Started

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.
* Git

### Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/gyanprakashkushwaha/internops.git](https://github.com/gyanprakashkushwaha/internops.git)
    cd internops/InternOps-MVP
    ```

2.  **Environment Setup**
    Create a `.env` file in the root directory. You **must** configure your LLM API keys (e.g., Google GenAI) here.
    
    ```bash
    # .env example
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

    *Important: Ensure your `docker-compose.yml` is configured to pass these variables to the `web` and `worker` services (e.g., add `env_file: .env` or map the variables manually).*

3.  **Build and Run**
    Use Docker Compose to build the images and start the services.
    ```bash
    docker-compose up --build
    ```

---

## 💻 Usage

InternOps is designed to be run entirely via Docker. Here are the "Daily Driver" commands.

### Starting the App
* **Start everything (locks terminal to logs):**
    ```bash
    docker-compose up
    ```
* **Start in background (detached mode):**
    ```bash
    docker-compose up -d
    ```

### Stopping the App
* **Stop and remove containers:**
    ```bash
    docker-compose down
    ```
    *Note: Your database data persists due to configured Docker volumes.*

### Debugging & Logs
* **View live logs:**
    ```bash
    docker-compose logs -f
    ```
* **Check specific service logs (e.g., Worker):**
    ```bash
    docker-compose logs -f worker
    ```

### Accessing Internals
* **Open a shell inside the Web container:**
    ```bash
    docker-compose exec web bash
    ```
* **Access the PostgreSQL Database:**
    ```bash
    docker-compose exec -it db psql -U postgres -d internops
    ```

---

## 🗺️ Roadmap

Current progress and future plans:

- [x] **Core Agent Workflow:** ATS, Recruiter, HM agents with memory.
- [x] **Async Architecture:** Non-blocking task processing via Celery & Redis.
- [x] **3 Modes:** Toggle between Strict, Real-World, and Brutal modes.
- [x] **Docker Integration:** Full containerization.
- [x] **Frontend Support:** API endpoints ready for Vue Dashboard & Chrome Extension.
- [ ] **Rule-Based ATS:** A "dumb" filter for initial screening.
- [ ] **CI/CD Integration:** Automated testing and deployment.
- [ ] **AWS Deployment:** Cloud hosting infrastructure.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📞 Contact & Support

* **Project Maintainer:** Gyan Prakash Kushwaha
* **Issues:** Please report bugs via the [GitHub Issues](https://github.com/gyanprakashkushwaha/internops/issues) page.