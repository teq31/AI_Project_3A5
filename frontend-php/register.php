<?php
// frontend-php/register.php
session_start();
require 'db_connection.php';

$message = '';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $user = trim($_POST['username']);
    $pass = trim($_POST['password']);

    if ($user && $pass) {
        // Verificăm dacă userul există deja
        $stmt = $pdo->prepare("SELECT id FROM users WHERE username = ?");
        $stmt->execute([$user]);
        
        if ($stmt->fetch()) {
            $message = "Acest nume de utilizator este deja luat!";
        } else {
            // Hash-uim parola pentru securitate
            $hashed_pass = password_hash($pass, PASSWORD_DEFAULT);
            
            $stmt = $pdo->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
            if ($stmt->execute([$user, $hashed_pass])) {
                header("Location: login.php?success=1");
                exit;
            } else {
                $message = "Eroare la înregistrare.";
            }
        }
    } else {
        $message = "Completează toate câmpurile!";
    }
}
?>

<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Înregistrare - SmarTest</title>
    <link rel="stylesheet" href="css/style.css"> <style>
        .auth-container { max-width: 400px; margin: 100px auto; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; color: white; text-align: center; }
        input { width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: none; }
        button { width: 100%; padding: 10px; background: #6c5ce7; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #a29bfe; }
        .error { color: #ff7675; }
    </style>
</head>
<body>
    <div class="auth-container">
        <h2>Crează Cont</h2>
        <?php if($message): ?>
            <p class="error"><?= $message ?></p>
        <?php endif; ?>
        <form method="POST">
            <input type="text" name="username" placeholder="Nume utilizator" required>
            <input type="password" name="password" placeholder="Parolă" required>
            <button type="submit">Înregistrează-te</button>
        </form>
        <p>Ai deja cont? <a href="login.php" style="color: #a29bfe;">Loghează-te</a></p>
    </div>
</body>
</html>