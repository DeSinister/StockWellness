// Modern StockWellness Interactive JavaScript

// Initialize AOS (Animate On Scroll) Library
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS if available
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            offset: 100
        });
    }
    
    // Initialize the application
    initializeApp();
});

// Application State
const appState = {
    isLoading: false,
    currentAnalysis: null,
    loadingSteps: [
        'Analyzing global events...',
        'Searching investment literature...',
        'Processing company fundamentals...',
        'Generating AI insights...',
        'Crafting your investment story...'
    ],
    currentStep: 0
};

// Initialize Application
function initializeApp() {
    setupFormHandlers();
    setupTickerChips();
    setupInteractiveElements();
    setupScrollAnimations();
}

// Setup Form Handlers
function setupFormHandlers() {
    const form = document.getElementById('analysisForm');
    const tickerInput = document.getElementById('tickerInput');
    const analyzeBtn = form.querySelector('.btn-analyze');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const ticker = tickerInput.value.trim().toUpperCase();
        if (!ticker) {
            showNotification('Please enter a stock ticker symbol', 'warning');
            return;
        }
        
        if (ticker.length > 10) {
            showNotification('Ticker symbol too long', 'error');
            return;
        }
        
        startAnalysis(ticker);
    });
    
    // Real-time validation
    tickerInput.addEventListener('input', function(e) {
        let value = e.target.value.toUpperCase().replace(/[^A-Z]/g, '');
        e.target.value = value;
        
        // Add visual feedback
        if (value.length > 0) {
            e.target.classList.add('has-value');
        } else {
            e.target.classList.remove('has-value');
        }
    });
    
    // Focus animations
    tickerInput.addEventListener('focus', function() {
        this.parentElement.classList.add('focused');
    });
    
    tickerInput.addEventListener('blur', function() {
        this.parentElement.classList.remove('focused');
    });
}

// Setup Ticker Chips
function setupTickerChips() {
    const tickerChips = document.querySelectorAll('.ticker-chip');
    const tickerInput = document.getElementById('tickerInput');
    
    tickerChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const ticker = this.dataset.ticker;
            tickerInput.value = ticker;
            
            // Add selected animation
            this.classList.add('selected');
            setTimeout(() => this.classList.remove('selected'), 300);
            
            // Start analysis
            startAnalysis(ticker);
        });
    });
}

// Setup Interactive Elements
function setupInteractiveElements() {
    // Floating elements animation
    animateFloatingElements();
    
    // Hero stats counter animation
    animateStatsCounters();
    
    // Parallax effect for hero background
    setupParallaxEffect();
    
    // Interactive hover effects
    setupHoverEffects();
}

// Start Stock Analysis
function startAnalysis(ticker) {
    if (appState.isLoading) return;
    
    appState.isLoading = true;
    appState.currentStep = 0;
    
    // Update UI to loading state
    showLoadingState();
    scrollToResults();
    
    // Start loading animation
    startLoadingAnimation();
    
    // Make API request
    performAnalysis(ticker);
}

// Show Loading State
function showLoadingState() {
    const resultsSection = document.getElementById('resultsSection');
    const loadingState = document.getElementById('loadingState');
    const resultsContent = document.getElementById('resultsContent');
    const analyzeBtn = document.querySelector('.btn-analyze');
    
    // Show results section
    resultsSection.style.display = 'block';
    loadingState.style.display = 'flex';
    resultsContent.style.display = 'none';
    
    // Update button state
    analyzeBtn.classList.add('loading');
    analyzeBtn.disabled = true;
    
    // Trigger AOS refresh for new elements
    if (typeof AOS !== 'undefined') {
        AOS.refresh();
    }
}

// Start Loading Animation
function startLoadingAnimation() {
    const loadingSteps = document.getElementById('loadingSteps');
    
    function updateStep() {
        if (appState.currentStep < appState.loadingSteps.length) {
            loadingSteps.textContent = appState.loadingSteps[appState.currentStep];
            appState.currentStep++;
            
            // Add typewriter effect
            typeWriterEffect(loadingSteps, appState.loadingSteps[appState.currentStep - 1]);
            
            setTimeout(updateStep, 2000);
        }
    }
    
    updateStep();
}

// Typewriter Effect
function typeWriterEffect(element, text) {
    element.textContent = '';
    let i = 0;
    
    function typeChar() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(typeChar, 50);
        }
    }
    
    typeChar();
}

// Perform Analysis API Call
async function performAnalysis(ticker) {
    try {
        const formData = new FormData();
        formData.append('ticker', ticker);
        
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Simulate minimum loading time for better UX
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        displayResults(data);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message);
    } finally {
        appState.isLoading = false;
        resetLoadingState();
    }
}

// Display Results
function displayResults(data) {
    console.log('Displaying results:', data);
    
    try {
        appState.currentAnalysis = data;
        
        // Hide loading, show results
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('resultsContent').style.display = 'block';
        
        // Validate data structure
        if (!data || !data.analysis) {
            throw new Error('Invalid data structure received');
        }
        
        console.log('Analysis data:', data.analysis);
        
        // Populate all sections with error handling
        try { displayStoryHeader(data); } catch (e) { console.error('Error in displayStoryHeader:', e); }
        try { displayRecommendation(data.analysis); } catch (e) { console.error('Error in displayRecommendation:', e); }
        try { displayDetailedAnalysis(data); } catch (e) { console.error('Error in displayDetailedAnalysis:', e); }
        try { displayPriceChart(data.price_chart); } catch (e) { console.error('Error in displayPriceChart:', e); }
        try { displayGlobalContext(data.analysis.rag_context); } catch (e) { console.error('Error in displayGlobalContext:', e); }
        try { displayLiteratureContext(data.analysis.rag_context); } catch (e) { console.error('Error in displayLiteratureContext:', e); }
        try { displayReferences(data); } catch (e) { console.error('Error in displayReferences:', e); }
        
        // Trigger animations
        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
        
        // Add success notification
        showNotification('Analysis complete! Your investment story is ready.', 'success');
        
    } catch (error) {
        console.error('Error in displayResults:', error);
        showError('Failed to display analysis results: ' + error.message);
    }
}

// Display Story Header
function displayStoryHeader(data) {
    document.getElementById('companyName').textContent = data.company_data.name;
    document.getElementById('analysisTimestamp').textContent = formatTimestamp(data.generated_at);
}

// Display Recommendation
function displayRecommendation(analysis) {
    console.log('Displaying recommendation:', analysis);
    
    try {
        // Get DOM elements
        const recommendationText = document.getElementById('recommendationText');
        const confidenceScore = document.getElementById('confidenceScore');
        const recommendationRationale = document.getElementById('recommendationRationale');
        const priceTarget = document.getElementById('priceTarget');
        const recommendationBadge = document.querySelector('.recommendation-badge');
        
        // Check if elements exist
        if (!recommendationText || !confidenceScore || !recommendationRationale || !priceTarget || !recommendationBadge) {
            throw new Error('Required DOM elements not found');
        }
        
        // If analysis is a string (raw JSON), try to parse it
        if (typeof analysis === 'string') {
            console.log('Analysis is string, attempting to parse:', analysis);
            try {
                analysis = JSON.parse(analysis);
            } catch (e) {
                console.error('Failed to parse analysis JSON:', e);
                throw new Error('Invalid JSON in analysis');
            }
        }
        
        // Populate elements
        recommendationText.textContent = analysis.recommendation || 'N/A';
        confidenceScore.textContent = analysis.confidence_score || '0';
        recommendationRationale.textContent = analysis.rationale || 'No rationale available';
        priceTarget.textContent = analysis.price_target || 'N/A';
        
        // Update badge color based on recommendation
        recommendationBadge.setAttribute('data-recommendation', analysis.recommendation || 'HOLD');
        
        // Animate confidence circle
        animateConfidenceCircle(analysis.confidence_score || 0);
        
        // Color-code recommendation
        const colors = {
            'BUY': '#00b894',
            'HOLD': '#fdcb6e',
            'SELL': '#e17055'
        };
        
        recommendationBadge.style.background = colors[analysis.recommendation] || colors['HOLD'];
        
        console.log('Recommendation display completed successfully');
        
    } catch (error) {
        console.error('Error in displayRecommendation:', error);
        
        // Show fallback content
        const recommendationText = document.getElementById('recommendationText');
        const recommendationRationale = document.getElementById('recommendationRationale');
        
        if (recommendationText) recommendationText.textContent = 'Error';
        if (recommendationRationale) recommendationRationale.textContent = 'Failed to load recommendation data. Please try again.';
    }
}

// Display Detailed Analysis
function displayDetailedAnalysis(data) {
    console.log('Displaying detailed analysis:', data);
    
    try {
        const keyFactorsList = document.getElementById('keyFactorsList');
        const riskFactorsList = document.getElementById('riskFactorsList');
        const fundamentalsGrid = document.getElementById('fundamentalsGrid');
        
        if (!keyFactorsList || !riskFactorsList || !fundamentalsGrid) {
            throw new Error('Required analysis elements not found');
        }
        
        // Clear existing content
        keyFactorsList.innerHTML = '';
        riskFactorsList.innerHTML = '';
        fundamentalsGrid.innerHTML = '';
        
        // Populate key factors
        if (data.analysis && data.analysis.key_factors && Array.isArray(data.analysis.key_factors)) {
            data.analysis.key_factors.forEach((factor, index) => {
                const li = document.createElement('li');
                li.textContent = factor;
                li.style.animationDelay = `${index * 0.1}s`;
                li.classList.add('fade-in-up');
                keyFactorsList.appendChild(li);
            });
        } else {
            keyFactorsList.innerHTML = '<li>No key factors data available</li>';
        }
        
        // Populate risk factors
        if (data.analysis && data.analysis.risks && Array.isArray(data.analysis.risks)) {
            data.analysis.risks.forEach((risk, index) => {
                const li = document.createElement('li');
                li.textContent = risk;
                li.style.animationDelay = `${index * 0.1}s`;
                li.classList.add('fade-in-up');
                riskFactorsList.appendChild(li);
            });
        } else {
            riskFactorsList.innerHTML = '<li>No risk factors data available</li>';
        }
        
        // Populate fundamentals
        if (data.company_data) {
            const fundamentals = [
                { label: 'Market Cap', value: formatMarketCap(data.company_data.market_cap) },
                { label: 'P/E Ratio', value: data.company_data.pe_ratio || 'N/A' },
                { label: 'Forward P/E', value: data.company_data.forward_pe || 'N/A' },
                { label: 'Price to Book', value: data.company_data.price_to_book || 'N/A' },
                { label: 'Dividend Yield', value: data.company_data.dividend_yield || 'N/A' },
                { label: 'Current Price', value: data.company_data.current_price ? `$${data.company_data.current_price}` : 'N/A' }
            ];
            
            fundamentals.forEach((fundamental, index) => {
                const item = document.createElement('div');
                item.className = 'fundamental-item';
                item.innerHTML = `
                    <div class="fundamental-value">${fundamental.value}</div>
                    <div class="fundamental-label">${fundamental.label}</div>
                `;
                item.style.animationDelay = `${index * 0.1}s`;
                fundamentalsGrid.appendChild(item);
            });
        } else {
            fundamentalsGrid.innerHTML = '<div class="text-center">No company data available</div>';
        }
        
        console.log('Detailed analysis display completed successfully');
        
    } catch (error) {
        console.error('Error in displayDetailedAnalysis:', error);
        
        // Show error message in the sections
        const keyFactorsList = document.getElementById('keyFactorsList');
        const riskFactorsList = document.getElementById('riskFactorsList');
        
        if (keyFactorsList) keyFactorsList.innerHTML = '<li>Error loading key factors</li>';
        if (riskFactorsList) riskFactorsList.innerHTML = '<li>Error loading risk factors</li>';
    }
}

// Display Price Chart
function displayPriceChart(chartData) {
    if (chartData && typeof Plotly !== 'undefined') {
        const chartContainer = document.getElementById('priceChart');
        const plotData = JSON.parse(chartData);
        
        // Enhance chart with modern styling
        plotData.layout = {
            ...plotData.layout,
            font: {
                family: "'Inter', sans-serif",
                size: 12,
                color: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            margin: { l: 40, r: 40, t: 40, b: 40 }
        };
        
        Plotly.newPlot(chartContainer, plotData.data, plotData.layout, {
            responsive: true,
            displayModeBar: false
        });
    }
}

// Display Global Context
function displayGlobalContext(ragContext) {
    const container = document.getElementById('globalNewsContainer');
    container.innerHTML = '';
    
    if (ragContext && ragContext.global_news) {
        ragContext.global_news.forEach((article, index) => {
            const card = createNewsCard(article, index);
            container.appendChild(card);
        });
    } else {
        container.innerHTML = '<p class="text-center">No recent global news data available.</p>';
    }
}

// Display Literature Context
function displayLiteratureContext(ragContext) {
    const container = document.getElementById('literatureContainer');
    container.innerHTML = '';
    
    if (ragContext && ragContext.sources) {
        ragContext.sources.forEach((source, index) => {
            const card = createLiteratureCard(source, index);
            container.appendChild(card);
        });
    } else {
        container.innerHTML = '<p class="text-center">No investment literature context available.</p>';
    }
}

// Display References
function displayReferences(data) {
    const container = document.getElementById('referencesContainer');
    container.innerHTML = '';
    
    // Combine all news sources
    const allSources = [];
    
    // Add global news
    if (data.analysis.rag_context && data.analysis.rag_context.global_news) {
        allSources.push(...data.analysis.rag_context.global_news);
    }
    
    // Add any other news articles
    if (data.news_articles) {
        allSources.push(...data.news_articles);
    }
    
    if (allSources.length > 0) {
        allSources.forEach((source, index) => {
            const card = createReferenceCard(source, index);
            container.appendChild(card);
        });
    } else {
        container.innerHTML = '<p class="text-center">No reference sources available.</p>';
    }
}

// Create News Card
function createNewsCard(article, index) {
    const card = document.createElement('div');
    card.className = 'news-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    card.innerHTML = `
        <h5>${article.title}</h5>
        <p>${article.description}</p>
        <div class="card-meta">
            <span>${article.source} • ${formatDate(article.published_at)}</span>
            <a href="${article.url}" target="_blank" class="btn-link">Read more</a>
        </div>
    `;
    
    return card;
}

// Create Literature Card
function createLiteratureCard(source, index) {
    const card = document.createElement('div');
    card.className = 'literature-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    const bookImage = getBookImage(source.book);
    
    card.innerHTML = `
        <div class="d-flex">
            ${bookImage ? `<img src="${bookImage}" alt="${source.book}" class="book-image">` : ''}
            <div class="flex-grow-1">
                <h5>${source.book}</h5>
                <p><strong>Chapter:</strong> ${source.chapter}</p>
                <p><strong>Page:</strong> ${source.page}</p>
                <p class="text-preview">${source.text_preview}</p>
            </div>
        </div>
        <div class="card-meta">
            <span>Investment Literature</span>
            <span class="relevance-score">${Math.round(source.relevance_score * 100)}% relevant</span>
        </div>
    `;
    
    return card;
}

// Create Reference Card
function createReferenceCard(source, index) {
    const card = document.createElement('div');
    card.className = 'reference-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    card.innerHTML = `
        <h5>${source.title}</h5>
        <p>${source.description || 'No description available'}</p>
        <div class="card-meta">
            <span>${source.source} • ${formatDate(source.published_at)}</span>
            <a href="${source.url}" target="_blank" class="btn-link">View source</a>
        </div>
    `;
    
    return card;
}

// Get Book Image
function getBookImage(bookName) {
    const bookImages = {
        'The Intelligent Investor': '/static/images/books/intelligent-investor.jpg',
        'A Random Walk Down Wall Street': '/static/images/books/random-walk.jpg',
        'Common Stocks and Uncommon Profits': '/static/images/books/common-stocks.jpg',
        'One Up On Wall Street': '/static/images/books/one-up.jpg',
        'Stock Investing 101': '/static/images/books/stock-101.jpg',
        'The Little Book of Common Sense Investing': '/static/images/books/little-book.jpg'
    };
    
    return bookImages[bookName] || null;
}

// Animate Confidence Circle
function animateConfidenceCircle(score) {
    const circle = document.querySelector('.confidence-circle');
    const angle = (score / 100) * 360;
    
    circle.style.setProperty('--confidence-angle', `${angle}deg`);
    
    // Add animation class
    circle.classList.add('animating');
    setTimeout(() => circle.classList.remove('animating'), 1000);
}

// Animate Stats Counters
function animateStatsCounters() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const finalValue = stat.textContent;
        let currentValue = 0;
        const increment = finalValue.includes('%') ? 1 : 
                          finalValue.includes('$') ? 100000000 : 
                          finalValue.includes('ms') ? 1 : 1;
        
        const timer = setInterval(() => {
            currentValue += increment;
            
            if (finalValue.includes('%')) {
                stat.textContent = `${Math.min(currentValue, parseFloat(finalValue))}%`;
                if (currentValue >= parseFloat(finalValue)) clearInterval(timer);
            } else if (finalValue.includes('$')) {
                const value = Math.min(currentValue, parseFloat(finalValue.replace(/[$B+]/g, '')) * 1000000000);
                stat.textContent = `$${(value / 1000000000).toFixed(1)}B+`;
                if (currentValue >= parseFloat(finalValue.replace(/[$B+]/g, '')) * 1000000000) clearInterval(timer);
            } else if (finalValue.includes('ms')) {
                stat.textContent = `${Math.min(currentValue, parseFloat(finalValue))}ms`;
                if (currentValue >= parseFloat(finalValue)) clearInterval(timer);
            }
        }, 50);
    });
}

// Setup Scroll Animations
function setupScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    });
    
    document.querySelectorAll('[data-animate]').forEach(el => {
        observer.observe(el);
    });
}

// Setup Parallax Effect
function setupParallaxEffect() {
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('.hero-background');
        
        if (parallax) {
            const speed = scrolled * 0.5;
            parallax.style.transform = `translateY(${speed}px)`;
        }
    });
}

// Setup Hover Effects
function setupHoverEffects() {
    // Feature cards tilt effect
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        });
    });
}

// Animate Floating Elements
function animateFloatingElements() {
    const floatingElements = document.querySelectorAll('.float-element');
    
    floatingElements.forEach((element, index) => {
        // Random movement animation
        setInterval(() => {
            const randomX = Math.random() * 20 - 10;
            const randomY = Math.random() * 20 - 10;
            
            element.style.transform = `translate(${randomX}px, ${randomY}px)`;
        }, 3000 + index * 1000);
    });
}

// Utility Functions
function scrollToResults() {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetLoadingState() {
    const analyzeBtn = document.querySelector('.btn-analyze');
    analyzeBtn.classList.remove('loading');
    analyzeBtn.disabled = false;
}

function showError(message) {
    showNotification(message, 'error');
    
    // Hide loading state
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
    
    // Manual close
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

function formatMarketCap(marketCap) {
    if (!marketCap || marketCap === 'N/A') return 'N/A';
    
    const num = parseFloat(marketCap);
    if (num >= 1e12) return `$${(num / 1e12).toFixed(1)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(1)}M`;
    return `$${num.toLocaleString()}`;
}

// Add notification styles
const notificationStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 1000;
    animation: slideInRight 0.3s ease-out;
    max-width: 400px;
}

.notification-success { border-left: 4px solid #00b894; }
.notification-warning { border-left: 4px solid #fdcb6e; }
.notification-error { border-left: 4px solid #e17055; }
.notification-info { border-left: 4px solid #74b9ff; }

.notification i {
    font-size: 18px;
}

.notification-success i { color: #00b894; }
.notification-warning i { color: #fdcb6e; }
.notification-error i { color: #e17055; }
.notification-info i { color: #74b9ff; }

.notification-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #666;
    margin-left: auto;
}

@keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

.fade-in-up {
    animation: fadeInUp 0.6s ease-out forwards;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
`;

// Inject notification styles
const styleElement = document.createElement('style');
styleElement.textContent = notificationStyles;
document.head.appendChild(styleElement); 