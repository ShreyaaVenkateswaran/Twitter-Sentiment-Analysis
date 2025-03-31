document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const videoId = document.getElementById('videoId').value.trim();
    if (!videoId) return;
    
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    
    results.classList.add('hidden');
    error.classList.add('hidden');
    loading.classList.remove('hidden');
    
    try {
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_id: videoId, max_comments: 100 })
        });
        
        if (!response.ok) throw new Error(await response.text());
        
        const data = await response.json();
        displayResults(data);
    } catch (err) {
        error.textContent = `Error: ${err.message}`;
        error.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
    }
});

function displayResults(data) {
    // Update summary
    const total = data.total_comments;
    const positivePercent = Math.round((data.positive / total) * 100);
    const neutralPercent = Math.round((data.neutral / total) * 100);
    const negativePercent = Math.round((data.negative / total) * 100);
    
    document.getElementById('positiveMeter').style.width = `${positivePercent}%`;
    document.getElementById('neutralMeter').style.width = `${neutralPercent}%`;
    document.getElementById('negativeMeter').style.width = `${negativePercent}%`;
    
    document.getElementById('positiveText').textContent = 
        `Positive: ${positivePercent}% (${data.positive})`;
    document.getElementById('neutralText').textContent = 
        `Neutral: ${neutralPercent}% (${data.neutral})`;
    document.getElementById('negativeText').textContent = 
        `Negative: ${negativePercent}% (${data.negative})`;
    
    // Display sample comments
    const container = document.getElementById('commentsContainer');
    container.innerHTML = '';
    data.comments.forEach(comment => {
        const div = document.createElement('div');
        div.className = `comment ${comment.sentiment}-comment`;
        div.innerHTML = `
            <p><strong>${comment.sentiment.toUpperCase()}</strong> (${comment.polarity.toFixed(2)})</p>
            <p>${comment.text}</p>
        `;
        container.appendChild(div);
    });
    
    document.getElementById('results').classList.remove('hidden');
}