<?php
// frontend-php/logout.php
session_start();
session_unset();    // Șterge toate variabilele de sesiune
session_destroy();  // Distruge sesiunea
header("Location: login.php"); // Trimite userul înapoi la login
exit;
?>