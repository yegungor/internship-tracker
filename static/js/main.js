// Main JavaScript for Internship Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Load saved theme on page load
    loadTheme();
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
    
    // Search form - submit on enter
    const searchBox = document.querySelector('.search-box input');
    if (searchBox) {
        searchBox.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.form.submit();
            }
        });
    }
    
    // Confirm before delete
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this?')) {
                e.preventDefault();
            }
        });
    });
    
    // Theme switcher buttons
    const themeButtons = document.querySelectorAll('.theme-btn');
    themeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const theme = this.dataset.theme;
            setTheme(theme);
        });
    });
});

// ============ THEME FUNCTIONS ============

function setTheme(themeName) {
    // Update the CSS file
    const themeLink = document.getElementById('theme-css');
    themeLink.href = `/static/css/${themeName}.css`;
    
    // Save to localStorage
    localStorage.setItem('theme', themeName);
    
    // Update active button
    updateActiveThemeButton(themeName);
}

function loadTheme() {
    // Get saved theme or use default
    const savedTheme = localStorage.getItem('theme') || 'style-default';
    
    // Apply the theme
    const themeLink = document.getElementById('theme-css');
    if (themeLink) {
        themeLink.href = `/static/css/${savedTheme}.css`;
    }
    
    // Update active button
    updateActiveThemeButton(savedTheme);
}

function updateActiveThemeButton(themeName) {
    // Remove active class from all buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to current theme button
    const activeBtn = document.querySelector(`.theme-btn[data-theme="${themeName}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
}

// ============ STATUS FUNCTIONS ============

// Global function to toggle status menus
function toggleStatusMenu(button) {
    const menu = button.nextElementSibling;
    const allMenus = document.querySelectorAll('.status-menu');
    
    // Close all other menus
    allMenus.forEach(m => {
        if (m !== menu) m.classList.remove('show');
    });
    
    menu.classList.toggle('show');
}

// Global function to update application status
function updateStatus(appId, status) {
    fetch(`/application/${appId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Failed to update status');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update status');
    });
}

// Global function to toggle contact status
function toggleContact(contactId) {
    fetch(`/contact/${contactId}/toggle`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.closest('.status-dropdown')) {
        document.querySelectorAll('.status-menu').forEach(m => {
            m.classList.remove('show');
        });
    }
});
