<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход (dev) | LVR Music Publishing</title>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="{{ asset('static/css/style.css') }}">
</head>
<body class="auth-page">
    <div class="auth-layout">
        <div class="auth-card auth-card-form">
            <h1 class="auth-card-title">Вход для разработки</h1>
            @if(session('error') || session('success') || session('info'))
            <div class="auth-flash-messages">
                @if(session('error'))<div class="auth-flash auth-flash-error">{{ session('error') }}</div>@endif
                @if(session('success'))<div class="auth-flash auth-flash-success">{{ session('success') }}</div>@endif
                @if(session('info'))<div class="auth-flash auth-flash-info">{{ session('info') }}</div>@endif
            </div>
            @endif
            <form method="POST" action="{{ route('auth.dev-login') }}" class="auth-form">
                @csrf
                <div class="auth-form-group">
                    <label for="login">Логин</label>
                    <input type="text" id="login" name="login" required class="auth-input">
                </div>
                <div class="auth-form-group">
                    <label for="password">Пароль</label>
                    <input type="password" id="password" name="password" required class="auth-input">
                </div>
                <button type="submit" class="auth-submit-btn">Войти</button>
            </form>
            <p style="margin-top: 1rem;">
                <a href="{{ route('auth.dev-setup') }}">Создать тестовые данные</a>
            </p>
        </div>
    </div>
</body>
</html>
