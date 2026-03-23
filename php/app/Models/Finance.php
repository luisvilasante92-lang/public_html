<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Finance extends Model
{
    protected $fillable = ['user_id', 'quarter', 'year', 'amount', 'file_path', 'uploaded_by'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function uploader()
    {
        return $this->belongsTo(User::class, 'uploaded_by');
    }

    public function approval()
    {
        return $this->hasOne(FinanceApproval::class);
    }

    public function getQuarterDisplayAttribute(): string
    {
        $quarters = ['I', 'II', 'III', 'IV'];
        return $quarters[$this->quarter - 1] . ' квартал ' . $this->year;
    }

    public function getFileUrlAttribute(): ?string
    {
        return $this->file_path ? '/uploads/finances/' . $this->file_path : null;
    }

    public function getAmountFormattedAttribute(): string
    {
        return number_format($this->amount, 2, '.', ' ') . ' ₽';
    }

    public function getHasApprovalRequestAttribute(): bool
    {
        return $this->approval()->exists();
    }
}
