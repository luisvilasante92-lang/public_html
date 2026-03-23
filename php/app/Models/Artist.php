<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Artist extends Model
{
    protected $fillable = ['user_id', 'name', 'role'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public static function getRoles(): array
    {
        return ['Исполнитель', 'Композитор', 'Автор'];
    }
}
