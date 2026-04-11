// API configuration and constants
// Auto-detect environment based on hostname
function getApiBaseUrl() {
    const hostname = window.location.hostname;

    // If running on QA domain, use QA backend
    if (hostname.includes('-qa.') || hostname.includes('qa-')) {
        return 'https://mbgg-api-qa.up.railway.app';
    }

    // Default to production
    return 'https://mbgg-api.up.railway.app';
}

window.AppConfig = {
    API_BASE_URL: getApiBaseUrl(),

    CHARACTERS: [
        {
            id: 'ironclad',
            name: 'Ironclad',
            colors: {
                primary: '#dc2626',    // red-600
                secondary: '#991b1b',  // red-800
                accent: '#fca5a5',     // red-300
                gradient: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)'
            }
        },
        {
            id: 'silent',
            name: 'Silent',
            colors: {
                primary: '#059669',    // emerald-600
                secondary: '#065f46',  // emerald-800
                accent: '#6ee7b7',     // emerald-300
                gradient: 'linear-gradient(135deg, #059669 0%, #065f46 100%)'
            }
        },
        {
            id: 'regent',
            name: 'Regent',
            colors: {
                primary: '#ea580c',    // orange-600
                secondary: '#c2410c',  // orange-700
                accent: '#fdba74',     // orange-300
                gradient: 'linear-gradient(135deg, #ea580c 0%, #c2410c 100%)'
            }
        },
        {
            id: 'necrobinder',
            name: 'Necrobinder',
            colors: {
                primary: '#7c3aed',    // violet-600
                secondary: '#5b21b6',  // violet-800
                accent: '#c4b5fd',     // violet-300
                gradient: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)'
            }
        },
        {
            id: 'defect',
            name: 'Defect',
            colors: {
                primary: '#0891b2',    // cyan-600
                secondary: '#0e7490',  // cyan-700
                accent: '#67e8f9',     // cyan-300
                gradient: 'linear-gradient(135deg, #0891b2 0%, #0e7490 100%)'
            }
        }
    ],

    MODES: [
        { id: 'singleplayer', name: 'Singleplayer' },
        { id: 'multiplayer', name: 'Multiplayer' },
        { id: 'all', name: 'All Games' }
    ],

    ASCENSIONS: [
        { id: 'a10', name: 'A10' },
        { id: 'a0-9', name: 'A0-9' },
        { id: 'all', name: 'All Ascensions' }
    ]
};
