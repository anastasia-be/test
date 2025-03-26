function sayHello() {
    alert("Hello! Welcome to my first web app!");
}

function changeBackgroundColor() {
    const colors = [
        '#f0f0f0', // light gray
        '#ffebee', // light red
        '#e8f5e9', // light green
        '#e3f2fd', // light blue
        '#fff3e0', // light orange
        '#f3e5f5'  // light purple
    ];
    
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    document.body.style.backgroundColor = randomColor;
}

async function analyzeIssue() {
    const issueNumber = document.getElementById('issueNumber').value;
    const resultDiv = document.getElementById('analysisResult');
    
    if (!issueNumber) {
        resultDiv.innerHTML = '<div class="error">Please enter an issue number</div>';
        resultDiv.classList.add('visible');
        return;
    }

    try {
        resultDiv.innerHTML = '<p>Analyzing issue...</p>';
        resultDiv.classList.add('visible');

        const response = await fetch(`/analyze/${issueNumber}`);
        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }

        resultDiv.innerHTML = `
            <h2>Analysis Results</h2>
            <p><strong>Title:</strong> ${data.title}</p>
            <p><strong>Sentiment:</strong> ${data.sentiment}</p>
            <p><strong>Summary:</strong> ${data.summary}</p>
            <p><strong>Key Points:</strong></p>
            <ul>
                ${data.key_points.map(point => `<li>${point}</li>`).join('')}
            </ul>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<div class="error">Error analyzing issue: ${error.message}</div>`;
    }
}

function displayAnalysisResult(data) {
    const resultDiv = document.getElementById('analysisResult');
    const sentimentClass = getSentimentClass(data.sentiment);
    
    resultDiv.innerHTML = `
        <div class="result-item">
            <h3>Issue #${data.issue_number}: ${data.title}</h3>
            <p><strong>Creator:</strong> ${data.creator}</p>
            <p><strong>Created:</strong> ${new Date(data.creation_date).toLocaleDateString()}</p>
            <p><strong>Comments:</strong> ${data.total_comments} (${data.unique_users} unique users)</p>
        </div>
        <div class="result-item">
            <h4>Analysis Results:</h4>
            <p><strong>Sentiment:</strong> <span class="${sentimentClass}">${data.sentiment}</span></p>
            <p><strong>Priority:</strong> ${data.priority}</p>
            <p><strong>Suggested Actions:</strong> ${data.suggested_actions}</p>
            <p><strong>Improvement Suggestion:</strong> ${data.improvement_suggestion}</p>
        </div>
    `;
}

function getSentimentClass(sentiment) {
    switch(sentiment) {
        case 'very_frustrated':
        case 'frustrated':
            return 'sentiment-high';
        case 'mildly_frustrated':
        case 'neutral':
            return 'sentiment-medium';
        case 'happy':
        case 'very_happy':
            return 'sentiment-low';
        default:
            return '';
    }
}
  