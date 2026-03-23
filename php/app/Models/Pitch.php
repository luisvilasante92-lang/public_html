<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Pitch extends Model
{
    protected $fillable = ['user_id', 'release_id', 'title', 'artists', 'genre', 'comment', 'status'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function release()
    {
        return $this->belongsTo(Release::class);
    }

    public function getStatusDisplayAttribute(): string
    {
        return match ($this->status) {
            'pending' => 'На рассмотрении',
            'in_review' => 'В работе',
            'approved' => 'Одобрено',
            'rejected' => 'Отклонено',
            default => $this->status,
        };
    }

    public function getStatusClassAttribute(): string
    {
        return match ($this->status) {
            'pending' => 'status-pending',
            'in_review' => 'status-review',
            'approved' => 'status-approved',
            'rejected' => 'status-rejected',
            default => '',
        };
    }
}
