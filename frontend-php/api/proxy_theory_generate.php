<?php
header("Content-Type: application/json");

$topic_id = isset($_GET['topic_id']) ? $_GET['topic_id'] : '';
$question_type = isset($_GET['question_type']) ? $_GET['question_type'] : '';
$theory_file = isset($_GET['theory_file']) ? $_GET['theory_file'] : 'example_theory.json';
$seed = isset($_GET['seed']) ? $_GET['seed'] : '';

$url = "http://127.0.0.1:8000/theory/generate?theory_file=" . urlencode($theory_file);
if ($topic_id !== '') { $url .= "&topic_id=" . urlencode($topic_id); }
if ($question_type !== '') { $url .= "&question_type=" . urlencode($question_type); }
if ($seed !== '') { $url .= "&seed=" . urlencode($seed); }

// Use cURL for better error handling
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    echo json_encode([
        "error" => "Connection error: " . $error,
        "message" => "Nu s-a putut conecta la backend. Verifică că serverul FastAPI rulează pe http://127.0.0.1:8000"
    ]);
    http_response_code(500);
    exit;
}

if ($httpCode !== 200) {
    echo json_encode([
        "error" => "HTTP Error $httpCode",
        "message" => "Backend-ul a returnat o eroare. Verifică log-urile serverului."
    ]);
    http_response_code($httpCode);
    exit;
}

// Check if response is valid JSON
$decoded = json_decode($response, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode([
        "error" => "Invalid JSON response",
        "message" => "Backend-ul a returnat un răspuns invalid: " . substr($response, 0, 200),
        "raw_response" => substr($response, 0, 500)
    ]);
    http_response_code(500);
    exit;
}

echo $response;
?>

