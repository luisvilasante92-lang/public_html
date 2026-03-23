<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class LinkVisit extends Model
{
    protected $fillable = ['link_code', 'ip_address', 'user_agent'];

    protected $casts = ['visited_at' => 'datetime'];

    public $timestamps = false;

    protected static function booted()
    {
        static::creating(fn ($m) => $m->visited_at ??= now());
    }

    public function smartLink()
    {
        return $this->belongsTo(SmartLink::class, 'link_code', 'link_code');
    }
}
