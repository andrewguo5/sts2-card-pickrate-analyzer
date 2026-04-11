// SkipRateChart - Chart.js visualization for skip rates with baseline comparison
const SkipRateChart = ({ skipRateData, baselineSkipData }) => {
    const canvasRef = React.useRef(null);
    const chartRef = React.useRef(null);

    React.useEffect(() => {
        if (!canvasRef.current || !skipRateData || skipRateData.length === 0) return;

        // Destroy existing chart if it exists
        if (chartRef.current) {
            chartRef.current.destroy();
        }

        const ctx = canvasRef.current.getContext('2d');

        // Get character colors from CSS custom properties
        const root = document.documentElement;
        const primaryColor = getComputedStyle(root).getPropertyValue('--char-primary').trim();
        const secondaryColor = getComputedStyle(root).getPropertyValue('--char-secondary').trim();

        // Helper function to convert hex to rgba
        const hexToRgba = (hex, alpha) => {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        };

        // Boss floors and act boundaries
        const BOSS_FLOORS = [17, 34, 51];
        const ACT_BOUNDARIES = [
            { start: 2, end: 17, label: 'Act 1', color: 'rgba(0, 0, 0, 0.03)' },
            { start: 17, end: 34, label: 'Act 2', color: 'rgba(0, 0, 0, 0.06)' },
            { start: 34, end: 51, label: 'Act 3', color: 'rgba(0, 0, 0, 0.09)' }
        ];

        const floors = skipRateData.map(d => d.floor);
        const cardSkipRates = skipRateData.map(d => d.smoothed);
        const baselineSkipRates = skipRateData.map(d => d.baseline || 0);

        chartRef.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: floors,
                datasets: [
                    {
                        label: 'Card Skip Rate',
                        data: cardSkipRates,
                        borderColor: primaryColor,
                        backgroundColor: hexToRgba(primaryColor, 0.1),
                        borderWidth: 3,
                        pointRadius: 3,
                        pointHoverRadius: 5,
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: 'Baseline Skip Rate',
                        data: baselineSkipRates,
                        borderColor: hexToRgba(secondaryColor, 0.5),
                        backgroundColor: hexToRgba(secondaryColor, 0.05),
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 2,
                        pointHoverRadius: 4,
                        fill: false,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Floor',
                            font: { size: 14, weight: 'bold' }
                        },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Skip Rate (%)',
                            font: { size: 14, weight: 'bold' }
                        },
                        min: 0,
                        max: 100,
                        ticks: {
                            callback: value => `${value}%`
                        },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: context => {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y.toFixed(1);
                                return `${label}: ${value}%`;
                            }
                        }
                    },
                    annotation: {
                        annotations: {
                            // Act background shading
                            ...ACT_BOUNDARIES.reduce((acc, act, index) => {
                                acc[`act${index + 1}Box`] = {
                                    type: 'box',
                                    xMin: act.start,
                                    xMax: act.end,
                                    backgroundColor: act.color,
                                    borderWidth: 0
                                };
                                return acc;
                            }, {}),
                            // Boss floor markers
                            ...BOSS_FLOORS.reduce((acc, floor, index) => {
                                acc[`boss${index}`] = {
                                    type: 'line',
                                    xMin: floor,
                                    xMax: floor,
                                    borderColor: hexToRgba(secondaryColor, 0.4),
                                    borderWidth: 2,
                                    borderDash: [8, 4]
                                };
                                return acc;
                            }, {})
                        }
                    }
                }
            }
        });

        return () => {
            if (chartRef.current) {
                chartRef.current.destroy();
            }
        };
    }, [skipRateData, baselineSkipData]);

    return React.createElement('canvas', { ref: canvasRef });
};

// Export component
window.SkipRateChart = SkipRateChart;
