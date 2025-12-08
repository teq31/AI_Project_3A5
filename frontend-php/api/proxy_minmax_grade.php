<?php
header("Content-Type: application/json");

$body = file_get_contents("php://input");

$opts = ['http' => [
  'method' => 'POST',
  'header' => "Content-Type: application/json\r\n",
  'content' => $body
]];
$ctx = stream_context_create($opts);
echo file_get_contents("http://127.0.0.1:8000/minmax/grade", false, $ctx);
?>

