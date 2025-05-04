// scripts.js - Main application JavaScript

// Initialize CSRF token for AJAX requests
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

// Service Control Functions
function controlService(action) {
    showLoader();
    fetch(`/service/control/${action}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(handleResponse)
    .catch(handleError);
}

// Real-time Status Updates
function updateServiceStatus() {
    fetch('/service/status')
        .then(response => response.json())
        .then(data => {
            updateStatusIndicator(data);
            updateControlButtons(data);
        })
        .catch(handleError);
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    return Array.from(inputs).every(input => {
        if (!input.value.trim()) {
            showMessage(`Please fill in the ${input.name} field`, 'warning');
            input.focus();
            return false;
        }
        return true;
    });
}

// Generic Helpers
function showMessage(message, type = 'info') {
    const messageBar = document.querySelector('.message-bar');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    messageBar.prepend(alert);
}

function showLoader() {
    const loader = document.createElement('div');
    loader.className = 'loader-overlay';
    loader.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoader() {
    const loader = document.querySelector('.loader-overlay');
    if (loader) loader.remove();
}

function handleResponse(response) {
    hideLoader();
    if (response.ok) {
        showMessage('Operation completed successfully', 'success');
        setTimeout(() => location.reload(), 1500);
    } else {
        throw new Error('Server response not OK');
    }
}

function handleError(error) {
    hideLoader();
    console.error('Error:', error);
    showMessage('Operation failed. Please try again.', 'danger');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Service Control Buttons
    document.querySelectorAll('[data-service-action]').forEach(button => {
        button.addEventListener('click', (e) => {
            const action = e.target.dataset.serviceAction;
            if (['stop', 'restart'].includes(action)) {
                showConfirmationModal(action);
            } else {
                controlService(action);
            }
        });
    });

    // Auto-refresh status every 10 seconds
    setInterval(updateServiceStatus, 10000);

    // Form Validation
    document.querySelectorAll('form.needs-validation').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form.id)) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Confirmation Modal Handler
function showConfirmationModal(action) {
    const modal = new bootstrap.Modal('#confirmationModal');
    const modalMessage = document.getElementById('modalMessage');
    const confirmBtn = document.getElementById('confirmActionButton');
    
    modalMessage.textContent = `Are you sure you want to ${action} the service?`;
    
    confirmBtn.onclick = () => {
        modal.hide();
        controlService(action);
    };
    
    modal.show();
}

// Status Indicator Update
function updateStatusIndicator(status) {
    const indicator = document.getElementById('statusIndicator');
    if (indicator) {
        indicator.className = `badge bg-${status.active ? 'success' : 'danger'}`;
        indicator.textContent = status.active ? 'RUNNING' : 'STOPPED';
    }
}

function updateControlButtons(status) {
    const startBtn = document.getElementById('startButton');
    const stopBtn = document.getElementById('stopButton');
    const restartBtn = document.getElementById('restartButton');
    
    if (startBtn) startBtn.disabled = status.active;
    if (stopBtn) stopBtn.disabled = !status.active;
    if (restartBtn) restartBtn.disabled = !status.active;
}