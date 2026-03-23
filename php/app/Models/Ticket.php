<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Ticket extends Model
{
    protected $fillable = ['user_id', 'subject', 'message', 'status'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function messages()
    {
        return $this->hasMany(TicketMessage::class)->orderBy('created_at');
    }

    public function getStatusDisplayAttribute(): string
    {
        return $this->status === 'open' ? 'Открыт' : 'Закрыт';
    }

    public function getMessagesCountAttribute(): int
    {
        return $this->messages()->count();
    }

    public function getLastMessageAttribute(): ?TicketMessage
    {
        return $this->messages()->latest()->first();
    }

    public function getIsOpenAttribute(): bool
    {
        return $this->status === 'open';
    }
}
