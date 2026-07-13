// CardList - Sidebar with searchable list of cards
const CardList = ({
    cards,
    selectedCard,
    onSelectCard,
    searchTerm,
    onSearchChange,
    sortBy,
    onSortChange,
    filterTypes,
    onToggleType,
    filterRarities,
    onToggleRarity,
    filterCosts,
    onToggleCost,
    activeTab,
    showTrend
}) => {
    return React.createElement('div', { className: 'sidebar' },
        // Search and filters box
        React.createElement('div', { className: 'search-box' },
            // Sort dropdown — on top so Search sits directly above the palette.
            React.createElement('select', {
                className: 'filter-select',
                value: sortBy,
                onChange: (e) => onSortChange(e.target.value),
                style: { width: '100%', marginBottom: '8px', fontSize: '13px', padding: '6px' }
            },
                React.createElement('option', { value: 'offered' }, 'Sort: Most Offered'),
                React.createElement('option', { value: 'pickrate' }, 'Sort: Pick Rate %'),
                React.createElement('option', { value: 'winrate' }, 'Sort: Win Rate %'),
                React.createElement('option', { value: 'skiprate' }, 'Sort: Least Skipped'),
                React.createElement('option', { value: 'alphabetical' }, 'Sort: Alphabetical')
            ),

            // Search + Type/Rarity/Cost palette — shared with the Chart sidebar
            // so the two views can't drift apart.
            React.createElement(window.SearchFilterBlock, {
                searchTerm,
                onSearchChange,
                filterTypes,
                filterRarities,
                filterCosts,
                onToggleType,
                onToggleRarity,
                onToggleCost
            })
        ),

        // Card list
        React.createElement('div', { className: 'card-list' },
            cards.length > 0
                ? cards.map(card => {
                    // Badge % and trend arrow follow the active detail tab.
                    const { rate, deltaPp, sufficient } = window.resolveTabStat(card, activeTab);
                    return React.createElement('div', {
                        key: card.id,
                        className: `card-item ${selectedCard?.id === card.id ? 'selected' : ''}`,
                        onClick: () => onSelectCard(card)
                    },
                        React.createElement('div', { className: 'card-name' }, card.name || card.id.replace('CARD.', '')),
                        React.createElement('div', { className: 'card-stats' },
                            React.createElement('span', { className: 'stat-badge' }, `${card.total_offered} offered`),
                            React.createElement('span', { className: 'stat-badge' }, `${(rate * 100).toFixed(1)}%`),
                            showTrend && React.createElement(window.DeltaBadge, {
                                deltaPp,
                                sufficient,
                                hideWhenFlat: true
                            })
                        )
                    );
                })
                : React.createElement('div', { style: { padding: '20px', textAlign: 'center', color: '#9ca3af' } },
                    'No cards match filters'
                )
        )
    );
};

// Export component
window.CardList = CardList;
