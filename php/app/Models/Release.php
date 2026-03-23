<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Release extends Model
{
    protected $fillable = [
        'user_id', 'cover', 'title', 'version', 'artists', 'type', 'genre',
        'release_date', 'yandex_presave', 'partner_code', 'copyright', 'upc',
        'status', 'moderator_comment', 'platforms'
    ];

    protected $casts = [
        'release_date' => 'date',
        'yandex_presave' => 'boolean',
        'platforms' => 'array',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function tracks(): HasMany
    {
        return $this->hasMany(Track::class)->orderBy('track_order');
    }

    public function analytics()
    {
        return $this->hasMany(ReleaseAnalytics::class);
    }

    public function smartLinks()
    {
        return $this->hasMany(SmartLink::class);
    }

    public function getCoverUrlAttribute(): string
    {
        return $this->cover
            ? asset('storage/covers/' . $this->cover)
            : asset('static/img/default-cover.png');
    }

    public function getTracksCountAttribute(): int
    {
        return $this->tracks()->count();
    }

    public function getStatusDisplayAttribute(): string
    {
        return match ($this->status) {
            'draft' => 'Черновик',
            'moderation' => 'На модерации',
            'approved' => 'Одобрено',
            'rejected' => 'Отклонено',
            'deletion' => 'На удалении',
            default => $this->status,
        };
    }

    public function getStatusClassAttribute(): string
    {
        return match ($this->status) {
            'draft' => 'status-draft',
            'moderation' => 'status-moderation',
            'approved' => 'status-approved',
            'rejected' => 'status-rejected',
            'deletion' => 'status-deletion',
            default => '',
        };
    }

    public function getTypeDisplayAttribute(): string
    {
        return match ($this->type) {
            'Single' => 'Сингл',
            'EP' => 'EP',
            'Album' => 'Альбом',
            default => $this->type,
        };
    }

    public function canEdit(): bool
    {
        return in_array($this->status, ['draft', 'rejected']);
    }

    public function canSubmit(): bool
    {
        return in_array($this->status, ['draft', 'rejected'])
            && $this->cover
            && $this->tracks()->count() > 0;
    }

    public function canDelete(): bool
    {
        return in_array($this->status, ['draft', 'approved', 'rejected']);
    }
}
