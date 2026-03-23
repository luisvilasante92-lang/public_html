@extends('layouts.base')

@section('title', 'Новый релиз')
@section('page_title', 'Новый релиз')

@section('content')
<form method="POST" action="{{ route('releases.store') }}" enctype="multipart/form-data" class="release-form">
    @csrf
    <div class="form-grid">
        <div class="form-group">
            <label for="title">Название *</label>
            <input type="text" id="title" name="title" required value="{{ old('title') }}" class="form-input">
        </div>
        <div class="form-group">
            <label for="artists">Артисты *</label>
            <input type="text" id="artists" name="artists" required value="{{ old('artists') }}" class="form-input">
        </div>
        <div class="form-group">
            <label for="version">Версия</label>
            <input type="text" id="version" name="version" value="{{ old('version') }}" class="form-input">
        </div>
        <div class="form-group">
            <label for="type">Тип</label>
            <select id="type" name="type" class="form-select">
                <option value="Single">Сингл</option>
                <option value="EP">EP</option>
                <option value="Album">Альбом</option>
            </select>
        </div>
        <div class="form-group">
            <label for="genre">Жанр *</label>
            <select id="genre" name="genre" required class="form-select">
                @foreach($genres as $g)
                <option value="{{ $g }}" {{ old('genre') == $g ? 'selected' : '' }}>{{ $g }}</option>
                @endforeach
            </select>
        </div>
        <div class="form-group">
            <label for="release_date">Дата релиза *</label>
            <input type="date" id="release_date" name="release_date" required value="{{ old('release_date') }}" class="form-input">
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" name="yandex_presave" value="1" {{ old('yandex_presave') ? 'checked' : '' }}>
                Яндекс Пре-сейв
            </label>
        </div>
        <div class="form-group">
            <label for="cover">Обложка</label>
            <input type="file" id="cover" name="cover" accept="image/jpeg,image/png" class="form-input">
        </div>
    </div>
    <div class="form-actions">
        <button type="submit" class="btn btn-primary">Создать</button>
        <a href="{{ route('releases.index') }}" class="btn btn-ghost">Отмена</a>
    </div>
</form>
@endsection
