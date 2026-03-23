<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход | LVR Music Publishing</title>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="{{ asset('static/css/style.css') }}">
</head>
<body class="auth-page auth-page-new">
    <div class="auth-layout">
        <div class="auth-card auth-card-form">
            <h1 class="auth-card-title">Вход в аккаунт</h1>
            @if(session('error') || session('success') || session('support') || session('info'))
            <div class="auth-flash-messages">
                @if(session('error'))
                <div class="auth-flash auth-flash-error">
                    <span class="material-icons">error</span> {{ session('error') }}
                </div>
                @endif
                @if(session('success'))
                <div class="auth-flash auth-flash-success">
                    <span class="material-icons">check_circle</span> {{ session('success') }}
                </div>
                @endif
                @if(session('support'))
                <div class="auth-flash auth-flash-support">
                    <span class="material-icons">support_agent</span> {{ session('support') }}
                </div>
                @endif
                @if(session('info'))
                <div class="auth-flash auth-flash-info">
                    <span class="material-icons">info</span> {{ session('info') }}
                </div>
                @endif
            </div>
            @endif
            <form method="POST" action="{{ route('auth.login') }}" class="auth-form">
                @csrf
                <div class="auth-form-group">
                    <label for="login">Эл. почта</label>
                    <input type="text" id="login" name="login" required class="auth-input" value="{{ old('login') }}" placeholder="Логин или email">
                </div>
                <div class="auth-form-group">
                    <label for="password">Пароль</label>
                    <div class="auth-password-wrap">
                        <input type="password" id="password" name="password" required class="auth-input" placeholder="Пароль">
                        <button type="button" class="auth-password-toggle" onclick="var p=document.getElementById('password');p.type=p.type==='password'?'text':'password';" aria-label="Показать пароль">
                            <span class="material-icons">visibility</span>
                        </button>
                    </div>
                </div>
                <div class="auth-forgot-wrap">
                    <a href="{{ route('auth.forgot') }}" class="auth-forgot-link">Забыли пароль?</a>
                </div>
                <button type="submit" class="auth-submit-btn">Войти</button>
            </form>
        </div>
        <div class="auth-card auth-card-info">
            <div class="auth-info-brand">
                <img src="{{ asset('static/img/logo.svg') }}" alt="LVR Music Publishing" class="auth-logo-img">
                <h2 class="auth-info-title">Там, где музыка и технологии едины</h2>
            </div>
            <div class="auth-info-advantages">
                <h3 class="auth-advantages-title">Преимущества публикаций релизов</h3>
                <ul class="auth-advantages-list">
                    <li><span class="material-icons auth-note-icon">music_note</span>максимальное вознаграждение за использование вашего репертуара</li>
                    <li><span class="material-icons auth-note-icon">music_note</span>гибкие условия лицензирования</li>
                    <li><span class="material-icons auth-note-icon">music_note</span>подробные отчёты об использовании репертуара</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
