<?php
session_start();
require_once __DIR__ . '/../db_connection.php';

header('Content-Type: application/json');

if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(["error" => "Unauthorized"]);
    exit;
}

$json_input = file_get_contents('php://input');

$url = "http://127.0.0.1:8000/theory/grade";

// Use cURL for better error handling
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $json_input);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Content-Length: ' . strlen($json_input)
]);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

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
    // Try to decode response to get more details
    $responseData = json_decode($response, true);
    $errorMsg = "HTTP Error $httpCode";
    if ($responseData && isset($responseData['error'])) {
        $errorMsg = $responseData['error'];
    } elseif ($responseData && isset($responseData['detail'])) {
        $errorMsg = $responseData['detail'];
    }
    
    echo json_encode([
        "error" => $errorMsg,
        "correct" => false,
        "score" => 0,
        "feedback" => "Backend-ul a returnat o eroare."
    ]);
    http_response_code($httpCode);
    exit;
}

// Check if response is valid JSON
$result = json_decode($response, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode([
        "error" => "Invalid JSON response: " . json_last_error_msg(),
        "correct" => false,
        "score" => 0,
        "feedback" => "Backend-ul a returnat un răspuns invalid."
    ]);
    http_response_code(500);
    exit;
}

// Save to database if we have a valid result
if ($httpCode === 200 && $result && isset($result['score'])) {
    $original = json_decode($json_input, true);
    $payloadJson = null;
    if (is_array($original) && isset($original['payload'])) {
        $payloadJson = json_encode($original['payload']);
    }
    
    try {
        $stmt = $pdo->prepare("INSERT INTO results (user_id, topic, score, feedback, payload) VALUES (?, ?, ?, ?, ?)");
        $stmt->execute([
            $_SESSION['user_id'],
            'Teorie',
            $result['score'],
            $result['feedback'] ?? '',
            $payloadJson
        ]);
    } catch (PDOException $e) {
        // Silently fail if DB insert fails - don't break the response
    }
}

http_response_code($httpCode);
echo $response;
?>