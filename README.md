# LegalMind Assistant

LegalMind is an AI-powered legal assistant that joins meetings, generates transcripts, and performs real-world legal tasks for your company. The application leverages the MeetStream API to join meetings, record transcripts, and then processes these transcripts using advanced AI to extract actionable legal insights.

## Features

- 🎯 **Meeting Integration**: Seamlessly join Zoom and Google Meet meetings to capture and transcribe discussions
- 📝 **Automated Transcription**: Generate accurate transcripts of all meeting content
- 🤖 **AI-Powered Analysis**: Process meeting transcripts to extract legal insights and actions
- 🛡️ **Compliance & Risk Management**: Identify regulatory compliance, legal risks, ethics, and workplace safety issues
- 🧾 **Contract Management**: Track contracts, renewals, and legal documents
- 🧠 **IP & Tech Law Support**: Monitor intellectual property, software licensing, and data privacy concerns
- 📜 **Corporate Governance**: Support board functions and maintain legal structure
- 👨‍⚖️ **Litigation Management**: Track disputes, investigations, and M&A legal aspects

## Architecture

The application is built using Streamlit and organized into the following components:

- **UI**: Beautiful, interactive user interface for visualizing and managing legal insights
- **Services**: Integration with MeetStream, Zoom OAuth, and AI processing systems
- **Models**: Legal task definitions and processors for managing insights and actions
- **Utils**: Helper functions for data processing and formatting

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Pip package manager

### Installation

1. Clone the repository or create the directory structure:

```bash
mkdir -p legal_assistant/services legal_assistant/models legal_assistant/ui legal_assistant/utils
```

2. Install the required dependencies:

```bash
pip install streamlit requests openai pandas plotly python-dotenv
```

3. Create the necessary files as shown in the directory structure, copying the code from each file in this repository.

4. Create a `.env` file in the root directory with your API keys (optional):

