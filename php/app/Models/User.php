<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Support\Facades\Hash;

class User extends Authenticatable
{
    use HasFactory, Notifiable;

    protected $fillable = [
        'login', 'password', 'email', 'role', 'name', 'avatar', 'copyright',
        'partner_code', 'is_active'
    ];

    protected $hidden = ['password'];

    protected $casts = [
        'is_active' => 'boolean',
        'created_at' => 'datetime',
    ];

    public function setPasswordAttribute($value): void
    {
        $this->attributes['password'] = Hash::make($value);
    }

    public function checkPassword(string $password): bool
    {
        return password_verify($password, $this->password);
    }

    public function getIsAdminAttribute(): bool
    {
        return $this->role === 'admin';
    }

    public function getIsLabelAttribute(): bool
    {
        return $this->role === 'label';
    }

    public function getIsArtistAttribute(): bool
    {
        return $this->role === 'artist';
    }

    public function getDisplayNameAttribute(): string
    {
        return $this->name ?: $this->login;
    }

    public function getAvatarUrlAttribute(): string
    {
        return $this->avatar
            ? asset('storage/avatars/' . $this->avatar)
            : asset('static/img/default-avatar.png');
    }

    public function getDefaultCopyright(): string
    {
        return $this->copyright ?: '© ' . date('Y') . ' ' . $this->name;
    }

    public function releases()
    {
        return $this->hasMany(Release::class);
    }

    public function finances()
    {
        return $this->hasMany(Finance::class);
    }

    public function tickets()
    {
        return $this->hasMany(Ticket::class);
    }

    public function contracts()
    {
        return $this->hasMany(Contract::class);
    }

    public function labels()
    {
        return $this->hasMany(Label::class);
    }

    public function artists()
    {
        return $this->hasMany(Artist::class);
    }

    public function smartLinks()
    {
        return $this->hasMany(SmartLink::class);
    }

    public function news()
    {
        return $this->hasMany(News::class, 'author_id');
    }

    public function notifications()
    {
        return $this->hasMany(Notification::class);
    }
}
