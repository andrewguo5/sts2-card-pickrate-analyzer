// CardScatterPlot - Interactive 2D scatter plot for card visualization
const CardScatterPlot = ({ coordinateData, onCardClick, selectedCardId }) => {
    const { useState, useEffect, useRef } = React;
    const chartRef = useRef(null);
    const chartInstanceRef = useRef(null);

    useEffect(() => {
        if (!chartRef.current || !coordinateData || !coordinateData.coordinates) return;

        const ctx = chartRef.current.getContext('2d');

        // Destroy previous chart instance
        if (chartInstanceRef.current) {
            chartInstanceRef.current.destroy();
        }

        // Prepare data points
        const cards = Object.entries(coordinateData.coordinates).map(([cardId, data]) => ({
            x: data.x * 100, // Convert to percentage for display
            y: data.y * 100,
            cardId,
            name: data.name,
            type: data.type,
            rarity: data.rarity,
            cost: data.cost,
            total_offered: data.total_offered,
            total_picked: data.total_picked,
            pick_rate_estimate: data.pick_rate_estimate,
            skip_rate_estimate: data.skip_rate_estimate,
            win_rate_estimate: data.win_rate_estimate
        }));

        // Group by card type for different colors
        const typeColors = {
            'attack': 'rgba(220, 53, 69, 0.7)',
            'skill': 'rgba(40, 167, 69, 0.7)',
            'power': 'rgba(255, 193, 7, 0.7)',
            'curse': 'rgba(108, 117, 125, 0.7)',
            'status': 'rgba(23, 162, 184, 0.7)'
        };

        // Group cards by type
        const datasets = {};
        cards.forEach(card => {
            const type = card.type || 'unknown';
            if (!datasets[type]) {
                datasets[type] = {
                    label: type.charAt(0).toUpperCase() + type.slice(1),
                    data: [],
                    backgroundColor: typeColors[type] || 'rgba(150, 150, 150, 0.7)',
                    borderColor: typeColors[type]?.replace('0.7', '1') || 'rgba(150, 150, 150, 1)',
                    borderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 10
                };
            }
            datasets[type].data.push(card);
        });

        // Highlight selected card
        if (selectedCardId) {
            Object.values(datasets).forEach(dataset => {
                dataset.data = dataset.data.map(point => ({
                    ...point,
                    pointRadius: point.cardId === selectedCardId ? 12 : 6,
                    pointBorderWidth: point.cardId === selectedCardId ? 3 : 2,
                    pointBackgroundColor: point.cardId === selectedCardId ?
                        'rgba(255, 215, 0, 0.9)' : dataset.backgroundColor
                }));
            });
        }

        const chartData = {
            datasets: Object.values(datasets)
        };

        const config = {
            type: 'scatter',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Pickability (Pick Rate - Skip Rate)',
                            font: { size: 14, weight: 'bold' }
                        },
                        min: 0,
                        max: 100,
                        grid: {
                            color: 'rgba(200, 200, 200, 0.2)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Conditional Power (Win Rate)',
                            font: { size: 14, weight: 'bold' }
                        },
                        min: 0,
                        max: 100,
                        grid: {
                            color: 'rgba(200, 200, 200, 0.2)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: (context) => {
                                const point = context[0].raw;
                                return point.name;
                            },
                            label: (context) => {
                                const point = context.raw;
                                return [
                                    `Type: ${point.type || 'Unknown'}`,
                                    `Rarity: ${point.rarity || 'Unknown'}`,
                                    `Cost: ${point.cost !== undefined ? point.cost : 'N/A'}`,
                                    ``,
                                    `Pickability: ${point.x.toFixed(1)}%`,
                                    `  Pick Rate Est: ${(point.pick_rate_estimate * 100).toFixed(1)}%`,
                                    `  Skip Rate Est: ${(point.skip_rate_estimate * 100).toFixed(1)}%`,
                                    ``,
                                    `Conditional Power: ${point.y.toFixed(1)}%`,
                                    `  Win Rate Est: ${(point.win_rate_estimate * 100).toFixed(1)}%`,
                                    ``,
                                    `Offered: ${point.total_offered} times`,
                                    `Picked: ${point.total_picked} times`
                                ];
                            }
                        },
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 12 },
                        padding: 12,
                        displayColors: false
                    },
                    annotation: {
                        annotations: {
                            line1: {
                                type: 'line',
                                xMin: 50,
                                xMax: 50,
                                borderColor: 'rgba(100, 100, 100, 0.3)',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {
                                    display: false
                                }
                            },
                            line2: {
                                type: 'line',
                                yMin: 50,
                                yMax: 50,
                                borderColor: 'rgba(100, 100, 100, 0.3)',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {
                                    display: false
                                }
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const element = elements[0];
                        const datasetIndex = element.datasetIndex;
                        const index = element.index;
                        const point = chartData.datasets[datasetIndex].data[index];
                        if (onCardClick) {
                            onCardClick(point.cardId);
                        }
                    }
                }
            }
        };

        chartInstanceRef.current = new Chart(ctx, config);

        return () => {
            if (chartInstanceRef.current) {
                chartInstanceRef.current.destroy();
            }
        };
    }, [coordinateData, onCardClick, selectedCardId]);

    if (!coordinateData || !coordinateData.coordinates) {
        return React.createElement('div', { className: 'loading', style: { padding: '40px', textAlign: 'center' } },
            'No coordinate data available'
        );
    }

    return React.createElement('div', { className: 'scatter-plot-container' },
        React.createElement('canvas', { ref: chartRef })
    );
};

// Export component
window.CardScatterPlot = CardScatterPlot;
