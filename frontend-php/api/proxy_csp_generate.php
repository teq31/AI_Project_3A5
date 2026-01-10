<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type');

$problem_type = $_GET['problem_type'] ?? 'simple';
$optimization = $_GET['optimization'] ?? 'FC';
$seed = $_GET['seed'] ?? null;

$url = "http://127.0.0.1:8000/csp/generate?problem_type=" . urlencode($problem_type) . "&optimization=" . urlencode($optimization);
if ($seed) $url .= "&seed=" . urlencode($seed);

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

http_response_code($httpCode);
echo $response;
?>

