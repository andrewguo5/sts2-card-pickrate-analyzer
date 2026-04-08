// CardDetail - Main panel displaying card statistics, charts, and detailed data
const CardDetail = ({ selectedCard, chartData }) => {
    if (!selectedCard) {
        return React.createElement('div', { className: 'empty-state' },
            React.createElement('div', { className: 'empty-state-icon' }, '📊'),
            React.createElement('h3', null, 'Select a card to view pick rate analysis')
        );
    }

    return React.createElement(React.Fragment, null,
        // Card title
        React.createElement('h2', { className: 'card-title' }, selectedCard.name),

        // Summary stats grid (using summary-stats className instead of stats-grid)
        React.createElement('div', { className: 'summary-stats' },
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Overall Pick Rate'),
                React.createElement('div', { className: 'stat-value' },
                    `${(selectedCard.overall_pickrate * 100).toFixed(1)}%`
                )
            ),
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Total Offered'),
                React.createElement('div', { className: 'stat-value' }, selectedCard.total_offered)
            ),
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Total Picked'),
                React.createElement('div', { className: 'stat-value' }, selectedCard.total_picked)
            ),
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Total Passed'),
                React.createElement('div', { className: 'stat-value' }, selectedCard.total_passed)
            )
        ),

        // Chart section
        React.createElement('div', { className: 'chart-section' },
            React.createElement('h3', { className: 'chart-title' }, 'Pick Rate by Floor (Kernel Smoothed)'),
            React.createElement('div', { className: 'chart-container' },
                chartData && chartData.length > 0
                    ? React.createElement(window.ChartComponent, { chartData })
                    : React.createElement('p', null, 'No data available for this card')
            )
        ),

        // Data table
        React.createElement('div', { className: 'data-table' },
            React.createElement('h3', { className: 'chart-title' }, 'Detailed Floor Data'),
            chartData && chartData.length > 0
                ? React.createElement('div', { className: 'table-wrapper' },
                        React.createElement('table', null,
                            React.createElement('thead', null,
                                React.createElement('tr', null,
                                    React.createElement('th', null, 'Floor'),
                                    React.createElement('th', null, 'Offered'),
                                    React.createElement('th', null, 'Picked'),
                                    React.createElement('th', null, 'Pick Rate (Raw)'),
                                    React.createElement('th', null, 'Pick Rate (Smoothed)'),
                                    React.createElement('th', null, 'Pick Rate (Smoothed)')
                                )
                            ),
                            React.createElement('tbody', null,
                                chartData.map(row =>
                                    React.createElement('tr', { key: row.floor },
                                        React.createElement('td', null, React.createElement('strong', null, row.floor)),
                                        React.createElement('td', null, row.offered),
                                        React.createElement('td', null, row.picked),
                                        React.createElement('td', null, `${row.raw.toFixed(1)}%`),
                                        React.createElement('td', null, React.createElement('strong', null, `${row.smoothed.toFixed(1)}%`)),
                                        React.createElement('td', null,
                                            React.createElement('div', { className: 'progress-bar' },
                                                React.createElement('div', {
                                                    className: 'progress-fill',
                                                    style: { width: `${row.smoothed}%` }
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
window.CardDetail = CardDetail;
