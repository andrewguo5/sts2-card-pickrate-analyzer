// WinRateTab - Win rate analysis by act
const WinRateTab = ({ selectedCard, winRateData }) => {
    // Get overall win rate (runs won where card picked / runs where card picked)
    const overallData = selectedCard.winrate_data?.overall || { picked: 0, won: 0 };
    const totalPicked = overallData.picked;
    const totalWon = overallData.won;
    const overallWinRate = totalPicked > 0 ? (totalWon / totalPicked) : 0;

    return React.createElement(React.Fragment, null,
        // Summary stats grid
        React.createElement('div', { className: 'summary-stats' },
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Overall Win Rate'),
                React.createElement('div', { className: 'stat-value' },
                    `${(overallWinRate * 100).toFixed(1)}%`
                )
            ),
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Runs with Card'),
                React.createElement('div', { className: 'stat-value' }, totalPicked)
            ),
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Runs Won'),
                React.createElement('div', { className: 'stat-value' }, totalWon)
            )
        ),

        // Chart section
        React.createElement('div', { className: 'chart-section' },
            React.createElement('h3', { className: 'chart-title' }, 'Win Rate by Act Picked'),
            React.createElement('div', { className: 'chart-container' },
                winRateData && winRateData.length > 0
                    ? React.createElement(window.WinRateChart, { winRateData })
                    : React.createElement('p', null, 'No data available for this card')
            )
        ),

        // Data table
        React.createElement('div', { className: 'data-table' },
            React.createElement('h3', { className: 'chart-title' }, 'Detailed Act Data'),
            winRateData && winRateData.length > 0
                ? React.createElement('div', { className: 'table-wrapper' },
                        React.createElement('table', null,
                            React.createElement('thead', null,
                                React.createElement('tr', null,
                                    React.createElement('th', null, 'Act'),
                                    React.createElement('th', null, 'Times Picked'),
                                    React.createElement('th', null, 'Wins'),
                                    React.createElement('th', null, 'Win Rate'),
                                    React.createElement('th', null, 'Win Rate')
                                )
                            ),
                            React.createElement('tbody', null,
                                winRateData.map(row =>
                                    React.createElement('tr', { key: row.act },
                                        React.createElement('td', null, React.createElement('strong', null, `Act ${row.act}`)),
                                        React.createElement('td', null, row.picked),
                                        React.createElement('td', null, row.won),
                                        React.createElement('td', null, React.createElement('strong', null, `${row.winrate.toFixed(1)}%`)),
                                        React.createElement('td', null,
                                            React.createElement('div', { className: 'progress-bar' },
                                                React.createElement('div', {
                                                    className: 'progress-fill',
                                                    style: { width: `${row.winrate}%` }
                                                })
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                : React.createElement('p', null, 'No data available')
        )
    );
};

// Export component
window.WinRateTab = WinRateTab;
