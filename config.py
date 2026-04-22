# config.py - Global configuration, constants and API 

# ─────────────────────────────────────────
# LLM Configuration
# ─────────────────────────────────────────
LLM_MODEL       = "qwen3.5:9b"
LLM_TEMPERATURE = 0

# ─────────────────────────────────────────
# Agent Configuration
# ─────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a precise job search agent. Search for jobs posted in Germany."
)

# ─────────────────────────────────────────
# Scraper Configuration
# ─────────────────────────────────────────
JOBS_TIME_FILTER  = "r86400"   # Last 24 hours (LinkedIn filter code)
MAX_JOBS_DISPLAY  = 10         # Max job cards to return