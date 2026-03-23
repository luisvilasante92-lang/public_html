<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\ReleaseController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return auth()->check() ? redirect()->route('dashboard') : redirect()->route('auth.login');
});

Route::controller(AuthController::class)->group(function () {
    Route::get('/login', 'showLogin')->name('auth.login');
    Route::post('/login', 'login');
    Route::get('/logout', 'logout')->middleware('auth')->name('auth.logout');
    Route::get('/login/forgot-password', 'forgotPassword')->name('auth.forgot');
    Route::get('/auth/callback', 'callback')->name('auth.callback');
    Route::get('/dev-login', 'devLogin')->name('auth.dev-login');
    Route::post('/dev-login', 'devLogin');
    Route::get('/dev-setup', 'devSetup')->name('auth.dev-setup');
});

Route::middleware(['auth'])->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');

    Route::controller(ReleaseController::class)->prefix('releases')->name('releases.')->group(function () {
        Route::get('/', 'index')->name('index');
        Route::get('/create', 'create')->name('create');
        Route::post('/', 'store')->name('store');
        Route::get('/export/csv', 'export')->name('export');
        Route::get('/{id}', 'view')->name('view');
        Route::get('/{id}/edit', 'edit')->name('edit');
        Route::post('/{id}', 'update')->name('update');
        Route::post('/{id}/submit', 'submit')->name('submit');
        Route::post('/{id}/delete', 'delete')->name('delete');
    });

    Route::get('/profile', fn () => redirect()->route('dashboard'))->name('profile');
});
