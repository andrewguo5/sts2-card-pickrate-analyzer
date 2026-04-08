// CardList - Sidebar with searchable list of cards
const CardList = ({ cards, selectedCard, onSelectCard, searchTerm, onSearchChange }) => {
    return React.createElement('div', { className: 'sidebar' },
        // Search box
        React.createElement('div', { className: 'search-box' },
            React.createElement('input', {
                type: 'text',
                className: 'search-input',
                placeholder: 'Search cards...',
                value: searchTerm,
                onChange: (e) => onSearchChange(e.target.value)
            })
        ),

        // Card list
        React.createElement('div', { className: 'card-list' },
            cards.map(card =>
                React.createElement('div', {
                    key: card.id,
                    className: `card-item ${selectedCard?.id === card.id ? 'selected' : ''}`,
                    onClick: () => onSelectCard(card)
                },
                    React.createElement('div', { className: 'card-name' }, card.name),
                    React.createElement('div', { className: 'card-stats' },
                        React.createElement('span', { className: 'stat-badge' }, `${card.total_offered} offered`),
                        React.createElement('span', { className: 'stat-badge' }, `${(card.overall_pickrate * 100).toFixed(1)}%`)
                    )
                )
            )
        )
    );
};

// Export component
window.CardList = CardList;
