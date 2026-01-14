<?php
header("Content-Type: application/json");

$url = "http://127.0.0.1:8000/nlp/status";

// Use cURL for better error handling
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    echo json_encode([
        "error" => "Connection error: " . $error . ". Make sure the backend server is running on port 8000.",
        "status" => "error",
        "semantic_similarity_available" => false,
        "nlp_available" => false,
        "model_loaded" => false
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
        "status" => "error",
        "semantic_similarity_available" => false,
        "nlp_available" => false,
        "model_loaded" => false
    ]);
    http_response_code($httpCode);
    exit;
}

// Validate JSON response
$responseData = json_decode($response, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode([
        "error" => "Invalid JSON response from backend: " . json_last_error_msg(),
        "status" => "error",
        "semantic_similarity_available" => false,
        "nlp_available" => false,
        "model_loaded" => false
    ]);
    http_response_code(500);
    exit;
}

echo $response;
?>

