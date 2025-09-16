# FlightService AI

An experimental "Artificial Flight Service" that emulates a pre‑flight briefing assistant. Pilots enter planned flight details and the system gathers live aviation weather & airport data, then invokes an Azure AI Agent to generate a structured, safety‑focused briefing rendered as Markdown in a React UI.

## Key Features

- Pilot flight input form (aircraft, routing, timing, alternates, qualifications)
- Automated fetch of METARs / TAFs / (stub for PIREPs & additional data) via `aviationweather.gov`
- Azure AI Agent analysis pipeline (async thread → message → run → response aggregation)
- Clean separation of concerns (models, data aggregation, agent orchestration)
- React frontend with dark/light adaptive styling and secure Markdown rendering
- Environment‑driven configuration + token-based Azure auth (`DefaultAzureCredential`)

## High-Level Architecture

```
frontend (Vite + React)
	└── Submits flight plan JSON → Displays structured JSON + AI Markdown briefing

backend (Python / Flask)
	├── models.py (dataclasses / data schema)
	├── data_fetcher.py (weather & airport data aggregation)
	├── fs_agent.py (Azure AI Agent workflow)
	├── fs_server.py (API endpoint /api/flight)
	└── model_test.py (stand‑alone async agent test harness)

Azure AI (Agents)
	└── Accepts thread + user message → processes with configured agent → returns run messages
```

## Technology Stack

| Layer        | Tech |
|--------------|------|
| Frontend     | React 19, Vite, `react-markdown`, `remark-gfm`, `rehype-sanitize` |
| Backend      | Python 3, Flask, `azure-ai-projects`, `azure-ai-agents` models |
| Auth         | `DefaultAzureCredential` (CLI login / Managed Identity) |
| Data Sources | aviationweather.gov (METAR/TAF) |
| AI           | Azure AI Agents (threaded, async message workflow) |

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+ (virtual environment recommended)
- Azure subscription + configured Azure AI Project / Agent
- Logged in to Azure CLI (`az login`) or other supported credential source

## Initial Setup

### 1. Clone & Enter Project
```bash
git clone <your-fork-or-repo-url>
cd flightservice-ai
```

### 2. Python Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # (If a requirements file is later added)
```

### 3. Configure Backend Environment
Run the provided setup script (creates `backend/.env`).
```bash
./setup_environment.sh
```
You will be prompted for:
* `PROJECT_ENDPOINT` (e.g. `https://<your-project>.<region>.ai.azure.com/`)
* `AGENT_ID` (from Azure AI Studio / Foundry)

The script reminds you that authentication uses `DefaultAzureCredential`—ensure you are logged in:
```bash
az login
```

### 4. Frontend Dependencies
```bash
cd frontend
npm install
# If not already installed by previous work:
npm install react-markdown remark-gfm rehype-sanitize
```

### 5. Run Services
In two terminals:
```bash
# Terminal 1 (backend)
source .venv/bin/activate
python backend/fs_server.py

# Terminal 2 (frontend)
cd frontend
npm run dev
```

Visit the printed Vite dev server URL (default: http://localhost:5173).

## API Overview

### POST `/api/flight`
Request Body (example):
```json
{
	"pilotName": "Jane Doe",
	"pilotQualifications": "IFR",
	"flightRules": "IFR",
	"aircraftType": "C172",
	"aircraftEquipment": "GPS",
	"trueAirspeed": "115",
	"departureAirport": "KJFK",
	"destinationAirport": "KBOS",
	"takeoffTime": "2025-09-16T14:00",
	"estimatedEnroute": "1h 15m",
	"alternateAirports": "KBDR, KPVD"
}
```

Response (abridged):
```json
{
	"status": "success",
	"flight_info": {
		"pilot_data": { ... },
		"online_resources": { "weather": {"metar": ...}, ... },
		"ai_analysis": { "briefing": "# Briefing\n...markdown..." }
	}
}
```

## Azure AI Agent Flow

`FlightServiceAgent` now uses an explicit async workflow:
1. Create thread
2. Post user-composed prompt (includes pilot + weather + route info)
3. `create_and_process` run
4. Iterate messages (paged async) filtering by `run_id`
5. Aggregate assistant text → return
6. Delete thread (cleanup)

## Frontend Briefing Rendering

Returned Markdown is rendered safely:
- `react-markdown` + `remark-gfm` for GFM features (lists, tables)
- `rehype-sanitize` strips unsafe HTML
- Custom CSS (`.markdown-briefing`) adjusts readability + dark mode harmony

## Development Tips

- If Azure auth fails, ensure: `az login` succeeded and `PROJECT_ENDPOINT` matches your configured project.
- To debug raw agent output, you can temporarily log intermediate messages in `fs_agent.py`.
- Keep threads short—excess historical context not yet persisted intentionally.

## Troubleshooting
| Issue | Possible Cause | Fix |
|-------|----------------|-----|
| `DefaultAzureCredential failed` | Not logged into Azure | Run `az login` |
| Empty `briefing` | Agent returned no assistant messages | Check prompt size / agent configuration |
| CORS error in browser | Backend missing allowed origin | Ensure `CORS_ORIGINS` in `.env` includes frontend URL |
| Slow response | External weather API latency or AI run time | Increase `API_TIMEOUT` or add progressive UI state |

## Security Considerations

- No API key persisted—token auth via Azure identity chain.
- Environment variables isolated to backend `.env` (ignored by Git).
- Sanitized Markdown prevents script injection in the frontend.

## Roadmap / Potential Enhancements

- Add PIREPs / NOTAMs / winds aloft ingestion
- Sectioned structured AI output (JSON schema + deterministic rendering)
- Streaming partial analysis (Server-Sent Events or WebSocket)
- Risk scoring model (numerical factors + color coding)
- Export briefing to PDF / Markdown download
- Authentication + user sessions for multi-pilot usage
- Caching layer for repeated weather lookups
- Unit/integration tests (pytest) + contract tests for agent prompt changes

## Contributing
1. Fork / feature branch
2. Follow existing code style (Black / Ruff can be added later)
3. Provide concise PR description & test evidence

## License

Currently unlicensed (all rights reserved). Add an OSS license (MIT/Apache-2.0) if you plan to distribute.

---
Questions or ideas? Open an issue or extend the roadmap section.

