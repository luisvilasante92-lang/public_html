/**
 * LVR Music Publishing - Личный кабинет
 * JavaScript приложения
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация
    // Тема задаётся в base.html (data-theme, data-accent) — чёрно-оранжевый кабинет
    initSidebar();
    initFlashMessages();
    initModals();
    initForms();
});

/**
 * Мобильное меню
 */
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mobileToggle = document.getElementById('mobileMenuToggle');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const overlay = document.getElementById('sidebarOverlay');
    
    function setDrawerOpen(open) {
        document.body.classList.toggle('nav-drawer-open', open);
        if (mobileToggle) mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (overlay) overlay.setAttribute('aria-hidden', open ? 'false' : 'true');
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        setDrawerOpen(false);
    }
    
    function openSidebar() {
        if (sidebar) sidebar.classList.add('open');
        setDrawerOpen(true);
    }
    
    function toggleSidebar() {
        if (!sidebar) return;
        var willOpen = !sidebar.classList.contains('open');
        sidebar.classList.toggle('open');
        setDrawerOpen(sidebar.classList.contains('open'));
    }
    
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleSidebar();
        });
    }
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            closeSidebar();
        });
    }
    
    if (overlay && sidebar) {
        overlay.addEventListener('click', closeSidebar);
    }
    
    // Закрытие при клике вне меню (десктоп, если меню открыто)
    document.addEventListener('click', function(e) {
        if (sidebar && sidebar.classList.contains('open')) {
            if (!sidebar.contains(e.target) && mobileToggle && !mobileToggle.contains(e.target)) {
                closeSidebar();
            }
        }
    });
    
    // Закрытие при переходе на широкий экран
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) closeSidebar();
    });
}

/**
 * Автоскрытие flash-сообщений
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(function(message) {
        // Автоскрытие через 5 секунд
        setTimeout(function() {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * Модальные окна
 */
function initModals() {
    // Закрытие по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                activeModal.classList.remove('active');
            }
        }
    });
}

/**
 * Открытие модального окна
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

/**
 * Закрытие модального окна
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Инициализация форм
 */
function initForms() {
    // Превью изображений
    const fileInputs = document.querySelectorAll('input[type="file"][data-preview]');
    
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const previewId = this.getAttribute('data-preview');
            const preview = document.getElementById(previewId);
            const file = e.target.files[0];
            
            if (file && preview) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                };
                reader.readAsDataURL(file);
            }
        });
    });
    
    // Подтверждение опасных действий
    const dangerForms = document.querySelectorAll('form[data-confirm]');
    
    dangerForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const message = this.getAttribute('data-confirm') || 'Вы уверены?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * AJAX запрос
 */
function ajax(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const config = { ...defaults, ...options };
    
    // Добавление CSRF токена
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
    }
    
    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

/**
 * Показать уведомление
 */
function showNotification(message, type = 'info') {
    const container = document.querySelector('.flash-messages') || createFlashContainer();
    
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type}`;
    notification.innerHTML = `
        <span class="material-icons">
            ${type === 'success' ? 'check_circle' : 
              type === 'error' ? 'error' : 
              type === 'warning' ? 'warning' : 'info'}
        </span>
        <span>${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()">
            <span class="material-icons">close</span>
        </button>
    `;
    
    container.appendChild(notification);
    
    // Автоскрытие
    setTimeout(function() {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    const content = document.querySelector('.content');
    if (content) {
        content.parentNode.insertBefore(container, content);
    }
    return container;
}

/**
 * Форматирование чисел
 */
function formatNumber(num) {
    return new Intl.NumberFormat('ru-RU').format(num);
}

/**
 * Форматирование валюты
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 2
    }).format(amount);
}

/**
 * Форматирование даты
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    }).format(date);
}

/**
 * Debounce функция
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Копирование в буфер обмена
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Скопировано в буфер обмена', 'success');
    }).catch(function() {
        showNotification('Не удалось скопировать', 'error');
    });
}
