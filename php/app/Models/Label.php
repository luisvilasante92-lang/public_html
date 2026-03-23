<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;


class Label extends Model
{
    protected $fillable = ['user_id', 'name', 'copyright'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function getReleasesCountAttribute(): int
    {
        return Release::where('copyright', $this->copyright)->count();
    }
}
