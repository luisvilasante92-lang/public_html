@extends('layouts.base')

@section('title', 'Редактирование: ' . $release->title)
@section('page_title', 'Редактирование релиза')

@section('content')
<form method="POST" action="{{ route('releases.update', $release->id) }}" enctype="multipart/form-data" class="release-form">
    @csrf
    <div class="form-grid">
        <div class="form-group">
            <label for="title">Название *</label>
            <input type="text" id="title" name="title" required value="{{ old('title', $release->title) }}" class="form-input">
        </div>
        <div class="form-group">
            <label for="artists">Артисты *</label>
            <input type="text" id="artists" name="artists" required value="{{ old('artists', $release->artists) }}" class="form-input">
        </div>
        <div class="form-group">
            <label for="version">Версия</label>
            <input type="text" id="version" name="version" value="{{ old('version', $release->version) }}" class="form-input">
        </div>
        <div class="form-group">
            <label for="type">Тип</label>
            <select id="type" name="type" class="form-select">
                <option value="Single" {{ $release->type === 'Single' ? 'selected' : '' }}>Сингл</option>
                <option value="EP" {{ $release->type === 'EP' ? 'selected' : '' }}>EP</option>
                <option value="Album" {{ $release->type === 'Album' ? 'selected' : '' }}>Альбом</option>
            </select>
        </div>
        <div class="form-group">
            <label for="genre">Жанр *</label>
            <input type="text" id="genre" name="genre" required value="{{ old('genre', $release->genre) }}" class="form-input">
        </div>
        <div class="form-group">
            <label for="release_date">Дата релиза *</label>
            <input type="date" id="release_date" name="release_date" required value="{{ old('release_date', $release->release_date?->format('Y-m-d')) }}" class="form-input">
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" name="yandex_presave" value="1" {{ $release->yandex_presave ? 'checked' : '' }}>
                Яндекс Пре-сейв
            </label>
        </div>
        <div class="form-group">
            <label for="cover">Обложка</label>
            @if($release->cover)
            <p>Текущая: <img src="{{ $release->cover_url }}" alt="" style="max-height:60px"></p>
            @endif
            <input type="file" id="cover" name="cover" accept="image/jpeg,image/png" class="form-input">
        </div>
    </div>
    <div class="form-actions">
        <button type="submit" class="btn btn-primary">Сохранить</button>
        @if($release->canSubmit())
        <form method="POST" action="{{ route('releases.submit', $release->id) }}" style="display:inline">
            @csrf
            <button type="submit" class="btn btn-primary">Отправить на модерацию</button>
        </form>
        @endif
        <a href="{{ route('releases.view', $release->id) }}" class="btn btn-ghost">Отмена</a>
    </div>
</form>

<div class="tracks-section">
    <h3>Треки</h3>
    @foreach($release->tracks as $track)
    <div class="track-item">
        <span class="track-order">{{ $track->track_order }}</span>
        <span class="track-title">{{ $track->display_title }}</span>
        <span class="track-artists">{{ $track->artists }}</span>
    </div>
    @endforeach
    <p><em>Добавление/редактирование треков — в полной версии</em></p>
</div>
@endsection
