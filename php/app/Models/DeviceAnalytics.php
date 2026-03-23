<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class DeviceAnalytics extends Model
{
    protected $fillable = ['release_analytics_id', 'device_type', 'streams', 'downloads'];

    public function releaseAnalytics()
    {
        return $this->belongsTo(ReleaseAnalytics::class);
    }

    public static function getDeviceTypes(): array
    {
        return ['Mobile', 'Desktop', 'Tablet', 'Smart TV'];
    }
}
