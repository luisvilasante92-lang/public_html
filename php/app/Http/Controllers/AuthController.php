<?php

namespace App\Http\Controllers;

use App\Models\AuthToken;
use App\Models\Platform;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class AuthController extends Controller
{
    public function showLogin()
    {
        if (Auth::check()) {
            return redirect()->route('dashboard');
        }
        return view('auth.login');
    }

    public function login(Request $request)
    {
        if (Auth::check()) {
            return redirect()->route('dashboard');
        }

        $login = trim($request->input('login', ''));
        $password = $request->input('password', '');

        if (!$login || !$password) {
            return back()->with('error', 'Введите логин и пароль')->withInput();
        }

        $user = User::where('login', $login)->orWhere('email', $login)->first();

        if ($user && $user->checkPassword($password)) {
            if (!$user->is_active) {
                return back()->with('error', 'Ваш аккаунт заблокирован')->withInput();
            }
            Auth::login($user, true);
            return redirect()->route('dashboard')->with('success', "Добро пожаловать, {$user->display_name}!");
        }

        return back()->with('error', 'Неверный логин или пароль')->withInput();
    }

    public function logout(Request $request)
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();
        return redirect()->route('auth.login')->with('info', 'Вы вышли из системы');
    }

    public function forgotPassword()
    {
        return redirect()->route('auth.login')->with('support', 'Если вы забыли пароль, обратитесь в службу поддержки по электронной почте: support@lvr-music-publishing.ru. Либо на официальном сайте, в разделе «Контакты», в форме обратной связи.');
    }

    public function callback(Request $request)
    {
        $tokenStr = $request->query('token');
        if (!$tokenStr) {
            return redirect()->route('auth.login')->with('error', 'Токен авторизации не предоставлен');
        }

        $token = AuthToken::where('token', $tokenStr)->first();
        if (!$token) {
            return redirect()->route('auth.login')->with('error', 'Недействительный токен авторизации');
        }
        if ($token->is_expired) {
            return redirect()->route('auth.login')->with('error', 'Срок действия токена истек');
        }
        if ($token->is_used) {
            return redirect()->route('auth.login')->with('error', 'Токен уже был использован');
        }

        $user = User::find($token->user_id);
        if (!$user) {
            return redirect()->route('auth.login')->with('error', 'Пользователь не найден');
        }
        if (!$user->is_active) {
            return redirect()->route('auth.login')->with('error', 'Ваш аккаунт заблокирован');
        }

        $token->markAsUsed();
        Auth::login($user, true);

        return redirect()->route('dashboard')->with('success', "Добро пожаловать, {$user->display_name}!");
    }

    public function devLogin(Request $request)
    {
        if (!config('app.debug')) {
            return redirect()->route('auth.login');
        }
        if (Auth::check()) {
            return redirect()->route('dashboard');
        }

        if ($request->isMethod('post')) {
            $login = $request->input('login');
            $password = $request->input('password');
            $user = User::where('login', $login)->first();

            if ($user && $user->checkPassword($password)) {
                if (!$user->is_active) {
                    return back()->with('error', 'Ваш аккаунт заблокирован');
                }
                Auth::login($user, true);
                return redirect()->route('dashboard')->with('success', "Добро пожаловать, {$user->display_name}!");
            }
            return back()->with('error', 'Неверный логин или пароль');
        }

        return view('auth.dev_login');
    }

    public function devSetup()
    {
        if (!config('app.debug')) {
            return redirect()->route('auth.login');
        }
        if (User::count() > 0) {
            return redirect()->route('auth.dev-login')->with('info', 'Тестовые данные уже созданы');
        }

        User::create([
            'login' => 'admin',
            'email' => 'press.saidman@gmail.com',
            'name' => 'Администратор',
            'role' => 'admin',
            'password' => 'Admin123!',
        ]);
        User::create([
            'login' => 'artist',
            'email' => 'artist@example.com',
            'name' => 'Тестовый Артист',
            'role' => 'artist',
            'copyright' => '© 2026 Тестовый Артист',
            'password' => 'Artist123!',
        ]);
        User::create([
            'login' => 'label',
            'email' => 'label@example.com',
            'name' => 'Тестовый Лейбл',
            'role' => 'label',
            'copyright' => '© 2026 Test Records',
            'partner_code' => 'TEST001',
            'password' => 'Label123!',
        ]);

        foreach (Platform::getDefaultPlatforms() as $data) {
            Platform::create($data);
        }

        return redirect()->route('auth.dev-login')->with('success',
            'Тестовые данные созданы. Логины: admin, artist, label. Пароли: Admin123!, Artist123!, Label123!');
    }
}
