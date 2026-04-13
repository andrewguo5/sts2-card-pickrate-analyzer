// MetadataBar - Displays metadata about the current dataset
const MetadataBar = ({ metadata, usernameCache }) => {
    if (!metadata) return null;

    // Get username from cache if available, otherwise show steam ID
    const getUserDisplay = (steamId) => {
        if (!steamId) return null;
        const username = usernameCache[steamId];
        return username || steamId;
    };

    return React.createElement('div', { className: 'metadata' },
        React.createElement('div', { className: 'metadata-item' },
            React.createElement('span', { className: 'metadata-label' }, 'Character: '),
            React.createElement('span', { className: 'metadata-value' },
                metadata.character.replace('CHARACTER.', '')
            )
        ),
        React.createElement('div', { className: 'metadata-item' },
            React.createElement('span', { className: 'metadata-label' }, 'Ascension: '),
            React.createElement('span', { className: 'metadata-value' }, metadata.ascension_level)
        ),
        React.createElement('div', { className: 'metadata-item' },
            React.createElement('span', { className: 'metadata-label' }, 'Mode: '),
            React.createElement('span', { className: 'metadata-value' }, metadata.multiplayer_filter || 'all')
        ),
        React.createElement('div', { className: 'metadata-item' },
            React.createElement('span', { className: 'metadata-label' }, 'Runs: '),
            React.createElement('span', { className: 'metadata-value' }, metadata.runs_processed)
        ),
        React.createElement('div', { className: 'metadata-item' },
            React.createElement('span', { className: 'metadata-label' }, 'Kernel Smoothing: '),
            React.createElement('span', { className: 'metadata-value' }, `b=${metadata.kernel_bandwidth}`)
        ),
        metadata.steam_id && React.createElement('div', { className: 'metadata-item' },
            React.createElement('span', { className: 'metadata-label' }, 'User: '),
            React.createElement('span', { className: 'metadata-value' }, getUserDisplay(metadata.steam_id))
        )
    );
};

// Export component
window.MetadataBar = MetadataBar;
