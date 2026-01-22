/**
 * Pricing Analysis - Price History Chart
 * Initializes Chart.js line chart for Keepa price history data
 */

function initPriceChart(canvasId, chartData) {
    /**
     * Initialize price history chart with Chart.js
     *
     * @param {string} canvasId - ID of the canvas element
     * @param {Object} chartData - Data object containing labels, prices, and currency
     */

    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error('Canvas element not found:', canvasId);
        return;
    }

    if (!chartData || !chartData.labels || chartData.labels.length === 0) {
        console.warn('No chart data available');
        return;
    }

    // Create the chart
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: `Precio (${chartData.currency})`,
                data: chartData.prices,
                borderColor: '#0d6efd',  // Bootstrap primary blue
                backgroundColor: 'rgba(13, 110, 253, 0.1)',  // 10% opacity
                borderWidth: 2,
                fill: true,
                tension: 0.4,  // Curve smoothness
                pointRadius: 3,
                pointHoverRadius: 6,
                pointBackgroundColor: '#0d6efd',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            const price = context.parsed.y;
                            return `Precio: $${price.toFixed(2)} ${chartData.currency}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        maxTicksLimit: 15  // Limit to 15 labels max
                    },
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });

    console.log('Price chart initialized successfully');
}
