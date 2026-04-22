# config.py - Global configuration, constants and API 

# ─────────────────────────────────────────
# LLM Configuration
# ─────────────────────────────────────────
LLM_MODEL       = "qwen3.6:35b-a3b-q4_K_M"
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
MAX_JOBS_DISPLAY  = 100         # Max job cards to return