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
        payload TEXT,                 -- JSON cu payload-ul complet al testului (pentru reluare)
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )");

    // Migrare simplă: adăugăm coloana payload dacă tabela results există deja fără ea
    try {
        $cols = $pdo->query("PRAGMA table_info(results)")->fetchAll();
        $hasPayload = false;
        foreach ($cols as $col) {
            if (isset($col['name']) && $col['name'] === 'payload') {
                $hasPayload = true;
                break;
            }
        }
        if (!$hasPayload) {
            $pdo->exec("ALTER TABLE results ADD COLUMN payload TEXT");
        }
    } catch (PDOException $e) {
        // Ignorăm erorile de migrare, aplicația va continua să funcționeze
    }

    // 3. Tabel QUIZZES (pentru quiz-uri complete, nu doar întrebări individuale)
    $pdo->exec("CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        score REAL NOT NULL,          -- scorul mediu al quiz-ului
        question_count INTEGER NOT NULL,
        time_spent INTEGER DEFAULT 0, -- timpul petrecut în secunde
        payload TEXT NOT NULL,        -- JSON cu întreaga configurație și întrebările quiz-ului
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )");

    // Migrare: adăugăm coloana time_spent dacă nu există
    try {
        $cols = $pdo->query("PRAGMA table_info(quizzes)")->fetchAll();
        $hasTimeSpent = false;
        foreach ($cols as $col) {
            if (isset($col['name']) && $col['name'] === 'time_spent') {
                $hasTimeSpent = true;
                break;
            }
        }
        if (!$hasTimeSpent) {
            $pdo->exec("ALTER TABLE quizzes ADD COLUMN time_spent INTEGER DEFAULT 0");
        }
    } catch (PDOException $e) {
        // Ignorăm erorile de migrare
    }

} catch (PDOException $e) {
    die("Eroare la conectarea cu baza de date: " . $e->getMessage());
}
?>