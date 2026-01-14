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

$url = "http://127.0.0.1:8000/nash/grade";

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $json_input);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Content-Length: ' . strlen($json_input)
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($httpCode === 200 && $response) {
    $result = json_decode($response, true);

    // extragem payload-ul original al exercițiului din request-ul inițial
    $original = json_decode($json_input, true);
    $payloadJson = null;
    if (is_array($original) && isset($original['payload'])) {
        $payloadJson = json_encode($original['payload']);
    }
    
    if (isset($result['score'])) {
        try {
            $stmt = $pdo->prepare("INSERT INTO results (user_id, topic, score, feedback, payload) VALUES (?, ?, ?, ?, ?)");
            $stmt->execute([
                $_SESSION['user_id'],
                'Echilibru Nash',
                $result['score'],
                $result['feedback'],
                $payloadJson
            ]);
        } catch (PDOException $e) {
        }
    }
}

http_response_code($httpCode);
echo $response;
?>