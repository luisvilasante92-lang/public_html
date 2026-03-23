<?php

use Illuminate\Support\Facades\Facade;

return [
    'name' => env('APP_NAME', 'LVR Music Publishing'),
    'env' => env('APP_ENV', 'production'),
    'debug' => (bool) env('APP_DEBUG', false),
    'url' => env('APP_URL', 'http://localhost'),
    'timezone' => 'Europe/Moscow',
    'locale' => 'ru',
    'fallback_locale' => 'en',
    'faker_locale' => 'ru_RU',
    'key' => env('APP_KEY'),
    'cipher' => 'AES-256-CBC',
    'maintenance' => [
        'driver' => 'file',
    ],
    'smart_link_base_url' => env('SMART_LINK_BASE_URL', 'https://lnk.luisv-records.ru/link'),
    'providers' => require __DIR__.'/../bootstrap/providers.php',
];
