# ◈ ResearchMind — Bioluminescent Multi-Agent Research System

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/framework-LangChain-green.svg)](https://github.com/langchain-ai/langchain)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![Model](https://img.shields.io/badge/LLM-Mistral--Medium-orange.svg)](https://mistral.ai/)

**ResearchMind** is a production-grade, distributed-agent orchestration pipeline that automates the deep research process. By connecting four specialized AI nodes on a single trace, the system automatically transitions from a user query to web search, deep HTML content extraction, professional report generation, and automated critique evaluation.

Featuring a bespoke, high-performance terminal UI themed with a bioluminescent design, ResearchMind illustrates how sequential LLM orchestration can replace manual, multi-tab information gathering with single-click sourced intelligence.

---

## 🏗️ System Architecture & Workflow

The system is designed around a decoupled, sequential agent architecture. Rather than relying on a single monolithic prompt, the workload is decomposed into four discrete, state-preserving phases.

### Agent Orchestration Flow

```mermaid
graph TD
    User([User Research Query]) -->|Input| App[Streamlit State Controller]
    
    subgraph Pipeline [The Signal Rail Orchestration]
        App -->|Stage 1: Trigger| SearchAgent[01. Search Agent]
        SearchAgent -->|Tavily API| Web((The Internet))
        Web -->|Results: Titles, URLs, Snippets| SearchAgent
        SearchAgent -->|State Update & Rerun| App
        
        App -->|Stage 2: Trigger| ReaderAgent[02. Reader Agent]
        ReaderAgent -->|HTTP GET Request| TargetSites[Web Scraping Engine]
        TargetSites -->|Cleaned Text Extract| ReaderAgent
        ReaderAgent -->|State Update & Rerun| App
        
        App -->|Stage 3: Trigger| WriterChain[03. Writer Chain]
        WriterChain -->|Synthesizes Search + Scraped Data| WriterChain
        WriterChain -->|Drafts Markdown Report| App
        
        App -->|Stage 4: Trigger| CriticChain[04. Critic Chain]
        CriticChain -->|Strict Evaluation rubric| CriticChain
        CriticChain -->|Scorecard & Improvements| App
    end
    
    App -->|Render Outputs| UI[Bespoke UI Terminal View]
    UI -->|Interactive Download| MD[Markdown Report Export]
```

### The State Machine (Sequential Lifecycle Execution)

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant App as Streamlit Orchestrator
    participant State as Session State
    participant Agents as LangChain Agents & Tools
    
    User->>App: Input Query & Click RUN PIPELINE
    App->>State: Initialize State & Set Running = True
    
    loop Phase Execution (One Stage per Script Pass)
        Note over App,State: Stage 1: Web Searching
        App->>Agents: Build & Invoke Search Agent (web_search tool)
        Agents-->>App: Return Search Results (Structured URLs)
        App->>State: Store Search Result
        App->>App: Trigger Rerun (st.rerun)
        
        Note over App,State: Stage 2: Target Site Scraping
        App->>Agents: Build & Invoke Reader Agent (scrape_url tool)
        Agents-->>App: Clean Text Extract (max 3000 chars)
        App->>State: Store Scraped Contents
        App->>App: Trigger Rerun (st.rerun)
        
        Note over App,State: Stage 3: Report Synthesis
        App->>Agents: Invoke Writer Chain (structured prompt)
        Agents-->>App: Generated Draft Report (Markdown)
        App->>State: Store Draft Report
        App->>App: Trigger Rerun (st.rerun)
        
        Note over App,State: Stage 4: Critical Review
        App->>Agents: Invoke Critic Chain (evaluation rubric)
        Agents-->>App: Metric Score & Feedback Details
        App->>State: Store Critic feedback & Set Running = False
        App->>App: Trigger Final Rerun (st.rerun)
    end
    App-->>User: Render Dashboard (Circular Score Dial, TOC, Interactive Reports)
```

---

## 🛠️ Pipeline Stages & Node Breakdown

### 01. Search Agent (`agents.py` / `tools.py`)
* **Role**: Information Harvester.
* **Mechanism**: Utilizes `ChatMistralAI` coupled with the `TavilyClient` API.
* **Prompt Mandate**: Strictly prohibited from answering using internal LLM weights. It must use the `web_search` tool and format output as:
  ```text
  Title: [Article Title]
  URL: [Target URL]
  Summary: [Snippet Description]
  ```

### 02. Reader Agent (`agents.py` / `tools.py`)
* **Role**: Content Deep-Diver.
* **Mechanism**: Runs a robust web scraper powered by Python `requests` and `BeautifulSoup4`.
* **Token Denoising**: Automatically filters and decomposes high-noise tags (e.g., `<script>`, `<style>`, `<nav>`, `<footer>`) to maximize context-window density.
* **Output**: Extracts up to 3,000 characters of clean body text from the primary source URLs identified in the search step.

### 03. Writer Chain (`agents.py`)
* **Role**: Lead Synthesizer.
* **Mechanism**: A deterministic LangChain expression language (LCEL) chain (`writer_prompt | llm | StrOutputParser`).
* **Format**: Consolidates scraped research and formats a professional document consisting of an *Introduction*, *Key Findings* (minimum 3 deeply analyzed items), a *Conclusion*, and *Sourced References*.

### 04. Critic Chain (`agents.py`)
* **Role**: Quality Assurance.
* **Mechanism**: An independent evaluation chain that reviews the drafted report against a strict structural and factual rubric.
* **Evaluation Metrics**: Computes an objective numeric score (`Score: X/10`), highlights strengths, lists specific areas for improvement, and issues a final, one-line verdict.

---

## 💾 Technical Stack & Tooling

| Layer | Component | Description |
| :--- | :--- | :--- |
| **Core Framework** | `langchain` / `langchain-core` | Declarative agent definition, tool binding, and LLM orchestration. |
| **Language Model** | `ChatMistralAI` (`mistral-medium-3-5`) | Low-latency inference, strict template compliance, and structured returns. |
| **External Search** | `tavily-python` | Specialized developer search engine for real-time web grounding. |
| **Web Scraping** | `beautifulsoup4` / `requests` / `lxml` | Clean raw HTML processing and structural component decomposition. |
| **UI Framework** | `streamlit` | Reactive state management and customized UI components. |
| **Robustness** | `tenacity` | Adaptive back-off and retry logic for network dependencies. |
| **UX & Logging** | `rich` | Terminal visualization and pipeline tracing logs. |

---

## 📝 Production Engineering Design Logs

> [!NOTE]
> *Reflections from a Senior Production Engineer on the design constraints, architecture compromises, and robustness safeguards implemented in this codebase.*

### 1. State Preservation Over a Stateless UI (Streamlit Rerun Loop)
Streamlit executes files linearly from top-to-bottom on every user interaction or state update. Executing a long-running multi-stage AI pipeline in a single Streamlit script execution runs a high risk of browser timeouts, API blocks, or screen-freezes. 
* **The Solution**: We modeled the execution as a **state-machine execution loop**. The pipeline executes exactly **one** agent phase per script run, updates `st.session_state` with the result, and immediately triggers `st.rerun()`.
* **The Benefit**: This creates an asynchronous feel in a synchronous UI. The visual "Signal Rail" updates in real-time, showing precisely which node is active, and guarantees that if an API call fails at Stage 4, the data from Stages 1-3 is safely cached in memory rather than lost.

### 2. The Scraping Denoising Strategy & Token Economy
Raw web scraping averages 50KB to 200KB of HTML markup, navigation blocks, scripts, and CSS style rules. Passing this raw string into an LLM context is highly inefficient—wasting tokens, increasing latency, and cloud costs.
* **The Solution**: The `scrape_url` tool actively decomposes noisy subtrees:
  ```python
  for tag in soup(["script", "style", "nav", "footer"]):
      tag.decompose()
  ```
  Additionally, text extraction is sliced to the top 3,000 characters using `get_text(separator=" ", strip=True)[:3000]`. This cleans the input payload by up to 90% while keeping the primary semantic body context intact.

### 3. Graceful Network Exceptions and Boundaries
When designing agentic workflows, the outside network is the most frequent point of failure. Websites implement DDoS protection, return HTTP 403 errors, or timeout.
* **The Solution**: Inside `pipeline.py` and `tools.py`, every web scraper call is wrapped in defensive try-except blocks:
  ```python
  try:
      resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
      ...
  except Exception as e:
      return f"Could not scrape URL: {str(e)}"
  ```
  If a single site fails to scrape, the system logs the failure, saves the error boundary trace to the scraped contents pool, and moves on to the next source. A single broken network link will **never** trigger a pipeline crash.

### 4. Decoupling Synthesis and Evaluation (Writer vs. Critic)
Combining writing and editing inside a single prompt creates a confirmation bias where the LLM struggles to find issues in its own output.
* **The Solution**: Decoupled the generation stage (`WriterChain`) from the inspection stage (`CriticChain`). The Critic has a strict, separate system instruction set that forces it to act as an adversarial editor, generating a metrics dial from 0 to 100 based on a strict X/10 parsing format.

---

## ⚡ Setup & Installation

Follow these steps to deploy and run ResearchMind locally:

### 1. Clone & Set Up Directory
Navigate to the root project folder:
```bash
cd "Multi Agent Research System"
```

### 2. Configure Virtual Environment
Create and activate a clean Python virtual environment to avoid dependency conflicts:
```bash
# Create
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries specified in the manifest:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and insert your developer API credentials:
```env
MISTRAL_API_KEY="your_mistral_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"
```

---

## 🚀 Execution & Usage

ResearchMind can be operated in two modes:

### Mode A: Bespoke UI (Streamlit Web Dashboard)
To run the high-fidelity web application:
```bash
streamlit run app.py
```
1. Open the URL shown in your terminal (usually `http://localhost:8501`).
2. Input a target topic (e.g., *"LLM agents breakthroughs in 2025"*).
3. Click **RUN PIPELINE**.
4. Monitor the active signal green rails as the pipeline steps from 01 to 04.
5. Review the final report, dynamic score dial, and click **Download report (.md)** to save your research locally.

### Mode B: CLI Pipeline (Lightweight Terminal Run)
To execute the pipeline directly in the terminal:
```bash
python pipeline.py
```
1. Enter your research topic in the terminal prompt.
2. Watch the step logs output information as the pipeline processes.
3. The final synthesized report and critic review will print directly to the console.
