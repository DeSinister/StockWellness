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
    currentStep: 0,
    cachingEnabled: false, // Toggle this to enable/disable caching - DISABLED FOR PRODUCTION
    currentNewsIndex: 0 // For news carousel
};

// Cached results for popular tickers (for frontend testing)
const cachedResults = {
    'AAPL': {
        "success": true,
        "company_data": {
            "name": "Apple Inc.",
            "current_price": 185.50,
            "market_cap": 2850000000000,
            "pe_ratio": 28.5,
            "forward_pe": 24.8,
            "price_to_book": 8.2,
            "dividend_yield": "0.52%"
        },
        "analysis": {
            "recommendation": "BUY",
            "rationale": "Apple demonstrates strong fundamentals with consistent revenue growth, robust ecosystem expansion, and innovative product pipeline. The company's services segment continues to show remarkable growth, providing recurring revenue streams. Strategic AI investments position Apple well for future growth.",
            "price_target": "$210.00",
            "key_factors": [
                "Strong Q4 2024 earnings with 8% revenue growth year-over-year",
                "iPhone 15 series showing strong adoption with Pro models leading sales",
                "Services revenue reached record highs with 16% growth",
                "AI chip developments putting Apple ahead in mobile AI capabilities",
                "Strong cash position enabling continued shareholder returns"
            ],
            "risks": [
                "China market dependency remains a geopolitical risk",
                "Increasing competition in the smartphone market",
                "Regulatory scrutiny around App Store policies",
                "Supply chain constraints affecting production timelines"
            ],
            "rag_context": {
                "global_news": [
                    {
                        "title": "Apple's AI Strategy Gains Momentum with New Chip Developments",
                        "description": "Apple is reportedly developing advanced AI chips that could revolutionize mobile computing, positioning the company as a leader in artificial intelligence hardware.",
                        "source": "TechCrunch",
                        "url": "https://techcrunch.com/apple-ai-chips",
                        "published_at": "2024-12-12T10:30:00Z"
                    },
                    {
                        "title": "iPhone Sales Surge in Holiday Season Despite Market Headwinds",
                        "description": "Apple's iPhone sales have shown remarkable resilience during the holiday shopping season, with Pro models driving premium segment growth.",
                        "source": "Reuters",
                        "url": "https://reuters.com/apple-iphone-sales",
                        "published_at": "2024-12-11T15:45:00Z"
                    },
                    {
                        "title": "Apple Services Revenue Hits New Record High",
                        "description": "The company's services division, including App Store, iCloud, and Apple Music, generated record revenue in Q4 2024, showcasing the strength of Apple's ecosystem.",
                        "source": "Bloomberg",
                        "url": "https://bloomberg.com/apple-services-revenue",
                        "published_at": "2024-12-10T09:20:00Z"
                    },
                    {
                        "title": "China Market Shows Signs of Recovery for Apple",
                        "description": "Apple's China operations are showing signs of improvement after several challenging quarters, with local partnerships driving growth.",
                        "source": "Financial Times",
                        "url": "https://ft.com/apple-china-recovery",
                        "published_at": "2024-12-09T14:15:00Z"
                    },
                    {
                        "title": "Apple's Sustainability Initiative Gains Investor Attention",
                        "description": "Apple's commitment to carbon neutrality by 2030 is attracting ESG-focused investors and setting industry standards.",
                        "source": "Wall Street Journal",
                        "url": "https://wsj.com/apple-sustainability",
                        "published_at": "2024-12-08T11:30:00Z"
                    },
                    {
                        "title": "Mixed Reality Headset Vision Pro Shows Promise",
                        "description": "Early adoption metrics for Apple's Vision Pro mixed reality headset indicate strong potential in enterprise applications.",
                        "source": "The Verge",
                        "url": "https://theverge.com/apple-vision-pro",
                        "published_at": "2024-12-07T16:45:00Z"
                    }
                ],
                "sources": [
                    {
                        "book": "The Intelligent Investor",
                        "chapter": "Chapter 8: The Investor and Market Fluctuations",
                        "page": "203",
                        "text_preview": "The intelligent investor should recognize that market prices fluctuate much more widely than underlying business values. Apple exemplifies how a quality company with strong fundamentals can weather market volatility through consistent execution and innovation.",
                        "relevance_score": 0.92
                    },
                    {
                        "book": "Common Stocks and Uncommon Profits",
                        "chapter": "Chapter 3: What to Buy - The Fifteen Points to Look for in a Common Stock",
                        "page": "48",
                        "text_preview": "Companies with strong research and development programs, like Apple's continuous innovation in technology, tend to maintain competitive advantages that translate into superior long-term returns for shareholders.",
                        "relevance_score": 0.89
                    }
                ]
            }
        },
        "chart_data": "{\"data\":[{\"x\":[\"2024-06-12\",\"2024-07-12\",\"2024-08-12\",\"2024-09-12\",\"2024-10-12\",\"2024-11-12\",\"2024-12-12\"],\"y\":[175.84,183.27,189.45,178.92,185.50,182.33,185.50],\"type\":\"scatter\",\"mode\":\"lines+markers\",\"name\":\"AAPL Price\",\"line\":{\"color\":\"#667eea\",\"width\":3}}],\"layout\":{\"title\":\"AAPL 6-Month Price Performance\",\"xaxis\":{\"title\":\"Date\"},\"yaxis\":{\"title\":\"Price ($)\"}}}",
        "generated_at": "2024-12-12T10:30:00Z"
    },
    'QQQ': {
        "success": true,
        "company_data": {
            "name": "Invesco QQQ Trust ETF",
            "current_price": 408.25,
            "market_cap": 185000000000,
            "pe_ratio": 28.1,
            "forward_pe": 25.3,
            "price_to_book": 7.8,
            "dividend_yield": "0.51%"
        },
        "analysis": {
            "recommendation": "BUY",
            "rationale": "QQQ provides excellent exposure to technology sector growth with top-tier companies driving innovation. The ETF benefits from AI revolution, cloud computing expansion, and digital transformation trends. Strong diversification across NASDAQ's best performers makes it an attractive growth investment.",
            "price_target": "$450.00",
            "key_factors": [
                "Technology sector leading market performance with AI-driven growth",
                "Strong performance from top holdings including Apple, Microsoft, NVIDIA",
                "Cloud computing and digital services showing accelerated adoption",
                "Low expense ratio of 0.20% making it cost-effective for investors",
                "Consistent inflows indicating strong investor confidence"
            ],
            "risks": [
                "High concentration in technology sector creates volatility risk",
                "Interest rate sensitivity affecting growth valuations",
                "Geopolitical tensions impacting global technology companies",
                "Market concentration in top 10 holdings creates single-stock risk"
            ],
            "rag_context": {
                "global_news": [
                    {
                        "title": "NASDAQ 100 Reaches New All-Time Highs on AI Optimism",
                        "description": "The NASDAQ 100 index, tracked by QQQ, has surged to record levels as investors bet on artificial intelligence and technology sector growth.",
                        "source": "CNBC",
                        "url": "https://cnbc.com/nasdaq-100-highs",
                        "published_at": "2024-12-12T09:15:00Z"
                    },
                    {
                        "title": "Technology ETFs See Record Inflows as AI Revolution Accelerates",
                        "description": "ETFs like QQQ are experiencing unprecedented inflows as investors seek exposure to the AI and technology revolution sweeping global markets.",
                        "source": "MarketWatch",
                        "url": "https://marketwatch.com/tech-etf-inflows",
                        "published_at": "2024-12-11T14:30:00Z"
                    },
                    {
                        "title": "Cloud Computing Giants Drive QQQ Performance Higher",
                        "description": "Major cloud computing companies in the QQQ portfolio are reporting strong earnings, driving the ETF's outperformance.",
                        "source": "Barron's",
                        "url": "https://barrons.com/qqq-cloud-performance",
                        "published_at": "2024-12-10T16:45:00Z"
                    },
                    {
                        "title": "Semiconductor Stocks Boost NASDAQ 100 Momentum",
                        "description": "Semiconductor companies within QQQ's holdings are seeing strong demand, particularly from AI and data center applications.",
                        "source": "Seeking Alpha",
                        "url": "https://seekingalpha.com/semiconductor-nasdaq",
                        "published_at": "2024-12-09T11:20:00Z"
                    }
                ],
                "sources": [
                    {
                        "book": "A Random Walk Down Wall Street",
                        "chapter": "Chapter 14: A Practical Guide for Random Walkers",
                        "page": "385",
                        "text_preview": "Index funds like QQQ offer investors broad diversification at low cost. The NASDAQ 100's focus on growth companies provides exposure to innovation leaders while maintaining reasonable diversification across the technology sector.",
                        "relevance_score": 0.95
                    }
                ]
            }
        },
        "chart_data": "{\"data\":[{\"x\":[\"2024-06-12\",\"2024-07-12\",\"2024-08-12\",\"2024-09-12\",\"2024-10-12\",\"2024-11-12\",\"2024-12-12\"],\"y\":[398.45,402.30,385.67,391.28,408.25,405.12,408.25],\"type\":\"scatter\",\"mode\":\"lines+markers\",\"name\":\"QQQ Price\",\"line\":{\"color\":\"#667eea\",\"width\":3}}],\"layout\":{\"title\":\"QQQ 6-Month Price Performance\",\"xaxis\":{\"title\":\"Date\"},\"yaxis\":{\"title\":\"Price ($)\"}}}",
        "generated_at": "2024-12-12T10:30:00Z"
    },
    'TSLA': {
        "success": true,
        "company_data": {
            "name": "Tesla Inc.",
            "current_price": 245.67,
            "market_cap": 780000000000,
            "pe_ratio": 85.4,
            "forward_pe": 58.2,
            "price_to_book": 12.8,
            "dividend_yield": "0.00%"
        },
        "analysis": {
            "recommendation": "HOLD",
            "rationale": "Tesla continues to lead electric vehicle innovation but faces increasing competition. Strong autonomous driving progress and energy business growth offset concerns about automotive margin pressure. Execution of robotaxi vision will be crucial for future valuation.",
            "price_target": "$280.00",
            "key_factors": [
                "Leading position in electric vehicle market with strong brand",
                "Full Self-Driving capabilities showing significant progress",
                "Energy storage and solar business growing rapidly",
                "Gigafactory expansion increasing production capacity globally",
                "Strong cash generation and improving operational efficiency"
            ],
            "risks": [
                "Increasing competition from traditional automakers in EV space",
                "Regulatory challenges affecting autonomous driving rollout", 
                "Economic slowdown impacting luxury vehicle demand",
                "Key person risk associated with leadership changes"
            ],
            "rag_context": {
                "global_news": [
                    {
                        "title": "Tesla's Full Self-Driving Makes Major Breakthrough",
                        "description": "Tesla's latest FSD update shows remarkable improvement in autonomous driving capabilities, bringing the company closer to full autonomy.",
                        "source": "Electrek",
                        "url": "https://electrek.co/tesla-fsd-breakthrough",
                        "published_at": "2024-12-12T08:45:00Z"
                    },
                    {
                        "title": "Electric Vehicle Market Competition Intensifies",
                        "description": "Traditional automakers are launching competitive EV models, creating pressure on Tesla's market share and pricing power.",
                        "source": "Automotive News",
                        "url": "https://autonews.com/ev-competition",
                        "published_at": "2024-12-11T13:20:00Z"
                    }
                ],
                "sources": [
                    {
                        "book": "One Up On Wall Street",
                        "chapter": "Chapter 11: Stalking the Tenbagger",
                        "page": "142",
                        "text_preview": "Companies like Tesla that revolutionize entire industries can provide exceptional returns, but investors must carefully evaluate whether the innovation can sustain competitive advantages as the market matures.",
                        "relevance_score": 0.87
                    }
                ]
            }
        },
        "chart_data": "{\"data\":[{\"x\":[\"2024-06-12\",\"2024-07-12\",\"2024-08-12\",\"2024-09-12\",\"2024-10-12\",\"2024-11-12\",\"2024-12-12\"],\"y\":[195.32,218.45,201.89,238.77,245.67,240.12,245.67],\"type\":\"scatter\",\"mode\":\"lines+markers\",\"name\":\"TSLA Price\",\"line\":{\"color\":\"#667eea\",\"width\":3}}],\"layout\":{\"title\":\"TSLA 6-Month Price Performance\",\"xaxis\":{\"title\":\"Date\"},\"yaxis\":{\"title\":\"Price ($)\"}}}",
        "generated_at": "2024-12-12T10:30:00Z"
    }
};

// Initialize Application
function initializeApp() {
    console.log('🚀 StockWellness initialized successfully');
    console.log('📡 PRODUCTION MODE: Cache disabled - using live API calls');
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
    
    // Hide any existing results
    hideResultsSections();
    
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
        // Check if caching is enabled and we have cached data
        if (appState.cachingEnabled && cachedResults[ticker]) {
            console.log(`Using cached results for ${ticker}`);
            
            // Simulate API delay for realistic UX
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            displayResults(cachedResults[ticker]);
            return;
        }
        
        // Make actual API call
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
        // Show results section and new individual sections
        const resultsSection = document.getElementById('resultsSection');
        const resultsContent = document.getElementById('resultsContent');
        
        // Show main results
        resultsSection.style.display = 'block';
        resultsContent.style.display = 'block';
        
        // Show individual sections
        const priceSection = document.querySelector('.price-performance-section');
        const globalSection = document.querySelector('.global-context-section');
        const literatureSection = document.querySelector('.literature-insights-section');
        const referencesSection = document.querySelector('.sources-references-section');
        
        if (priceSection) priceSection.classList.add('show');
        if (globalSection) globalSection.classList.add('show');
        if (literatureSection) literatureSection.classList.add('show');
        if (referencesSection) referencesSection.classList.add('show');
        
        // Display each component
        try { displayStoryHeader(data); } catch (e) { console.error('Error in displayStoryHeader:', e); }
        try { displayRecommendation(data.analysis); } catch (e) { console.error('Error in displayRecommendation:', e); }
        try { displayDetailedAnalysis(data); } catch (e) { console.error('Error in displayDetailedAnalysis:', e); }
        try { 
            console.log('Chart data being passed:', data.chart_data); 
            displayPriceChart(data.chart_data); 
        } catch (e) { console.error('Error in displayPriceChart:', e); }
        try { displayGlobalContext(data.analysis.rag_context); } catch (e) { console.error('Error in displayGlobalContext:', e); }
        try { displayLiteratureContext(data.analysis.rag_context); } catch (e) { console.error('Error in displayLiteratureContext:', e); }
        try { displayReferences(data); } catch (e) { console.error('Error in displayReferences:', e); }
        
        // Refresh AOS animations for new content
        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
        
        console.log('Results display completed successfully');
        
    } catch (error) {
        console.error('Error in displayResults:', error);
        showError('Failed to display analysis results. Please try again.');
    } finally {
        resetLoadingState();
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
        const recommendationRationale = document.getElementById('recommendationRationale');
        const priceTarget = document.getElementById('priceTarget');
        const recommendationBadge = document.querySelector('.recommendation-badge');
        
        // Check if elements exist
        if (!recommendationText || !recommendationRationale || !priceTarget || !recommendationBadge) {
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
        recommendationRationale.textContent = analysis.rationale || 'No rationale available';
        priceTarget.textContent = analysis.price_target || 'N/A';
        
        // Update badge color based on recommendation
        recommendationBadge.setAttribute('data-recommendation', analysis.recommendation || 'HOLD');
        
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
    console.log('Attempting to display chart with data:', chartData);
    
    const chartContainer = document.getElementById('priceChart');
    if (!chartContainer) {
        console.error('Chart container not found');
        return;
    }
    
    if (!chartData) {
        console.warn('No chart data provided');
        chartContainer.innerHTML = '<div style="text-align: center; padding: 2rem; color: #666;">Chart data not available</div>';
        return;
    }
    
    if (typeof Plotly === 'undefined') {
        console.error('Plotly.js not loaded');
        chartContainer.innerHTML = '<div style="text-align: center; padding: 2rem; color: #666;">Chart library not loaded</div>';
        return;
    }
    
    try {
        const plotData = typeof chartData === 'string' ? JSON.parse(chartData) : chartData;
        
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
        
        console.log('Chart rendered successfully');
        
    } catch (error) {
        console.error('Error rendering chart:', error);
        chartContainer.innerHTML = '<div style="text-align: center; padding: 2rem; color: #666;">Error loading chart data</div>';
    }
}

// Display Global Context with Carousel
function displayGlobalContext(ragContext) {
    console.log('displayGlobalContext called with:', ragContext);
    const container = document.getElementById('globalNewsContainer');
    
    if (!container) {
        console.error('globalNewsContainer not found!');
        return;
    }
    
    container.innerHTML = '';
    
    // // Temporary test - show arrows even without data for debugging
    // if (!ragContext || !ragContext.global_news || ragContext.global_news.length === 0) {
    //     console.log('No global news data, creating test carousel...');
    //     const testNews = [
    //         { title: 'Test News 1', description: 'Test description 1', source: 'Test Source', published_at: new Date().toISOString(), url: '#' },
    //         { title: 'Test News 2', description: 'Test description 2', source: 'Test Source', published_at: new Date().toISOString(), url: '#' },
    //         { title: 'Test News 3', description: 'Test description 3', source: 'Test Source', published_at: new Date().toISOString(), url: '#' }
    //     ];
    //     ragContext = { global_news: testNews };
    // }
    
    if (ragContext && ragContext.global_news && ragContext.global_news.length > 0) {
        const allNews = ragContext.global_news;
        const newsPerPage = 2; // Changed from 4 to 2
        const totalPages = Math.ceil(allNews.length / newsPerPage);
        
        // Create carousel container
        const carouselContainer = document.createElement('div');
        carouselContainer.className = 'global-news-carousel-container';
        
        // Create carousel header with navigation
        const carouselHeader = document.createElement('div');
        carouselHeader.className = 'global-carousel-header';
        carouselHeader.innerHTML = `
            <div class="global-carousel-info">
                <span class="global-news-count">${allNews.length} Global News Stories</span>
                <span class="global-page-indicator">Page <span id="currentGlobalPage">1</span> of ${totalPages}</span>
            </div>
            <div class="global-carousel-controls">
                <button class="global-carousel-btn prev" id="prevGlobalNews" ${appState.currentNewsIndex === 0 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-left"></i>
                    <span style="font-size: 20px; display: none;">‹</span>
                </button>
                <button class="global-carousel-btn next" id="nextGlobalNews" ${appState.currentNewsIndex >= totalPages - 1 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-right"></i>
                    <span style="font-size: 20px; display: none;">›</span>
                </button>
            </div>
        `;
        
        // Create news grid
        const newsGrid = document.createElement('div');
        newsGrid.className = 'global-news-carousel-grid';
        
        // Function to display current page
        function displayCurrentPage() {
            newsGrid.innerHTML = '';
            const startIndex = appState.currentNewsIndex * newsPerPage;
            const endIndex = Math.min(startIndex + newsPerPage, allNews.length);
            const currentNews = allNews.slice(startIndex, endIndex);
            
            currentNews.forEach((article, index) => {
                const card = createGlobalNewsCard(article, index);
                newsGrid.appendChild(card);
            });
            
            // Update page indicator
            document.getElementById('currentGlobalPage').textContent = appState.currentNewsIndex + 1;
            
            // Update button states
            const prevBtn = document.getElementById('prevGlobalNews');
            const nextBtn = document.getElementById('nextGlobalNews');
            
            prevBtn.disabled = appState.currentNewsIndex === 0;
            nextBtn.disabled = appState.currentNewsIndex >= totalPages - 1;
            
            // Animate cards entrance
            const cards = newsGrid.querySelectorAll('.global-news-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(40px) scale(0.95)';
                
                setTimeout(() => {
                    card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0) scale(1)';
                }, index * 150);
            });
        }
        
        // Add event listeners for navigation
        carouselHeader.addEventListener('click', (e) => {
            if (e.target.closest('#prevGlobalNews') && appState.currentNewsIndex > 0) {
                appState.currentNewsIndex--;
                displayCurrentPage();
            } else if (e.target.closest('#nextGlobalNews') && appState.currentNewsIndex < totalPages - 1) {
                appState.currentNewsIndex++;
                displayCurrentPage();
            }
        });
        
        // Assemble carousel
        carouselContainer.appendChild(carouselHeader);
        carouselContainer.appendChild(newsGrid);
        container.appendChild(carouselContainer);
        
        // Display first page
        displayCurrentPage();
        
        // Check if Font Awesome icons loaded, fallback to text arrows
        setTimeout(() => {
            const iconElements = carouselHeader.querySelectorAll('.fas');
            iconElements.forEach(icon => {
                if (getComputedStyle(icon).fontFamily.indexOf('Font Awesome') === -1) {
                    icon.style.display = 'none';
                    const textArrow = icon.nextElementSibling;
                    if (textArrow) textArrow.style.display = 'inline';
                }
            });
        }, 100);
        
        // Elegant entrance animation for container
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            container.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 300);
        
        console.log('Carousel created with arrows for', allNews.length, 'news items');
        
    } else {
        container.innerHTML = '<div class="empty-state"><p class="text-center">No recent global news data available.</p></div>';
    }
}

// Create Global News Card (decoupled from literature)
function createGlobalNewsCard(article, index) {
    const card = document.createElement('div');
    card.className = 'global-news-card';
    
    // Sophisticated click interaction
    card.addEventListener('click', function(e) {
        if (!e.target.closest('.global-btn-link')) {
            // Add subtle click feedback
            this.style.transform = 'perspective(1000px) rotateX(2deg) translateY(-12px) scale(0.98)';
            setTimeout(() => {
                this.style.transform = 'perspective(1000px) rotateX(2deg) translateY(-12px) scale(1)';
            }, 150);
            
            const link = this.querySelector('.global-btn-link');
            if (link) {
                setTimeout(() => {
                    window.open(link.href, '_blank');
                }, 200);
            }
        }
    });
    
    // Premium hover interactions
    card.addEventListener('mouseenter', function() {
        const title = this.querySelector('h5');
        if (title) {
            title.style.transition = 'color 0.3s ease';
        }
    });
    
    const titleElement = document.createElement('h5');
    titleElement.textContent = article.title;
    
    const descriptionElement = document.createElement('p');
    descriptionElement.textContent = article.description;
    
    const metaElement = document.createElement('div');
    metaElement.className = 'global-card-meta';
    metaElement.innerHTML = `
        <span>${article.source} • ${formatDate(article.published_at)}</span>
        <a href="${article.url}" target="_blank" class="global-btn-link" onclick="event.stopPropagation()">Read Article</a>
    `;
    
    card.appendChild(titleElement);
    card.appendChild(descriptionElement);
    card.appendChild(metaElement);
    
    // Initial state for entrance animation
    card.style.opacity = '0';
    card.style.transform = 'translateY(40px) scale(0.95)';
    
    return card;
}

// Display Literature Context
function displayLiteratureContext(ragContext) {
    const container = document.getElementById('literatureContainer');
    container.innerHTML = '';
    
    if (ragContext && ragContext.sources) {
        // Create a grid container like the features section
        const gridContainer = document.createElement('div');
        gridContainer.className = 'features-grid literature-grid';
        
        ragContext.sources.forEach((source, index) => {
            const card = createLiteratureCard(source, index);
            gridContainer.appendChild(card);
        });
        
        container.appendChild(gridContainer);
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
        // Create APA style reference list
        const referenceList = document.createElement('div');
        referenceList.className = 'apa-references';
        
        allSources.forEach((source, index) => {
            const referenceItem = createAPAReference(source, index);
            referenceList.appendChild(referenceItem);
        });
        
        container.appendChild(referenceList);
    } else {
        container.innerHTML = '<p class="text-center">No reference sources available.</p>';
    }
}

// Create Literature Card
function createLiteratureCard(source, index) {
    const card = document.createElement('div');
    card.className = 'feature-card literature-feature-card';
    card.style.animationDelay = `${index * 0.1}s`;
    card.setAttribute('data-aos', 'fade-up');
    card.setAttribute('data-aos-delay', index * 100);
    
    // Format the book name and get the image
    const formattedBookName = formatBookName(source.book);
    const bookImage = getBookImage(source.book);
    
    // Truncate text preview at exactly 200 characters
    const maxTextLength = 200;
    const truncatedText = source.text_preview && source.text_preview.length > maxTextLength 
        ? source.text_preview.substring(0, maxTextLength) + '...' 
        : source.text_preview || '';
    
    // Create the card content
    if (bookImage) {
        card.innerHTML = `
            <div class="literature-icon">
                <img src="${bookImage}" alt="${formattedBookName}" class="book-feature-image" 
                     onerror="this.style.display='none'; this.parentElement.innerHTML='<i class=\\"fas fa-book\\"></i>';">
            </div>
            <h4 class="book-title" title="${formattedBookName}">${formattedBookName}</h4>
            <div class="book-reference">
                <small class="chapter-info">Chapter: ${source.chapter}</small>
                <small class="page-info">Page: ${source.page}</small>
            </div>
            <p class="book-excerpt" title="${source.text_preview || ''}">${truncatedText}</p>
            <div class="relevance-indicator">
                <span class="relevance-score">${Math.round((source.relevance_score || 0) * 100)}% relevant</span>
            </div>
        `;
        
        // Debug logging
        console.log(`Book: "${source.book}" -> Formatted: "${formattedBookName}" -> Image: "${bookImage}"`);
    } else {
        card.innerHTML = `
            <div class="literature-icon">
                <i class="fas fa-book"></i>
            </div>
            <h4 class="book-title" title="${formattedBookName}">${formattedBookName}</h4>
            <div class="book-reference">
                <small class="chapter-info">Chapter: ${source.chapter}</small>
                <small class="page-info">Page: ${source.page}</small>
            </div>
            <p class="book-excerpt" title="${source.text_preview || ''}">${truncatedText}</p>
            <div class="relevance-indicator">
                <span class="relevance-score">${Math.round((source.relevance_score || 0) * 100)}% relevant</span>
            </div>
        `;
        
        // Debug logging
        console.log(`No image found for book: "${source.book}" -> Formatted: "${formattedBookName}"`);
    }
    
    return card;
}

// Create APA Reference
function createAPAReference(source, index) {
    const referenceItem = document.createElement('div');
    referenceItem.className = 'apa-reference-item';
    referenceItem.style.animationDelay = `${index * 0.1}s`;
    
    // Format date for APA style (YYYY, Month DD)
    const publishDate = source.published_at ? new Date(source.published_at) : new Date();
    const formattedDate = publishDate.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    
    // Create APA style citation
    const citation = `${source.source || 'Unknown Source'}. (${formattedDate}). ${source.title}. Retrieved from <a href="${source.url}" target="_blank" class="reference-link">${source.url}</a>`;
    
    referenceItem.innerHTML = `
        <div class="apa-citation">
            <span class="reference-number">${index + 1}.</span>
            <span class="citation-text">${citation}</span>
        </div>
    `;
    
    return referenceItem;
}

// Format book name - now books have proper spacing already
function formatBookName(bookName) {
    // Book names now come properly formatted from the PDF filenames
    return bookName || '';
}

// Get Book Image
function getBookImage(bookName) {
    if (!bookName) return null;
    
    // Mapping to actual book cover images (URL-friendly names)
    const bookImages = {
        'The Intelligent Investor': '/static/images/books/the-intelligent-investor.png',
        'A Random Walk Down Wall Street': '/static/images/books/a-random-walk-down-wall-street.png',
        'Common Stocks and Uncommon Profits': '/static/images/books/common-stocks-and-uncommon-profits.png',
        'One Up On Wall Street': '/static/images/books/one-up-on-wall-street.png',
        'Stock Investing 101': '/static/images/books/stock-investing-101.png',
        'The Little Book of Common Sense Investing': '/static/images/books/the-little-book-of-common-sense-investing.png'
    };
    
    console.log(`Getting image for book: "${bookName}" -> ${bookImages[bookName] ? 'Found' : 'Not found'}`);
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

// Reset Loading State
function resetLoadingState() {
    const analyzeBtn = document.querySelector('.btn-analyze');
    const loadingState = document.getElementById('loadingState');
    
    if (analyzeBtn) {
        analyzeBtn.classList.remove('loading');
        analyzeBtn.disabled = false;
    }
    
    if (loadingState) {
        loadingState.style.display = 'none';
    }
    
    appState.isLoading = false;
    appState.currentStep = 0;
}

// Hide Results Sections
function hideResultsSections() {
    // Reset carousel index
    appState.currentNewsIndex = 0;
    
    // Hide individual sections
    const sections = [
        '.price-performance-section',
        '.global-context-section', 
        '.literature-insights-section',
        '.sources-references-section'
    ];
    
    sections.forEach(selector => {
        const section = document.querySelector(selector);
        if (section) {
            section.classList.remove('show');
        }
    });
    
    // Hide main results content
    const resultsContent = document.getElementById('resultsContent');
    if (resultsContent) {
        resultsContent.style.display = 'none';
    }
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

/* Caching Indicator */
.caching-indicator {
    position: fixed;
    bottom: 20px;
    left: 20px;
    background: ${appState.cachingEnabled ? '#00b894' : '#e17055'};
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    z-index: 1000;
    animation: pulse 2s infinite;
    cursor: pointer;
    transition: all 0.3s ease;
}

.caching-indicator:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
`;

// Inject notification styles
const styleElement = document.createElement('style');
styleElement.textContent = notificationStyles;
document.head.appendChild(styleElement);

// Toggle caching (for when you want to switch back to live API)
function toggleCaching(enabled) {
    appState.cachingEnabled = enabled;
    console.log(`Caching ${enabled ? 'enabled' : 'disabled'}`);
    
    // Update the persistent indicator
    showCachingIndicator();
    
    // Show temporary notification
    showNotification(
        `Caching ${enabled ? 'enabled' : 'disabled'}. ${enabled ? 'Using cached data for popular tickers.' : 'Making live API calls.'}`,
        enabled ? 'success' : 'warning'
    );
}

// Show caching indicator
function showCachingIndicator() {
    // Remove existing indicator
    const existing = document.querySelector('.caching-indicator');
    if (existing) existing.remove();
    
    const indicator = document.createElement('div');
    indicator.className = 'caching-indicator';
    indicator.innerHTML = `
        <i class="fas fa-${appState.cachingEnabled ? 'database' : 'wifi'}"></i>
        ${appState.cachingEnabled ? 'Cache ON' : 'Live API'}
    `;
    indicator.style.background = appState.cachingEnabled ? '#00b894' : '#e17055';
    
    indicator.addEventListener('click', () => {
        toggleCaching(!appState.cachingEnabled);
    });
    
    document.body.appendChild(indicator);
}

// Caching indicator disabled for production

// Developer convenience functions (available in console)
window.StockWellness = {
    toggleCaching: (enabled) => toggleCaching(enabled),
    enableCaching: () => toggleCaching(true),
    disableCaching: () => toggleCaching(false),
    showCachedTickers: () => {
        console.log('Available cached tickers:', Object.keys(cachedResults));
        return Object.keys(cachedResults);
    },
    currentState: () => appState
}; 