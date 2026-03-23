<?php

namespace App\Http\Controllers;

use App\Models\Finance;
use App\Models\News;
use App\Models\Release;
use Illuminate\Http\Request;

class DashboardController extends Controller
{
    public function index(Request $request)
    {
        $user = $request->user();
        $latestNews = News::orderBy('created_at', 'desc')->first();
        $currentYear = (int) date('Y');
        $currentQuarter = (int) ceil(date('n') / 3);

        $quartersData = [];
        for ($q = 1; $q <= 4; $q++) {
            $finance = null;
            if (!$user->is_admin) {
                $finance = Finance::where('user_id', $user->id)
                    ->where('year', $currentYear)
                    ->where('quarter', $q)
                    ->first();
            }
            $quartersData[] = [
                'quarter' => $q,
                'quarter_roman' => ['I', 'II', 'III', 'IV'][$q - 1],
                'amount' => $finance?->amount,
                'has_data' => $finance !== null,
            ];
        }

        $stats = [];
        if (!$user->is_admin) {
            $stats = [
                'total_releases' => Release::where('user_id', $user->id)->count(),
                'approved_releases' => Release::where('user_id', $user->id)->where('status', 'approved')->count(),
                'pending_releases' => Release::where('user_id', $user->id)->where('status', 'moderation')->count(),
            ];
        }

        return view('dashboard.index', [
            'latest_news' => $latestNews,
            'quarters_data' => $quartersData,
            'current_quarter' => $currentQuarter,
            'current_year' => $currentYear,
            'stats' => $stats,
        ]);
    }
}
