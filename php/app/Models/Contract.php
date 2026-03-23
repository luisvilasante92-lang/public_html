<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Contract extends Model
{
    protected $fillable = [
        'title', 'original_filename', 'file_path', 'user_id', 'admin_id',
        'sign_deadline', 'status', 'signed_filename', 'signed_file_path', 'signed_at'
    ];

    protected $casts = [
        'sign_deadline' => 'datetime',
        'signed_at' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function admin()
    {
        return $this->belongsTo(User::class, 'admin_id');
    }

    public function getFileUrlAttribute(): string
    {
        return '/uploads/contracts/original/' . $this->file_path;
    }

    public function getSignedFileUrlAttribute(): ?string
    {
        return $this->signed_file_path
            ? '/uploads/contracts/signed/' . $this->signed_file_path
            : null;
    }

    public function getStatusDisplayAttribute(): string
    {
        return match ($this->status) {
            'pending' => 'Ожидает подписания',
            'signed' => 'Подписан',
            'expired' => 'Просрочен',
            'rejected' => 'Отклонен',
            default => $this->status,
        };
    }

    public function getIsExpiredAttribute(): bool
    {
        return $this->sign_deadline && $this->status === 'pending' && now()->gt($this->sign_deadline);
    }

    public function getDaysUntilDeadlineAttribute(): ?int
    {
        if ($this->sign_deadline && $this->status === 'pending') {
            return max(0, (int) now()->diffInDays($this->sign_deadline, false) * -1);
        }
        return null;
    }

    public function getDeadlineFormattedAttribute(): string
    {
        return $this->sign_deadline ? $this->sign_deadline->format('d.m.Y') : '-';
    }

    public function checkAndUpdateStatus(): bool
    {
        if ($this->is_expired && $this->status === 'pending') {
            $this->update(['status' => 'expired']);
            return true;
        }
        return false;
    }
}
