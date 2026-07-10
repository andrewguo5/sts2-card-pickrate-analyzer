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
    const [searchTerm, setSearchTerm] = useState('');
    const [showDeltas, setShowDeltas] = useState(false);

    // Baseline positions power the deltas animation. Buckets with too few runs come
    // back with none, so the button is disabled rather than doing nothing.
    const hasDeltas = !!(
        coordinateData &&
        coordinateData.baseline_coordinates &&
        Object.keys(coordinateData.baseline_coordinates).length > 0
    );

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
        // Content area with sidebar and chart
        React.createElement('div', { className: 'content' },
            // Filter sidebar (left)
            React.createElement('div', { className: 'sidebar' },
                React.createElement('div', { style: { padding: '20px' } },
                    React.createElement('h3', { style: { marginTop: 0, marginBottom: '15px', fontSize: '16px' } }, 'Filters'),

                // Search input
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
                    }, 'Search'),
                    React.createElement('input', {
                        type: 'text',
                        className: 'search-input',
                        placeholder: 'Search cards...',
                        value: searchTerm,
                        onChange: (e) => setSearchTerm(e.target.value),
                        style: {
                            width: '100%',
                            padding: '8px 12px',
                            border: '2px solid #374151',
                            borderRadius: '6px',
                            background: '#111827',
                            color: 'white',
                            fontSize: '14px',
                            fontWeight: '500'
                        }
                    })
                ),

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
                        React.createElement('option', { value: 'Power' }, 'Power')
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
                        position: 'relative', // anchor the floating "See Deltas" button
                        height: 'calc(100vh - 200px)',
                        margin: '20px',
                        padding: '20px',
                        backgroundColor: '#fafafa',
                        borderRadius: '8px',
                        border: '2px solid #e5e7eb'
                    }
                },
                    // Floating deltas button, clipping the chart's top-right corner.
                    // Hold to play the animation; release snaps back.
                    coordinateData && React.createElement('button', {
                        onMouseDown: () => hasDeltas && setShowDeltas(true),
                        onMouseUp: () => setShowDeltas(false),
                        onMouseLeave: () => setShowDeltas(false),
                        onTouchStart: (e) => {
                            e.preventDefault(); // avoid the synthetic click / scroll
                            if (hasDeltas) setShowDeltas(true);
                        },
                        onTouchEnd: () => setShowDeltas(false),
                        disabled: !hasDeltas,
                        title: hasDeltas
                            ? 'Hold to see how the last 10 runs shifted each card'
                            : 'Not enough runs to show deltas',
                        style: {
                            position: 'absolute',
                            top: 0,
                            right: 0,
                            zIndex: 5,
                            padding: '8px 16px',
                            // Clip the corner: flush to the top-right, only the
                            // inner (bottom-left) corner is rounded.
                            borderRadius: '0 6px 0 10px',
                            border: 'none',
                            background: showDeltas ? '#4338ca' : 'rgba(17, 24, 39, 0.85)',
                            color: hasDeltas ? 'white' : '#6b7280',
                            fontSize: '13px',
                            fontWeight: '600',
                            letterSpacing: '0.3px',
                            cursor: hasDeltas ? 'pointer' : 'not-allowed',
                            transition: 'background 0.2s',
                            userSelect: 'none' // holding shouldn't select the label
                        }
                    },
                        // Dot always occupies its slot so the button width is fixed;
                        // it only becomes visible (with the color change) while held.
                        React.createElement('span', {
                            style: {
                                marginRight: '6px',
                                opacity: showDeltas ? 1 : 0,
                                transition: 'opacity 0.2s'
                            }
                        }, '●'),
                        'See Deltas'
                    ),

                    coordinateData
                        ? React.createElement(window.CardScatterPlot, {
                            coordinateData: filteredCoordinateData,
                            onCardClick,
                            selectedCardId,
                            searchTerm,
                            showDeltas: showDeltas && hasDeltas
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
