<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('auth_tokens', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('token', 256)->unique();
            $table->datetime('expires_at');
            $table->boolean('is_used')->default(false);
            $table->timestamps();
        });

        Schema::create('registration_requests', function (Blueprint $table) {
            $table->id();
            $table->string('code', 32)->unique();
            $table->string('email', 120);
            $table->string('artist_type', 50);
            $table->string('artist_name', 256);
            $table->integer('start_year')->nullable();
            $table->string('status', 20)->default('pending');
            $table->datetime('processed_at')->nullable();
            $table->foreignId('processed_by')->nullable()->constrained('users')->nullOnDelete();
            $table->text('notes')->nullable();
            $table->timestamps();
        });

        Schema::create('labels', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('name', 256);
            $table->string('copyright', 256);
            $table->timestamps();
        });

        Schema::create('artists', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('name', 256);
            $table->string('role', 50)->default('Исполнитель');
            $table->timestamps();
        });

        Schema::create('finances', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->integer('quarter');
            $table->integer('year');
            $table->float('amount')->default(0);
            $table->string('file_path', 256)->nullable();
            $table->foreignId('uploaded_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamps();
        });

        Schema::create('finance_approvals', function (Blueprint $table) {
            $table->id();
            $table->foreignId('finance_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('contact_info', 256)->nullable();
            $table->float('amount');
            $table->string('card_number', 20)->nullable();
            $table->string('account_number', 30)->nullable();
            $table->text('admin_comment')->nullable();
            $table->string('status', 20)->default('pending');
            $table->datetime('processed_at')->nullable();
            $table->timestamps();
        });

        Schema::create('news', function (Blueprint $table) {
            $table->id();
            $table->string('title', 256);
            $table->text('content');
            $table->string('cover_image', 256)->nullable();
            $table->foreignId('author_id')->constrained('users')->cascadeOnDelete();
            $table->timestamps();
        });

        Schema::create('tickets', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('subject', 256);
            $table->text('message');
            $table->string('status', 20)->default('open');
            $table->timestamps();
        });

        Schema::create('ticket_messages', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->text('message');
            $table->boolean('is_admin')->default(false);
            $table->timestamps();
        });

        Schema::create('notifications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('kind', 32);
            $table->string('title', 256);
            $table->text('message')->nullable();
            $table->foreignId('ticket_id')->nullable()->constrained()->nullOnDelete();
            $table->boolean('is_read')->default(false);
            $table->timestamps();
        });

        Schema::create('contracts', function (Blueprint $table) {
            $table->id();
            $table->string('title', 256);
            $table->string('original_filename', 256);
            $table->string('file_path', 256);
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('admin_id')->nullable()->constrained('users')->nullOnDelete();
            $table->datetime('sign_deadline')->nullable();
            $table->string('status', 20)->default('pending');
            $table->string('signed_filename', 256)->nullable();
            $table->string('signed_file_path', 256)->nullable();
            $table->datetime('signed_at')->nullable();
            $table->timestamps();
        });

        Schema::create('smart_links', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('release_id')->constrained()->cascadeOnDelete();
            $table->string('link_code', 32)->unique();
            $table->string('custom_name', 256)->nullable();
            $table->json('platform_links')->nullable();
            $table->string('theme', 10)->default('dark');
            $table->timestamps();
        });

        Schema::create('link_visits', function (Blueprint $table) {
            $table->id();
            $table->string('link_code', 32);
            $table->string('ip_address', 45)->nullable();
            $table->string('user_agent', 512)->nullable();
            $table->datetime('visited_at')->nullable();
            $table->foreign('link_code')->references('link_code')->on('smart_links')->cascadeOnDelete();
        });

        Schema::create('link_clicks', function (Blueprint $table) {
            $table->id();
            $table->string('link_code', 32);
            $table->string('platform', 50);
            $table->string('ip_address', 45)->nullable();
            $table->datetime('clicked_at')->nullable();
            $table->foreign('link_code')->references('link_code')->on('smart_links')->cascadeOnDelete();
        });

        Schema::create('release_analytics', function (Blueprint $table) {
            $table->id();
            $table->foreignId('release_id')->constrained()->cascadeOnDelete();
            $table->integer('month')->nullable();
            $table->integer('week')->nullable();
            $table->integer('year');
            $table->integer('streams')->default(0);
            $table->integer('downloads')->default(0);
            $table->float('revenue')->default(0);
            $table->timestamps();
        });

        Schema::create('device_analytics', function (Blueprint $table) {
            $table->id();
            $table->foreignId('release_analytics_id')->constrained('release_analytics')->cascadeOnDelete();
            $table->string('device_type', 50);
            $table->integer('streams')->default(0);
            $table->integer('downloads')->default(0);
        });

        Schema::create('platform_analytics', function (Blueprint $table) {
            $table->id();
            $table->foreignId('release_analytics_id')->constrained('release_analytics')->cascadeOnDelete();
            $table->string('platform_name', 100);
            $table->integer('streams')->default(0);
            $table->integer('downloads')->default(0);
            $table->float('revenue')->default(0);
        });

        Schema::create('pitches', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('release_id')->nullable()->constrained()->nullOnDelete();
            $table->string('title', 256);
            $table->string('artists', 512);
            $table->string('genre', 100)->nullable();
            $table->text('comment')->nullable();
            $table->string('status', 20)->default('pending');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pitches');
        Schema::dropIfExists('platform_analytics');
        Schema::dropIfExists('device_analytics');
        Schema::dropIfExists('release_analytics');
        Schema::dropIfExists('link_clicks');
        Schema::dropIfExists('link_visits');
        Schema::dropIfExists('smart_links');
        Schema::dropIfExists('contracts');
        Schema::dropIfExists('notifications');
        Schema::dropIfExists('ticket_messages');
        Schema::dropIfExists('tickets');
        Schema::dropIfExists('news');
        Schema::dropIfExists('finance_approvals');
        Schema::dropIfExists('finances');
        Schema::dropIfExists('artists');
        Schema::dropIfExists('labels');
        Schema::dropIfExists('registration_requests');
        Schema::dropIfExists('auth_tokens');
    }
};
