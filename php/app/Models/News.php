<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class News extends Model
{
    protected $fillable = ['title', 'content', 'cover_image', 'author_id'];

    public function author()
    {
        return $this->belongsTo(User::class, 'author_id');
    }

    public function getCoverUrlAttribute(): string
    {
        return $this->cover_image
            ? asset('storage/news_covers/' . $this->cover_image)
            : asset('static/img/default-news-cover.png');
    }

    public function getShortContentAttribute(): string
    {
        return strlen($this->content) > 70 ? substr($this->content, 0, 70) . '...' : $this->content;
    }

    public function getDateFormattedAttribute(): string
    {
        return $this->created_at->format('d.m.Y');
    }
}
