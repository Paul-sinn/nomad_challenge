# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses `uv` for package management and Python 3.13+.

```bash
# Install dependencies
uv sync

# Run the Streamlit UI
uv run streamlit run <app_file>.py

# Launch Jupyter for notebook work
uv run jupyter notebook

# Add a dependency
uv add <package>
```

There are no tests or linters configured.

## Architecture

This is an experimental LLM agent project (NomadCoders challenge) with two separate experiments:

### `main.ipynb` — Movie Agent (primary work)

Uses the **OpenAI Responses API** (`client.responses.create`) with function calling to build a conversational movie assistant. The agent answers in Korean.

**Agent loop:**
1. Append user message to `messages` list (persistent conversation history)
2. Call `client.responses.create` with `TOOLS` definitions
3. If the response contains `function_call` output items, extract `tool_name` + `args`, call `call_tool()`, then send a follow-up `client.responses.create` with `previous_response_id` and `function_call_output`
4. Append final assistant response to `messages`

**Movie API** (NomadCoders wrapper around TMDB):
- Base: `https://nomad-movies.nomadcoders.workers.dev/movies`
- Endpoints: `/movies`, `/movies/{id}`, `/movies/{id}/credits`, `/movies/{id}/videos`

**Tools defined:** `get_popular_movies`, `get_movie_details`, `get_movie_credits`, `get_movie_videos`

Note: The agent currently handles only the first function call in each turn (single-step tool use, not multi-step).

### `sd.ipynb` — Simple Chat (earlier experiment)

A minimal chatbot loop using `chat.completions.create` with a persistent `messages` list. No tools.

### `life_coach.py` — LangChain Agent (in progress)

Starts with `from langchain_core.tools import tool` — a LangChain/LangGraph-based agent that is not yet implemented.

## Environment

Requires `OPENAI_API_KEY` in `.env` (already gitignored).
