<?php
header("Content-Type: application/json");

$rows = isset($_GET['rows']) ? intval($_GET['rows']) : 3;
$cols = isset($_GET['cols']) ? intval($_GET['cols']) : 3;
$ensure = isset($_GET['ensure']) ? $_GET['ensure'] : 'atleast_one';
$seed = isset($_GET['seed']) ? $_GET['seed'] : '';

$url = "http://127.0.0.1:8000/nash/generate?rows={$rows}&cols={$cols}&ensure={$ensure}";
if ($seed !== '') { $url .= "&seed=" . urlencode($seed); }

echo file_get_contents($url);
