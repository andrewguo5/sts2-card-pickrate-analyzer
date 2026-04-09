// CardList - Sidebar with searchable list of cards
const CardList = ({
    cards,
    selectedCard,
    onSelectCard,
    searchTerm,
    onSearchChange,
    sortBy,
    onSortChange,
    filterType,
    onFilterTypeChange,
    filterRarity,
    onFilterRarityChange
}) => {
    return React.createElement('div', { className: 'sidebar' },
        // Search and filters box
        React.createElement('div', { className: 'search-box' },
            // Search input
            React.createElement('input', {
                type: 'text',
                className: 'search-input',
                placeholder: 'Search cards...',
                value: searchTerm,
                onChange: (e) => onSearchChange(e.target.value),
                style: { marginBottom: '10px' }
            }),

            // Sort dropdown
            React.createElement('select', {
                className: 'filter-select',
                value: sortBy,
                onChange: (e) => onSortChange(e.target.value),
                style: { width: '100%', marginBottom: '8px', fontSize: '13px', padding: '6px' }
            },
                React.createElement('option', { value: 'offered' }, 'Sort: Most Offered'),
                React.createElement('option', { value: 'pickrate' }, 'Sort: Pick Rate %'),
                React.createElement('option', { value: 'alphabetical' }, 'Sort: Alphabetical')
            ),

            // Type filter dropdown
            React.createElement('select', {
                className: 'filter-select',
                value: filterType,
                onChange: (e) => onFilterTypeChange(e.target.value),
                style: { width: '100%', marginBottom: '8px', fontSize: '13px', padding: '6px' }
            },
                React.createElement('option', { value: 'all' }, 'Type: All'),
                React.createElement('option', { value: 'Attack' }, 'Type: Attack'),
                React.createElement('option', { value: 'Skill' }, 'Type: Skill'),
                React.createElement('option', { value: 'Power' }, 'Type: Power')
            ),

            // Rarity filter dropdown
            React.createElement('select', {
                className: 'filter-select',
                value: filterRarity,
                onChange: (e) => onFilterRarityChange(e.target.value),
                style: { width: '100%', fontSize: '13px', padding: '6px' }
            },
                React.createElement('option', { value: 'all' }, 'Rarity: All'),
                React.createElement('option', { value: 'Common' }, 'Rarity: Common'),
                React.createElement('option', { value: 'Uncommon' }, 'Rarity: Uncommon'),
                React.createElement('option', { value: 'Rare' }, 'Rarity: Rare')
            )
        ),

        // Card list
        React.createElement('div', { className: 'card-list' },
            cards.length > 0
                ? cards.map(card =>
                    React.createElement('div', {
                        key: card.id,
                        className: `card-item ${selectedCard?.id === card.id ? 'selected' : ''}`,
                        onClick: () => onSelectCard(card)
                    },
                        React.createElement('div', { className: 'card-name' }, card.name || card.id.replace('CARD.', '')),
                        React.createElement('div', { className: 'card-stats' },
                            React.createElement('span', { className: 'stat-badge' }, `${card.total_offered} offered`),
                            React.createElement('span', { className: 'stat-badge' }, `${(card.overall_pickrate * 100).toFixed(1)}%`)
                        )
                    )
                )
                : React.createElement('div', { style: { padding: '20px', textAlign: 'center', color: '#9ca3af' } },
                    'No cards match filters'
                )
        )
    );
};

// Export component
window.CardList = CardList;
