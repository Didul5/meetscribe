# LegalMind Assistant

LegalMind is a legal assistant powered by AI that attends meetings, creates transcripts, and does actual-world legal work for your business. The app uses the MeetStream API to attend meetings, record transcripts, and subsequently processes these transcripts with advanced AI to pull out actionable legal information.

## Features

- ???? **Meeting Integration**: Easily attend Zoom and Google Meet meetings to record and transcribe conversations
- ???? **Automated Transcription**: Create precise transcripts of all meeting material
- ???? **AI-Powered Analysis**: Analyze meeting transcripts to determine legal conclusions and actions
- ????️ **Compliance & Risk Management**: Detect regulatory compliance, legal risks, ethics, and workplace safety concerns
- ???? **Contract Management**: Monitor contracts, renewals, and legal documents
- ???? **IP & Tech Law Support**: Monitor intellectual property, software licensing, and data privacy issues
- ???? **Corporate Governance**: Accommodate board functions and hold legal structure
- ????‍⚖️ **Litigation Management**: Monitor disputes, investigations, and M&A legal matters

## Architecture

The app is developed with Streamlit and designed into the below components:

- **UI**: Stunning, interactive user interface to visualize and oversee legal insights
- **Services**: MeetStream integration, Zoom OAuth, and AI processing frameworks
- **Models**: Legal task definitions and processors to govern insights and actions
- **Utils**: Data processing and formatting helper functions

## Setup Instructions

### Prerequisites

- Python 3.8 or greater
- Pip package manager

### Installation

1. Create the repository by cloning or directory structure:

```bash
mkdir -p legal_assistant/services legal_assistant/models legal_assistant/ui legal_assistant/utils
```

2. Install the necessary packages:

```bash
pip install streamlit requests openai pandas plotly python-dotenv
```

3. Initialize the required files as indicated in the directory structure, copying code for each file within this repository.

4. Create a root directory `.env` file that contains your API keys (if needed):

```bash
MEETSTREAM_API_URL=https://api-meetstream-tst-hackathon.meetstream.ai/api/v1
MEETSTREAM_API_KEY=ms_XQmQZPip5wmTPMNqlgUVwhqLpsnxW1sy
ZOOM_CLIENT_ID=qTMTH
```
