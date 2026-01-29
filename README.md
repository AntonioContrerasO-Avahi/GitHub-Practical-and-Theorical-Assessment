# GitHub Practical and Theoretical Assessment

A CV extraction and analysis system using LangChain and AWS Bedrock.

## Overview

This project demonstrates a conversational AI agent that analyzes CVs/resumes. The agent uses AWS Bedrock's Nova Pro model through LangChain to extract information, answer questions, and provide insights about candidate profiles.

**Key Features:**
- Conversational interface for CV analysis
- Professional summary generation
- Chat history for contextual conversations
- Structured CV data extraction using Pydantic schemas
- AWS Bedrock integration (Nova Pro model)

## Project Structure

```
.
├── agents/
│   ├── agent.py       # CVExtractionAgent implementation
│   ├── chatbot.py     # Main chatbot interface
│   ├── templates.py   # LangChain prompt templates
│   └── schemas.py     # Pydantic CV data models
├── examples/
│   └── sample_cv.txt  # Sample CV for testing
└── pyproject.toml     # Project dependencies (managed by uv)
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GitHub-Practical-and-Theorical-Assessment
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure AWS credentials**
   ```bash
   aws configure
   ```
   Enter your AWS Access Key ID, Secret Access Key, and region when prompted.

4. **Run the chatbot**
   ```bash
   python agents/chatbot.py
   ```

## Usage

The chatbot will:
1. Load a CV from the `examples/` folder (default: `sample_cv.txt`)
2. Generate an initial professional summary
3. Enter chat mode where you can ask questions about the CV

**Available commands:**
- `summary` - Generate a new professional summary
- `clear` - Clear chat history
- `quit` - Exit the chatbot

## Requirements

- Python 3.12+
- AWS account with Bedrock access (Nova Pro model enabled)
- Valid AWS credentials configured