// Profile page functionality

document.addEventListener('DOMContentLoaded', function() {
    // Handle profile image upload
    const avatarInput = document.getElementById('avatarInput');
    if (avatarInput) {
        avatarInput.addEventListener('change', uploadAvatar);
    }

    // Initialize forms
    const profileForm = document.getElementById('profileForm');
    const securityForm = document.getElementById('securityForm');

    if (profileForm) {
        profileForm.addEventListener('submit', updateProfile);
    }

    if (securityForm) {
        securityForm.addEventListener('submit', updatePassword);
    }
});

// Avatar upload handling
function uploadAvatar(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
        showAlert('Please select an image file', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('avatar', file);
    toggleLoading(true);

    fetch('/api/profile/avatar', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            document.querySelector('.rounded-circle').src = data.avatar_url;
            showAlert('Profile picture updated successfully!', 'success');
        })
        .catch(error => handleApiError(error))
        .finally(() => toggleLoading(false));
}

// Update profile information
function updateProfile(event) {
    event.preventDefault();

    if (!validateForm('#profileForm')) return;

    const formData = new FormData(event.target);
    toggleLoading(true);

    fetch('/api/profile/update', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            showAlert('Profile updated successfully!', 'success');
            updateProfileDisplay(data);
        })
        .catch(error => handleApiError(error))
        .finally(() => toggleLoading(false));
}

// Update password
function updatePassword(event) {
    event.preventDefault();

    if (!validateForm('#securityForm')) return;

    const formData = new FormData(event.target);
    
    // Validate password match
    if (formData.get('new_password') !== formData.get('confirm_password')) {
        showAlert('New passwords do not match', 'danger');
        return;
    }

    toggleLoading(true);

    fetch('/api/profile/password', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            showAlert('Password updated successfully!', 'success');
            event.target.reset();
        })
        .catch(error => handleApiError(error))
        .finally(() => toggleLoading(false));
}

// Update profile display
function updateProfileDisplay(userData) {
    const nameDisplay = document.querySelector('h4');
    if (nameDisplay) {
        nameDisplay.textContent = `${userData.first_name} ${userData.last_name}`;
    }
}

// API key management
function generateApiKey() {
    if (!confirm('Are you sure you want to generate a new API key? This will invalidate your current key.')) {
        return;
    }

    toggleLoading(true);

    fetch('/api/profile/generate-key', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('apiKey').value = data.api_key;
            showAlert('New API key generated successfully!', 'success');
        })
        .catch(error => handleApiError(error))
        .finally(() => toggleLoading(false));
}

// Two-factor authentication
function setupTwoFactor() {
    toggleLoading(true);

    fetch('/api/profile/2fa/setup', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            // Show QR code modal
            const modal = new bootstrap.Modal(document.getElementById('twoFactorModal'));
            document.getElementById('qrCode').src = data.qr_code;
            document.getElementById('backupCodes').textContent = data.backup_codes.join('\n');
            modal.show();
        })
        .catch(error => handleApiError(error))
        .finally(() => toggleLoading(false));
} 