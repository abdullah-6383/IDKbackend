// Frontend Configuration
const CONFIG = {
    // API Backend URLs for different environments
    API_URLS: {
        development: 'http://localhost:8000',
        staging: 'https://your-staging-backend.com',
        production: 'https://your-production-backend.com'
    },
    
    // Current environment (development, staging, production)
    ENVIRONMENT: 'development',
    
    // Feature flags
    FEATURES: {
        debugMode: true,
        mockData: false,
        analytics: false
    },
    
    // UI Settings
    UI: {
        theme: 'light',
        autoRefresh: false,
        animationsEnabled: true
    }
};

// Export for use in other scripts
window.APP_CONFIG = CONFIG;