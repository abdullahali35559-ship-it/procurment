# Procurement Agent 🚀

An Intelligent Tender Processing System designed for modern procurement workflows. This agent acts as the "**Intelligent Front Gate**," automatically extracting critical data from complex tender packages (PDF, Excel, Images) and preparing them for the Procurement Agent.

## ✨ Key Features

- **🧠 OpenRouter Integration**: Powered by **Gemma 3 12B** via OpenRouter for high-performance extraction and cost-efficiency.
- **📊 Real-time Progress Tracking**: A dynamic dashboard UI that shows the agent's live status and batch progress.
- **📧 Multi-Provider Email Ingestion**: Seamless integration with **Gmail** and **Outlook (Office 365)** using OAuth2.
- **📋 Procurement Generator**: Automatically drafts clarification emails for missing documents or metadata.
- **📂 Standardized Storage**: Strict 01-08 folder hierarchy for organized tender management.
- **⚡ Fast-API Backend**: High-performance asynchronous API for real-time data access.

## 🏗️ Project Structure

```text
/Procurement-Agent/
├── agents/           # Core AI Logic (Classification, Extraction, Procurements)
├── api/              # FastAPI Endpoints & OAuth Callbacks
├── config/           # App Settings, Database Config, and LLM Prompts
├── database/         # SQLAlchemy Models & Migrations
├── integrations/     # Gmail/Outlook Listeners & Storage Handlers
├── models/           # Unified LLM Client (OpenRouter/Ollama)
├── scripts/          # Background Processors & Run Scripts
├── ui/               # Modern Dashboard (HTML/JS/CSS)
└── storage/          # Tender file storage (Mandatory 01-08 structure)
```

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- PostgreSQL
- OpenRouter API Key (for Claude 3.5 Sonnet)
- **ClamAV** (Optional but recommended for malware scanning):
  - On Linux: `sudo apt-get install clamav clamav-daemon`
  - On Windows: Download and install from [ClamAV.net](https://www.clamav.net/) and add to PATH.

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Configuration
Rename `.env.example` (or edit existing `.env`) and add your credentials:
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

### 4. Running the App
Start the Web Dashboard:
```bash
python -m uvicorn api.main:app --reload
```

Start the Email Monitoring Agent:
```bash
python scripts/run_procurement_agent.py
```

## 📂 Mandatory Tender Structure
1. `01_Instructions` - ITT & Rules
2. `02_Scope_of_Work` - SOW Documents
3. `03_Drawings` - Drawings & Site Maps
4. `04_Specifications` - Technical Specs
5. `05_BOQ` - Bill of Quantities
6. `06_Standards` - SBC, SASO Standards
7. `07_Commercial` - Terms & Bonds
8. `08_Output` - AI Intelligence & JSON metadata

---
Developed for high-efficiency procurement teams. 🛠️
