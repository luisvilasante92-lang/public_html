@extends('layouts.base')

@section('title', 'Главная')
@section('page_title', 'Главная')

@section('content')
<div class="dashboard">
    <div class="dashboard-legal-notice" role="alert">
        <span class="dashboard-legal-notice__icon material-icons" aria-hidden="true">report</span>
        <div class="dashboard-legal-notice__body">
            <p class="dashboard-legal-notice__eyebrow">Обязательно к сведению</p>
            <h3 class="dashboard-legal-notice__title">Важно</h3>
            <div class="dashboard-legal-notice__copy">
                <p>С 1 марта 2026 в силу вступил закон о запрете пропаганды наркотических средств, поэтому наши партнёры проводят проверку всего отгруженного контента.</p>
                <p>Часть релизов была удалена по инициативе площадки, так как по результатам автоматического аудита они признаны несущими риски финансового и уголовного преследования, поэтому часть ваших релизов может быть отозвана с витрин.</p>
                <p>Если вы наблюдаете релизы на площадках, то данное ограничение не коснулось их.</p>
                <p>Согласно правилам работы с площадками, мы обязаны соблюдать их требования.</p>
                <p class="dashboard-legal-notice__final">Удаление произошло на стороне партнёра, поэтому восстановить или перезагрузить данные релизы невозможно — это технически заблокировано модерацией. Мы не можем повлиять на этот процесс, даже если вы уверены в отсутствии нарушений.</p>
            </div>
        </div>
    </div>
    <div class="welcome-card">
        <div class="welcome-content">
            <h2>Добро пожаловать, {{ auth()->user()->display_name }}!</h2>
            <p>Управляйте своими релизами, отслеживайте статистику и финансы</p>
        </div>
        <a href="{{ route('releases.create') }}" class="btn btn-primary">
            <span class="material-icons">add</span>
            Новый релиз
        </a>
    </div>

    @if(!auth()->user()->is_admin && !empty($stats))
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon"><span class="material-icons">album</span></div>
            <div class="stat-content">
                <div class="stat-value">{{ $stats['total_releases'] }}</div>
                <div class="stat-label">Всего релизов</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon success"><span class="material-icons">check_circle</span></div>
            <div class="stat-content">
                <div class="stat-value">{{ $stats['approved_releases'] }}</div>
                <div class="stat-label">Одобрено</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon warning"><span class="material-icons">pending</span></div>
            <div class="stat-content">
                <div class="stat-value">{{ $stats['pending_releases'] }}</div>
                <div class="stat-label">На модерации</div>
            </div>
        </div>
    </div>
    @endif

    <div class="dashboard-grid">
        <div class="dashboard-card">
            <div class="card-header">
                <h3><span class="material-icons">newspaper</span> Последняя новость</h3>
            </div>
            <div class="card-content">
                @if($latest_news)
                <div class="news-preview">
                    @if($latest_news->cover_image)
                    <img src="{{ $latest_news->cover_url }}" alt="{{ $latest_news->title }}" class="news-cover">
                    @endif
                    <div class="news-info">
                        <h4>{{ $latest_news->title }}</h4>
                        <p>{{ $latest_news->short_content }}</p>
                        <div class="news-meta">
                            <span class="news-date">{{ $latest_news->date_formatted }}</span>
                        </div>
                    </div>
                </div>
                @else
                <div class="empty-state">
                    <span class="material-icons">article</span>
                    <p>Новостей пока нет</p>
                </div>
                @endif
            </div>
        </div>

        <div class="dashboard-card">
            <div class="card-header">
                <h3><span class="material-icons">payments</span> Финансы {{ $current_year }}</h3>
            </div>
            <div class="card-content">
                <div class="quarters-grid">
                    @foreach($quarters_data as $quarter)
                    <div class="quarter-card {{ $quarter['quarter'] == $current_quarter ? 'current' : '' }}">
                        <div class="quarter-number">{{ $quarter['quarter_roman'] }}</div>
                        <div class="quarter-label">квартал</div>
                        @if($quarter['has_data'])
                        <div class="quarter-amount">{{ number_format($quarter['amount'], 2) }} ₽</div>
                        @else
                        <div class="quarter-empty">
                            <span class="material-icons">remove</span>
                            <span>Нет данных</span>
                        </div>
                        @endif
                    </div>
                    @endforeach
                </div>
            </div>
        </div>
    </div>

    <div class="quick-actions">
        <h3>Быстрые действия</h3>
        <div class="actions-grid">
            <a href="{{ route('releases.create') }}" class="action-card">
                <span class="material-icons">add_circle</span>
                <span>Создать релиз</span>
            </a>
            <a href="{{ route('releases.index') }}" class="action-card">
                <span class="material-icons">album</span>
                <span>Мои релизы</span>
            </a>
        </div>
    </div>
</div>
@endsection
