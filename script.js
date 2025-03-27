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
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    
    if (!issueNumber) {
        result.innerHTML = '<div class="error">Please enter an issue number</div>';
        return;
    }

    loading.style.display = 'block';
    result.innerHTML = '';

    try {
        const response = await fetch(`/analyze/${issueNumber}`);
        const data = await response.json();

        if (response.ok) {
            result.innerHTML = `
                <div class="section">
                    <h2>Issue Summary</h2>
                    <p>${data.summary || 'No summary available'}</p>
                </div>
                <div class="section">
                    <h2>Analysis</h2>
                    <p><strong>Sentiment:</strong> <span class="sentiment-${(data.sentiment || 'neutral').toLowerCase()}">${data.sentiment || 'Neutral'}</span></p>
                    <p><strong>Priority:</strong> <span class="priority-${(data.priority || 'medium').toLowerCase()}">${data.priority || 'Medium'}</span></p>
                </div>
                <div class="section">
                    <h2>Suggested Actions</h2>
                    <ul>
                        ${(data.suggested_actions || []).map(action => `<li>${action}</li>`).join('') || '<li>No suggested actions available</li>'}
                    </ul>
                </div>
                <div class="section">
                    <h2>Improvement Suggestions</h2>
                    <ul>
                        ${(data.improvement_suggestions || []).map(suggestion => `<li>${suggestion}</li>`).join('') || '<li>No improvement suggestions available</li>'}
                    </ul>
                </div>
                <div class="section">
                    <h2>Key Points</h2>
                    <ul>
                        ${(data.key_points || []).map(point => `<li>${point}</li>`).join('') || '<li>No key points available</li>'}
                    </ul>
                </div>
            `;
        } else {
            result.innerHTML = `<div class="error">${data.error || 'Failed to analyze issue'}</div>`;
        }
    } catch (error) {
        result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    } finally {
        loading.style.display = 'none';
    }
}

// Add event listener for Enter key
document.getElementById('issueNumber').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        analyzeIssue();
    }
});

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
  