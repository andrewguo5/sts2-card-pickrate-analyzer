// SearchFilterBlock - The shared "Search input + FilterPalette" block rendered by
// BOTH the Table sidebar (CardList) and the Chart sidebar (VisualizationTab), so
// the two views can't drift apart. Each view still owns its own filter/search
// state; this component is presentation only.
//
// Props:
//   searchTerm      - current search string
//   onSearchChange  - (value) => void
//   filterTypes / filterRarities / filterCosts       - active-value arrays
//   onToggleType / onToggleRarity / onToggleCost      - (value) => void
const SearchFilterBlock = ({
    searchTerm,
    onSearchChange,
    filterTypes,
    filterRarities,
    filterCosts,
    onToggleType,
    onToggleRarity,
    onToggleCost
}) => {
    return React.createElement(React.Fragment, null,
        // Search input — sits directly above the palette so they read as one block.
        React.createElement('input', {
            type: 'text',
            className: 'search-input',
            placeholder: 'Search cards...',
            value: searchTerm,
            onChange: (e) => onSearchChange(e.target.value),
            style: { marginBottom: '14px' }
        }),

        // Type / Rarity / Cost filters — shared condensed icon palette.
        React.createElement(window.FilterPalette, {
            filterTypes,
            filterRarities,
            filterCosts,
            onToggleType,
            onToggleRarity,
            onToggleCost
        })
    );
};

// Export component
window.SearchFilterBlock = SearchFilterBlock;
