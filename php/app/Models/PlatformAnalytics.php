<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PlatformAnalytics extends Model
{
    protected $fillable = ['release_analytics_id', 'platform_name', 'streams', 'downloads', 'revenue'];

    public function releaseAnalytics()
    {
        return $this->belongsTo(ReleaseAnalytics::class);
    }

    public static function getMainPlatforms(): array
    {
        return ['Spotify', 'Apple Music', 'YouTube Music', 'VK Music', 'Яндекс Музыка'];
    }
}
