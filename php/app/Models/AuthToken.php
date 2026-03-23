<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AuthToken extends Model
{
    protected $fillable = ['user_id', 'token', 'expires_at', 'is_used'];

    protected $casts = [
        'expires_at' => 'datetime',
        'is_used' => 'boolean',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public static function generateToken(): string
    {
        return bin2hex(random_bytes(32));
    }

    public static function createForUser(int $userId, int $expiresInMinutes = 30): self
    {
        return self::create([
            'user_id' => $userId,
            'token' => self::generateToken(),
            'expires_at' => now()->addMinutes($expiresInMinutes),
        ]);
    }

    public function getIsValidAttribute(): bool
    {
        return !$this->is_used && now()->lt($this->expires_at);
    }

    public function getIsExpiredAttribute(): bool
    {
        return now()->gte($this->expires_at);
    }

    public function markAsUsed(): void
    {
        $this->update(['is_used' => true]);
    }
}
