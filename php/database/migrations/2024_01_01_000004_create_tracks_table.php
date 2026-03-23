<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('tracks', function (Blueprint $table) {
            $table->id();
            $table->foreignId('release_id')->constrained()->cascadeOnDelete();
            $table->string('wav_file', 256);
            $table->string('title', 256);
            $table->string('version', 100)->nullable();
            $table->string('artists', 512);
            $table->string('composers', 512)->nullable();
            $table->string('authors', 512)->nullable();
            $table->boolean('explicit')->default(false);
            $table->string('language', 50)->nullable();
            $table->string('isrc', 20)->nullable();
            $table->text('lyrics')->nullable();
            $table->integer('track_order')->default(1);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('tracks');
    }
};
