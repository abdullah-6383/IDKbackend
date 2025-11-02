// Global state management
let currentAnalysis = null;
let processSteps = [];
let debateData = null;
let resultsData = [];

// API Base URL - Update this when deploying to GCP
const API_BASE_URL = 'http://localhost:8000'; // Change to your GCP Cloud Run URL

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Information Trust Analysis System loaded');
    loadSampleData(); // Load sample data by default
});

// Tab Management
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked tab button
    event.target.classList.add('active');
}

// Load sample data
function loadSampleData() {
    document.getElementById('topic').value = 'Charles James Kirk (October 14, 1993 – September 10, 2025)';
    document.getElementById('context').value = 'at the age of 31, Kirk was assassinated by gunshot on September 10, 2025, while speaking at a TPUSA debate at Utah Valley University in Orem, Utah. His assassination garnered international attention and widespread condemnation of political violence. Donald Trump announced that Kirk would be honored posthumously. Since his death, Kirk has been considered an icon of contemporary conservatism.';
    document.getElementById('significance').value = '0.99';
    
    addLog('Sample data loaded successfully', 'info');
}

// Start the analysis process
async function startAnalysis() {
    const topic = document.getElementById('topic').value.trim();
    const context = document.getElementById('context').value.trim();
    const significance = parseFloat(document.getElementById('significance').value) || 0.8;
    
    if (!topic) {
        alert('Please enter a topic to analyze');
        return;
    }
    
    // Prepare the input data
    const inputData = {
        topic: topic,
        text: context,
        significance_score: significance
    };
    
    // Reset process status
    resetProcessStatus();
    
    // Switch to process tab
    showTab('process');
    
    // Update UI
    document.querySelector('[onclick="startAnalysis()"]').disabled = true;
    document.querySelector('[onclick="startAnalysis()"]').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    
    addLog('Starting information trust analysis...', 'info');
    addLog(`Topic: ${topic}`, 'info');
    
    try {
        // Step 1: Send data to backend
        updateStepStatus(1, 'processing', 'Sending data to analysis system...');
        await sleep(1000);
        
        // Simulate API call to start analysis
        const response = await fetch(`${API_BASE_URL}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(inputData)
        });
        
        if (response.ok) {
            updateStepStatus(1, 'completed', 'Data sent successfully');
            addLog('Analysis request sent to backend', 'success');
            
            // Start monitoring process
            await monitorAnalysisProcess();
        } else {
            throw new Error('Failed to start analysis');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        addLog(`Error: ${error.message}`, 'error');
        updateStepStatus(1, 'error', 'Failed to start analysis');
        
        // For demo purposes, simulate the process locally
        addLog('Simulating analysis process locally...', 'info');
        await simulateAnalysisProcess();
    }
    
    // Re-enable button
    document.querySelector('[onclick="startAnalysis()"]').disabled = false;
    document.querySelector('[onclick="startAnalysis()"]').innerHTML = '<i class="fas fa-play"></i> Start Analysis';
}

// Monitor the analysis process
async function monitorAnalysisProcess() {
    const steps = [
        'Data Input & Configuration',
        'Query Enhancement',
        'Google Search',
        'Content Extraction',
        'Relevance Analysis',
        'Trust Score Evaluation',
        'Results Processing'
    ];
    
    for (let i = 2; i <= 7; i++) {
        updateStepStatus(i, 'processing', `${steps[i-1]} in progress...`);
        updateProgress((i-1) / 9 * 100);
        
        // Simulate processing time
        await sleep(2000 + Math.random() * 3000);
        
        updateStepStatus(i, 'completed', `${steps[i-1]} completed`);
        addLog(`Step ${i}: ${steps[i-1]} completed`, 'success');
    }
    
    updateProgress(77);
    addLog('Analysis complete! Results processed.', 'success');
    
    // Load results (simulate or fetch from API)
    await loadResults();
}

// Simulate analysis process for demo
async function simulateAnalysisProcess() {
    const steps = [
        { name: 'Data Input & Configuration', duration: 1000 },
        { name: 'Query Enhancement', duration: 2000 },
        { name: 'Google Search', duration: 3000 },
        { name: 'Content Extraction', duration: 4000 },
        { name: 'Relevance Analysis', duration: 3000 },
        { name: 'Trust Score Evaluation', duration: 2000 },
        { name: 'Results Processing', duration: 1500 }
    ];
    
    for (let i = 0; i < steps.length; i++) {
        const stepNum = i + 2;
        updateStepStatus(stepNum, 'processing', `${steps[i].name} in progress...`);
        updateProgress((i + 1) / 9 * 100);
        
        await sleep(steps[i].duration);
        
        updateStepStatus(stepNum, 'completed', `${steps[i].name} completed`);
        addLog(`Step ${stepNum}: ${steps[i].name} completed`, 'success');
    }
    
    updateProgress(77);
    addLog('Analysis complete! Loading sample results...', 'success');
    
    // Load sample results
    await loadSampleResults();
}

// Load analysis results
async function loadResults() {
    try {
        // Fetch results from API
        const response = await fetch(`${API_BASE_URL}/results`);
        if (response.ok) {
            const data = await response.json();
            displayResults(data);
        } else {
            throw new Error('Failed to load results');
        }
    } catch (error) {
        console.error('Error loading results:', error);
        addLog('Error loading results, showing sample data', 'error');
        await loadSampleResults();
    }
}

// Load sample results for demo
async function loadSampleResults() {
    const sampleResults = [
        {
            title: "Wikipedia - Charles James Kirk",
            url: "https://en.wikipedia.org/wiki/Charles_James_Kirk",
            snippet: "Charles James Kirk (October 14, 1993 – September 10, 2025) was an American political activist, entrepreneur, and media personality...",
            trust_score: 0.75,
            source_type: "Encyclopedia",
            relevance_confidence: 0.95,
            perspective: "common"
        },
        {
            title: "Breaking: Political Violence Claims Another Life",
            url: "https://example-leftist-news.com/kirk-assassination",
            snippet: "The tragic assassination of Charles Kirk highlights the dangerous escalation of political violence in America...",
            trust_score: 0.68,
            source_type: "News Media",
            relevance_confidence: 0.87,
            perspective: "leftist"
        },
        {
            title: "Remembering a Conservative Icon",
            url: "https://example-conservative-outlet.com/kirk-tribute",
            snippet: "Charles Kirk's legacy as a conservative voice will continue to inspire future generations...",
            trust_score: 0.71,
            source_type: "Opinion Blog",
            relevance_confidence: 0.82,
            perspective: "rightist"
        },
        {
            title: "Social Media Reactions to Kirk's Death",
            url: "https://facebook.com/groups/political-discussion",
            snippet: "Community members share their thoughts and condolences following the tragic news...",
            trust_score: 0.32,
            source_type: "Social Media",
            relevance_confidence: 0.65,
            perspective: "common"
        }
    ];
    
    resultsData = sampleResults;
    displayResults({ results: sampleResults });
    addLog('Sample results loaded successfully', 'success');
    updateProgress(85);
}

// Display results in the UI
function displayResults(data) {
    const resultsGrid = document.getElementById('results-grid');
    const results = data.results || [];
    
    // Update summary cards
    updateSummaryCards(results);
    
    if (results.length === 0) {
        resultsGrid.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <p>No results found for the current analysis.</p>
            </div>
        `;
        return;
    }
    
    // Clear existing results
    resultsGrid.innerHTML = '';
    
    // Display each result
    results.forEach(result => {
        const resultCard = createResultCard(result);
        resultsGrid.appendChild(resultCard);
    });
    
    addLog(`Displaying ${results.length} analysis results`, 'success');
}

// Create a result card element
function createResultCard(result) {
    const card = document.createElement('div');
    card.className = 'result-card fade-in';
    
    const trustLevel = getTrustLevel(result.trust_score);
    const trustBadge = `<span class="trust-badge trust-${trustLevel}">${(result.trust_score * 100).toFixed(0)}% Trust</span>`;
    
    card.innerHTML = `
        <div class="result-header">
            <h4>${result.title}</h4>
            <div class="result-meta">
                <span><i class="fas fa-link"></i> ${result.source_type}</span>
                <span><i class="fas fa-eye"></i> ${result.perspective}</span>
                <span><i class="fas fa-percentage"></i> ${(result.relevance_confidence * 100).toFixed(0)}% relevant</span>
            </div>
        </div>
        <div class="result-body">
            <p>${result.snippet}</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                ${trustBadge}
                <a href="${result.url}" target="_blank" class="btn btn-secondary" style="padding: 5px 10px; font-size: 0.8em;">
                    <i class="fas fa-external-link-alt"></i> View Source
                </a>
            </div>
        </div>
    `;
    
    return card;
}

// Update summary cards
function updateSummaryCards(results) {
    const totalLinks = results.length;
    const relevantLinks = results.filter(r => r.relevance_confidence >= 0.6).length;
    const avgTrust = results.length > 0 ? 
        Math.round(results.reduce((sum, r) => sum + r.trust_score, 0) / results.length * 100) : 0;
    
    document.getElementById('total-links').textContent = totalLinks;
    document.getElementById('relevant-links').textContent = relevantLinks;
    document.getElementById('avg-trust').textContent = `${avgTrust}%`;
    document.getElementById('processing-time').textContent = '45s'; // Sample time
}

// Get trust level category
function getTrustLevel(score) {
    if (score >= 0.8) return 'high';
    if (score >= 0.5) return 'medium';
    return 'low';
}

// Apply filters to results
function applyFilters() {
    const perspectiveFilter = document.getElementById('perspective-filter').value;
    const trustFilter = document.getElementById('trust-filter').value;
    
    let filteredResults = [...resultsData];
    
    // Apply perspective filter
    if (perspectiveFilter !== 'all') {
        filteredResults = filteredResults.filter(r => r.perspective === perspectiveFilter);
    }
    
    // Apply trust filter
    if (trustFilter !== 'all') {
        switch (trustFilter) {
            case 'high':
                filteredResults = filteredResults.filter(r => r.trust_score >= 0.8);
                break;
            case 'medium':
                filteredResults = filteredResults.filter(r => r.trust_score >= 0.5 && r.trust_score < 0.8);
                break;
            case 'low':
                filteredResults = filteredResults.filter(r => r.trust_score < 0.5);
                break;
        }
    }
    
    displayResults({ results: filteredResults });
    addLog(`Applied filters: ${filteredResults.length} results shown`, 'info');
}

// Start debate simulation
async function startDebate() {
    console.log('startDebate called');
    const debateBtn = document.getElementById('debate-btn');
    debateBtn.disabled = true;
    debateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting Debate...';
    
    addLog('Initiating AI debate simulation...', 'info');
    
    try {
        // Check if analysis results exist
        if (!resultsData || resultsData.length === 0) {
            addLog('No analysis results found, using sample data...', 'info');
            // Don't block debate, allow it to proceed with sample data
        }
        
        // Step 8: Start debate
        updateStepStatus(8, 'processing', 'AI agents preparing arguments...');
        updateProgress(85);
        
        console.log('Making API call to:', `${API_BASE_URL}/debate`);
        
        // Simulate API call to start debate
        const response = await fetch(`${API_BASE_URL}/debate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        console.log('API response status:', response.status);
        
        if (response.ok) {
            const debateResult = await response.json();
            console.log('Debate result:', debateResult);
            addLog(`Debate API response: ${debateResult.message}`, 'success');
            
            if (debateResult.debate_transcript) {
                // Use real debate transcript from API
                await displayRealDebate(debateResult.debate_transcript, debateResult.trust_score);
            } else {
                // Fall back to simulation
                await simulateDebateProcess();
            }
        } else {
            console.error('API response not ok:', response.status);
            throw new Error(`API returned ${response.status}`);
        }
    } catch (error) {
        console.error('Debate error:', error);
        addLog(`Error starting debate: ${error.message}, running local simulation...`, 'error');
        await simulateDebateProcess();
    } finally {
        debateBtn.disabled = false;
        debateBtn.innerHTML = '<i class="fas fa-play"></i> Start Debate';
    }
}

// Display real debate from API
async function displayRealDebate(transcript, finalScore) {
    const debateTranscript = document.getElementById('debate-transcript');
    debateTranscript.innerHTML = '';
    
    // Display each message from the transcript
    for (let i = 0; i < transcript.length; i++) {
        await sleep(1500);
        
        const messageDiv = document.createElement('div');
        const message = transcript[i];
        
        if (message.agent === 'judge') {
            // Handle judge message differently
            continue; // Skip for now, handle in judge section
        }
        
        messageDiv.className = `debate-message ${message.agent} fade-in`;
        
        const agentName = message.agent === 'leftist' ? 'Leftist Agent' : 'Rightist Agent';
        const agentIcon = message.agent === 'leftist' ? 'fas fa-user-tie' : 'fas fa-user-shield';
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <i class="${agentIcon}"></i>
                ${agentName}
            </div>
            <div class="message-content">
                ${message.message}
            </div>
        `;
        
        debateTranscript.appendChild(messageDiv);
        debateTranscript.scrollTop = debateTranscript.scrollHeight;
        
        addLog(`${agentName} presented argument`, 'info');
    }
    
    updateStepStatus(8, 'completed', 'AI debate completed');
    updateProgress(90);
    
    // Step 9: Judge verdict
    await sleep(2000);
    updateStepStatus(9, 'processing', 'Judge AI analyzing debate...');
    
    await sleep(3000);
    
    // Show judge section with real score
    await showJudgeVerdict(finalScore);
    
    updateStepStatus(9, 'completed', 'Final verdict delivered');
    updateProgress(100);
    
    addLog('Real debate completed successfully!', 'success');
}

// Simulate debate process
async function simulateDebateProcess() {
    const debateTranscript = document.getElementById('debate-transcript');
    debateTranscript.innerHTML = '';
    
    const sampleDebate = [
        {
            agent: 'leftist',
            message: 'The information surrounding Charles Kirk\'s death appears credible based on Wikipedia (Trust Score: 0.75), but we must consider the systemic issues that may have contributed to this tragedy. The Facebook post mentioning gun violence points to broader societal problems that require attention.'
        },
        {
            agent: 'rightist',
            message: 'While the core facts are trustworthy, we should focus on established sources rather than speculative claims. The Wikipedia entry provides reliable information, and we should respect the family\'s privacy rather than pushing political narratives based on unreliable social media posts.'
        },
        {
            agent: 'leftist',
            message: 'Dismissing potential systemic factors isn\'t helpful. The low trust score of social media doesn\'t invalidate the broader issues of gun violence and inadequate mental healthcare that may have played a role. We can acknowledge these without exploiting the tragedy.'
        },
        {
            agent: 'rightist',
            message: 'Speculation without evidence is inappropriate. We should stick to verified facts from credible sources. The focus should be on offering compassion and support to his loved ones, not advancing unrelated political agendas based on unreliable sources.'
        }
    ];
    
    // Display debate messages one by one
    for (let i = 0; i < sampleDebate.length; i++) {
        await sleep(2000);
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `debate-message ${sampleDebate[i].agent} fade-in`;
        
        const agentName = sampleDebate[i].agent === 'leftist' ? 'Leftist Agent' : 'Rightist Agent';
        const agentIcon = sampleDebate[i].agent === 'leftist' ? 'fas fa-user-tie' : 'fas fa-user-shield';
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <i class="${agentIcon}"></i>
                ${agentName}
            </div>
            <div class="message-content">
                ${sampleDebate[i].message}
            </div>
        `;
        
        debateTranscript.appendChild(messageDiv);
        debateTranscript.scrollTop = debateTranscript.scrollHeight;
        
        addLog(`${agentName} presented argument ${i + 1}`, 'info');
    }
    
    updateStepStatus(8, 'completed', 'AI debate completed');
    updateProgress(90);
    
    // Step 9: Judge verdict
    await sleep(2000);
    updateStepStatus(9, 'processing', 'Judge AI analyzing debate...');
    
    await sleep(3000);
    
    // Show judge section and final verdict
    await showJudgeVerdict();
    
    updateStepStatus(9, 'completed', 'Final verdict delivered');
    updateProgress(100);
    
    addLog('Debate simulation completed successfully!', 'success');
}

// Show judge verdict
async function showJudgeVerdict(trustScore = null) {
    const judgeSection = document.getElementById('judge-section');
    const trustScoreDisplay = document.getElementById('trust-score-display');
    const judgeVerdict = document.getElementById('judge-verdict');
    
    judgeSection.style.display = 'block';
    trustScoreDisplay.style.display = 'block';
    
    // Use provided trust score or default to 55
    const finalTrustScore = trustScore || 55;
    const verdict = `Based on the debate analysis, the information receives a trust score of ${finalTrustScore}%. While the core fact of Charles Kirk's death is well-documented through reliable sources like Wikipedia, the circumstances and interpretations vary significantly. The debate highlighted concerns about source reliability, with social media posts providing limited credibility. Both sides presented valid points about respecting factual evidence while acknowledging broader societal issues.`;
    
    // Animate trust score
    document.getElementById('final-trust-score').textContent = `${finalTrustScore}%`;
    document.getElementById('trust-verdict').textContent = verdict;
    
    // Update score circle color based on trust level
    const scoreCircle = document.querySelector('.score-circle');
    if (finalTrustScore >= 80) {
        scoreCircle.style.background = 'conic-gradient(from 0deg, #28a745 0%, #28a745 100%)';
    } else if (finalTrustScore >= 60) {
        scoreCircle.style.background = 'conic-gradient(from 0deg, #ffc107 0%, #28a745 70%, #28a745 100%)';
    } else {
        scoreCircle.style.background = 'conic-gradient(from 0deg, #dc3545 0%, #ffc107 30%, #28a745 70%, #28a745 100%)';
    }
    
    judgeVerdict.innerHTML = `
        <h4>Final Judgment</h4>
        <p>${verdict}</p>
        <div style="margin-top: 15px;">
            <strong>Key Factors:</strong>
            <ul style="text-align: left; margin-top: 10px;">
                <li>Source credibility varies significantly across findings</li>
                <li>Core facts supported by reliable sources</li>
                <li>Speculative elements require further verification</li>
                <li>Both perspectives presented valid evidence-based arguments</li>
            </ul>
        </div>
    `;
    
    addLog(`Final trust score: ${finalTrustScore}%`, 'success');
}

// Clear debate
function clearDebate() {
    document.getElementById('debate-transcript').innerHTML = `
        <div class="no-debate">
            <i class="fas fa-comments"></i>
            <p>No debate started yet. Click "Start Debate" to begin the AI analysis.</p>
        </div>
    `;
    
    document.getElementById('judge-section').style.display = 'none';
    document.getElementById('trust-score-display').style.display = 'none';
    
    addLog('Debate cleared', 'info');
}

// Update step status
function updateStepStatus(stepNumber, status, message) {
    const step = document.getElementById(`step-${stepNumber}`);
    const statusIcon = document.getElementById(`status-${stepNumber}`);
    const statusText = document.getElementById(`text-${stepNumber}`);
    
    // Remove existing status classes
    step.classList.remove('processing', 'completed', 'error');
    statusIcon.classList.remove('waiting', 'processing', 'completed', 'error');
    
    // Add new status class
    step.classList.add(status);
    statusIcon.classList.add(status);
    
    // Update icon
    switch (status) {
        case 'processing':
            statusIcon.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            break;
        case 'completed':
            statusIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
            break;
        case 'error':
            statusIcon.innerHTML = '<i class="fas fa-times-circle"></i>';
            break;
        default:
            statusIcon.innerHTML = '<i class="fas fa-clock"></i>';
    }
    
    statusText.textContent = message;
}

// Reset process status
function resetProcessStatus() {
    for (let i = 1; i <= 9; i++) {
        updateStepStatus(i, 'waiting', 'Waiting');
    }
    updateProgress(0);
    document.getElementById('current-status').textContent = 'Processing';
    
    // Clear logs
    document.getElementById('log-container').innerHTML = '';
}

// Update progress bar
function updateProgress(percentage) {
    document.getElementById('progress-fill').style.width = `${percentage}%`;
}

// Add log entry
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container');
    const logEntry = document.createElement('p');
    logEntry.className = `log-entry ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    logEntry.textContent = `[${timestamp}] ${message}`;
    
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Utility function for delays
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Tab switching with click events
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('tab-btn')) {
        const tabName = e.target.getAttribute('onclick').match(/showTab\('(.+)'\)/)[1];
        showTab(tabName);
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl + Enter to start analysis
    if (e.ctrlKey && e.key === 'Enter') {
        startAnalysis();
    }
    
    // Ctrl + D to start debate
    if (e.ctrlKey && e.key === 'd') {
        startDebate();
    }
});