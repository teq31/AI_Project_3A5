<?php
session_start();
require_once __DIR__ . '/../db_connection.php';

header('Content-Type: application/json');

if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(["error" => "Unauthorized"]);
    exit;
}

$user_id = $_SESSION['user_id'];

// Primim ID-ul quiz-ului de șters
$raw = file_get_contents('php://input');
$data = json_decode($raw, true);

if (!isset($data['id']) || !is_numeric($data['id'])) {
    http_response_code(400);
    echo json_encode(["error" => "Missing or invalid quiz ID"]);
    exit;
}

$quiz_id = intval($data['id']);

try {
    // Verificăm că quiz-ul aparține utilizatorului curent
    $stmt = $pdo->prepare("SELECT user_id FROM quizzes WHERE id = ?");
    $stmt->execute([$quiz_id]);
    $quiz = $stmt->fetch();

    if (!$quiz) {
        http_response_code(404);
        echo json_encode(["error" => "Quiz not found"]);
        exit;
    }

    if ($quiz['user_id'] != $user_id) {
        http_response_code(403);
        echo json_encode(["error" => "Forbidden - not your quiz"]);
        exit;
    }

    // Ștergem quiz-ul
    $stmt = $pdo->prepare("DELETE FROM quizzes WHERE id = ?");
    $stmt->execute([$quiz_id]);

    echo json_encode([
        "success" => true,
        "message" => "Quiz șters cu succes"
    ]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(["error" => "Database error: " . $e->getMessage()]);
}
