// CardDetail - Main panel displaying card statistics with tabs for different analyses
const CardDetail = ({ selectedCard, chartData, skipRateData, winRateData, baselineSkipData, activeTab, setActiveTab }) => {
    if (!selectedCard) {
        return React.createElement('div', { className: 'empty-state' },
            React.createElement('div', { className: 'empty-state-icon' }, '📊'),
            React.createElement('h3', null, 'Select a card to view analysis')
        );
    }

    return React.createElement(React.Fragment, null,
        // Card title
        React.createElement('h2', { className: 'card-title' }, selectedCard.name),

        // Tab navigation
        React.createElement('div', { className: 'tab-navigation' },
            React.createElement('button', {
                className: activeTab === 'pickrate' ? 'tab-button active' : 'tab-button',
                onClick: () => setActiveTab('pickrate')
            }, 'Pick Rate'),
            React.createElement('button', {
                className: activeTab === 'skiprate' ? 'tab-button active' : 'tab-button',
                onClick: () => setActiveTab('skiprate')
            }, 'Skip Rate'),
            React.createElement('button', {
                className: activeTab === 'winrate' ? 'tab-button active' : 'tab-button',
                onClick: () => setActiveTab('winrate')
            }, 'Win Rate')
        ),

        // Tab content
        React.createElement('div', { className: 'tab-content' },
            activeTab === 'pickrate' && React.createElement(window.PickRateTab, { selectedCard, chartData }),
            activeTab === 'skiprate' && React.createElement(window.SkipRateTab, { selectedCard, skipRateData, baselineSkipData }),
            activeTab === 'winrate' && React.createElement(window.WinRateTab, { selectedCard, winRateData })
        )
    );
};

// Export component
window.CardDetail = CardDetail;
