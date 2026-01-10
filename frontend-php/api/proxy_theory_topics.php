<?php
header("Content-Type: application/json");

$theory_file = isset($_GET['theory_file']) ? $_GET['theory_file'] : 'example_theory.json';

$url = "http://127.0.0.1:8000/theory/topics?theory_file=" . urlencode($theory_file);

echo file_get_contents($url);
?>

