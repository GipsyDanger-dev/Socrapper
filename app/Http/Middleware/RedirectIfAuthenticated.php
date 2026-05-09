<?php

namespace App\Http\Middleware;

use Illuminate\Auth\Middleware\RedirectIfAuthenticated;

class RedirectIfAuthenticated extends RedirectIfAuthenticated
{
    protected function redirectTo($request)
    {
        if (auth()->check()) {
            return route('dashboard');
        }
    }
}
