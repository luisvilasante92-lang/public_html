<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('releases', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('cover', 256)->nullable();
            $table->string('title', 256);
            $table->string('version', 100)->nullable();
            $table->string('artists', 512);
            $table->string('type', 20)->default('Single');
            $table->string('genre', 100);
            $table->date('release_date');
            $table->boolean('yandex_presave')->default(false);
            $table->string('partner_code', 50)->nullable();
            $table->string('copyright', 256)->nullable();
            $table->string('upc', 20)->nullable();
            $table->string('status', 20)->default('draft');
            $table->text('moderator_comment')->nullable();
            $table->json('platforms')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('releases');
    }
};
