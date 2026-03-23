<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class LinkClick extends Model
{
    protected $fillable = ['link_code', 'platform', 'ip_address'];

    protected $casts = ['clicked_at' => 'datetime'];

    public $timestamps = false;

    protected static function booted()
    {
        static::creating(fn ($m) => $m->clicked_at ??= now());
    }

    public function smartLink()
    {
        return $this->belongsTo(SmartLink::class, 'link_code', 'link_code');
    }
}
