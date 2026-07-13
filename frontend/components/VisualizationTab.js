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
    // Multi-select filters — empty array means "show all" for that dimension.
    // Independent from the Table view's own filter state.
    const [filterTypes, setFilterTypes] = useState([]);
    const [filterRarities, setFilterRarities] = useState([]);
    const [filterCosts, setFilterCosts] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [showDeltas, setShowDeltas] = useState(false);

    const toggleType = (value) => setFilterTypes(prev => window.toggleInArray(prev, value));
    const toggleRarity = (value) => setFilterRarities(prev => window.toggleInArray(prev, value));
    const toggleCost = (value) => setFilterCosts(prev => window.toggleInArray(prev, value));

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
            // Each filter narrows only when its selection is non-empty; an empty
            // selection means "show all" for that dimension.
            if (filterTypes.length && !filterTypes.includes(data.type)) return;
            if (filterRarities.length && !filterRarities.includes(data.rarity)) return;
            if (filterCosts.length && !filterCosts.includes(window.costBucket(data.cost, data.is_x_cost))) return;

            filteredCoords[cardId] = data;
        });

        return {
            ...coordinateData,
            coordinates: filteredCoords
        };
    }, [coordinateData, filterTypes, filterRarities, filterCosts]);

    return React.createElement(React.Fragment, null,
        // Content area with sidebar and chart. .content--viz shares the desktop
        // grid with the Table but opts out of the Table's mobile slide-over track
        // (see .content--table); on mobile it stacks the sidebar above the chart.
        React.createElement('div', { className: 'content content--viz' },
            // Filter sidebar (left)
            React.createElement('div', { className: 'sidebar' },
                React.createElement('div', { style: { padding: '20px' } },
                    React.createElement('h3', { style: { marginTop: 0, marginBottom: '15px', fontSize: '16px' } }, 'Filters'),

                // Search + Type/Rarity/Cost palette — shared with the Table sidebar
                // so the two views can't drift apart.
                React.createElement(window.SearchFilterBlock, {
                    searchTerm,
                    onSearchChange: setSearchTerm,
                    filterTypes,
                    filterRarities,
                    filterCosts,
                    onToggleType: toggleType,
                    onToggleRarity: toggleRarity,
                    onToggleCost: toggleCost
                }),

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
                    className: 'chart-section viz-chart-section',
                    style: {
                        position: 'relative', // anchor the floating "See Deltas" button
                        height: 'calc(100vh - 200px)',
                        // Tighter top gap so the chart starts higher; sides/bottom
                        // keep their breathing room. Height is unchanged.
                        margin: '8px 20px 20px',
                        padding: '8px 20px 20px',
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
                            showDeltas: showDeltas && hasDeltas,
                            baselineWinrate: coordinateData.baseline_winrate
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
