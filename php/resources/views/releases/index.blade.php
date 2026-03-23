@extends('layouts.base')

@section('title', 'Релизы')
@section('page_title', 'Релизы')

@section('content')
<div class="releases-header">
    <a href="{{ route('releases.create') }}" class="btn btn-primary">
        <span class="material-icons">add</span>
        Новый релиз
    </a>
    <form method="GET" class="releases-filters">
        <input type="text" name="search" value="{{ $search }}" placeholder="Поиск..." class="form-input">
        <select name="status" class="form-select">
            @foreach($statuses as $val => $label)
            <option value="{{ $val }}" {{ $current_status == $val ? 'selected' : '' }}>{{ $label }}</option>
            @endforeach
        </select>
        <button type="submit" class="btn btn-ghost">Фильтр</button>
    </form>
</div>

<div class="releases-grid">
    @forelse($releases as $release)
    <div class="release-card">
        <img src="{{ $release->cover_url }}" alt="{{ $release->title }}" class="release-cover">
        <div class="release-info">
            <h3>{{ $release->title }}</h3>
            <p class="release-artists">{{ $release->artists }}</p>
            <span class="status-badge {{ $release->status_class }}">{{ $release->status_display }}</span>
        </div>
        <div class="release-actions">
            <a href="{{ route('releases.view', $release->id) }}" class="btn btn-ghost btn-sm">Просмотр</a>
            @if($release->canEdit())
            <a href="{{ route('releases.edit', $release->id) }}" class="btn btn-ghost btn-sm">Редактировать</a>
            @endif
        </div>
    </div>
    @empty
    <div class="empty-state">
        <span class="material-icons">album</span>
        <p>Релизов пока нет</p>
        <a href="{{ route('releases.create') }}" class="btn btn-primary">Создать релиз</a>
    </div>
    @endforelse
</div>

@if($releases->hasPages())
<div class="pagination">
    {{ $releases->links() }}
</div>
@endif
@endsection
