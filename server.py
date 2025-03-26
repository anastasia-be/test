from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import openai
from datetime import timezone, datetime
import re
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load API Keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

print(f"Loaded GitHub token: {GITHUB_TOKEN[:10]}...")  # Print first 10 chars for debugging

if not OPENAI_API_KEY or not GITHUB_TOKEN:
    raise ValueError("Missing API keys! Make sure OPENAI_API_KEY and GITHUB_TOKEN are set in your .env file")

# Initialize OpenAI client without proxies
openai.api_key = OPENAI_API_KEY
openai.base_url = "https://api.openai.com/v1"

# Define function calling schema
functions = [
    {
        "name": "analyze_github_issue",
        "description": "Analyzes a GitHub issue for sentiment, priority, suggested actions, and improvement suggestions.",
        "parameters": {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "enum": ["very_frustrated", "frustrated", "mildly_frustrated", "neutral", "happy", "very_happy"],
                    "description": "Sentiment classification of the GitHub issue."
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Priority level of the issue."
                },
                "suggested_actions": {
                    "type": "string",
                    "description": "Recommended actions based on the issue sentiment."
                },
                "improvement_suggestion": {
                    "type": "string",
                    "description": "A one-sentence suggestion to improve the GitHub issue."
                }
            },
            "required": ["sentiment", "priority", "suggested_actions", "improvement_suggestion"]
        }
    }
]

# GitHub Repository Info
OWNER = "espressif"
REPO = "esp-idf"
GITHUB_API_BASE = "https://api.github.com"

def get_github_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_issue(issue_number):
    """Fetch issue details from GitHub API."""
    url = f"{GITHUB_API_BASE}/repos/{OWNER}/{REPO}/issues/{issue_number}"
    response = requests.get(url, headers=get_github_headers())
    response.raise_for_status()
    return response.json()

def get_issue_comments(issue_number):
    """Fetch issue comments from GitHub API."""
    url = f"{GITHUB_API_BASE}/repos/{OWNER}/{REPO}/issues/{issue_number}/comments"
    response = requests.get(url, headers=get_github_headers())
    response.raise_for_status()
    return response.json()

def clean_issue_text(issue_data, comments_data, max_comment_length=200):
    """Cleans the issue text and removes log-like content."""
    cleaned_text = f"Issue Title: {issue_data['title']}\n\n"
    cleaned_text += f"Issue Created: {issue_data['created_at']}\n\n"
    cleaned_text += f"Issue Body (Cleaned): {remove_log_like_text(remove_debug_logs(issue_data['body']))}\n\n"
    
    for comment in comments_data:
        cleaned_comment = truncate_comments(remove_log_like_text(remove_debug_logs(comment['body'])), max_comment_length)
        cleaned_text += f"Comment by {comment['user']['login']} at {comment['created_at']}:\n{cleaned_comment}\n\n"
    
    return cleaned_text, len(comments_data), len(set(comment['user']['login'] for comment in comments_data))

def remove_debug_logs(text):
    """Removes debug logs enclosed in triple backticks."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL).strip()

def remove_log_like_text(text):
    """Removes log-like lines (e.g., 'E (1234) Error: Something went wrong')."""
    return re.sub(r"^[A-Z]\s*\(\d+\)\s\w+:.*$", "", text, flags=re.MULTILINE).strip()

def truncate_comments(text, max_length=200):
    """Truncates long comments to the specified length."""
    return text[:max_length] + "..." if len(text) > max_length else text

def format_issue_prompt(cleaned_text, total_comments, unique_users, creation_date):
    return f"""
You are an AI assistant analyzing GitHub issues. Your task is to classify the sentiment of the issue and comments, prioritize the issue, and suggest actions.
Issue Details:
- Cleaned Text: {cleaned_text}
- Total Comments: {total_comments}
- Unique Users: {unique_users}
- Days Since Creation: {creation_date}
Provide:
1. Sentiment classification (one of: very_frustrated, frustrated, mildly_frustrated, neutral, happy, very_happy).
2. Priority (high, medium, low).
3. Suggested actions.
4. A one-sentence improvement suggestion.
"""

def get_completion(cleaned_text, total_comments, unique_users, creation_date, model="gpt-4"):
    """Calls GPT and returns structured output."""
    prompt = format_issue_prompt(cleaned_text, total_comments, unique_users, creation_date)
    messages = [{"role": "system", "content": "You are an AI assistant analyzing GitHub issues. Provide your analysis in JSON format with the following fields: sentiment (one of: very_frustrated, frustrated, mildly_frustrated, neutral, happy, very_happy), priority (high, medium, low), suggested_actions, and improvement_suggestion."},
                {"role": "user", "content": prompt}]
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.3
    )
    
    # Parse the response to get structured data
    try:
        # Extract JSON from the response
        response_text = response.choices[0].message.content
        # Find JSON-like content between triple backticks if present
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        # Parse the JSON response
        analysis = json.loads(response_text)
        
        # Validate required fields
        required_fields = ['sentiment', 'priority', 'suggested_actions', 'improvement_suggestion']
        for field in required_fields:
            if field not in analysis:
                raise ValueError(f"Missing required field: {field}")
        
        return analysis
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response_text}")
        raise

def extract_key_points(text):
    """Extracts key points from the issue text using OpenAI."""
    prompt = f"""
    Extract 3-5 key points from this GitHub issue text. Focus on the main problems, solutions, or important information.
    Format each point as a clear, concise sentence.
    
    Issue Text:
    {text}
    
    Return only the key points, one per line.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts key points from GitHub issues."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    # Split the response into individual points and clean them
    points = [point.strip() for point in response.choices[0].message.content.split('\n') if point.strip()]
    return points[:5]  # Limit to 5 points maximum

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/analyze/<int:issue_number>')
def analyze_issue(issue_number):
    try:
        # Get the issue and comments
        issue_data = get_issue(issue_number)
        comments_data = get_issue_comments(issue_number)
        
        # Clean and format the issue text
        cleaned_text, total_comments, unique_users = clean_issue_text(issue_data, comments_data)
        
        # Calculate days since creation using timestamps
        current_timestamp = datetime.now(timezone.utc).timestamp()
        issue_timestamp = datetime.fromisoformat(issue_data['created_at'].replace('Z', '+00:00')).timestamp()
        creation_date = int((current_timestamp - issue_timestamp) / (24 * 60 * 60))
        
        # Get analysis from OpenAI
        analysis = get_completion(cleaned_text, total_comments, unique_users, creation_date)
        
        # Extract key points from the issue
        key_points = extract_key_points(cleaned_text)
        
        return jsonify({
            'title': issue_data['title'],
            'sentiment': analysis['sentiment'],
            'summary': analysis['suggested_actions'],
            'key_points': key_points
        })
    except Exception as e:
        print(f"Error analyzing issue: {str(e)}")  # Add debug logging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the server on all available interfaces with debug mode
    app.run(host='127.0.0.1', port=5001, debug=True) 