```markdown
# 🤖 Robotics Job Agent

Multi-site job search agent for robotics roles in Germany, powered by LangChain + Ollama.  
It can search **LinkedIn**, **Indeed (Germany)**, and **Jobbörse (Bundesagentur für Arbeit)** for jobs posted in the **last 24 hours**.

---

## ✨ Features

- 🔍 **Multi-site search**
  - LinkedIn (scraped with Playwright + BeautifulSoup)
  - Indeed Germany (scraped with Playwright + BeautifulSoup)
  - Jobbörse / Bundesagentur für Arbeit (via official REST API)
- 🧠 **LLM-powered agent** (LangChain `create_agent` + local Ollama model)
- 🧱 **Modular architecture**
  - `agents/` – agent assembly
  - `llms/` – LLM factory
  - `tools/` – one tool/scraper per job website
  - `utils/` – formatting helpers
  - `config.py` – central configuration
- 🧪 Easy to extend – add a new job website by:
  - creating a new scraper in `tools/`
  - registering it in `tools/tool_factory.py`

> ⚠️ **Not production-ready**: LinkedIn & Indeed scrapers are brittle by design and will break when HTML changes. This is a personal / learning tool.

---

## 🧰 Tech Stack

- **Python** 3.10+
- **LangChain** (`langchain`, `langchain-core`, `langchain-ollama`)
- **Ollama** (local LLM, e.g. `qwen3.5:9b`)
- **Playwright** (browser automation) + **BeautifulSoup4** (HTML parsing)
- **Requests** (for Jobbörse REST API)
- CLI entrypoint via `main.py`

---

## 📁 Project Structure

```bash
.
├── .env                  # your local env vars (NOT committed)
├── .env.example          # template of required env vars
├── .gitignore
├── README.md
├── requirements.txt
│
├── config.py             # model name, temperature, filters, prompts, etc.
│
├── main.py               # CLI entry, runs the agent
│
├── agents/
│   ├── __init__.py
│   └── job_agent.py      # builds the LangChain agent (LLM + tools + prompt)
│
├── llms/
│   ├── __init__.py
│   └── llm_factory.py    # returns configured LLM (Ollama ChatOllama)
│
├── tools/
│   ├── __init__.py
│   ├── linkedin_scraper.py   # LinkedIn scraper (Playwright + BS4)
│   ├── indeed_scraper.py     # Indeed.de scraper (Playwright + BS4)
│   ├── jobboerse_scraper.py  # Jobbörse scraper (official REST API)
│   └── tool_factory.py       # returns list of all tools for the agent
│
└── utils/
    ├── __init__.py
    └── output_formatter.py   # shared formatting helpers for results
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python **3.10+**
-  installed and running locally
- A model available in Ollama, e.g.:

```bash
ollama pull qwen3.5:9b
```

> If you change the model name, update it in `config.py`.

---

### 2. Clone & Create Virtual Environment

```bash
git clone <YOUR_REPO_URL>.git
cd <YOUR_REPO_NAME>

python -m venv .venv
source .venv/bin/activate      # on macOS/Linux
# .venv\Scripts\activate       # on Windows
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Playwright also needs its browser binaries:

```bash
playwright install
```

---

### 4. Environment Variables

This project doesn’t strictly require any API keys right now (Ollama is local), but `./.env` is reserved for future use (e.g. switching to OpenAI, Kimi, etc.).

Example `.env.example`:

```bash
# Example only – not required with the current Ollama setup
OPENAI_API_KEY=your_api_key_here
KIMI_API_KEY=your_api_key_here
```

- Copy to `.env` and fill in values when/if you add cloud LLMs.
- `.env` is **gitignored** on purpose.

---

## 🏃‍♂️ Running the Agent

From the project root:

```bash
python main.py
```

By default (current version), `main.py`:

- builds a job search agent (`create_job_agent()` from `agents/job_agent.py`)
- asks it to:
  - find robotics-related jobs in Hamburg, Germany
  - posted in the last 24 hours
  - across LinkedIn, Indeed, and Jobbörse
- prints a formatted list of results to the terminal

To change the query, edit the `content` field inside `main.py`:

```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": (
            "Find robotics / Robotik jobs posted in the last 24 hours "
            "in Hamburg Germany on LinkedIn, Indeed, and Jobbörse."
        )
    }]
})
```

---

## 🧠 How It Works

### 1. LLM Setup (`llms/llm_factory.py` + `config.py`)

```python
# config.py
LLM_MODEL       = "qwen3.5:9b"
LLM_TEMPERATURE = 0
SYSTEM_PROMPT = (
    "You are a precise job search agent. "
    "Search for jobs posted in the last 24 hours in Germany."
)
```

```python
# llms/llm_factory.py
from langchain_ollama import ChatOllama
from config import LLM_MODEL, LLM_TEMPERATURE

def get_llm():
    return ChatOllama(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
```

You can swap to another local model by changing `LLM_MODEL` in `config.py`.

---

### 2. Tools / Scrapers (`tools/`)

Each site has its own tool function decorated with `@tool` so LangChain can call it:

- `scrape_linkedin_jobs(keyword, location)`
- `scrape_indeed_jobs(keyword, location)`
- `scrape_jobboerse_jobs(keyword, location)`

They are registered in `tools/tool_factory.py`:

```python
from tools.linkedin_scraper  import scrape_linkedin_jobs
from tools.indeed_scraper    import scrape_indeed_jobs
from tools.jobboerse_scraper import scrape_jobboerse_jobs

def get_tools() -> list:
    return [
        scrape_linkedin_jobs,
        scrape_indeed_jobs,
        scrape_jobboerse_jobs,
    ]
```

#### LinkedIn & Indeed

- Use **Playwright** to load content and bypass basic bot detection
- Use **BeautifulSoup** to parse rendered HTML
- Apply **site-specific CSS selectors** to extract:
  - job title
  - company
  - location
  - link
- Use filters for “last 24 hours”:
  - LinkedIn: `&f_TPR=r86400`
  - Indeed: `fromage=1`

#### Jobbörse (Bundesagentur für Arbeit)

- Uses the **official public REST API** via `requests`
- No browser/Playwright needed
- Filters on:
  - `veroeffentlichtseit=1` → last 1 day
  - `angebotsart=1` → jobs (not apprenticeships)
- Uses public header: `X-API-Key: jobboerse-jobsuche`

Because this is structured JSON, Jobbörse is **much more stable** than HTML scrapers.

---

### 3. Agent Assembly (`agents/job_agent.py`)

```python
from langchain.agents import create_agent
from llms.llm_factory import get_llm
from tools.tool_factory import get_tools
from config import SYSTEM_PROMPT

def create_job_agent():
    llm   = get_llm()
    tools = get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent
```

---

### 4. Entry Point (`main.py`)

```python
from agents.job_agent import create_job_agent

def main():
    print("🤖 Starting Robotics Job Agent...\n")

    agent = create_job_agent()

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": (
                "Find robotics / Robotik jobs posted in the last 24 hours "
                "in Hamburg Germany on LinkedIn, Indeed, and Jobbörse."
            )
        }]
    })

    final_answer = result["messages"][-1].content
    print(final_answer)

if __name__ == "__main__":
    main()
```

---

## ⚠️ Limitations & Reality Check

- **LinkedIn & Indeed scrapers are brittle**
  - Any HTML / CSS class change on the website can break the scraper
  - Fix by inspecting `debug_*.html` (if you add such dumps) and updating selectors
- **Not production-ready**
  - This is a personal / learning project
  - Production systems should use:
    - official APIs (where available), or
    - third-party aggregated job APIs
- **Jobbörse is the exception**
  - Uses an official REST API → much more stable and “production-like”

---

## 🛠️ Extending the Project

### Add a New Job Website

1. Create a new file in `tools/`, e.g. `tools/glassdoor_scraper.py`
2. Implement a function decorated with `@tool`, similar to existing scrapers
3. Register it in `tools/tool_factory.py`:

```python
from tools.glassdoor_scraper import scrape_glassdoor_jobs

def get_tools() -> list:
    return [
        scrape_linkedin_jobs,
        scrape_indeed_jobs,
        scrape_jobboerse_jobs,
        scrape_glassdoor_jobs,   # new
    ]
```

### Future Enhancements (Roadmap Ideas)

- [ ] Add `argparse` to `main.py` to accept CLI args:
  - `--keyword`, `--location`, `--sites`
- [ ] Config-driven generic scraper to reduce duplicated scraper code
- [ ] Add logging & error monitoring
- [ ] Add unit tests for formatters and API parsing
- [ ] Optional: Dockerfile for reproducible environment

---

## 📜 License

Add your license information here (e.g. MIT, Apache 2.0, etc.).

---