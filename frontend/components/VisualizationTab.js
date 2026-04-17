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
    const { useState, useMemo } = React;
    const [filterType, setFilterType] = useState('all');
    const [filterRarity, setFilterRarity] = useState('all');
    const [filterCost, setFilterCost] = useState('all');

    // Filter coordinate data based on selected filters
    const filteredCoordinateData = useMemo(() => {
        if (!coordinateData || !coordinateData.coordinates) return coordinateData;

        const filteredCoords = {};
        Object.entries(coordinateData.coordinates).forEach(([cardId, data]) => {
            // Type filter
            if (filterType !== 'all' && data.type !== filterType) {
                return;
            }

            // Rarity filter
            if (filterRarity !== 'all' && data.rarity !== filterRarity) {
                return;
            }

            // Cost filter
            if (filterCost !== 'all') {
                const cardCost = data.cost;
                if (filterCost === '0' && cardCost !== 0) return;
                if (filterCost === '1' && cardCost !== 1) return;
                if (filterCost === '2' && cardCost !== 2) return;
                if (filterCost === '3+' && (cardCost === null || cardCost === undefined || cardCost < 3)) return;
            }

            filteredCoords[cardId] = data;
        });

        return {
            ...coordinateData,
            coordinates: filteredCoords
        };
    }, [coordinateData, filterType, filterRarity, filterCost]);

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

        // Filter controls
        React.createElement('div', {
            style: {
                display: 'flex',
                gap: '15px',
                marginBottom: '20px',
                padding: '15px',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                alignItems: 'center'
            }
        },
            React.createElement('span', { style: { fontWeight: '600', fontSize: '14px' } }, 'Filters:'),

            // Type filter
            React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '8px' } },
                React.createElement('label', { style: { fontSize: '14px', fontWeight: '500' } }, 'Type:'),
                React.createElement('select', {
                    value: filterType,
                    onChange: (e) => setFilterType(e.target.value),
                    style: {
                        padding: '6px 10px',
                        borderRadius: '4px',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        color: 'inherit',
                        fontSize: '13px',
                        cursor: 'pointer'
                    }
                },
                    React.createElement('option', { value: 'all' }, 'All Types'),
                    React.createElement('option', { value: 'Attack' }, 'Attack'),
                    React.createElement('option', { value: 'Skill' }, 'Skill'),
                    React.createElement('option', { value: 'Power' }, 'Power'),
                    React.createElement('option', { value: 'Curse' }, 'Curse'),
                    React.createElement('option', { value: 'Status' }, 'Status')
                )
            ),

            // Rarity filter
            React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '8px' } },
                React.createElement('label', { style: { fontSize: '14px', fontWeight: '500' } }, 'Rarity:'),
                React.createElement('select', {
                    value: filterRarity,
                    onChange: (e) => setFilterRarity(e.target.value),
                    style: {
                        padding: '6px 10px',
                        borderRadius: '4px',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        color: 'inherit',
                        fontSize: '13px',
                        cursor: 'pointer'
                    }
                },
                    React.createElement('option', { value: 'all' }, 'All Rarities'),
                    React.createElement('option', { value: 'Common' }, 'Common'),
                    React.createElement('option', { value: 'Uncommon' }, 'Uncommon'),
                    React.createElement('option', { value: 'Rare' }, 'Rare')
                )
            ),

            // Cost filter
            React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '8px' } },
                React.createElement('label', { style: { fontSize: '14px', fontWeight: '500' } }, 'Cost:'),
                React.createElement('select', {
                    value: filterCost,
                    onChange: (e) => setFilterCost(e.target.value),
                    style: {
                        padding: '6px 10px',
                        borderRadius: '4px',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        color: 'inherit',
                        fontSize: '13px',
                        cursor: 'pointer'
                    }
                },
                    React.createElement('option', { value: 'all' }, 'All Costs'),
                    React.createElement('option', { value: '0' }, '0'),
                    React.createElement('option', { value: '1' }, '1'),
                    React.createElement('option', { value: '2' }, '2'),
                    React.createElement('option', { value: '3+' }, '3+')
                )
            ),

            // Card count
            coordinateData && coordinateData.coordinates && React.createElement('div', {
                style: {
                    marginLeft: 'auto',
                    fontSize: '13px',
                    color: 'rgba(255, 255, 255, 0.7)'
                }
            },
                `Showing ${Object.keys(filteredCoordinateData.coordinates).length} of ${Object.keys(coordinateData.coordinates).length} cards`
            )
        ),

        // Scatter plot
        React.createElement('div', {
            className: 'chart-section',
            style: { height: '600px' }
        },
            coordinateData
                ? React.createElement(window.CardScatterPlot, {
                    coordinateData: filteredCoordinateData,
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
