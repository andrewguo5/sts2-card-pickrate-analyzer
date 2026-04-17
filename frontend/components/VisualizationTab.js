// VisualizationTab - 2D card visualization view
const VisualizationTab = ({
    coordinateData,
    onCardClick,
    selectedCardId,
    character,
    mode,
    ascension,
    selectedUser
}) => {
    return React.createElement(React.Fragment, null,
        // Description section
        React.createElement('div', { className: 'visualization-description', style: {
            padding: '20px',
            marginBottom: '20px',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '8px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
        }},
            React.createElement('h3', { style: { marginTop: 0, marginBottom: '10px' } },
                'Card 2D Visualization',
                React.createElement(window.InfoIcon, { term: 'card_visualization' })
            ),
            React.createElement('p', { style: { margin: '8px 0', fontSize: '14px' } },
                'Each point represents a card. Hover over points to see details, or click to select a card.'
            ),
            React.createElement('div', { style: { display: 'flex', gap: '30px', marginTop: '15px', flexWrap: 'wrap' } },
                React.createElement('div', { style: { flex: '1', minWidth: '200px' } },
                    React.createElement('strong', null, 'X-axis: Pickability'),
                    React.createElement('p', { style: { margin: '5px 0 0 0', fontSize: '13px', color: 'rgba(255, 255, 255, 0.7)' } },
                        'Measures how pickable/playable a card is. Higher values = more picked, less skipped.'
                    ),
                    React.createElement('p', { style: { margin: '5px 0 0 0', fontSize: '12px', color: 'rgba(255, 255, 255, 0.5)', fontStyle: 'italic' } },
                        'Formula: (Pick Rate - Skip Rate) normalized to [0, 100]'
                    )
                ),
                React.createElement('div', { style: { flex: '1', minWidth: '200px' } },
                    React.createElement('strong', null, 'Y-axis: Conditional Power'),
                    React.createElement('p', { style: { margin: '5px 0 0 0', fontSize: '13px', color: 'rgba(255, 255, 255, 0.7)' } },
                        'Measures how well a card performs when picked. Higher values = higher win rate.'
                    ),
                    React.createElement('p', { style: { margin: '5px 0 0 0', fontSize: '12px', color: 'rgba(255, 255, 255, 0.5)', fontStyle: 'italic' } },
                        'Formula: Win Rate (with Rule of Succession smoothing)'
                    )
                )
            )
        ),

        // Scatter plot
        React.createElement('div', {
            className: 'chart-section',
            style: { height: '600px' }
        },
            coordinateData
                ? React.createElement(window.CardScatterPlot, {
                    coordinateData,
                    onCardClick,
                    selectedCardId
                })
                : React.createElement('div', { className: 'loading', style: { padding: '40px', textAlign: 'center' } },
                    'Loading coordinate data...'
                )
        ),

        // Summary statistics
        coordinateData && coordinateData.coordinates && React.createElement('div', {
            className: 'summary-stats',
            style: { marginTop: '20px' }
        },
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Total Cards'),
                React.createElement('div', { className: 'stat-value' },
                    Object.keys(coordinateData.coordinates).length
                )
            ),
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Runs Analyzed'),
                React.createElement('div', { className: 'stat-value' },
                    coordinateData.metadata?.runs_processed || 0
                )
            )
        )
    );
};

// Export component
window.VisualizationTab = VisualizationTab;
