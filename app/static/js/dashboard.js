// Dashboard specific JavaScript

// Initialize trading chart
function initTradingChart() {
    const ctx = document.getElementById('tradingChart').getContext('2d');
    const tradingChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Will be populated with dates
            datasets: [{
                label: 'Profit/Loss',
                data: [], // Will be populated with P/L values
                borderColor: '#1a237e',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    return tradingChart;
}

// Fetch and update trading data
function updateTradingData() {
    fetch('/api/trading/history')
        .then(response => response.json())
        .then(data => {
            const chart = Chart.getChart('tradingChart');
            chart.data.labels = data.dates;
            chart.data.datasets[0].data = data.values;
            chart.update();
            updateStatistics(data.statistics);
        })
        .catch(error => handleApiError(error));
}

// Update dashboard statistics
function updateStatistics(stats) {
    document.getElementById('activeBots').textContent = stats.activeBots;
    document.getElementById('totalProfit').textContent = `$${stats.totalProfit}`;
    document.getElementById('winRate').textContent = `${stats.winRate}%`;
    document.getElementById('totalTrades').textContent = stats.totalTrades;
}

// Bot management functions
function createBot() {
    if (!validateForm('#newBotForm')) return;

    const formData = new FormData(document.getElementById('newBotForm'));
    toggleLoading(true);

    fetch('/api/bots/create', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            showAlert('Bot created successfully!', 'success');
            $('#newBotModal').modal('hide');
            refreshBotsList();
        })
        .catch(error => handleApiError(error))
        .finally(() => toggleLoading(false));
}

function stopBot(botId) {
    if (!confirm('Are you sure you want to stop this bot?')) return;

    toggleLoading(true);
    fetch(`/api/bots/${botId}/stop`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showAlert('Bot stopped successfully!', 'success');
            refreshBotsList();
        })
        .catch(error => handleApiError(error))
        .finally(() => toggleLoading(false));
}

function refreshBotsList() {
    fetch('/api/bots/list')
        .then(response => response.json())
        .then(data => {
            const botsTableBody = document.querySelector('#botsTable tbody');
            botsTableBody.innerHTML = data.bots.map(bot => `
                <tr>
                    <td>${bot.name}</td>
                    <td>${bot.strategy}</td>
                    <td class="${bot.profit >= 0 ? 'text-success' : 'text-danger'}">
                        $${bot.profit}
                    </td>
                    <td>${bot.win_rate}%</td>
                    <td>
                        <span class="badge bg-${bot.status === 'active' ? 'success' : 'danger'}">
                            ${bot.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="viewBot(${bot.id})">
                            <i class='bx bx-show'></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="stopBot(${bot.id})">
                            <i class='bx bx-stop-circle'></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => handleApiError(error));
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initTradingChart();
    updateTradingData();
    refreshBotsList();

    // Set up auto-refresh
    setInterval(updateTradingData, 60000); // Update every minute
    setInterval(refreshBotsList, 30000);  // Update every 30 seconds
});
