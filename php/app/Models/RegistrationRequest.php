<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class RegistrationRequest extends Model
{
    protected $fillable = [
        'code', 'email', 'artist_type', 'artist_name', 'start_year',
        'status', 'processed_at', 'processed_by', 'notes'
    ];

    protected $casts = ['processed_at' => 'datetime'];

    public function processor()
    {
        return $this->belongsTo(User::class, 'processed_by');
    }

    public static function generateCode(): string
    {
        return bin2hex(random_bytes(8));
    }

    public function getStatusDisplayAttribute(): string
    {
        return match ($this->status) {
            'pending' => 'На рассмотрении',
            'approved' => 'Одобрено',
            'rejected' => 'Отклонено',
            default => $this->status,
        };
    }

    public function getArtistTypeDisplayAttribute(): string
    {
        return match ($this->artist_type) {
            'artist' => 'Артист',
            'label' => 'Лейбл',
            default => $this->artist_type,
        };
    }
}
