<?php
// frontend-php/profile.php
session_start();
require 'db_connection.php';

if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

$user_id = $_SESSION['user_id'];
$username = $_SESSION['username'];

// --- 1. Statistici Generale ---
$stmt = $pdo->prepare("SELECT COUNT(*) as total_tests, AVG(score) as global_avg FROM results WHERE user_id = ?");
$stmt->execute([$user_id]);
$general_stats = $stmt->fetch();
$total_tests = $general_stats['total_tests'] ?? 0;
$global_avg = round($general_stats['global_avg'] ?? 0, 1);

// --- 2. Statistici pe Categorii ---
$stmt = $pdo->prepare("SELECT topic, AVG(score) as avg_score, COUNT(*) as count FROM results WHERE user_id = ? GROUP BY topic");
$stmt->execute([$user_id]);
$topic_stats = $stmt->fetchAll();

$chart_labels = [];
$chart_data = [];
$scores_by_topic = []; // Array asociativ pentru acces rapid la note

foreach ($topic_stats as $stat) {
    $chart_labels[] = $stat['topic'];
    $chart_data[] = round($stat['avg_score'], 1);
    $scores_by_topic[$stat['topic']] = $stat['avg_score'];
}

// --- 3. LOGICA DE RECOMANDARE (TUTORE VIRTUAL) ---
$recommendation = [];

// Lista tuturor capitolelor posibile (trebuie să corespundă cu ce ai pus în proxy_*.php)
$all_topics = [
    'Identificare Strategie' => 'strategy.php',
    'Echilibru Nash' => 'nash.php',
    'CSP' => 'csp.php',
    'MinMax' => 'minmax.php',
    'Teorie' => 'theory.php'
];

if ($total_tests == 0) {
    // Cazul 1: Utilizator nou
    $recommendation = [
        'title' => 'Bun venit! Începe cu începutul.',
        'text' => 'Nu ai rezolvat nicio problemă încă. Îți recomandăm să începi cu <strong>Teoria</strong> sau cu <strong>Identificarea Strategiilor</strong>.',
        'link' => 'theory.php',
        'btn_text' => 'Mergi la Teorie',
        'color' => '#0984e3' // Albastru
    ];
} else {
    // Căutăm cel mai slab punct
    $weakest_topic = null;
    $min_score = 101;

    foreach ($scores_by_topic as $topic => $score) {
        if ($score < $min_score) {
            $min_score = $score;
            $weakest_topic = $topic;
        }
    }

    if ($min_score < 60 && $weakest_topic) {
        // Cazul 2: Avem o restanță (notă mică)
        $link = $all_topics[$weakest_topic] ?? 'index.php';
        $recommendation = [
            'title' => 'Concentrează-te pe punctele slabe',
            'text' => "Am observat că ai dificultăți la <strong>$weakest_topic</strong> (Media: " . round($min_score) . "%). Îți recomandăm să mai exersezi acest capitol.",
            'link' => $link,
            'btn_text' => 'Exersează ' . $weakest_topic,
            'color' => '#d63031' // Roșu
        ];
    } else {
        // Cazul 3: Note bune, verificăm ce capitole lipsesc
        $missing_topics = array_diff(array_keys($all_topics), array_keys($scores_by_topic));
        
        if (!empty($missing_topics)) {
            // Luăm primul capitol lipsă
            $next_topic = array_values($missing_topics)[0];
            $link = $all_topics[$next_topic];
            
            $recommendation = [
                'title' => 'Explorează noi orizonturi',
                'text' => "Te descurci excelent la ce ai făcut până acum! Încă nu ai încercat capitolul <strong>$next_topic</strong>.",
                'link' => $link,
                'btn_text' => 'Încearcă ' . $next_topic,
                'color' => '#6c5ce7' // Violet
            ];
        } else {
            // Cazul 4: A terminat totul cu note bune -> Generare Quiz
            $recommendation = [
                'title' => 'Ești un expert!',
                'text' => 'Ai parcurs toate capitolele cu succes. Ești pregătit pentru un test complet de recapitulare.',
                'link' => 'quiz.php',
                'btn_text' => 'Generează un Quiz Mixt',
                'color' => '#00b894' // Verde
            ];
        }
    }
}

// --- 4. Istoric ---
$stmt = $pdo->prepare("SELECT topic, score, feedback, created_at FROM results WHERE user_id = ? ORDER BY created_at DESC LIMIT 5");
$stmt->execute([$user_id]);
$history = $stmt->fetchAll();
?>

<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Profilul Meu - SmarTest</title>
    <link rel="stylesheet" href="css/style.css?v=8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        @media (max-width: 768px) { .dashboard-grid { grid-template-columns: 1fr; } }

        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            color: white;
            margin-bottom: 20px;
        }
        
        /* Stiluri pentru Recomandare */
        .recommendation-card {
            border-left: 5px solid <?= $recommendation['color'] ?>;
            background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        }
        .rec-btn {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background-color: <?= $recommendation['color'] ?>;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: 0.3s;
        }
        .rec-btn:hover { filter: brightness(1.1); transform: translateY(-2px); }

        .stat-number { font-size: 2.5em; font-weight: bold; color: #fab1a0; }
        .stat-label { font-size: 1.1em; color: #dfe6e9; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 10px; color: white; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { background: rgba(0,0,0,0.2); }
        .score-high { color: #55efc4; } .score-med { color: #ffeaa7; } .score-low { color: #ff7675; }
        .back-btn { display: inline-block; margin-bottom: 20px; color: #74b9ff; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>

<div class="container" style="max-width: 1000px;">
    <a href="index.php" class="back-btn">← Înapoi la Meniu</a>
    
    <h1>Profil: <?= htmlspecialchars($username) ?></h1>

    <div class="card recommendation-card">
        <h2 style="margin-top:0; color: <?= $recommendation['color'] ?>">💡 Recomandarea Tutorelui</h2>
        <h3><?= $recommendation['title'] ?></h3>
        <p><?= $recommendation['text'] ?></p>
        <a href="<?= $recommendation['link'] ?>" class="rec-btn"><?= $recommendation['btn_text'] ?></a>
    </div>

    <div class="dashboard-grid">
        <div class="card" style="text-align: center;">
            <div class="stat-number"><?= $total_tests ?></div>
            <div class="stat-label">Teste Finalizate</div>
        </div>
        <div class="card" style="text-align: center;">
            <div class="stat-number"><?= $global_avg ?>%</div>
            <div class="stat-label">Media Globală</div>
        </div>
    </div>

    <div class="card">
        <h3>Performanță pe Categorii</h3>
        <?php if($total_tests > 0): ?>
            <canvas id="skillsChart" style="max-height: 300px;"></canvas>
        <?php else: ?>
            <p>Nu ai date suficiente pentru grafic.</p>
        <?php endif; ?>
    </div>

    <div class="card">
        <h3>Ultimele 5 Rezultate</h3>
        <?php if(count($history) > 0): ?>
        <table>
            <thead><tr><th>Data</th><th>Subiect</th><th>Nota</th><th>Feedback</th></tr></thead>
            <tbody>
                <?php foreach($history as $row): ?>
                    <?php 
                        $cls = ($row['score']>=80)?'score-high':(($row['score']>=50)?'score-med':'score-low');
                        $fb = (strlen($row['feedback']) > 60) ? substr($row['feedback'], 0, 60)."..." : $row['feedback'];
                    ?>
                    <tr>
                        <td><?= date('d.m H:i', strtotime($row['created_at'])) ?></td>
                        <td><?= htmlspecialchars($row['topic']) ?></td>
                        <td class="<?= $cls ?>"><b><?= $row['score'] ?>%</b></td>
                        <td style="font-size:0.9em; opacity:0.8"><?= htmlspecialchars($fb) ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <?php else: ?>
            <p>Fără istoric.</p>
        <?php endif; ?>
    </div>
</div>

<script>
    <?php if($total_tests > 0): ?>
    const ctx = document.getElementById('skillsChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: <?= json_encode($chart_labels) ?>,
            datasets: [{
                label: 'Media (%)',
                data: <?= json_encode($chart_data) ?>,
                backgroundColor: ['#ff7675', '#74b9ff', '#55efc4', '#a29bfe', '#fdcb6e'],
                borderColor: 'rgba(255,255,255,0.5)', borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                x: { ticks: { color: 'white' }, grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
    <?php endif; ?>
</script>
</body>
</html>