<?php
header("Content-Type: application/json");

$data = json_decode(file_get_contents('php://input'), true);

$payload = $data['payload'] ?? [];
$answer = $data['answer'] ?? '';

$postData = json_encode([
    'payload' => $payload,
    'answer' => $answer
]);

$url = "http://127.0.0.1:8000/theory/grade";

// Use cURL for better error handling
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    echo json_encode([
        "error" => "Connection error: " . $error,
        "correct" => false,
        "score" => 0,
        "feedback" => "Nu s-a putut conecta la backend. Verifică că serverul FastAPI rulează."
    ]);
    http_response_code(500);
    exit;
}

if ($httpCode !== 200) {
    echo json_encode([
        "error" => "HTTP Error $httpCode",
        "correct" => false,
        "score" => 0,
        "feedback" => "Backend-ul a returnat o eroare."
    ]);
    http_response_code($httpCode);
    exit;
}

// Check if response is valid JSON
$decoded = json_decode($response, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode([
        "error" => "Invalid JSON response",
        "correct" => false,
        "score" => 0,
        "feedback" => "Backend-ul a returnat un răspuns invalid."
    ]);
    http_response_code(500);
    exit;
}

echo $response;
?>

