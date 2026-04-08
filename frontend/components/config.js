// API configuration
const API_BASE_URL = 'https://mbgg-api.up.railway.app';

// Character options
const CHARACTERS = [
    { id: 'ironclad', name: 'Ironclad' },
    { id: 'silent', name: 'Silent' },
    { id: 'regent', name: 'Regent' },
    { id: 'necrobinder', name: 'Necrobinder' },
    { id: 'defect', name: 'Defect' }
];

// Mode options
const MODES = [
    { id: 'singleplayer', name: 'Singleplayer' },
    { id: 'multiplayer', name: 'Multiplayer' },
    { id: 'all', name: 'All Games' }
];

// Ascension options
const ASCENSIONS = [
    { id: 'a10', name: 'A10' },
    { id: 'a0-9', name: 'A0-9' },
    { id: 'all', name: 'All Ascensions' }
];

// Export for use in other modules
window.AppConfig = {
    API_BASE_URL,
    CHARACTERS,
    MODES,
    ASCENSIONS
};
