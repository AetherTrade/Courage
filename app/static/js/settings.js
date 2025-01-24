// Admin settings page functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all forms
    const forms = {
        apiSettings: document.getElementById('apiSettingsForm'),
        botSettings: document.getElementById('botSettingsForm'),
        emailSettings: document.getElementById('emailSettingsForm')
    };

    // Add submit handlers
    Object.entries(forms).forEach(([key, form]) => {
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                saveSettings(key, form);
            });
        }
    });

    // Initialize range input display
    const riskLevel = document.querySelector('input[name="risk_level"]');
    if (riskLevel) {
        updateRiskDisplay(riskLevel.value);
        riskLevel.addEventListener('input', (e) => updateRiskDisplay(e.target.value));
    }
});

// Save settings to server
function saveSettings(settingType, form) {
    if (!validateForm(`#${form.id}`)) return;

    const formData = new FormData(form);
    const endpoint = `/api/admin/settings/${settingType}`;
    
    toggleLoading(true);

    fetch(endpoint, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            showAlert('Settings updated successfully!', 'success');
            updateSettingsDisplay(settingType, data);
        })
        .catch(error => handleApiError(error))
        .finally(() => toggleLoading(false));
}

// Test email configuration
function testEmailConfig() {
    toggleLoading(true);

    fetch('/api/admin/settings/test-email', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            showAlert('Test email sent successfully!', 'success');
        })
        .catch(error => handleApiError(error))
        .finally(() => toggleLoading(false));
}

// Update risk level display
function updateRiskDisplay(value) {
    const display = document.getElementById('riskLevelDisplay');
    if (display) {
        display.textContent = value;
        
        // Update color based on risk level
        const colors = {
            low: 'success',
            medium: 'warning',
            high: 'danger'
        };
        
        const riskCategory = value <= 3 ? 'low' : value <= 7 ? 'medium' : 'high';
        display.className = `badge bg-${colors[riskCategory]}`;
    }
}

// Update settings display after save
function updateSettingsDisplay(settingType, data) {
    switch (settingType) {
        case 'apiSettings':
            updateApiSettingsDisplay(data);
            break;
        case 'botSettings':
            updateBotSettingsDisplay(data);
            break;
        case 'emailSettings':
            updateEmailSettingsDisplay(data);
            break;
    }
}

// Helper functions for updating displays
function updateApiSettingsDisplay(data) {
    document.querySelector('input[name="api_endpoint"]').value = data.endpoint;
    document.querySelector('input[name="api_timeout"]').value = data.timeout;
}

function updateBotSettingsDisplay(data) {
    document.querySelector('input[name="max_bots"]').value = data.max_bots;
    document.querySelector('input[name="investment_limit"]').value = data.investment_limit;
    document.querySelector('input[name="risk_level"]').value = data.risk_level;
    updateRiskDisplay(data.risk_level);
}

function updateEmailSettingsDisplay(data) {
    document.querySelector('input[name="smtp_server"]').value = data.smtp_server;
    document.querySelector('input[name="smtp_port"]').value = data.smtp_port;
    document.querySelector('input[name="smtp_username"]').value = data.smtp_username;
}

// Backup system settings
function backupSettings() {
    fetch('/api/admin/settings/backup', {
        method: 'GET'
    })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `settings_backup_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        })
        .catch(error => handleApiError(error));
}

// Restore system settings
function restoreSettings(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const settings = JSON.parse(e.target.result);
            
            fetch('/api/admin/settings/restore', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            })
                .then(response => response.json())
                .then(data => {
                    showAlert('Settings restored successfully!', 'success');
                    location.reload();
                })
                .catch(error => handleApiError(error));
        } catch (error) {
            showAlert('Invalid backup file', 'danger');
        }
    };
    reader.readAsText(file);
} 