<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TicketMessage extends Model
{
    protected $fillable = ['ticket_id', 'user_id', 'message', 'is_admin'];

    public function ticket()
    {
        return $this->belongsTo(Ticket::class);
    }

    public function author()
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function getTimeFormattedAttribute(): string
    {
        return $this->created_at->format('d.m.Y H:i');
    }
}
