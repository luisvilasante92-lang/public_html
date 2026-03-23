<!DOCTYPE html>
<html lang="ru" data-theme="light" data-accent="orange">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#f5f5f5">
    <title>@yield('title', 'Личный кабинет') | LVR Music Publishing</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="{{ asset('static/css/style.css') }}">
    @stack('styles')
</head>
<body>
    <div class="app-container">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <a href="{{ route('dashboard') }}" class="logo">
                    <svg class="logo-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 52" fill="none" aria-label="LVR Music Publishing">
                        <defs>
                            <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:var(--logo-text)"/>
                                <stop offset="100%" style="stop-color:var(--logo-subtitle)"/>
                            </linearGradient>
                            <linearGradient id="logoAccent" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" style="stop-color:var(--logo-accent)"/>
                                <stop offset="100%" style="stop-color:var(--logo-accent-end)"/>
                            </linearGradient>
                        </defs>
                        <g transform="translate(0, 4)">
                            <ellipse cx="12" cy="28" rx="6" ry="4" fill="url(#logoAccent)"/>
                            <path d="M18 28 V8 L28 14 V28" stroke="url(#logoAccent)" stroke-width="3" fill="none" stroke-linecap="round"/>
                            <circle cx="28" cy="28" r="3" fill="url(#logoAccent)"/>
                        </g>
                        <text x="52" y="34" font-family="Manrope, sans-serif" font-size="26" font-weight="700" letter-spacing="2" fill="url(#logoGrad)">LVR</text>
                        <text x="52" y="48" font-family="Manrope, sans-serif" font-size="11" font-weight="500" letter-spacing="2" fill="var(--logo-subtitle)">MUSIC PUBLISHING</text>
                    </svg>
                </a>
                <button class="sidebar-toggle" id="sidebarToggle"><span class="material-icons">menu</span></button>
            </div>
            <nav class="sidebar-nav">
                <a href="{{ route('releases.create') }}" class="btn btn-primary sidebar-btn">
                    <span class="material-icons">add</span>
                    <span>Новый релиз</span>
                </a>
                <div class="nav-section">
                    <a href="{{ route('releases.index') }}" class="nav-item {{ request()->routeIs('releases.*') ? 'active' : '' }}">
                        <span class="material-icons">album</span>
                        <span>Релизы</span>
                    </a>
                </div>
                <div class="nav-section">
                    <div class="nav-section-title">Прочее</div>
                    <a href="{{ route('profile') }}" class="nav-item">
                        <span class="material-icons">person</span>
                        <span>Профиль</span>
                    </a>
                </div>
            </nav>
            <div class="sidebar-footer">
                © LVR Music Publishing, 2022-2026
                <span class="sidebar-version">v1.10.0</span>
            </div>
        </aside>
        <div class="sidebar-overlay" id="sidebarOverlay"></div>
        <main class="main-content">
            <header class="header">
                <div class="header-left">
                    <button class="mobile-menu-toggle" id="mobileMenuToggle"><span class="material-icons">menu</span></button>
                    <h1 class="page-title">@yield('page_title', 'Главная')</h1>
                </div>
                <div class="header-right">
                    <div class="user-menu">
                        <a href="{{ route('profile') }}" class="user-info">
                            <img src="{{ auth()->user()->avatar_url }}" alt="Avatar" class="user-avatar">
                            <span class="user-name">{{ auth()->user()->display_name }}</span>
                        </a>
                        <a href="{{ route('auth.logout') }}" class="btn btn-ghost btn-sm" title="Выйти">
                            <span class="material-icons">logout</span>
                        </a>
                    </div>
                </div>
            </header>
            @if(session('success') || session('error') || session('info') || session('warning'))
            <div class="flash-messages">
                @foreach(['success', 'error', 'info', 'warning'] as $type)
                    @if(session($type))
                    <div class="flash-message flash-{{ $type }}">
                        <span class="material-icons">
                            @if($type === 'success') check_circle
                            @elseif($type === 'error') error
                            @elseif($type === 'warning') warning
                            @else info
                            @endif
                        </span>
                        <span>{{ session($type) }}</span>
                        <button class="flash-close" onclick="this.parentElement.remove()"><span class="material-icons">close</span></button>
                    </div>
                    @endif
                @endforeach
            </div>
            @endif
            <div class="content">
                @yield('content')
            </div>
        </main>
    </div>
    <script src="{{ asset('static/js/app.js') }}"></script>
    @stack('scripts')
</body>
</html>
