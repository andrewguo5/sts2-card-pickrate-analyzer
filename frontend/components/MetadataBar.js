// MetadataBar - Displays metadata about the current dataset
const MetadataBar = ({ metadata }) => {
    if (!metadata) return null;

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
            React.createElement('span', { className: 'metadata-label' }, 'Steam ID: '),
            React.createElement('span', { className: 'metadata-value' }, metadata.steam_id)
        )
    );
};

// Export component
window.MetadataBar = MetadataBar;
