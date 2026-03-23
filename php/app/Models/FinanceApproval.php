<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class FinanceApproval extends Model
{
    protected $fillable = [
        'finance_id', 'user_id', 'contact_info', 'amount', 'card_number',
        'account_number', 'admin_comment', 'status'
    ];

    protected $casts = ['processed_at' => 'datetime'];

    public function finance()
    {
        return $this->belongsTo(Finance::class);
    }

    public function user()
    {
        return $this->belongsTo(User::class);
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

    public function getMaskedCardAttribute(): ?string
    {
        return $this->card_number && strlen($this->card_number) >= 4
            ? '**** **** **** ' . substr($this->card_number, -4)
            : null;
    }

    public function getAmountFormattedAttribute(): string
    {
        return number_format($this->amount, 2, '.', ' ') . ' ₽';
    }
}
