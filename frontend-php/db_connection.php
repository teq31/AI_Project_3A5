<?php
// frontend-php/db_connection.php

// Calea către fișierul bazei de date (va fi creat în folderul 'db' din rădăcină)
$db_file = __DIR__ . '/../db/smartest.db';

try {
    // Creăm conexiunea la SQLite
    $pdo = new PDO("sqlite:" . $db_file);
    // Setăm modul de eroare
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    // Setăm fetch mode implicit la array asociativ
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

    // --- CREARE TABELE AUTOMATĂ (dacă nu există) ---

    // 1. Tabel UTILIZATORI
    $pdo->exec("CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )");

    // 2. Tabel REZULTATE
    $pdo->exec("CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic TEXT NOT NULL,          -- ex: 'nash', 'minmax', 'csp'
        score INTEGER NOT NULL,       -- ex: 100, 85, 0
        feedback TEXT,                -- feedback-ul scurt de la AI
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )");

} catch (PDOException $e) {
    die("Eroare la conectarea cu baza de date: " . $e->getMessage());
}
?>