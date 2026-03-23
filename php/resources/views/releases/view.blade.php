@extends('layouts.base')

@section('title', $release->title)
@section('page_title', $release->title)

@section('content')
<div class="release-detail">
    <div class="release-detail-header">
        <img src="{{ $release->cover_url }}" alt="{{ $release->title }}" class="release-detail-cover">
        <div class="release-detail-info">
            <h2>{{ $release->title }} @if($release->version)<span class="version">({{ $release->version }})</span>@endif</h2>
            <p class="release-artists">{{ $release->artists }}</p>
            <span class="status-badge {{ $release->status_class }}">{{ $release->status_display }}</span>
            <p><strong>Тип:</strong> {{ $release->type_display }} | <strong>Жанр:</strong> {{ $release->genre }}</p>
            <p><strong>Дата релиза:</strong> {{ $release->release_date->format('d.m.Y') }}</p>
            @if($release->moderator_comment && $release->status === 'rejected')
            <div class="moderator-comment">
                <strong>Комментарий модератора:</strong> {{ $release->moderator_comment }}
            </div>
            @endif
            <div class="release-detail-actions">
                @if($release->canEdit())
                <a href="{{ route('releases.edit', $release->id) }}" class="btn btn-primary">Редактировать</a>
                @endif
                @if($release->canSubmit())
                <form method="POST" action="{{ route('releases.submit', $release->id) }}" style="display:inline">
                    @csrf
                    <button type="submit" class="btn btn-primary">Отправить на модерацию</button>
                </form>
                @endif
                @if($release->canDelete())
                <form method="POST" action="{{ route('releases.delete', $release->id) }}" style="display:inline" onsubmit="return confirm('Удалить релиз?')">
                    @csrf
                    <button type="submit" class="btn btn-ghost">Удалить</button>
                </form>
                @endif
            </div>
        </div>
    </div>
    <div class="tracks-list">
        <h3>Треки ({{ $tracks->count() }})</h3>
        @forelse($tracks as $track)
        <div class="track-item">
            <span class="track-order">{{ $track->track_order }}</span>
            <span class="track-title">{{ $track->display_title }}</span>
            <span class="track-artists">{{ $track->artists }}</span>
        </div>
        @empty
        <p>Треков пока нет</p>
        @endforelse
    </div>
</div>
@endsection
