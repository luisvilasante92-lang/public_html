<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Platform extends Model
{
    protected $fillable = ['name', 'category', 'is_active', 'warning_message', 'sort_order', 'icon'];

    protected $casts = ['is_active' => 'boolean'];

    public function getCategoryDisplayAttribute(): string
    {
        return match ($this->category) {
            'streaming' => 'Стриминговые сервисы',
            'social' => 'Социальные сети',
            'video' => 'Видео платформы',
            'database' => 'Музыкальные базы',
            'store' => 'Магазины',
            'radio' => 'Радио',
            'dj' => 'DJ платформы',
            'international' => 'Международные',
            default => $this->category,
        };
    }

    public static function getDefaultPlatforms(): array
    {
        return [
            ['name' => 'Spotify', 'category' => 'streaming', 'sort_order' => 1],
            ['name' => 'Apple Music', 'category' => 'streaming', 'sort_order' => 2],
            ['name' => 'Яндекс Музыка', 'category' => 'streaming', 'sort_order' => 3],
            ['name' => 'VK Music', 'category' => 'streaming', 'sort_order' => 4],
            ['name' => 'YouTube Music', 'category' => 'streaming', 'sort_order' => 5],
            ['name' => 'Deezer', 'category' => 'streaming', 'sort_order' => 6],
            ['name' => 'Zvooq', 'category' => 'streaming', 'sort_order' => 7],
            ['name' => 'SberZvuk', 'category' => 'streaming', 'sort_order' => 8],
            ['name' => 'Tidal', 'category' => 'streaming', 'sort_order' => 9],
            ['name' => 'Amazon Music', 'category' => 'streaming', 'sort_order' => 10],
            ['name' => 'TikTok', 'category' => 'social', 'sort_order' => 20],
            ['name' => 'Instagram/Facebook', 'category' => 'social', 'sort_order' => 21],
            ['name' => 'Snapchat', 'category' => 'social', 'sort_order' => 22],
            ['name' => 'YouTube Content ID', 'category' => 'video', 'sort_order' => 30],
            ['name' => 'iTunes', 'category' => 'store', 'sort_order' => 40],
            ['name' => 'Google Play', 'category' => 'store', 'sort_order' => 41],
            ['name' => 'Shazam', 'category' => 'database', 'sort_order' => 50],
            ['name' => 'Genius', 'category' => 'database', 'sort_order' => 51],
        ];
    }
}
