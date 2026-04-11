// WinRateChart - Bar chart visualization for win rates by act
const WinRateChart = ({ winRateData }) => {
    const canvasRef = React.useRef(null);
    const chartRef = React.useRef(null);

    React.useEffect(() => {
        if (!canvasRef.current || !winRateData || winRateData.length === 0) return;

        // Destroy existing chart if it exists
        if (chartRef.current) {
            chartRef.current.destroy();
        }

        const ctx = canvasRef.current.getContext('2d');

        // Get character colors from CSS custom properties
        const root = document.documentElement;
        const primaryColor = getComputedStyle(root).getPropertyValue('--char-primary').trim();
        const accentColor = getComputedStyle(root).getPropertyValue('--char-accent').trim();

        // Helper function to convert hex to rgba
        const hexToRgba = (hex, alpha) => {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        };

        const acts = winRateData.map(d => `Act ${d.act}`);
        const winRates = winRateData.map(d => d.winrate);

        chartRef.current = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: acts,
                datasets: [{
                    label: 'Win Rate (%)',
                    data: winRates,
                    backgroundColor: hexToRgba(primaryColor, 0.7),
                    borderColor: primaryColor,
                    borderWidth: 2,
                    hoverBackgroundColor: hexToRgba(accentColor, 0.8),
                    hoverBorderColor: primaryColor
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Act Card Was Picked',
                            font: { size: 14, weight: 'bold' }
                        },
                        grid: { display: false }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Win Rate (%)',
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
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: context => {
                                const value = context.parsed.y.toFixed(1);
                                const dataIndex = context.dataIndex;
                                const picked = winRateData[dataIndex].picked;
                                const won = winRateData[dataIndex].won;
                                return [
                                    `Win Rate: ${value}%`,
                                    `Picked: ${picked} times`,
                                    `Won: ${won} times`
                                ];
                            }
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
    }, [winRateData]);

    return React.createElement('canvas', { ref: canvasRef });
};

// Export component
window.WinRateChart = WinRateChart;
