<?php
// frontend-php/login.php
session_start();
require 'db_connection.php';

$message = '';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $user = trim($_POST['username']);
    $pass = trim($_POST['password']);

    $stmt = $pdo->prepare("SELECT id, username, password FROM users WHERE username = ?");
    $stmt->execute([$user]);
    $user_data = $stmt->fetch();

    if ($user_data && password_verify($pass, $user_data['password'])) {
        // Logare cu succes -> Salvăm în sesiune
        $_SESSION['user_id'] = $user_data['id'];
        $_SESSION['username'] = $user_data['username'];
        
        header("Location: index.php");
        exit;
    } else {
        $message = "Nume sau parolă incorectă!";
    }
}
?>

<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Login - SmarTest</title>
    <link rel="stylesheet" href="css/style.css">
    <style>
        .auth-container { max-width: 400px; margin: 100px auto; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; color: white; text-align: center; }
        input { width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: none; }
        button { width: 100%; padding: 10px; background: #0984e3; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #74b9ff; }
        .error { color: #ff7675; }
    </style>
</head>
<body>
    <div class="auth-container">
        <h2>Autentificare</h2>
        <?php if(isset($_GET['success'])): ?>
            <p style="color: #55efc4;">Cont creat! Te poți loga.</p>
        <?php endif; ?>
        <?php if($message): ?>
            <p class="error"><?= $message ?></p>
        <?php endif; ?>
        <form method="POST">
            <input type="text" name="username" placeholder="Nume utilizator" required>
            <input type="password" name="password" placeholder="Parolă" required>
            <button type="submit">Intră în cont</button>
        </form>
        <p>Nu ai cont? <a href="register.php" style="color: #74b9ff;">Înregistrează-te</a></p>
    </div>
</body>
</html>