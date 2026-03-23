<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->string('login', 80)->unique();
            $table->string('password', 256);
            $table->string('email', 120)->unique();
            $table->string('role', 20)->default('artist');
            $table->string('name', 120);
            $table->string('avatar', 256)->nullable();
            $table->string('copyright', 256)->nullable();
            $table->string('partner_code', 50)->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('users');
    }
};
