// ChartComponent - Displays pick rate chart using Chart.js
const ChartComponent = ({ chartData }) => {
    const { useRef, useEffect } = React;
    const chartRef = useRef(null);
    const chartInstanceRef = useRef(null);

    useEffect(() => {
        if (!chartRef.current || !chartData || chartData.length === 0) return;

        // Destroy previous chart instance
        if (chartInstanceRef.current) {
            chartInstanceRef.current.destroy();
        }

        const ctx = chartRef.current.getContext('2d');

        // Get character colors from CSS custom properties
        const root = document.documentElement;
        const primaryColor = getComputedStyle(root).getPropertyValue('--char-primary').trim();
        const secondaryColor = getComputedStyle(root).getPropertyValue('--char-secondary').trim();
        const accentColor = getComputedStyle(root).getPropertyValue('--char-accent').trim();

        // Convert hex to rgba for transparency
        const hexToRgba = (hex, alpha) => {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        };

        // Boss floors and act boundaries
        const BOSS_FLOORS = [17, 34, 51];
        const ACT_BOUNDARIES = [
            { start: 2, end: 17, label: 'Act 1', color: 'rgba(0, 0, 0, 0.02)' },
            { start: 17, end: 34, label: 'Act 2', color: 'rgba(0, 0, 0, 0.04)' },
            { start: 34, end: 51, label: 'Act 3', color: 'rgba(0, 0, 0, 0.06)' }
        ];

        chartInstanceRef.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.map(d => d.floor),
                datasets: [
                    {
                        label: 'Smoothed Pick Rate',
                        data: chartData.map(d => d.smoothed),
                        borderColor: primaryColor,
                        backgroundColor: hexToRgba(primaryColor, 0.1),
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Raw Pick Rate',
                        data: chartData.map(d => d.raw),
                        borderColor: secondaryColor,
                        backgroundColor: 'transparent',
                        fill: false,
                        borderDash: [5, 5],
                        borderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: secondaryColor
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const dataPoint = chartData[context.dataIndex];
                                return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}% (${dataPoint.picked}/${dataPoint.offered})`;
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
                                    borderWidth: 0,
                                    label: {
                                        display: true,
                                        content: act.label,
                                        position: 'start',
                                        color: '#6b7280',
                                        font: {
                                            size: 11,
                                            weight: 'bold'
                                        },
                                        yAdjust: -10
                                    }
                                };
                                return acc;
                            }, {}),
                            // Boss floor markers
                            ...BOSS_FLOORS.reduce((acc, floor, index) => {
                                acc[`boss${index}`] = {
                                    type: 'line',
                                    xMin: floor,
                                    xMax: floor,
                                    borderColor: hexToRgba(secondaryColor, 0.5),
                                    borderWidth: 2,
                                    borderDash: [8, 4],
                                    label: {
                                        display: true,
                                        content: `Act ${index + 1} Boss`,
                                        position: 'start',
                                        backgroundColor: hexToRgba(secondaryColor, 0.9),
                                        color: 'white',
                                        font: {
                                            size: 10,
                                            weight: 'bold'
                                        },
                                        yAdjust: 10
                                    }
                                };
                                return acc;
                            }, {})
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Floor'
                        },
                        type: 'linear',
                        min: 2,
                        max: 46
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Pick Rate (%)'
                        },
                        min: 0,
                        max: 100
                    }
                }
            }
        });

        return () => {
            if (chartInstanceRef.current) {
                chartInstanceRef.current.destroy();
            }
        };
    }, [chartData]);

    return React.createElement('canvas', {
        ref: chartRef,
        style: { maxHeight: '400px' }
    });
};

// Export component
window.ChartComponent = ChartComponent;
