<?php
header("Content-Type: application/json");

$url = "http://127.0.0.1:8000/chat/ask";
$json_input = file_get_contents('php://input');

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $json_input);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Content-Length: ' . strlen($json_input)
]);
curl_setopt($ch, CURLOPT_TIMEOUT, 15);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    echo json_encode([
        "error" => "Connection error: " . $error . ". Backend-ul nu răspunde.",
        "status" => "error"
    ]);
    http_response_code(500);
    exit;
}

if ($httpCode !== 200) {
    $responseData = json_decode($response, true);
    $errorMsg = "HTTP Error $httpCode";
    if ($responseData && isset($responseData['error'])) {
        $errorMsg = $responseData['error'];
    } elseif ($responseData && isset($responseData['detail'])) {
        $errorMsg = $responseData['detail'];
    }
    echo json_encode([
        "error" => $errorMsg,
        "status" => "error"
    ]);
    http_response_code($httpCode);
    exit;
}

$responseData = json_decode($response, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode([
        "error" => "Invalid JSON response from backend: " . json_last_error_msg(),
        "status" => "error"
    ]);
    http_response_code(500);
    exit;
}

echo $response;
?>

