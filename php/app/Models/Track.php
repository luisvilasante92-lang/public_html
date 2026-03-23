<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Track extends Model
{
    protected $fillable = [
        'release_id', 'wav_file', 'title', 'version', 'artists', 'composers',
        'authors', 'explicit', 'language', 'isrc', 'lyrics', 'track_order'
    ];

    protected $casts = [
        'explicit' => 'boolean',
    ];

    public function release()
    {
        return $this->belongsTo(Release::class);
    }

    public function getFileUrlAttribute(): string
    {
        return '/uploads/tracks/' . $this->wav_file;
    }

    public function getDisplayTitleAttribute(): string
    {
        return $this->version ? "{$this->title} ({$this->version})" : $this->title;
    }
}
