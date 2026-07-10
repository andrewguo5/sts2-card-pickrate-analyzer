// CardScatterPlot - Interactive 2D scatter plot for card visualization
const CardScatterPlot = ({ coordinateData, onCardClick, selectedCardId, searchTerm, showDeltas, baselineWinrate }) => {
    const { useState, useEffect, useRef } = React;
    const chartRef = useRef(null);
    const chartInstanceRef = useRef(null);
    const animationRef = useRef(null);

    useEffect(() => {
        if (!chartRef.current || !coordinateData || !coordinateData.coordinates) return;

        // Baseline positions (coords over all runs except the most recent N) let us
        // animate how recent play shifted each card. Absent for buckets with too
        // few runs; those cards simply hold their current position.
        const baselineCoordinates = coordinateData.baseline_coordinates || {};

        const ctx = chartRef.current.getContext('2d');

        // Destroy previous chart instance
        if (chartInstanceRef.current) {
            chartInstanceRef.current.destroy();
        }

        // Prepare data points
        const cards = Object.entries(coordinateData.coordinates).map(([cardId, data]) => {
            // Check if card matches search term
            const normalizedSearch = (searchTerm || '').toLowerCase().trim();
            const matchesSearch = !normalizedSearch ||
                data.name.toLowerCase().includes(normalizedSearch);

            // Current position (percentage). Baseline falls back to current when the
            // card has no baseline entry, so it stays put during the shift animation.
            const currentX = data.x * 100;
            const currentY = data.y * 100;
            const baseline = baselineCoordinates[cardId];
            const baselineX = baseline ? baseline.x * 100 : currentX;
            const baselineY = baseline ? baseline.y * 100 : currentY;

            return {
                x: currentX, // Convert to percentage for display
                y: currentY,
                currentX,
                currentY,
                baselineX,
                baselineY,
                cardId,
                name: data.name,
                type: data.type,
                rarity: data.rarity,
                cost: data.cost,
                total_offered: data.total_offered,
                total_picked: data.total_picked,
                pick_rate_estimate: data.pick_rate_estimate,
                skip_rate_estimate: data.skip_rate_estimate,
                win_rate_estimate: data.win_rate_estimate,
                matchesSearch
            };
        });

        // Group by card type for different colors and shapes
        const typeColors = {
            'Attack': 'rgba(220, 53, 69, 0.7)',      // Red
            'Skill': 'rgba(40, 167, 69, 0.7)',       // Green
            'Power': 'rgba(255, 193, 7, 0.7)',       // Yellow/Gold
            'Curse': 'rgba(108, 117, 125, 0.7)',     // Gray
            'Status': 'rgba(23, 162, 184, 0.7)'      // Cyan
        };

        const typeShapes = {
            'Attack': 'triangle',       // Triangle for Attack
            'Skill': 'rect',            // Square for Skill
            'Power': 'circle',          // Circle for Power
            'Curse': 'crossRot',        // X for Curse
            'Status': 'star'            // Star for Status
        };

        // Group cards by type, and further split by search match status
        const datasets = {};
        cards.forEach(card => {
            const type = card.type || 'Unknown';

            // Create separate datasets for matching and non-matching cards
            const matchKey = card.matchesSearch ? `${type}_match` : `${type}_nomatch`;

            if (!datasets[matchKey]) {
                const baseColor = typeColors[type] || 'rgba(150, 150, 150, 0.7)';
                // Reduce opacity for non-matching cards
                const opacity = card.matchesSearch ? 0.7 : 0.15;
                const color = baseColor.replace('0.7', opacity.toString());

                datasets[matchKey] = {
                    label: type,
                    data: [],
                    backgroundColor: color,
                    borderColor: baseColor.replace('0.7', card.matchesSearch ? '1' : '0.3'),
                    borderWidth: card.matchesSearch ? 2 : 1,
                    pointRadius: card.matchesSearch ? 6 : 4,
                    pointHoverRadius: 10,
                    pointStyle: typeShapes[type] || 'circle',
                    // Hide from legend if it's a non-matching dataset
                    hidden: false,
                    showInLegend: card.matchesSearch
                };
            }
            datasets[matchKey].data.push(card);
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

        // Plugin: draw a thin line from each card's baseline position to its current
        // position while the shift animation plays, so every card's full trajectory
        // is visible at once. Drawn beneath the points (beforeDatasetsDraw). Gated on
        // a mutable flag the animation effect toggles, so it costs nothing when idle.
        const shiftLinesPlugin = {
            id: 'shiftLines',
            beforeDatasetsDraw(chart) {
                if (!chart.$showShiftLines) return;

                const { ctx, scales: { x: xScale, y: yScale } } = chart;
                const hasSearch = !!(searchTerm && searchTerm.trim());

                ctx.save();
                chart.data.datasets.forEach(dataset => {
                    dataset.data.forEach(point => {
                        // Skip zero-length lines (cards with no baseline shift) and,
                        // during a search, cards that don't match (kept faint/quiet).
                        if (point.baselineX === point.currentX && point.baselineY === point.currentY) return;

                        const x1 = xScale.getPixelForValue(point.baselineX);
                        const y1 = yScale.getPixelForValue(point.baselineY);
                        const x2 = xScale.getPixelForValue(point.currentX);
                        const y2 = yScale.getPixelForValue(point.currentY);

                        ctx.beginPath();
                        ctx.moveTo(x1, y1);
                        ctx.lineTo(x2, y2);
                        ctx.lineWidth = 1;
                        ctx.strokeStyle = (hasSearch && !point.matchesSearch)
                            ? 'rgba(120, 120, 120, 0.10)'
                            : 'rgba(120, 120, 120, 0.45)';
                        ctx.stroke();
                    });
                });
                ctx.restore();
            }
        };

        const config = {
            type: 'scatter',
            data: chartData,
            plugins: [shiftLinesPlugin],
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                interaction: {
                    mode: 'nearest',
                    intersect: true,
                    axis: 'xy',
                    filter: (element) => {
                        // If there's a search term, only allow interaction with matching cards
                        if (searchTerm && searchTerm.trim()) {
                            const point = element.element.$context.raw;
                            return point.matchesSearch;
                        }
                        return true;
                    }
                },
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
                            padding: 15,
                            filter: (legendItem, chartData) => {
                                // Only show matching datasets in legend (avoid duplicates)
                                const dataset = chartData.datasets[legendItem.datasetIndex];
                                return dataset.showInLegend !== false;
                            }
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
                            },
                            // The Y-axis is win rate, so the bucket-wide baseline win
                            // rate lands as a horizontal benchmark: points above it
                            // beat the average run, points below trail it. Only drawn
                            // when a positive baseline is present.
                            ...(typeof baselineWinrate === 'number' && baselineWinrate > 0
                                ? {
                                    baselineWinrateLine: {
                                        type: 'line',
                                        yMin: baselineWinrate * 100,
                                        yMax: baselineWinrate * 100,
                                        borderColor: 'rgba(31, 41, 55, 0.55)',
                                        borderWidth: 2,
                                        borderDash: [6, 4],
                                        label: {
                                            display: true,
                                            content: `Avg. WR ${(baselineWinrate * 100).toFixed(1)}%`,
                                            position: 'end',
                                            backgroundColor: 'rgba(31, 41, 55, 0.75)',
                                            color: 'white',
                                            font: { size: 11, weight: 'bold' },
                                            padding: { x: 6, y: 3 }
                                        }
                                    }
                                }
                                : {})
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
    }, [coordinateData, onCardClick, selectedCardId, searchTerm, baselineWinrate]);

    // "Recent shift" animation: while the button is held, each point snaps to its
    // baseline position (all runs except the most recent N) and accelerates to its
    // current position, holds there briefly, then restarts — so the collective drift
    // of the last N runs reads at a glance. Releasing snaps every point back to its
    // current position. Runs on the already-built chart; mutates point coords.
    useEffect(() => {
        const chart = chartInstanceRef.current;
        if (!chart) return;

        // One cycle: accelerate from baseline to current, then rest on current.
        const TRAVEL_MS = 750;    // baseline -> current, ease-in (accelerating)
        const END_HOLD_MS = 400;  // rest on current before restarting
        const CYCLE_MS = TRAVEL_MS + END_HOLD_MS;

        const setPointsToCurrent = () => {
            // The chart may have been destroyed (e.g. a filter change rebuilt it)
            // before this runs; touching a destroyed instance throws.
            if (chartInstanceRef.current !== chart) return;
            chart.$showShiftLines = false;
            chart.data.datasets.forEach(dataset => {
                dataset.data.forEach(point => {
                    point.x = point.currentX;
                    point.y = point.currentY;
                });
            });
            chart.update('none');
        };

        if (!showDeltas) {
            // Not held: ensure everything sits at its true current position.
            setPointsToCurrent();
            return;
        }

        // Trajectory lines are only drawn while the animation plays.
        chart.$showShiftLines = true;

        // Anchor the loop's phase to elapsed time so it stays smooth across frames.
        let startTime = null;

        const frame = (now) => {
            if (startTime === null) startTime = now;
            const elapsed = (now - startTime) % CYCLE_MS;

            // Travel phase blends a linear term (nonzero initial velocity, so points
            // leave the baseline already moving and the traversal feels quicker) with
            // a quartic ease-in (a snappy accelerating launch). Hold phase pins t at 1
            // so points rest on their current position before restarting.
            const INITIAL_VELOCITY = 0.4; // linear share; 0 = pure quartic (crawls out)
            let t;
            if (elapsed < TRAVEL_MS) {
                const progress = elapsed / TRAVEL_MS;
                const quartic = progress * progress * progress * progress;
                t = INITIAL_VELOCITY * progress + (1 - INITIAL_VELOCITY) * quartic;
            } else {
                t = 1;
            }

            chart.data.datasets.forEach(dataset => {
                dataset.data.forEach(point => {
                    point.x = point.baselineX + (point.currentX - point.baselineX) * t;
                    point.y = point.baselineY + (point.currentY - point.baselineY) * t;
                });
            });
            chart.update('none');

            animationRef.current = requestAnimationFrame(frame);
        };

        animationRef.current = requestAnimationFrame(frame);

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
                animationRef.current = null;
            }
            // Snap back to current so a release (or rebuild) never leaves points
            // frozen mid-tween.
            if (chartInstanceRef.current) {
                setPointsToCurrent();
            }
        };
    }, [showDeltas, coordinateData, searchTerm, selectedCardId]);

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
