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
      
      // Pentru multiple choice, nu afișăm răspunsul corect, doar explicația
      if (q.theory_type === 'multiple_choice') {
        if (q.explanation) {
          solutionText += `Explicație: ${q.explanation}\n\n`;
        }
      } else {
        // Pentru alte tipuri de întrebări, afișăm explicația
        if (q.explanation) {
          solutionText += `Explicație: ${q.explanation}\n\n`;
        }
        // Nu mai afișăm correct_answer pentru niciun tip de întrebare
        // (utilizatorul trebuie să înțeleagă din explicație)
      }
      
      // Nu mai afișăm correct_keywords și theory_reference pentru a simplifica
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
  
  // Extrage informații NLP din feedback sau din result
  let nlpInfo = '';
  if (result.similarity !== undefined) {
    const similarityPercent = Math.round(result.similarity * 100);
    nlpInfo = `<div style="margin-top: 8px; padding: 8px; background: rgba(0,0,0,0.05); border-radius: 6px; font-size: 0.9rem;">
      <strong>🔍 Analiză NLP:</strong> Similaritate semantică: <strong>${similarityPercent}%</strong>
      ${result.method ? ` | Metodă: ${result.method}` : ''}
    </div>`;
  }
  
  // Verifică dacă feedback-ul conține informații despre similaritate
  const feedback = result.feedback || '';
  if (feedback.includes('Similaritate') || feedback.includes('similaritate')) {
    // Informațiile sunt deja în feedback
  } else if (result.similarity === undefined && feedback) {
    // Nu avem informații NLP explicite, dar putem deduce din feedback
  }
  
  resultEl.innerHTML = `
    <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: ${bgColor};">
      <strong>Scor: ${score}%</strong><br>
      ${feedback}
      ${nlpInfo}
    </div>
  `;
}

// Check NLP status on page load (exported for button)
window.checkNLPStatus = async function() {
  try {
    const url = USE_PROXY
      ? 'api/proxy_nlp_status.php'
      : `${API}/nlp/status`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    console.log('NLP Status Data:', data); // Debug
    
    const statusEl = document.getElementById('nlpStatus');
    const iconEl = document.getElementById('nlpStatusIcon');
    const textEl = document.getElementById('nlpStatusText');
    
    // Verifică dacă NLP este activat (status enabled sau dacă avem semantic_similarity_available sau nlp_available)
    const nlpIsEnabled = data.status === 'enabled' || data.semantic_similarity_available || data.nlp_available;
    
    console.log('NLP Enabled:', nlpIsEnabled, 'Semantic:', data.semantic_similarity_available, 'NLP:', data.nlp_available); // Debug
    
    if (nlpIsEnabled) {
      if (data.model_loaded) {
        statusEl.style.background = '#c6f6d5';
        statusEl.style.borderColor = '#68d391';
        iconEl.textContent = '✅';
        textEl.innerHTML = `<strong>NLP Activ:</strong> Similaritate semantică ${data.semantic_similarity_available ? 'completă' : 'parțială'} | Model: <strong style="color: #22543d;">Încărcat</strong>`;
      } else {
        // Model disponibil dar nu încărcat (se va încărca la prima utilizare)
        statusEl.style.background = '#c6f6d5';
        statusEl.style.borderColor = '#68d391';
        iconEl.textContent = '✅';
        textEl.innerHTML = `<strong>NLP Activ:</strong> Similaritate semantică ${data.semantic_similarity_available ? 'completă' : 'parțială'} | Model: <strong style="color: #22543d;">Se va încărca la prima utilizare</strong>`;
      }
    } else if (data.status === 'disabled' || (!data.semantic_similarity_available && !data.nlp_available)) {
      statusEl.style.background = '#fed7d7';
      statusEl.style.borderColor = '#fc8181';
      iconEl.textContent = '⚠️';
      textEl.innerHTML = `<strong>NLP Dezactivat:</strong> Folosește metode fallback (matching simplu)`;
    } else {
      statusEl.style.background = '#feebc8';
      statusEl.style.borderColor = '#f6ad55';
      iconEl.textContent = '⚠️';
      textEl.innerHTML = `<strong>NLP Parțial:</strong> ${data.error || 'Status necunoscut'}`;
    }
  } catch (error) {
    const statusEl = document.getElementById('nlpStatus');
    const iconEl = document.getElementById('nlpStatusIcon');
    const textEl = document.getElementById('nlpStatusText');
    statusEl.style.background = '#fed7d7';
    statusEl.style.borderColor = '#fc8181';
    iconEl.textContent = '❌';
    textEl.innerHTML = `<strong>Eroare:</strong> Nu s-a putut verifica statusul NLP`;
    console.error('Error checking NLP status:', error);
  }
};

// Event listeners
document.getElementById('genBtn').addEventListener('click', loadQuestion);
document.getElementById('gradeBtn').addEventListener('click', gradeAnswer);

// Load topics and check NLP status on page load
loadTopics();
checkNLPStatus();

