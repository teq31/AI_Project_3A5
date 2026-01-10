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

echo file_get_contents($url);
?>

