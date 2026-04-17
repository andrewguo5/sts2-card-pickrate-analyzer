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
        // Title section spanning full width
        React.createElement('div', {
            style: {
                padding: '20px 30px',
                backgroundColor: 'white',
                borderBottom: '1px solid #e5e7eb'
            }
        },
            React.createElement('h2', { style: { margin: '0', fontSize: '20px' } },
                'Card 2D Visualization',
                React.createElement(window.InfoIcon, { term: 'card_visualization' })
            ),
            React.createElement('p', { style: { margin: '8px 0 0 0', fontSize: '14px', color: '#6b7280' } },
                'Each point represents a card. Hover over points to see details, or click to select a card.'
            )
        ),

        // Content area with sidebar and chart
        React.createElement('div', { className: 'content' },
            // Filter sidebar (left)
            React.createElement('div', { className: 'sidebar' },
                React.createElement('div', { style: { padding: '20px' } },
                    React.createElement('h3', { style: { marginTop: 0, marginBottom: '15px', fontSize: '16px' } }, 'Filters'),

                // Type filter
                React.createElement('div', { style: { marginBottom: '15px' } },
                    React.createElement('label', {
                        style: {
                            display: 'block',
                            fontSize: '12px',
                            fontWeight: '600',
                            color: '#9ca3af',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            marginBottom: '8px'
                        }
                    }, 'Type'),
                    React.createElement('select', {
                        className: 'filter-select',
                        value: filterType,
                        onChange: (e) => setFilterType(e.target.value),
                        style: { width: '100%' }
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
                React.createElement('div', { style: { marginBottom: '15px' } },
                    React.createElement('label', {
                        style: {
                            display: 'block',
                            fontSize: '12px',
                            fontWeight: '600',
                            color: '#9ca3af',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            marginBottom: '8px'
                        }
                    }, 'Rarity'),
                    React.createElement('select', {
                        className: 'filter-select',
                        value: filterRarity,
                        onChange: (e) => setFilterRarity(e.target.value),
                        style: { width: '100%' }
                    },
                        React.createElement('option', { value: 'all' }, 'All Rarities'),
                        React.createElement('option', { value: 'Common' }, 'Common'),
                        React.createElement('option', { value: 'Uncommon' }, 'Uncommon'),
                        React.createElement('option', { value: 'Rare' }, 'Rare')
                    )
                ),

                // Cost filter
                React.createElement('div', { style: { marginBottom: '15px' } },
                    React.createElement('label', {
                        style: {
                            display: 'block',
                            fontSize: '12px',
                            fontWeight: '600',
                            color: '#9ca3af',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            marginBottom: '8px'
                        }
                    }, 'Cost'),
                    React.createElement('select', {
                        className: 'filter-select',
                        value: filterCost,
                        onChange: (e) => setFilterCost(e.target.value),
                        style: { width: '100%' }
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
                        marginTop: '20px',
                        paddingTop: '15px',
                        borderTop: '1px solid #e5e7eb',
                        fontSize: '13px',
                        color: '#6b7280',
                        textAlign: 'center'
                    }
                },
                    React.createElement('div', null, `Showing ${Object.keys(filteredCoordinateData.coordinates).length}`),
                    React.createElement('div', null, `of ${Object.keys(coordinateData.coordinates).length} cards`)
                )
            )
        ),

            // Main panel (right) - chart area
            React.createElement('div', { className: 'main-panel' },
                // Chart with border
                React.createElement('div', {
                    className: 'chart-section',
                    style: {
                        height: 'calc(100vh - 280px)',
                        margin: '20px',
                        padding: '20px',
                        backgroundColor: '#fafafa',
                        borderRadius: '8px',
                        border: '2px solid #e5e7eb'
                    }
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
                )
            )
        )
    );
};

// Export component
window.VisualizationTab = VisualizationTab;
