<?php
header("Content-Type: application/json");

$data = json_decode(file_get_contents('php://input'), true);

$payload = $data['payload'] ?? [];
$answer = $data['answer'] ?? '';

$postData = json_encode([
    'payload' => $payload,
    'answer' => $answer
]);

$options = [
    'http' => [
        'method' => 'POST',
        'header' => 'Content-Type: application/json',
        'content' => $postData
    ]
];

$context = stream_context_create($options);
$url = "http://127.0.0.1:8000/theory/grade";
echo file_get_contents($url, false, $context);
?>

