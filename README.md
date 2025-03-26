# GitHub Issue Analyzer

This application analyzes GitHub issues using OpenAI's GPT model to provide insights and suggestions.

## Setup Instructions

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your API keys:
     - Get an OpenAI API key from: https://platform.openai.com/api-keys
     - Get a GitHub token from: https://github.com/settings/tokens
     - Add them to the `.env` file:
       ```
       OPENAI_API_KEY=your-openai-key-here
       GITHUB_TOKEN=your-github-token-here
       ```

## Running the Application

1. Start the server:
```bash
python server.py
```

2. Open your browser and navigate to:
```
http://localhost:5001
```

3. Enter a GitHub issue number to analyze (e.g., 15651)

## Features

- Analyzes GitHub issues for sentiment and priority
- Provides suggested actions and improvement suggestions
- Extracts key points from issue discussions
- Generates summaries of issue content

## Note

Make sure to keep your `.env` file secure and never commit it to version control. The `.env.example` file is provided as a template for setting up your environment variables. 