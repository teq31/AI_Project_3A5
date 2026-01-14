<?php
session_start();
require_once __DIR__ . '/../db_connection.php';

header('Content-Type: application/json');

if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(["error" => "Unauthorized"]);
    exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) {
    http_response_code(400);
    echo json_encode(["error" => "Invalid JSON body"]);
    exit;
}

$user_id = $_SESSION['user_id'];
$score = isset($data['score']) ? floatval($data['score']) : null;
$question_count = isset($data['question_count']) ? intval($data['question_count']) : null;
$time_spent = isset($data['time_spent']) ? intval($data['time_spent']) : 0;

if ($score === null || $question_count === null || $question_count <= 0) {
    http_response_code(400);
    echo json_encode(["error" => "Missing score or question_count"]);
    exit;
}

// Stocăm toată structura primită (config + questions) în payload
$payloadJson = json_encode([
    'config' => $data['config'] ?? null,
    'questions' => $data['questions'] ?? null,
]);

try {
    $stmt = $pdo->prepare("INSERT INTO quizzes (user_id, score, question_count, time_spent, payload) VALUES (?, ?, ?, ?, ?)");
    $stmt->execute([$user_id, $score, $question_count, $time_spent, $payloadJson]);
    $quizId = $pdo->lastInsertId();

    // Luăm created_at pentru feedback, dar nu este obligatoriu
    $stmt2 = $pdo->prepare("SELECT created_at FROM quizzes WHERE id = ?");
    $stmt2->execute([$quizId]);
    $row = $stmt2->fetch();

    echo json_encode([
        'id' => (int)$quizId,
        'score' => $score,
        'question_count' => $question_count,
        'created_at' => $row['created_at'] ?? null,
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(["error" => "DB error: " . $e->getMessage()]);
}
