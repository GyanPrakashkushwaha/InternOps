
### **System Analysis: The 3x3 Matrix**

Your system uses a **LangGraph workflow** (`ATS -> Recruiter -> HM`) where the "personality" and "strictness" of each agent change based on the selected `mode`.

#### **1. Strict Compliance Mode** (The "Bureaucratic Gatekeeper")

* **ATS:** Acts as a regex-like filter. Rejects based on exact keyword misses, formatting violations (columns/tables), or hard constraints (degrees/years). It doesn't infer; if it's not written, it doesn't exist.
* **Recruiter:** A high-volume screener looking for red flags. Rejects for gaps > 6 months or "job hopping" (>2 jobs in 2 years).
* **HM:** A compliance officer in a regulated industry. Checks if the "Skills" section matches the "Experience" section perfectly. Disqualifies if the stack isn't an exact match.

#### **2. Real-World ATS Mode** (The "Modern Tech Standard")

* **ATS:** Uses semantic matching (vector-style logic). It ranks by relevance (0-100) rather than binary keywords. It tolerates minor gaps and looks for "Probability of Fit".
* **Recruiter:** A Talent Acquisition Partner. Looks for career trajectory (promotion/growth) and soft skills (leadership/mentorship). Contextualizes gaps rather than rejecting them.
* **HM:** A Pragmatic Engineering Manager. Cares about complexity (scaling/refactoring), qualitative impact (automation), and learning curve/ramp-up speed.

#### **3. Brutal Signal Mode** (The "Elite/MAANG Headhunter")

* **ATS:** A High-Frequency Trading firm filter (99% rejection rate). Rejects "tutorial projects" (e.g., To-Do lists) and generic formatting. Demands "signals of excellence" (prestige, massive scale).
* **Recruiter:** A cynical Headhunter. Judges "velocity" (how fast you reached Senior). Ignores "we worked on" (low signal) vs. "I architected" (high signal).
* **HM:** A Skeptical Principal Architect. Assumes candidates lie. Flags inflated metrics ("1000% improvement") and demands low-level knowledge (memory/concurrency).

---

[vidoe](https://www.youtube.com/watch?v=c0TnU_QSlDg)