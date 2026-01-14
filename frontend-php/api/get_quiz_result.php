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
$quiz_id = isset($_GET['id']) ? intval($_GET['id']) : 0;

if ($quiz_id <= 0) {
    http_response_code(400);
    echo json_encode(["error" => "Missing or invalid id"]);
    exit;
}

$stmt = $pdo->prepare("SELECT id, score, question_count, payload, created_at FROM quizzes WHERE id = ? AND user_id = ?");
$stmt->execute([$quiz_id, $user_id]);
$row = $stmt->fetch();

if (!$row) {
    http_response_code(404);
    echo json_encode(["error" => "Quiz not found"]);
    exit;
}

$payload = null;
if (!empty($row['payload'])) {
    $decoded = json_decode($row['payload'], true);
    if (json_last_error() === JSON_ERROR_NONE) {
        $payload = $decoded;
    }
}

echo json_encode([
    'id' => (int)$row['id'],
    'score' => (float)$row['score'],
    'question_count' => (int)$row['question_count'],
    'created_at' => $row['created_at'],
    'payload' => $payload,
]);
