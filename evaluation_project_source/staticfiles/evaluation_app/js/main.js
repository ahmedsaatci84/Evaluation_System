// ================================
// Digital Watch and Sidebar Controls
// ================================

document.addEventListener('DOMContentLoaded', function() {
    initializeDigitalWatch();
    initializeSidebarToggle();
    initializeNavLinks();
    initializeLanguageSwitcher();
    initializeThemeToggle();
    initializeWeatherWidget();
});

// ================================
// Language Switcher Functionality
// ================================

function initializeLanguageSwitcher() {
    const languageBtn = document.getElementById('language-toggle');
    const languageDropdown = document.getElementById('language-dropdown');
    
    if (languageBtn && languageDropdown) {
        languageBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            languageDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!languageBtn.contains(event.target) && !languageDropdown.contains(event.target)) {
                languageDropdown.classList.remove('active');
            }
        });
        
        // Update current language display
        const currentLang = document.querySelector('.current-lang');
        const langOptions = document.querySelectorAll('.language-option');
        
        // Get current language from cookie or default to 'ar'
        const savedLang = getCookie('django_language') || 'ar';
        
        // Update display to show current language
        if (currentLang) {
            currentLang.textContent = savedLang.toUpperCase();
        }
        
        // Highlight active language option
        langOptions.forEach(option => {
            const lang = option.getAttribute('data-lang');
            if (lang === savedLang) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    }
}

// Helper function to get cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ================================
// Digital Watch Functionality
// ================================

function initializeDigitalWatch() {
    updateClock();
    setInterval(updateClock, 1000);
}

function updateClock() {
    const now = new Date();
    
    // Get current language
    const currentLang = document.body.getAttribute('data-language') || getCookie('django_language') || 'ar';
    
    // Get time components
    let hours = now.getHours();
    let minutes = now.getMinutes();
    let seconds = now.getSeconds();
    
    // Determine AM/PM
    let ampm = hours >= 12 ? 'PM' : 'AM';
    if (currentLang === 'ar') {
        ampm = hours >= 12 ? 'م' : 'ص';
    }
    
    // Convert to 12-hour format
    hours = hours % 12;
    hours = hours ? hours : 12;
    
    // Format with leading zeros
    hours = padZero(hours);
    minutes = padZero(minutes);
    seconds = padZero(seconds);
    
    // Get date components
    const daysEn = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const daysAr = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];
    const daysTr = ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'];
    const daysKu = ['یەکشەممە', 'دووشەممە', 'سێشەممە', 'چوارشەممە', 'پێنجشەممە', 'هەینی', 'شەممە'];
    
    const monthsEn = ['January', 'February', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December'];
    const monthsAr = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 
                    'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'];
    const monthsTr = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                    'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
    const monthsKu = ['کانوونی دووەم', 'شوبات', 'ئازار', 'نیسان', 'ئایار', 'حوزەیران', 
                    'تەممووز', 'ئاب', 'ئەیلوول', 'تشرینی یەکەم', 'تشرینی دووەم', 'کانوونی یەکەم'];
    
    let days = daysEn;
    let months = monthsEn;
    
    if (currentLang === 'ar') {
        days = daysAr;
        months = monthsAr;
    } else if (currentLang === 'tr') {
        days = daysTr;
        months = monthsTr;
    } else if (currentLang === 'ku' || currentLang === 'ckb') {
        days = daysKu;
        months = monthsKu;
    }
    
    const dayName = days[now.getDay()];
    const month = months[now.getMonth()];
    const date = now.getDate();
    const year = now.getFullYear();
    
    // Format date string
    let dateString;
    if (currentLang === 'ar' || currentLang === 'ku' || currentLang === 'ckb') {
        dateString = `${dayName}، ${date} ${month} ${year}`;
    } else {
        dateString = `${dayName}, ${month} ${date}, ${year}`;
    }
    
    // Update DOM
    const timeDisplay = document.getElementById('digital-time');
    const dateDisplay = document.getElementById('digital-date');
    const ampmDisplay = document.getElementById('digital-ampm');
    
    if (timeDisplay) {
        timeDisplay.textContent = `${hours}:${minutes}:${seconds}`;
    }
    
    if (dateDisplay) {
        dateDisplay.textContent = dateString;
    }
    
    if (ampmDisplay) {
        ampmDisplay.textContent = ampm;
    }
}

function padZero(num) {
    return String(num).padStart(2, '0');
}

// ================================
// Sidebar Toggle Functionality
// ================================

function initializeSidebarToggle() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const mainWrapper = document.querySelector('.main-wrapper');
    
    // On desktop, toggle hides/shows sidebar. On mobile, it shows overlay sidebar
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            if (window.innerWidth > 768) {
                // Desktop: toggle sidebar visibility
                sidebar.classList.toggle('hidden');
                if (sidebar.classList.contains('hidden')) {
                    sidebar.style.left = '-' + getComputedStyle(document.documentElement).getPropertyValue('--sidebar-width');
                    mainWrapper.style.left = '0';
                } else {
                    sidebar.style.left = '0';
                    mainWrapper.style.left = 'var(--sidebar-width)';
                }
            } else {
                // Mobile: overlay sidebar
                sidebar.classList.toggle('active');
                overlay.classList.toggle('active');
            }
        });
    }
    
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }
    
    // Close sidebar when clicking on a link (mobile only)
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            }
        });
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnToggle = toggleBtn && toggleBtn.contains(event.target);
            
            if (!isClickInsideSidebar && !isClickOnToggle && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            }
        }
    });
}

// ================================
// Navigation Link Active State
// ================================

function initializeNavLinks() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        // Check if the current path starts with the link's href
        if (currentPath === href || currentPath.startsWith(href + '/')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// ================================
// Utility Functions
// ================================

// Add smooth scroll behavior
function smoothScroll(target) {
    document.querySelector(target).scrollIntoView({
        behavior: 'smooth'
    });
}

// Show notification (optional)
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fade-in`;
    notification.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(notification, container.firstChild);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// ================================
// Responsive Adjustments
// ================================

window.addEventListener('resize', function() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const mainWrapper = document.querySelector('.main-wrapper');
    
    // Reset to default states when resizing
    if (window.innerWidth > 768) {
        // Desktop mode
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        
        // Restore sidebar if it was hidden by toggle
        if (!sidebar.classList.contains('hidden')) {
            sidebar.style.left = '0';
            mainWrapper.style.left = 'var(--sidebar-width)';
        }
    } else {
        // Mobile mode: hide sidebar by default
        sidebar.classList.remove('hidden');
        sidebar.style.left = '';
        mainWrapper.style.left = '';
    }
});

// ================================
// Theme Toggle Functionality
// ================================

function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (!themeToggle) {
        console.warn('Theme toggle button not found');
        return;
    }
    
    console.log('Theme toggle initialized');
    
    // Load saved theme from localStorage or default to 'light'
    const savedTheme = localStorage.getItem('theme') || 'light';
    console.log('Loading saved theme:', savedTheme);
    applyTheme(savedTheme, false);
    
    // Theme toggle click handler
    themeToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Theme toggle clicked');
        
        const currentTheme = document.body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        console.log('Switching from', currentTheme, 'to', newTheme);
        
        // Prevent multiple rapid clicks
        if (themeToggle.classList.contains('animating')) {
            console.log('Animation in progress, ignoring click');
            return;
        }
        
        themeToggle.classList.add('animating');
        
        // Apply theme with animation
        applyTheme(newTheme, true);
        
        // Remove animating class after animation completes
        setTimeout(() => {
            themeToggle.classList.remove('animating');
        }, 600);
    });
}

// Apply theme with smooth transitions
function applyTheme(theme, animate = true) {
    console.log('Applying theme:', theme, 'with animation:', animate);
    
    const themeToggle = document.getElementById('theme-toggle');
    
    // Add transition for smooth theme change
    if (animate) {
        document.body.style.transition = 'background 0.5s ease, color 0.5s ease';
        
        // Rotate button animation
        if (themeToggle) {
            const rotation = theme === 'dark' ? '360deg' : '-360deg';
            themeToggle.style.transition = 'transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
            themeToggle.style.transform = `rotate(${rotation})`;
            
            setTimeout(() => {
                themeToggle.style.transform = '';
            }, 600);
        }
    }
    
    // Apply theme to body and html
    document.body.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    
    // Save to localStorage
    localStorage.setItem('theme', theme);
    
    console.log('Theme applied. Body data-theme:', document.body.getAttribute('data-theme'));
    
    // Show notification
    if (animate) {
        showThemeNotification(theme);
    }
}

// Show theme change notification with enhanced styling
function showThemeNotification(theme) {
    // Remove existing notification if any
    const existingNotification = document.querySelector('.theme-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = 'theme-notification';
    
    const icon = theme === 'dark' ? 'moon' : 'sun';
    const label = theme === 'dark' ? 'Dark Mode Activated' : 'Light Mode Activated';
    
    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${label}</span>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 90px;
        right: 20px;
        background: ${theme === 'dark' ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)'};
        color: ${theme === 'dark' ? '#f1f5f9' : '#1e293b'};
        padding: 14px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, ${theme === 'dark' ? '0.6' : '0.2'});
        z-index: 10001;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 600;
        font-size: 14px;
        animation: slideInRight 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        border: 2px solid ${theme === 'dark' ? 'rgba(147, 197, 253, 0.3)' : 'rgba(59, 130, 246, 0.2)'};
        backdrop-filter: blur(10px);
    `;
    
    // Apply icon color
    const notificationIcon = notification.querySelector('i');
    if (notificationIcon) {
        notificationIcon.style.color = theme === 'dark' ? '#93c5fd' : '#fbbf24';
        notificationIcon.style.fontSize = '18px';
        notificationIcon.style.filter = theme === 'dark' 
            ? 'drop-shadow(0 0 8px rgba(147, 197, 253, 0.6))' 
            : 'drop-shadow(0 0 8px rgba(251, 191, 36, 0.6))';
    }
    
    document.body.appendChild(notification);
    
    // Animate out and remove
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
        setTimeout(() => notification.remove(), 400);
    }, 2500);
}

// ================================
// Weather Widget Functionality
// ================================

function initializeWeatherWidget() {
    console.log('Initializing weather widget');
    const weatherContainer = document.getElementById('footer-weather');
    
    if (!weatherContainer) {
        console.warn('Weather container not found');
        return;
    }
    
    // Use Kirkuk coordinates directly for more accurate weather
    const kirkukLat = 35.4681;
    const kirkukLon = 44.3922;
    
    // Try to get user's location
    if (navigator.geolocation && window.isSecureContext) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                fetchWeatherByCoords(lat, lon);
            },
            error => {
                // Silently fallback to Kirkuk coordinates when geolocation fails
                // (User may have denied permission or connection is not secure)
                fetchWeatherByCoords(kirkukLat, kirkukLon, 'Kirkuk');
            },
            {
                timeout: 5000,
                maximumAge: 300000 // Cache position for 5 minutes
            }
        );
    } else {
        // Fallback to Kirkuk coordinates (either no geolocation support or insecure context)
        fetchWeatherByCoords(kirkukLat, kirkukLon, 'Kirkuk');
    }
}

function fetchWeatherByCoords(lat, lon, cityName = null) {
    // Using Open-Meteo API - free, no API key required, very accurate
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=auto`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            displayWeather(data, lat, lon, cityName);
        })
        .catch(error => {
            console.error('Error fetching weather:', error);
            displayWeatherError();
        });
}

function displayWeather(data, lat, lon, cityName = null) {
    const weatherContainer = document.getElementById('footer-weather');
    
    if (!data || !data.current) {
        displayWeatherError();
        return;
    }
    
    const current = data.current;
    const temp = Math.round(current.temperature_2m);
    const feelsLike = Math.round(current.apparent_temperature);
    const humidity = current.relative_humidity_2m;
    const windSpeed = Math.round(current.wind_speed_10m);
    const weatherCode = current.weather_code;
    
    // Get location name
    const location = cityName || getCityName(lat, lon);
    
    // Get weather icon and description based on WMO weather code
    const weatherInfo = getWeatherFromWMO(weatherCode);
    
    weatherContainer.innerHTML = `
        <div class="weather-info">
            <div class="weather-icon">${weatherInfo.icon}</div>
            <div class="weather-details">
                <div class="weather-temp">${temp}°C</div>
                <div class="weather-location">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${location}</span>
                </div>
            </div>
        </div>
    `;
    
    // Add tooltip with more details
    weatherContainer.title = `${weatherInfo.description}\\nFeels like: ${feelsLike}°C\\nHumidity: ${humidity}%\\nWind: ${windSpeed} km/h`;
}

function getCityName(lat, lon) {
    // Simple coordinate-based city detection
    const kirkukLat = 35.4681;
    const kirkukLon = 44.3922;
    
    // If coordinates are close to Kirkuk
    if (Math.abs(lat - kirkukLat) < 0.5 && Math.abs(lon - kirkukLon) < 0.5) {
        return 'Kirkuk';
    }
    
    return 'Current Location';
}

function getWeatherFromWMO(code) {
    // WMO Weather interpretation codes
    const weatherCodes = {
        0: { icon: '☀️', description: 'Clear sky' },
        1: { icon: '🌤️', description: 'Mainly clear' },
        2: { icon: '⛅', description: 'Partly cloudy' },
        3: { icon: '☁️', description: 'Overcast' },
        45: { icon: '🌫️', description: 'Foggy' },
        48: { icon: '🌫️', description: 'Depositing rime fog' },
        51: { icon: '🌦️', description: 'Light drizzle' },
        53: { icon: '🌦️', description: 'Moderate drizzle' },
        55: { icon: '🌧️', description: 'Dense drizzle' },
        56: { icon: '🌨️', description: 'Light freezing drizzle' },
        57: { icon: '🌨️', description: 'Dense freezing drizzle' },
        61: { icon: '🌧️', description: 'Slight rain' },
        63: { icon: '🌧️', description: 'Moderate rain' },
        65: { icon: '🌧️', description: 'Heavy rain' },
        66: { icon: '🌨️', description: 'Light freezing rain' },
        67: { icon: '🌨️', description: 'Heavy freezing rain' },
        71: { icon: '🌨️', description: 'Slight snow' },
        73: { icon: '❄️', description: 'Moderate snow' },
        75: { icon: '❄️', description: 'Heavy snow' },
        77: { icon: '🌨️', description: 'Snow grains' },
        80: { icon: '🌦️', description: 'Slight rain showers' },
        81: { icon: '🌧️', description: 'Moderate rain showers' },
        82: { icon: '⛈️', description: 'Violent rain showers' },
        85: { icon: '🌨️', description: 'Slight snow showers' },
        86: { icon: '❄️', description: 'Heavy snow showers' },
        95: { icon: '⛈️', description: 'Thunderstorm' },
        96: { icon: '⛈️', description: 'Thunderstorm with hail' },
        99: { icon: '⛈️', description: 'Thunderstorm with heavy hail' }
    };
    
    return weatherCodes[code] || { icon: '🌤️', description: 'Unknown' };
}

function displayWeatherError() {
    const weatherContainer = document.getElementById('footer-weather');
    weatherContainer.innerHTML = `
        <div class="weather-error">
            <i class="fas fa-exclamation-triangle"></i>
            <span>Weather unavailable</span>
        </div>
    `;
}
