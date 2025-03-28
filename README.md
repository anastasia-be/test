# GitHub Issue Analyzer

A web application that analyzes GitHub issues from the ESP-IDF repository, providing insights about issue sentiment, priority, and suggested actions.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/anastasia-be/test.git
cd test
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up your GitHub API token:
   - Go to GitHub Settings -> Developer Settings -> Personal Access Tokens
   - Generate a new token with `repo` scope
   - Create a `.env` file in the project root and add your token:
   ```
   GITHUB_TOKEN=your_token_here
   ```

## Running the Application

1. Start the server:
```bash
./start_server.sh
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5001
```

3. Enter an ESP-IDF issue number (e.g., 12786) and click "Analyze Issue"

## Features

- Issue details display (title, creator, creation date, status)
- Sentiment analysis
- Priority assessment
- Suggested actions
- Improvement suggestions
- Comment analysis

## Troubleshooting

If you encounter any issues:

1. Check the server logs in `server.log`
2. Ensure your GitHub token is valid and has the correct permissions
3. Make sure all required packages are installed
4. Verify that port 5001 is not in use by another application

## Stopping the Application

To stop the server, run:
```bash
./stop_server.sh
```

## Note

The application uses the GitHub API to fetch issue data. Please be mindful of API rate limits when making multiple requests. 