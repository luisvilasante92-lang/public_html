<?php

namespace App\Http\Controllers;

use App\Models\Platform;
use App\Models\Release;
use App\Models\Track;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Validation\Rule;

class ReleaseController extends Controller
{
    private const RELEASE_GENRES = [
        'Pop', 'Hip-Hop', 'Rap', 'Rock', 'Alternative', 'Indie', 'Electronic',
        'Dance', 'House', 'Techno', 'Trance', 'R&B', 'Soul', 'Jazz', 'Blues',
        'Country', 'Folk', 'Classical', 'Metal', 'Punk', 'Reggae', 'Latin',
        'World', 'Ambient', 'Soundtrack', 'Children', 'Religion', 'Comedy',
        'Spoken Word', 'Другое'
    ];

    public function index(Request $request)
    {
        $query = Release::where('user_id', $request->user()->id);

        if ($status = $request->get('status')) {
            $query->where('status', $status);
        }
        if ($search = $request->get('search')) {
            $query->where(function ($q) use ($search) {
                $q->where('title', 'like', "%{$search}%")
                    ->orWhere('artists', 'like', "%{$search}%");
            });
        }

        $releases = $query->orderBy('created_at', 'desc')->paginate(12);

        return view('releases.index', [
            'releases' => $releases,
            'statuses' => [
                '' => 'Все',
                'draft' => 'Черновики',
                'moderation' => 'На модерации',
                'approved' => 'Одобренные',
                'rejected' => 'Отклонённые',
                'deletion' => 'На удалении',
            ],
            'current_status' => $status,
            'search' => $search,
        ]);
    }

    public function create()
    {
        return view('releases.create', ['genres' => self::RELEASE_GENRES]);
    }

    public function store(Request $request)
    {
        $user = $request->user();
        $validated = $request->validate([
            'title' => 'required|string|max:256',
            'artists' => 'required|string|max:512',
            'genre' => 'required|string|max:100',
            'release_date' => 'required|date',
            'type' => 'in:Single,EP,Album',
        ]);

        $platforms = Platform::where('is_active', true)->orderBy('sort_order')->pluck('id')->toArray();

        $release = Release::create([
            'user_id' => $user->id,
            'title' => $validated['title'],
            'version' => $request->input('version'),
            'artists' => $validated['artists'],
            'type' => $request->input('type', 'Single'),
            'genre' => $validated['genre'],
            'release_date' => $validated['release_date'],
            'yandex_presave' => $request->boolean('yandex_presave'),
            'partner_code' => $user->partner_code,
            'copyright' => $user->getDefaultCopyright(),
            'platforms' => $platforms ?: null,
            'status' => 'draft',
        ]);

        if ($request->hasFile('cover')) {
            $path = $request->file('cover')->store('covers', 'public');
            $release->update(['cover' => basename($path)]);
        }

        return redirect()->route('releases.edit', $release->id)
            ->with('success', 'Релиз создан. Добавьте треки и отправьте на модерацию.');
    }

    public function view(Request $request, int $id)
    {
        $release = Release::with('tracks')->findOrFail($id);
        if ($release->user_id !== $request->user()->id && !$request->user()->is_admin) {
            abort(403);
        }
        return view('releases.view', ['release' => $release, 'tracks' => $release->tracks]);
    }

    public function edit(Request $request, int $id)
    {
        $release = Release::with('tracks')->findOrFail($id);
        if ($release->user_id !== $request->user()->id) {
            abort(403);
        }
        if (!$release->canEdit()) {
            return redirect()->route('releases.view', $id)->with('error', 'Этот релиз нельзя редактировать');
        }
        return view('releases.edit', ['release' => $release]);
    }

    public function update(Request $request, int $id)
    {
        $release = Release::findOrFail($id);
        if ($release->user_id !== $request->user()->id || !$release->canEdit()) {
            abort(403);
        }

        $release->update([
            'title' => $request->input('title'),
            'version' => $request->input('version'),
            'artists' => $request->input('artists'),
            'type' => $request->input('type', 'Single'),
            'genre' => $request->input('genre'),
            'release_date' => $request->input('release_date'),
            'yandex_presave' => $request->boolean('yandex_presave'),
        ]);

        if ($request->hasFile('cover')) {
            if ($release->cover) {
                Storage::disk('public')->delete('covers/' . $release->cover);
            }
            $path = $request->file('cover')->store('covers', 'public');
            $release->update(['cover' => basename($path)]);
        }

        return redirect()->route('releases.edit', $id)->with('success', 'Релиз обновлён');
    }

    public function submit(Request $request, int $id)
    {
        $release = Release::findOrFail($id);
        if ($release->user_id !== $request->user()->id) {
            abort(403);
        }
        if (!$release->canSubmit()) {
            $msg = !$release->cover ? 'Добавьте обложку релиза' : ($release->tracks()->count() === 0 ? 'Добавьте хотя бы один трек' : 'Этот релиз нельзя отправить');
            return redirect()->route('releases.edit', $id)->with('error', $msg);
        }
        $release->update(['status' => 'moderation', 'moderator_comment' => null]);
        return redirect()->route('releases.view', $id)->with('success', 'Релиз отправлен на модерацию');
    }

    public function delete(Request $request, int $id)
    {
        $release = Release::with('tracks')->findOrFail($id);
        if ($release->user_id !== $request->user()->id) {
            abort(403);
        }
        if (!$release->canDelete()) {
            return redirect()->route('releases.view', $id)->with('error', 'Этот релиз нельзя удалить');
        }

        if ($release->status === 'draft') {
            if ($release->cover) {
                Storage::disk('public')->delete('covers/' . $release->cover);
            }
            foreach ($release->tracks as $track) {
                if ($track->wav_file) {
                    Storage::disk('public')->delete('tracks/' . $track->wav_file);
                }
            }
            $release->delete();
            return redirect()->route('releases.index')->with('success', 'Релиз удалён');
        }

        $release->update(['status' => 'deletion']);
        return redirect()->route('releases.view', $id)->with('info', 'Запрос на удаление отправлен');
    }

    public function export(Request $request)
    {
        $releases = Release::where('user_id', $request->user()->id)
            ->orderBy('created_at', 'desc')
            ->get();

        $csv = "ID;Название;Артисты;Тип;Жанр;Дата релиза;Статус;UPC;Копирайт;Дата создания;Кол-во треков\n";
        foreach ($releases as $r) {
            $csv .= implode(';', [
                $r->id,
                $r->title,
                $r->artists,
                $r->type,
                $r->genre,
                $r->release_date->format('d.m.Y'),
                $r->status_display,
                $r->upc ?? '',
                $r->copyright ?? '',
                $r->created_at->format('d.m.Y'),
                $r->tracks_count,
            ]) . "\n";
        }

        return response($csv, 200, [
            'Content-Type' => 'text/csv; charset=UTF-8',
            'Content-Disposition' => 'attachment; filename="releases_' . date('Ymd') . '.csv"',
        ]);
    }
}
