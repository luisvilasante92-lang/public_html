<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ReleaseAnalytics extends Model
{
    protected $fillable = ['release_id', 'month', 'week', 'year', 'streams', 'downloads', 'revenue'];

    public function release()
    {
        return $this->belongsTo(Release::class);
    }

    public function deviceAnalytics()
    {
        return $this->hasMany(DeviceAnalytics::class);
    }

    public function platformAnalytics()
    {
        return $this->hasMany(PlatformAnalytics::class);
    }

    public function getPeriodDisplayAttribute(): string
    {
        if ($this->month) {
            $months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
            return $months[$this->month - 1] . ' ' . $this->year;
        }
        if ($this->week) {
            return "Неделя {$this->week}, {$this->year}";
        }
        return (string) $this->year;
    }

    public function getPeriodTypeAttribute(): string
    {
        return $this->month ? 'monthly' : ($this->week ? 'weekly' : 'yearly');
    }
}
