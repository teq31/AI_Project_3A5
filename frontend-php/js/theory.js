const USE_PROXY = true;
const API = "http://127.0.0.1:8000";

let currentPayload = null;

// Load available topics on page load
async function loadTopics() {
  try {
    const url = USE_PROXY
      ? 'api/proxy_theory_topics.php'
      : `${API}/theory/topics`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    const topicSelect = document.getElementById('topicId');
    if (data.topics && Array.isArray(data.topics)) {
      data.topics.forEach(topic => {
        const option = document.createElement('option');
        option.value = topic.topic_id;
        option.textContent = `${topic.topic_name} (${topic.difficulty})`;
        topicSelect.appendChild(option);
      });
    }
  } catch (error) {
    console.error('Error loading topics:', error);
  }
}

// Load question
async function loadQuestion() {
  try {
    const topicId = document.getElementById('topicId').value;
    const questionType = document.getElementById('questionType').value;
    const seed = document.getElementById('seed').value;

    let url = USE_PROXY
      ? 'api/proxy_theory_generate.php?'
      : `${API}/theory/generate?`;
    
    if (topicId) url += `&topic_id=${encodeURIComponent(topicId)}`;
    if (questionType) url += `&question_type=${encodeURIComponent(questionType)}`;
    if (seed) url += `&seed=${encodeURIComponent(seed)}`;

    const response = await fetch(url);
    const data = await response.json();
    
    currentPayload = data;
    displayQuestion(data.question || data);
    
    const solutionEl = document.getElementById('solution');
    if (data.question || data) {
      const q = data.question || data;
      let solutionText = '';
      if (q.explanation) {
        solutionText += `Explicație: ${q.explanation}\n\n`;
      }
      if (q.correct_answer) {
        solutionText += `Răspuns corect: ${q.correct_answer}\n\n`;
      }
      if (q.correct_keywords) {
        solutionText += `Cuvinte cheie: ${q.correct_keywords.join(', ')}\n\n`;
      }
      if (q.theory_reference) {
        solutionText += `Referință teoretică:\n`;
        if (q.theory_reference.definition) {
          solutionText += `Definiție: ${q.theory_reference.definition}\n`;
        }
      }
      solutionEl.textContent = solutionText || 'Soluția nu este disponibilă';
    }
    
    const answerEl = document.getElementById('answer');
    if (answerEl) {
      answerEl.value = '';
    }
    
    const resultEl = document.getElementById('result');
    if (resultEl) {
      resultEl.innerHTML = '';
    }
  } catch (error) {
    console.error('Error loading question:', error);
    alert('Eroare la generarea întrebării: ' + error.message);
  }
}

function displayQuestion(question) {
  const container = document.getElementById('questionContainer');
  const theoryType = question.theory_type;
  
  let html = `<h4 style="color: #667eea; margin-bottom: 12px;">${question.topic_name || 'Teorie'}</h4>`;
  html += `<p style="font-size: 1.1rem; margin: 16px 0; font-weight: 500; line-height: 1.6;">${question.question_text || ''}</p>`;
  
  if (theoryType === 'multiple_choice') {
    const options = question.options || [];
    html += '<div style="margin: 16px 0;">';
    options.forEach((opt, idx) => {
      html += `<label style="display: block; padding: 12px; margin: 8px 0; background: #f7fafc; border: 2px solid #e2e8f0; border-radius: 8px; cursor: pointer;">
        <input type="radio" name="theory_option" value="${idx + 1}" style="margin-right: 8px;">
        ${idx + 1}. ${opt}
      </label>`;
    });
    html += '</div>';
    html += '<p><small style="color: #718096;">Răspunde cu numărul opțiunii (1-4) sau textul opțiunii</small></p>';
  } else if (theoryType === 'true_false') {
    html += '<p><small style="color: #718096;">Răspunde cu "Adevărat"/"True" sau "Fals"/"False" (acceptă variante: "Raspunsul este Fals", "Este Adevărat", etc.)</small></p>';
  } else if (theoryType === 'fill_blank') {
    html += '<p><small style="color: #718096;">Completează spațiile goale cu răspunsurile corecte (acceptă variante alternative)</small></p>';
  } else if (theoryType === 'short_answer') {
    html += '<p><small style="color: #718096;">Răspunde cu un răspuns scurt care să includă conceptele importante</small></p>';
  } else if (theoryType === 'justification') {
    html += '<p><small style="color: #718096;">Oferă o justificare detaliată. Folosește cuvinte precum "deoarece", "pentru că", etc.</small></p>';
  } else if (theoryType === 'example') {
    html += '<p><small style="color: #718096;">Oferă un exemplu concret. Folosește cuvinte precum "exemplu", "de exemplu", "instanță", etc.</small></p>';
  } else if (theoryType === 'comparison') {
    const concepts = question.concepts_to_compare || [];
    html += `<p><small style="color: #718096;">Compară ${concepts.join(' și ')}. Menționează diferențe și/sau similarități</small></p>`;
  } else if (theoryType === 'definition') {
    html += '<p><small style="color: #718096;">Oferă o definiție completă care să includă toate elementele esențiale</small></p>';
  } else if (theoryType === 'calculation') {
    html += '<p><small style="color: #718096;">Oferă rezultatul calculului (acceptă numere, formule, sau descrieri verbale)</small></p>';
  } else if (theoryType === 'matrix_analysis') {
    html += '<p><small style="color: #718096;">Analizează jocul matriceal și oferă răspunsul (ex: "există echilibru Nash", "nu există", etc.)</small></p>';
    if (question.matrix_data) {
      html += '<p><small style="color: #718096;"><em>Datele matricei sunt disponibile în întrebare</em></small></p>';
    }
  }
  
  container.innerHTML = html;
}

async function gradeAnswer() {
  if (!currentPayload) {
    alert('Generează mai întâi o întrebare!');
    return;
  }
  
  let answer = document.getElementById('answer').value.trim();
  
  // Pentru multiple choice, verifică dacă utilizatorul a selectat un radio button
  const question = currentPayload.question || currentPayload;
  if (question.theory_type === 'multiple_choice') {
    const radioButtons = document.querySelectorAll('input[name="theory_option"]');
    for (const radio of radioButtons) {
      if (radio.checked) {
        answer = radio.value; // Folosește numărul opțiunii
        break;
      }
    }
  }
  
  if (!answer) {
    alert('Te rog introdu un răspuns!');
    return;
  }
  
  try {
    const payload = currentPayload.question || currentPayload;
    const body = JSON.stringify({ payload: payload, answer: answer });
    
    const url = USE_PROXY
      ? 'api/proxy_theory_grade.php'
      : `${API}/theory/grade`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body
    });
    
    const result = await response.json();
    displayResult(result);
  } catch (error) {
    console.error('Error grading answer:', error);
    alert('Eroare la evaluarea răspunsului: ' + error.message);
  }
}

function displayResult(result) {
  const resultEl = document.getElementById('result');
  const score = result.score || 0;
  
  let bgColor = '#fed7d7'; // roșu
  if (score === 100) {
    bgColor = '#c6f6d5'; // verde
  } else if (score > 0) {
    bgColor = '#feebc8'; // galben
  }
  
  resultEl.innerHTML = `
    <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: ${bgColor};">
      <strong>Scor: ${score}%</strong><br>
      ${result.feedback || 'Fără feedback'}
    </div>
  `;
}

// Event listeners
document.getElementById('genBtn').addEventListener('click', loadQuestion);
document.getElementById('gradeBtn').addEventListener('click', gradeAnswer);

// Load topics on page load
loadTopics();

