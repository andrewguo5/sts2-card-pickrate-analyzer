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

        chartInstanceRef.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.map(d => d.floor),
                datasets: [
                    {
                        label: 'Smoothed Pick Rate',
                        data: chartData.map(d => d.smoothed),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Raw Pick Rate',
                        data: chartData.map(d => d.raw),
                        borderColor: '#8b5cf6',
                        backgroundColor: 'transparent',
                        fill: false,
                        borderDash: [5, 5],
                        borderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: '#8b5cf6'
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
