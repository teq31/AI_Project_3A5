<?php
header("Content-Type: application/json");

$depth = isset($_GET['depth']) ? intval($_GET['depth']) : 3;
$branching = isset($_GET['branching']) ? intval($_GET['branching']) : 2;
$valueMin = isset($_GET['valueMin']) ? intval($_GET['valueMin']) : -10;
$valueMax = isset($_GET['valueMax']) ? intval($_GET['valueMax']) : 10;
$seed = isset($_GET['seed']) ? $_GET['seed'] : '';

$url = "http://127.0.0.1:8000/minmax/generate?depth={$depth}&branching_factor={$branching}&value_min={$valueMin}&value_max={$valueMax}";
if ($seed !== '') { $url .= "&seed=" . urlencode($seed); }

echo file_get_contents($url);
?>

