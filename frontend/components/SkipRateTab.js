// SkipRateTab - Skip rate analysis view
const SkipRateTab = ({ selectedCard, skipRateData, baselineSkipData }) => {
    // Calculate overall skip rate
    const totalOffered = Object.values(selectedCard.skip_data || {}).reduce((sum, counts) => sum + counts.offered, 0);
    const totalSkipped = Object.values(selectedCard.skip_data || {}).reduce((sum, counts) => sum + counts.skipped, 0);
    const overallSkipRate = totalOffered > 0 ? (totalSkipped / totalOffered) : 0;

    return React.createElement(React.Fragment, null,
        // Summary stats grid
        React.createElement('div', { className: 'summary-stats' },
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' },
                    'Overall Skip Rate',
                    React.createElement(window.InfoIcon, { term: 'skip_rate' })
                ),
                React.createElement('div', { className: 'stat-value' },
                    `${(overallSkipRate * 100).toFixed(1)}%`
                )
            ),
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Total Offered'),
                React.createElement('div', { className: 'stat-value' }, totalOffered)
            ),
            React.createElement('div', { className: 'stat-card' },
                React.createElement('div', { className: 'stat-label' }, 'Total Skipped'),
                React.createElement('div', { className: 'stat-value' }, totalSkipped)
            )
        ),

        // Chart section
        React.createElement('div', { className: 'chart-section' },
            React.createElement('h3', { className: 'chart-title' }, 'Skip Rate by Floor (Kernel Smoothed)'),
            React.createElement('div', { className: 'chart-container' },
                skipRateData && skipRateData.length > 0
                    ? React.createElement(window.SkipRateChart, { skipRateData, baselineSkipData })
                    : React.createElement('p', null, 'No data available for this card')
            )
        ),

        // Data table
        React.createElement('div', { className: 'data-table' },
            React.createElement('h3', { className: 'chart-title' }, 'Detailed Floor Data'),
            skipRateData && skipRateData.length > 0
                ? React.createElement('div', { className: 'table-wrapper' },
                        React.createElement('table', null,
                            React.createElement('thead', null,
                                React.createElement('tr', null,
                                    React.createElement('th', null, 'Floor'),
                                    React.createElement('th', null, 'Offered'),
                                    React.createElement('th', null, 'Skipped'),
                                    React.createElement('th', null, 'Skip Rate (Raw)'),
                                    React.createElement('th', null, 'Skip Rate (Smoothed)'),
                                    React.createElement('th', null,
                                        'Baseline Skip Rate',
                                        React.createElement(window.InfoIcon, { term: 'baseline_skip_rate' })
                                    )
                                )
                            ),
                            React.createElement('tbody', null,
                                skipRateData.map(row =>
                                    React.createElement('tr', { key: row.floor },
                                        React.createElement('td', null, React.createElement('strong', null, row.floor)),
                                        React.createElement('td', null, row.offered),
                                        React.createElement('td', null, row.skipped),
                                        React.createElement('td', null, `${row.raw.toFixed(1)}%`),
                                        React.createElement('td', null, React.createElement('strong', null, `${row.smoothed.toFixed(1)}%`)),
                                        React.createElement('td', null,
                                            row.baseline !== undefined
                                                ? `${row.baseline.toFixed(1)}%`
                                                : 'N/A'
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
window.SkipRateTab = SkipRateTab;
