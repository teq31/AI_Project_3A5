const USE_PROXY = true;
const API = "http://127.0.0.1:8000";

let quizConfig = [];
let quizQuestions = [];
let currentQuestionIndex = 0;
let quizAnswers = [];
let quizResults = [];
let quizFinished = false;
let currentQuizId = null;
let isReplayMode = false;
let quizStartTime = null;
let quizTimerInterval = null;
let timeSpentSeconds = 0;

// Initialize
function init() {
  const params = new URLSearchParams(window.location.search);
  const replayQuizId = params.get('replay_quiz');

  if (replayQuizId) {
    // Mod replay: nu generăm un quiz nou, ci îl încărcăm pe cel salvat
    loadQuizReplay(replayQuizId);
  } else {
    // Comportament normal: propunem 3 întrebări default în configurator
    addQuestion();
    addQuestion();
    addQuestion();
  }
}

function addQuestion() {
  const container = document.getElementById('questionsConfig');
  const index = quizConfig.length;
  
  const div = document.createElement('div');
  div.className = 'quiz-question-config';
  div.innerHTML = `
    <label>Întrebarea ${index + 1}:</label>
    <select id="qtype_${index}">
      <option value="strategy">Problema 1: Identificare Strategie</option>
      <option value="nash">Problema 2: Echilibru Nash</option>
      <option value="csp">Problema 3: CSP cu Backtracking</option>
      <option value="minmax">Problema 4: MinMax Alpha-Beta</option>
      <option value="theory">Întrebare Teorie</option>
    </select>
    <button onclick="removeQuestion(${index})">✖</button>
  `;
  
  container.appendChild(div);
  quizConfig.push({ type: 'nash' });
}

function removeQuestion(index) {
  const container = document.getElementById('questionsConfig');
  container.children[index].remove();
  quizConfig.splice(index, 1);
  
  // Reindex
  Array.from(container.children).forEach((child, i) => {
    const label = child.querySelector('label');
    label.textContent = `Întrebarea ${i + 1}:`;
    const select = child.querySelector('select');
    select.id = `qtype_${i}`;
    const button = child.querySelector('button');
    button.setAttribute('onclick', `removeQuestion(${i})`);
  });
}

async function startQuiz() {
  if (quizConfig.length === 0) {
    alert('Adaugă cel puțin o întrebare!');
    return;
  }
  
  // Collect configuration
  quizConfig = [];
  const container = document.getElementById('questionsConfig');
  Array.from(container.children).forEach((child, i) => {
    const select = child.querySelector('select');
    quizConfig.push({ type: select.value });
  });
  
  // Reset state
  quizQuestions = [];
  quizAnswers = [];
  quizResults = [];
  quizFinished = false;
  currentQuizId = null;
  isReplayMode = false;
  timeSpentSeconds = 0;
  
  // Start timer
  startQuizTimer();

  // Generate questions
  try {
    document.getElementById('setupSection').classList.remove('active');
    document.getElementById('quizSection').classList.add('active');
    
    for (let i = 0; i < quizConfig.length; i++) {
      const config = quizConfig[i];
      let question;
      
      if (config.type === 'nash') {
        question = await generateNashQuestion();
      } else if (config.type === 'minmax') {
        question = await generateMinMaxQuestion();
      } else if (config.type === 'strategy') {
        question = await generateProblem1Question();
      } else if (config.type === 'csp') {
        question = await generateCSPQuestion();
      } else if (config.type === 'theory') {
        question = await generateTheoryQuestion(config.topic_id, config.question_type);
      }
      
      quizQuestions.push({
        ...question,
        type: config.type,
        userAnswer: '',
        submitted: false
      });
      quizAnswers.push('');
    }
    
    displayQuestion(0);
  } catch (error) {
    console.error('Error generating quiz:', error);
    alert('Eroare la generarea quiz-ului: ' + error.message);
  }
}

async function generateNashQuestion() {
  const rows = 2 + Math.floor(Math.random() * 3);
  const cols = 2 + Math.floor(Math.random() * 3);
  const ensure = ['atleast_one', 'unique', 'none'][Math.floor(Math.random() * 3)];
  
  const url = USE_PROXY 
    ? `api/proxy_nash_generate.php?rows=${rows}&cols=${cols}&ensure=${ensure}`
    : `${API}/nash/generate?rows=${rows}&cols=${cols}&ensure=${ensure}`;
  
  const response = await fetch(url);
  return await response.json();
}

async function generateMinMaxQuestion() {
  const depth = 2 + Math.floor(Math.random() * 2);
  const branching = 2 + Math.floor(Math.random() * 2);
  
  const url = USE_PROXY
    ? `api/proxy_minmax_generate.php?depth=${depth}&branching=${branching}&valueMin=-10&valueMax=10`
    : `${API}/minmax/generate?depth=${depth}&branching_factor=${branching}&value_min=-10&value_max=10`;
  
  const response = await fetch(url);
  return await response.json();
}

async function generateProblem1Question() {
  const problemTypes = ['n-queens', 'hanoi', 'graph_coloring', 'knight_tour'];
  const problemType = problemTypes[Math.floor(Math.random() * problemTypes.length)];
  
  const url = USE_PROXY
    ? `api/proxy_strategy_generate.php?problem_type=${problemType}`
    : `${API}/problem1/generate?problem_type=${problemType}`;
  
  const response = await fetch(url);
  return await response.json();
}

async function generateCSPQuestion() {
  const problemTypes = ['simple', 'graph_coloring', 'sudoku'];
  const problemType = problemTypes[Math.floor(Math.random() * problemTypes.length)];
  const optimization = 'FC';
  
  const url = USE_PROXY
    ? `api/proxy_csp_generate.php?problem_type=${problemType}&optimization=${optimization}`
    : `${API}/csp/generate?problem_type=${problemType}&optimization=${optimization}`;
  
  const response = await fetch(url);
  return await response.json();
}

async function generateTheoryQuestion(topicId = null, questionType = null) {
  let url = USE_PROXY
    ? `api/proxy_theory_generate.php?`
    : `${API}/theory/generate?`;
  
  if (topicId) url += `&topic_id=${encodeURIComponent(topicId)}`;
  if (questionType) url += `&question_type=${encodeURIComponent(questionType)}`;
  
  const response = await fetch(url);
  const data = await response.json();
  return data;
}

function displayQuestion(index) {
  currentQuestionIndex = index;
  const question = quizQuestions[index];
  
  document.getElementById('quizProgress').textContent = 
    `Întrebarea ${index + 1} din ${quizQuestions.length}`;
  
  const container = document.getElementById('currentQuestion');
  
  if (question.type === 'nash') {
    container.innerHTML = `
      <h4>Problema 2: Echilibru Nash (strategii pure)</h4>
      <pre style="white-space: pre-wrap; background: #1a202c; color: #e2e8f0; padding: 16px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 0.95rem; line-height: 1.6;">${question.question_text || ''}</pre>
      <p><small>Răspunde cu perechile (ex: R1 C2, R2 C3, (1,2), (RA,CB)) sau "none"</small></p>
    `;
  } else if (question.type === 'minmax') {
    // Pentru MinMax, creăm un container pentru arbore și apoi desenăm arborele
    container.innerHTML = `
      <h4>Problema 4: MinMax cu Alpha-Beta</h4>
      <p><strong>Cerință:</strong> Pentru arborele dat, care va fi valoarea din rădăcină și câte noduri frunze vor fi vizitate în cazul aplicării strategiei MinMax cu optimizarea Alpha-Beta?</p>
      <div id="quizTreeVisualization_${index}" style="margin: 20px 0; overflow-x: auto; padding: 20px; background: #f9f9f9; border-radius: 8px;"></div>
      <p><small>Răspunde flexibil: "valoare=5, frunze=4" sau "5 4" sau "Frunzele sunt 4, iar valoarea este 5"</small></p>
    `;
    
    // Desenează arborele vizual dacă există date
    if (question.tree) {
      const visitedLeaves = question.solution?.visited_leaves || [];
      setTimeout(() => {
        drawTreeForQuiz(`quizTreeVisualization_${index}`, question.tree, visitedLeaves);
      }, 100);
    }
  } else if (question.type === 'strategy') {
    container.innerHTML = `
      <h4>Problema 1: Identificare Strategie</h4>
      <pre style="white-space: pre-wrap; background: #1a202c; color: #e2e8f0; padding: 16px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 0.95rem; line-height: 1.6;">${question.question_text || ''}</pre>
      <p><small>Răspunde cu numele strategiei (ex: Backtracking) sau numărul opțiunii (1-4)</small></p>
    `;
  } else if (question.type === 'csp') {
    container.innerHTML = `
      <h4>Problema 3: CSP cu Backtracking</h4>
      <pre style="white-space: pre-wrap; background: #1a202c; color: #e2e8f0; padding: 16px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 0.95rem; line-height: 1.6;">${question.question_text || ''}</pre>
      <p><small>Răspunde cu numele optimizării (ex: Forward Checking) sau numărul opțiunii (1-4)</small></p>
    `;
    } else if (question.type === 'theory') {
    // Întrebarea de teorie poate avea structura în question.question sau direct în question
    const theoryQuestion = question.question || question;
    const theoryType = theoryQuestion.theory_type || '';
    
    let html = `<h4>Întrebare Teorie: ${theoryQuestion.topic_name || 'Teorie'}</h4>`;
    html += `<p style="font-size: 1.1rem; margin: 16px 0; font-weight: 500;">${theoryQuestion.question_text || ''}</p>`;
    
    if (theoryType === 'multiple_choice') {
      const options = theoryQuestion.options || [];
      html += '<div style="margin: 16px 0;">';
      options.forEach((opt, idx) => {
        html += `<label style="display: block; padding: 12px; margin: 8px 0; background: #f7fafc; border: 2px solid #e2e8f0; border-radius: 8px; cursor: pointer; transition: all 0.2s;">
          <input type="radio" name="theory_option_${index}" value="${idx + 1}" style="margin-right: 8px;">
          ${idx + 1}. ${opt}
        </label>`;
      });
      html += '</div>';
      html += '<p><small>Răspunde cu numărul opțiunii (1-4) sau textul opțiunii</small></p>';
      
      // Adaugă event listener pentru a actualiza input-ul când se selectează o opțiune
      setTimeout(() => {
        document.querySelectorAll(`input[name="theory_option_${index}"]`).forEach(radio => {
          radio.addEventListener('change', (e) => {
            if (e.target.checked) {
              const answerInput = document.getElementById('quizAnswer');
              if (answerInput) answerInput.value = e.target.value;
            }
          });
        });
      }, 100);
    } else if (theoryType === 'true_false') {
      html += '<p><small>Răspunde cu "Adevărat"/"True" sau "Fals"/"False" (acceptă variante: "Raspunsul este Fals", "Este Adevărat", etc.)</small></p>';
    } else if (theoryType === 'fill_blank') {
      html += '<p><small>Completează spațiile goale cu răspunsurile corecte (acceptă variante alternative)</small></p>';
    } else if (theoryType === 'short_answer') {
      html += '<p><small>Răspunde cu un răspuns scurt care să includă conceptele importante</small></p>';
    } else if (theoryType === 'justification') {
      html += '<p><small>Oferă o justificare detaliată. Folosește cuvinte precum "deoarece", "pentru că", etc.</small></p>';
    } else if (theoryType === 'example') {
      html += '<p><small>Oferă un exemplu concret. Folosește cuvinte precum "exemplu", "de exemplu", "instanță", etc.</small></p>';
    } else if (theoryType === 'comparison') {
      const concepts = theoryQuestion.concepts_to_compare || [];
      html += `<p><small>Compară ${concepts.join(' și ')}. Menționează diferențe și/sau similarități</small></p>`;
    } else if (theoryType === 'definition') {
      html += '<p><small>Oferă o definiție completă care să includă toate elementele esențiale</small></p>';
    } else if (theoryType === 'calculation') {
      html += '<p><small>Oferă rezultatul calculului (acceptă numere, formule, sau descrieri verbale)</small></p>';
    } else if (theoryType === 'matrix_analysis') {
      html += '<p><small>Analizează jocul matriceal și oferă răspunsul (ex: "există echilibru Nash", "nu există", etc.)</small></p>';
      if (theoryQuestion.matrix_data) {
        html += '<p><small><em>Datele matricei sunt disponibile în întrebare</em></small></p>';
      }
    }
    
    container.innerHTML = html;
  }
  
  const answerInput = document.getElementById('quizAnswer');
  answerInput.value = quizAnswers[index];
  
  const feedback = document.getElementById('questionFeedback');
  if (quizFinished && question.submitted && question.result) {
    feedback.innerHTML = `
      <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: ${
        question.result.score === 100 ? '#c6f6d5' : 
        question.result.score > 0 ? '#feebc8' : '#fed7d7'
      }">
        <strong>Scor: ${question.result.score}%</strong><br>
        ${question.result.feedback}
      </div>
    `;
  } else if (question.submitted) {
    feedback.innerHTML = `
      <div style="margin-top: 16px; padding: 12px; border-radius: 10px; background: #edf2ff; color: #434190;">
        ✅ Răspuns înregistrat. Scorul va apărea după Finalizează Quiz.
      </div>
    `;
  } else {
    feedback.innerHTML = '';
  }
  
  document.getElementById('prevBtn').style.display = index > 0 ? 'block' : 'none';
  document.getElementById('nextBtn').style.display = 
    index < quizQuestions.length - 1 ? 'block' : 'none';
  document.getElementById('finishBtn').style.display = 
    index === quizQuestions.length - 1 ? 'block' : 'none';
}

// Funcție pentru desenarea arborelui vizual (copiată și adaptată din minmax.js)
function drawTreeForQuiz(containerId, treeData, visitedLeaves = []) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Tree visualization container ${containerId} not found!`);
    return;
  }
  
  container.innerHTML = "";
  
  if (!treeData) {
    console.error("Tree data is missing!");
    return;
  }
  
  const levels = [];
  const nodeMap = new Map();
  
  function buildLevels(node, level = 0) {
    if (!levels[level]) levels[level] = [];
    
    const nodeInfo = {
      ...node,
      level,
      visited: visitedLeaves.includes(node.id)
    };
    
    levels[level].push(nodeInfo);
    nodeMap.set(node.id, nodeInfo);
    
    if (node.children && node.children.length > 0) {
      node.children.forEach(child => buildLevels(child, level + 1));
    }
  }
  
  buildLevels(treeData);
  
  const maxNodesPerLevel = Math.max(...levels.map(level => level.length));
  const nodeWidth = 80;
  const horizontalSpacing = Math.max(50, Math.min(100, 900 / Math.max(maxNodesPerLevel, 1)));
  const verticalSpacing = 100;
  
  const treeWrapper = document.createElement("div");
  treeWrapper.className = "tree-wrapper";
  treeWrapper.style.position = "relative";
  treeWrapper.style.width = "100%";
  treeWrapper.style.minHeight = `${levels.length * verticalSpacing}px`;
  treeWrapper.style.padding = "20px";
  
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.className = "tree-svg";
  svg.style.position = "absolute";
  svg.style.top = "0";
  svg.style.left = "0";
  svg.style.width = "100%";
  svg.style.height = "100%";
  svg.style.pointerEvents = "none";
  svg.style.zIndex = "1";
  svg.style.overflow = "visible";
  
  levels.forEach((levelNodes, levelIndex) => {
    const levelDiv = document.createElement("div");
    levelDiv.className = "tree-level";
    levelDiv.style.display = "flex";
    levelDiv.style.alignItems = "center";
    levelDiv.style.gap = "15px";
    levelDiv.style.marginBottom = "25px";
    levelDiv.style.position = "relative";
    levelDiv.style.zIndex = "10";
    levelDiv.style.minHeight = "70px";
    
    const levelLabel = document.createElement("div");
    levelLabel.className = "level-label";
    const levelType = levelNodes[0]?.type || "MAX";
    levelLabel.textContent = levelType;
    levelLabel.style.minWidth = "60px";
    levelLabel.style.fontWeight = "bold";
    levelLabel.style.textAlign = "center";
    levelLabel.style.padding = "8px";
    levelLabel.style.borderRadius = "6px";
    if (levelType === "MAX") {
      levelLabel.style.background = "#e3f2fd";
      levelLabel.style.color = "#1976d2";
    } else if (levelType === "MIN") {
      levelLabel.style.background = "#fff3e0";
      levelLabel.style.color = "#f57c00";
    } else {
      levelLabel.style.background = "#f1f8e9";
      levelLabel.style.color = "#558b2f";
    }
    levelDiv.appendChild(levelLabel);
    
    const nodesContainer = document.createElement("div");
    nodesContainer.style.display = "flex";
    nodesContainer.style.justifyContent = "center";
    nodesContainer.style.alignItems = "center";
    nodesContainer.style.gap = `${horizontalSpacing}px`;
    nodesContainer.style.width = "100%";
    nodesContainer.style.flexWrap = "nowrap";
    nodesContainer.style.paddingLeft = "20px";
    
    levelNodes.forEach((nodeInfo) => {
      const nodeDiv = document.createElement("div");
      const isVisited = nodeInfo.visited;
      const nodeType = nodeInfo.type.toLowerCase();
      
      let className = 'tree-node';
      if (nodeType === 'max') className += ' max';
      else if (nodeType === 'min') className += ' min';
      else if (nodeType === 'leaf') className += ' leaf';
      if (isVisited && nodeType !== 'leaf') className += ' visited';
      
      nodeDiv.className = className;
      nodeDiv.id = `node-${nodeInfo.id}`;
      nodeDiv.style.position = "relative";
      nodeDiv.style.flexShrink = "0";
      
      const labelDiv = document.createElement("div");
      labelDiv.className = "tree-node-label";
      labelDiv.textContent = nodeInfo.id;
      
      const valueDiv = document.createElement("div");
      valueDiv.className = "tree-node-value";
      if (nodeInfo.value !== null) {
        valueDiv.textContent = nodeInfo.value;
      } else {
        valueDiv.textContent = "";
        valueDiv.style.minHeight = "20px";
      }
      
      nodeDiv.appendChild(labelDiv);
      nodeDiv.appendChild(valueDiv);
      nodesContainer.appendChild(nodeDiv);
    });
    
    levelDiv.appendChild(nodesContainer);
    treeWrapper.appendChild(levelDiv);
  });
  
  treeWrapper.appendChild(svg);
  container.appendChild(treeWrapper);
  
  requestAnimationFrame(() => {
    setTimeout(() => {
      try {
        const wrapperRect = treeWrapper.getBoundingClientRect();
        const svgWidth = Math.max(wrapperRect.width, maxNodesPerLevel * (nodeWidth + horizontalSpacing) + 40);
        const svgHeight = levels.length * verticalSpacing + 40;
        
        svg.setAttribute("width", svgWidth);
        svg.setAttribute("height", svgHeight);
        svg.setAttribute("viewBox", `0 0 ${svgWidth} ${svgHeight}`);
        
        levels.forEach((levelNodes, levelIndex) => {
          if (levelIndex === 0) return;
          
          levelNodes.forEach((nodeInfo) => {
            const childElement = document.getElementById(`node-${nodeInfo.id}`);
            if (!childElement) return;
            
            const parentInfo = Array.from(nodeMap.values()).find(n => 
              n.children && n.children.some(c => c.id === nodeInfo.id)
            );
            
            if (parentInfo) {
              const parentElement = document.getElementById(`node-${parentInfo.id}`);
              if (parentElement) {
                const parentRect = parentElement.getBoundingClientRect();
                const childRect = childElement.getBoundingClientRect();
                
                const x1 = parentRect.left + parentRect.width / 2 - wrapperRect.left;
                const y1 = parentRect.top + parentRect.height - wrapperRect.top;
                
                const x2 = childRect.left + childRect.width / 2 - wrapperRect.left;
                const borderWidth = 2;
                const y2 = childRect.top - wrapperRect.top + borderWidth + 4;
                
                if (isNaN(x1) || isNaN(y1) || isNaN(x2) || isNaN(y2)) {
                  return;
                }
                
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", x1);
                line.setAttribute("y1", y1);
                line.setAttribute("x2", x2);
                line.setAttribute("y2", y2);
                line.setAttribute("stroke", "#333");
                line.setAttribute("stroke-width", "2.5");
                line.setAttribute("stroke-linecap", "round");
                line.setAttribute("stroke-linejoin", "round");
                svg.appendChild(line);
              }
            }
          });
        });
      } catch (error) {
        console.error("Error drawing tree lines:", error);
      }
    }, 200);
  });
}

async function submitAnswer() {
  const answer = document.getElementById('quizAnswer').value.trim();
  if (!answer) {
    alert('Te rog introdu un răspuns!');
    return;
  }
  
  quizAnswers[currentQuestionIndex] = answer;
  const question = quizQuestions[currentQuestionIndex];
  question.userAnswer = answer;
  
  // Show loading state
  const feedbackEl = document.getElementById('questionFeedback');
  if (feedbackEl) {
    feedbackEl.innerHTML = `
      <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: #edf2ff; color: #434190; text-align: center;">
        ⏳ Se evaluează răspunsul...
      </div>
    `;
  }
  
  try {
    let result;
    if (question.type === 'nash') {
      result = await gradeNashAnswer(question, answer);
    } else if (question.type === 'minmax') {
      result = await gradeMinMaxAnswer(question, answer);
    } else if (question.type === 'strategy') {
      result = await gradeProblem1Answer(question, answer);
    } else if (question.type === 'csp') {
      result = await gradeCSPAnswer(question, answer);
    } else if (question.type === 'theory') {
      result = await gradeTheoryAnswer(question, answer);
    }
    
    question.result = result;
    question.submitted = true;
    
    displayQuestion(currentQuestionIndex);
  } catch (error) {
    console.error('Error grading answer:', error);
    if (feedbackEl) {
      feedbackEl.innerHTML = `
        <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: #fed7d7; color: #742a2a;">
          <strong>Eroare:</strong> ${error.message}
        </div>
      `;
    }
    alert('Eroare la evaluarea răspunsului: ' + error.message);
  }
}

async function gradeNashAnswer(question, answer) {
  const body = JSON.stringify({ payload: question, answer });
  
  const url = USE_PROXY 
    ? 'api/proxy_nash_grade.php'
    : `${API}/nash/grade`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body
  });
  
  return await response.json();
}

async function gradeMinMaxAnswer(question, answer) {
  const body = JSON.stringify({ payload: question, answer });
  
  const url = USE_PROXY
    ? 'api/proxy_minmax_grade.php'
    : `${API}/minmax/grade`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body
  });
  
  return await response.json();
}

async function gradeProblem1Answer(question, answer) {
  const body = JSON.stringify({ payload: question, answer });
  
  const url = USE_PROXY
    ? 'api/proxy_strategy_grade.php'
    : `${API}/problem1/grade`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body
  });
  
  return await response.json();
}

async function gradeCSPAnswer(question, answer) {
  const body = JSON.stringify({ payload: question, answer });
  
  const url = USE_PROXY
    ? 'api/proxy_csp_grade.php'
    : `${API}/csp/grade`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body
  });
  
  return await response.json();
}

async function gradeTheoryAnswer(question, answer) {
  // Pentru întrebările multiple choice, verifică dacă utilizatorul a selectat un radio button
  const theoryQuestion = question.question || question;
  if (theoryQuestion.theory_type === 'multiple_choice') {
    const radioButtons = document.querySelectorAll(`input[name="theory_option_${currentQuestionIndex}"]`);
    for (const radio of radioButtons) {
      if (radio.checked) {
        answer = radio.value; // Folosește numărul opțiunii
        break;
      }
    }
  }
  
  const payload = question.question || question;
  const body = JSON.stringify({ payload: payload, answer: answer });
  
  const url = USE_PROXY
    ? 'api/proxy_theory_grade.php'
    : `${API}/theory/grade`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body
  });
  
  return await response.json();
}

function prevQuestion() {
  if (currentQuestionIndex > 0) {
    displayQuestion(currentQuestionIndex - 1);
  }
}

function nextQuestion() {
  if (currentQuestionIndex < quizQuestions.length - 1) {
    displayQuestion(currentQuestionIndex + 1);
  }
}

// Funcție pentru încărcarea răspunsurilor din document
async function loadAnswersFromFile() {
  const fileInput = document.getElementById('answerFile');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('Te rog selectează un fișier!');
    return;
  }
  
  if (quizQuestions.length === 0) {
    alert('Nu există întrebări generate. Te rog începe quiz-ul mai întâi!');
    return;
  }
  
  try {
    let answers = [];
    
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      answers = await processTextFile(file);
    } else if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      answers = await processPDFFile(file);
    } else {
      alert('Format de fișier nesuportat! Te rog folosește .txt sau .pdf');
      return;
    }
    
    if (answers.length === 0) {
      alert('Nu s-au găsit răspunsuri în document!');
      return;
    }
    
    // Populează răspunsurile
    for (let i = 0; i < Math.min(answers.length, quizQuestions.length); i++) {
      quizAnswers[i] = answers[i];
    }
    
    // Actualizează input-ul curent
    const answerInput = document.getElementById('quizAnswer');
    if (quizAnswers[currentQuestionIndex]) {
      answerInput.value = quizAnswers[currentQuestionIndex];
    }
    
    alert(`S-au încărcat ${Math.min(answers.length, quizQuestions.length)} răspunsuri din document!`);
    
    // Resetează input-ul de fișier
    fileInput.value = '';
    
  } catch (error) {
    console.error('Eroare la procesarea fișierului:', error);
    alert('Eroare la procesarea fișierului: ' + error.message);
  }
}

// Procesare fișier text
function processTextFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        // Împarte pe linii și filtrează liniile goale
        const answers = text.split('\n')
          .map(line => line.trim())
          .filter(line => line.length > 0);
        resolve(answers);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => reject(new Error('Eroare la citirea fișierului'));
    reader.readAsText(file);
  });
}

// Procesare fișier PDF
async function processPDFFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = async (e) => {
      try {
        const arrayBuffer = e.target.result;
        
        // Verifică dacă PDF.js este disponibil
        const pdfjs = window.pdfjsLib || window.pdfjs;
        if (!pdfjs) {
          reject(new Error('PDF.js nu este încărcat! Te rog reîncarcă pagina.'));
          return;
        }
        
        // Configurează PDF.js worker
        pdfjs.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';
        
        const loadingTask = pdfjs.getDocument({ data: arrayBuffer });
        const pdf = await loadingTask.promise;
        
        let fullText = '';
        
        // Citește toate paginile
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
          const page = await pdf.getPage(pageNum);
          const textContent = await page.getTextContent();
          const pageText = textContent.items.map(item => item.str).join('\n');
          fullText += pageText + '\n';
        }
        
        // Împarte pe linii și filtrează liniile goale
        const answers = fullText.split('\n')
          .map(line => line.trim())
          .filter(line => line.length > 0);
        
        resolve(answers);
      } catch (error) {
        reject(new Error('Eroare la procesarea PDF: ' + error.message));
      }
    };
    
    reader.onerror = () => reject(new Error('Eroare la citirea fișierului PDF'));
    reader.readAsArrayBuffer(file);
  });
}

async function finishQuiz() {
  // Check if all questions are answered
  const unanswered = quizQuestions.filter((q, i) => !quizAnswers[i].trim()).length;
  
  if (unanswered > 0) {
    if (!confirm(`Ai ${unanswered} întrebări fără răspuns. Vrei să finalizezi oricum?`)) {
      return;
    }
  }
  
  // Show loading state
  const finishBtn = document.getElementById('finishBtn');
  const originalFinishBtnText = finishBtn ? finishBtn.innerHTML : '';
  if (finishBtn) {
    finishBtn.disabled = true;
    finishBtn.innerHTML = '⏳ Se finalizează...';
  }
  
  const feedbackEl = document.getElementById('questionFeedback');
  if (feedbackEl) {
    feedbackEl.innerHTML = `
      <div style="margin-top: 16px; padding: 16px; border-radius: 10px; background: #edf2ff; color: #434190; text-align: center;">
        ⏳ Se evaluează răspunsurile finale...
      </div>
    `;
  }
  
  // Grade any remaining answers that were not submitted yet
  for (const [i, q] of quizQuestions.entries()) {
    if (!q.submitted && quizAnswers[i].trim()) {
      q.userAnswer = quizAnswers[i];
      try {
        if (q.type === 'nash') {
          q.result = await gradeNashAnswer(q, q.userAnswer);
        } else if (q.type === 'minmax') {
          q.result = await gradeMinMaxAnswer(q, q.userAnswer);
        } else if (q.type === 'strategy') {
          q.result = await gradeProblem1Answer(q, q.userAnswer);
        } else if (q.type === 'csp') {
          q.result = await gradeCSPAnswer(q, q.userAnswer);
        }
        q.submitted = true;
      } catch (error) {
        console.error('Error grading answer:', error);
      }
    }
  }
  
  // Restore button state
  if (finishBtn) {
    finishBtn.disabled = false;
    finishBtn.innerHTML = originalFinishBtnText;
  }

  quizFinished = true;

  // Calculate results
  let totalScore = 0;
  quizQuestions.forEach((q) => {
    if (q.result) {
      totalScore += q.result.score;
    }
  });
  
  const averageScore = quizQuestions.length > 0 
    ? (totalScore / quizQuestions.length).toFixed(2)
    : 0;

  // Salvăm quiz-ul în backend pentru a putea fi reluat ulterior
  try {
    const body = JSON.stringify({
      score: parseFloat(averageScore),
      question_count: quizQuestions.length,
      time_spent: timeSpentSeconds,
      config: quizConfig,
      questions: quizQuestions,
    });
    const resp = await fetch('api/save_quiz_result.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    });
    if (resp.ok) {
      const data = await resp.json();
      currentQuizId = data.id;
    }
  } catch (e) {
    console.error('Eroare la salvarea quiz-ului:', e);
  }
  
  // Oprește cronometrul
  stopQuizTimer();
  
  // Display results
  document.getElementById('quizSection').classList.remove('active');
  document.getElementById('resultsSection').classList.add('active');
  
  document.getElementById('quizScore').innerHTML = `
    <h2>Scor final: ${averageScore}%</h2>
    <p>Ai răspuns la ${quizQuestions.length} întrebări.</p>
    ${currentQuizId ? `<p style="margin-top:8px;font-size:0.9rem;color:#4a5568;">Acest quiz a fost salvat ca <strong>Test nr. ${currentQuizId}</strong> și poate fi reluat din profil.</p>` : ''}
  `;
  
  let detailsHTML = '<h4>Detalii pe întrebări:</h4>';
  quizQuestions.forEach((q, i) => {
    const score = q.result ? q.result.score : 0;
    const className = score === 100 ? 'correct' : score > 0 ? 'partial' : 'wrong';
    
    detailsHTML += `
      <div class="question-result ${className}">
        <strong>Întrebarea ${i + 1}</strong> (${
          q.type === 'nash' ? 'Problema 2: Echilibru Nash' :
          q.type === 'minmax' ? 'Problema 4: MinMax Alpha-Beta' :
          q.type === 'strategy' ? 'Problema 1: Identificare Strategie' :
          q.type === 'csp' ? 'Problema 3: CSP cu Backtracking' : q.type
        }): 
        <strong>${score}%</strong><br>
        <small>Răspunsul tău: ${q.userAnswer || '(necompletat)'}</small><br>
        ${q.result ? `<small>${q.result.feedback}</small>` : ''}
      </div>
    `;
  });
  
  document.getElementById('quizDetails').innerHTML = detailsHTML;
}

async function exportToPDF(mode = 'summary') {
  if (mode === 'summary') {
    const card = document.querySelector('#resultsSection .card');
    if (!card) {
      alert('Nu am găsit rezumatul pentru export.');
      return;
    }
    await captureElementToPDF(card, 'Rezumat');
  } else {
    const detailedView = buildDetailedPrintableView();
    document.body.appendChild(detailedView);
    await captureElementToPDF(detailedView, 'Detaliat');
    detailedView.remove();
  }
}

// Capture a DOM element exactly as seen in browser and paginate if needed
async function captureElementToPDF(element, label) {
  const { jsPDF } = window.jspdf;

  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    backgroundColor: getComputedStyle(document.body).backgroundColor || '#ffffff'
  });

  const imgData = canvas.toDataURL('image/png');
  const pdf = new jsPDF('p', 'pt', 'a4');
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;

  const imgWidth = pageWidth - margin * 2;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = margin;

  pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight);
  heightLeft -= (pageHeight - margin * 2);

  while (heightLeft > 0) {
    position = heightLeft - imgHeight + margin;
    pdf.addPage();
    pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight);
    heightLeft -= (pageHeight - margin * 2);
  }

  const timestamp = new Date().toISOString().slice(0, 10);
  pdf.save(`SmarTest_Quiz_${label}_${timestamp}.pdf`);
}

// Build a temporary detailed view that mirrors site styling
function buildDetailedPrintableView() {
  const container = document.createElement('div');
  container.style.width = '900px';
  container.style.margin = '0 auto';
  container.style.padding = '20px';

  const card = document.createElement('div');
  card.className = 'card';

  const header = document.createElement('div');
  header.className = 'quiz-results';
  const totalScore = quizQuestions.reduce((sum, q) => sum + (q.result ? q.result.score : 0), 0);
  const averageScore = quizQuestions.length ? (totalScore / quizQuestions.length).toFixed(2) : 0;
  header.innerHTML = `
    <h3>📋 Rezumat detaliat quiz</h3>
    <div id="quizScore"><h2>Scor final: ${averageScore}%</h2><p>Ai răspuns la ${quizQuestions.length} întrebări.</p></div>
  `;

  const list = document.createElement('div');
  list.style.marginTop = '16px';

  quizQuestions.forEach((q, idx) => {
    const cardQ = document.createElement('div');
    cardQ.className = 'quiz-question-card';

    const score = q.result ? q.result.score : 0;
    let scoreClass = 'wrong';
    if (score === 100) scoreClass = 'correct';
    else if (score > 0) scoreClass = 'partial';

    const treeText = q.type === 'minmax' && q.tree ? `<pre>${formatTreeForPDF(q.tree)}</pre>` : '';
    let statementText = '';
    let questionTitle = '';
    
    if (q.type === 'nash') {
      statementText = q.question_text || 'N/A';
      questionTitle = 'Problema 2: Echilibru Nash';
    } else if (q.type === 'minmax') {
      statementText = 'Arbore MinMax cu optimizare Alpha-Beta:';
      questionTitle = 'Problema 4: MinMax Alpha-Beta';
    } else if (q.type === 'strategy') {
      statementText = q.question_text || 'N/A';
      questionTitle = 'Problema 1: Identificare Strategie';
    } else if (q.type === 'csp') {
      statementText = q.question_text || 'N/A';
      questionTitle = 'Problema 3: CSP cu Backtracking';
    } else if (q.type === 'theory') {
      const theoryQ = q.question || q;
      statementText = theoryQ.question_text || 'N/A';
      questionTitle = `Întrebare Teorie: ${theoryQ.topic_name || 'Teorie'}`;
      if (theoryQ.theory_type === 'multiple_choice' && theoryQ.options) {
        statementText += '\n\nOpțiuni:';
        theoryQ.options.forEach((opt, idx) => {
          statementText += `\n${idx + 1}. ${opt}`;
        });
      }
    } else {
      statementText = q.question_text || 'N/A';
      questionTitle = q.type;
    }

    cardQ.innerHTML = `
      <h4 style="margin-top:0;">Întrebarea ${idx + 1} - ${questionTitle}</h4>
      <div style="background:#1a202c;color:#e2e8f0;padding:10px;border-radius:6px;margin-bottom:10px;">
        <strong>Enunț:</strong>
        <div style="margin-top:6px;white-space:pre-wrap;font-family:monospace;font-size:12px;">${statementText}</div>
        ${treeText}
      </div>
      <p><strong>Răspunsul tău:</strong> ${q.userAnswer || '(necompletat)'}</p>
      <div class="question-result ${scoreClass}" style="margin:10px 0;">
        <strong>Scor: ${score}%</strong><br>
        ${q.result && q.result.feedback ? `<small>${q.result.feedback}</small>` : ''}
      </div>
      ${q.solution?.explanation ? `<div style="background:#f9f9f9;border:1px solid #e2e8f0;border-radius:6px;padding:10px;"><strong>Soluția corectă:</strong><br><pre style="white-space:pre-wrap;font-family:monospace;font-size:12px;margin:4px 0 0;">${q.solution.explanation}</pre></div>` : ''}
    `;

    list.appendChild(cardQ);
  });

  card.appendChild(header);
  card.appendChild(list);
  container.appendChild(card);
  return container;
}

// Helper function to add page header
function addPageHeader(doc) {
  const pageWidth = doc.internal.pageSize.width;
  
  // Purple gradient background simulation
  doc.setFillColor(102, 126, 234); // #667eea
  doc.rect(0, 0, pageWidth, 35, 'F');
  
  // Title
  doc.setFontSize(20);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(255, 255, 255);
  doc.text('SmarTest', pageWidth / 2, 22, { align: 'center' });
}

function exportSummaryPDF(doc) {
  const pageWidth = doc.internal.pageSize.width;
  const pageHeight = doc.internal.pageSize.height;
  let yPos = 45;
  
  // Header
  addPageHeader(doc);
  
  // Main content area - white card background (simulating .card style)
  doc.setDrawColor(226, 232, 240); // #e2e8f0
  doc.setLineWidth(0.5);
  doc.setFillColor(255, 255, 255);
  doc.roundedRect(10, 40, pageWidth - 20, pageHeight - 50, 3, 3, 'S');
  
  // Quiz results section (simulating .quiz-results style)
  doc.setFillColor(240, 255, 244); // #f0fff4
  doc.setDrawColor(154, 230, 180); // #9ae6b4
  doc.setLineWidth(0.8);
  doc.roundedRect(15, yPos, pageWidth - 30, 35, 3, 3, 'FD');
  
  // Title "Rezultate Quiz" with emoji
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(34, 84, 61); // #22543d
  doc.text('📊 Rezultate Quiz', 20, yPos + 10);
  
  // Score
  const totalScore = quizQuestions.reduce((sum, q) => 
    sum + (q.result ? q.result.score : 0), 0);
  const averageScore = (totalScore / quizQuestions.length).toFixed(2);
  
  doc.setFontSize(14);
  doc.text(`Scor final: ${averageScore}%`, 20, yPos + 20);
  
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(74, 85, 104); // #4a5568
  doc.text(`Ai răspuns la ${quizQuestions.length} întrebări.`, 20, yPos + 28);
  
  yPos += 45;
  
  // "Detalii pe întrebări:" title
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(45, 55, 72); // #2d3748
  doc.text('Detalii pe întrebări:', 20, yPos);
  
  yPos += 10;
  
  // Question results (simulating .question-result cards)
  quizQuestions.forEach((q, i) => {
    const score = q.result ? q.result.score : 0;
    
    // Check if we need a new page
    if (yPos > pageHeight - 40) {
      doc.addPage();
      addPageHeader(doc);
      yPos = 45;
    }
    
    // Card background - white
    doc.setFillColor(255, 255, 255);
    doc.setDrawColor(226, 232, 240);
    doc.setLineWidth(0.3);
    doc.roundedRect(20, yPos, pageWidth - 40, 28, 2, 2, 'FD');
    
    // Left border color based on score (simulating .correct, .partial, .wrong)
    let borderColor;
    if (score === 100) {
      borderColor = [72, 187, 120]; // #48bb78 green
    } else if (score > 0) {
      borderColor = [237, 137, 54]; // #ed8936 orange
    } else {
      borderColor = [229, 62, 62]; // #e53e3e red
    }
    doc.setFillColor(...borderColor);
    doc.rect(20, yPos, 3, 28, 'F'); // 4px solid left border
    
    // Question text
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(45, 55, 72);
    doc.text(`Întrebarea ${i + 1}`, 28, yPos + 6);
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(74, 85, 104);
    const typeLabel = q.type === 'nash' ? 'Problema 2: Nash' :
                     q.type === 'minmax' ? 'Problema 4: MinMax' :
                     q.type === 'strategy' ? 'Problema 1: Strategie' :
                     q.type === 'csp' ? 'Problema 3: CSP' : q.type;
    doc.text(`(${typeLabel}): `, 55, yPos + 6);
    
    doc.setFont('helvetica', 'bold');
    doc.text(`${score}%`, 85, yPos + 6);
    
    // Answer
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.setTextColor(74, 85, 104);
    const answerText = `Răspunsul tău: ${q.userAnswer || '(necompletat)'}`;
    const answerLines = doc.splitTextToSize(answerText, pageWidth - 60);
    doc.text(answerLines[0], 28, yPos + 13);
    
    // Feedback
    if (q.result && q.result.feedback) {
      const feedbackText = q.result.feedback.substring(0, 100) + (q.result.feedback.length > 100 ? '...' : '');
      const feedbackLines = doc.splitTextToSize(feedbackText, pageWidth - 60);
      doc.text(feedbackLines.slice(0, 2), 28, yPos + 19);
    }
    
    yPos += 33;
  });
  
  // Footer
  doc.setFontSize(8);
  doc.setTextColor(160, 174, 192);
  doc.text(`Generat pe ${new Date().toLocaleDateString('ro-RO')}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
}

function exportDetailedPDF(doc) {
  const pageWidth = doc.internal.pageSize.width;
  const pageHeight = doc.internal.pageSize.height;
  let yPos = 45;
  
  // Header
  addPageHeader(doc);
  
  // Main white card background
  doc.setDrawColor(226, 232, 240);
  doc.setLineWidth(0.5);
  doc.setFillColor(255, 255, 255);
  doc.roundedRect(10, 40, pageWidth - 20, pageHeight - 50, 3, 3, 'S');
  
  // Quiz results header section
  doc.setFillColor(240, 255, 244);
  doc.setDrawColor(154, 230, 180);
  doc.setLineWidth(0.8);
  doc.roundedRect(15, yPos, pageWidth - 30, 35, 3, 3, 'FD');
  
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(34, 84, 61);
  doc.text('📊 Rezultate Quiz - Detaliat', 20, yPos + 10);
  
  const totalScore = quizQuestions.reduce((sum, q) => 
    sum + (q.result ? q.result.score : 0), 0);
  const averageScore = (totalScore / quizQuestions.length).toFixed(2);
  
  doc.setFontSize(14);
  doc.text(`Scor final: ${averageScore}%`, 20, yPos + 20);
  
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(74, 85, 104);
  doc.text(`Ai răspuns la ${quizQuestions.length} întrebări.`, 20, yPos + 28);
  
  yPos += 45;
  
  // Each question in detail
  quizQuestions.forEach((q, i) => {
    // Check if we need a new page
    if (yPos > pageHeight - 100) {
      doc.addPage();
      addPageHeader(doc);
      yPos = 45;
    }
    
    const score = q.result ? q.result.score : 0;
    
    // Question header (simulating quiz-question-card style)
    doc.setFillColor(247, 250, 252); // #f7fafc
    doc.setDrawColor(226, 232, 240);
    doc.setLineWidth(0.3);
    doc.roundedRect(15, yPos, pageWidth - 30, 10, 2, 2, 'FD');
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(102, 126, 234); // #667eea
    const questionTitle = q.type === 'nash' ? 'Problema 2: Echilibru Nash' :
                         q.type === 'minmax' ? 'Problema 4: MinMax Alpha-Beta' :
                         q.type === 'strategy' ? 'Problema 1: Identificare Strategie' :
                         q.type === 'csp' ? 'Problema 3: CSP cu Backtracking' : q.type;
    doc.text(`Întrebarea ${i + 1} - ${questionTitle}`, 20, yPos + 7);
    
    yPos += 15;
    
    // Question text in code-like box (simulating pre style)
    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(45, 55, 72);
    doc.text('Enunț:', 20, yPos);
    yPos += 6;
    
    // Code-like background
    doc.setFillColor(26, 32, 44); // #1a202c - dark background like pre
    doc.setDrawColor(45, 55, 72);
    
    let questionHeight = 30;
    let questionText = '';
    
    if (q.type === 'nash' || q.type === 'strategy' || q.type === 'csp') {
      questionText = q.question_text || 'N/A';
      const lines = doc.splitTextToSize(questionText, pageWidth - 50);
      questionHeight = Math.min(lines.length * 4 + 8, 50);
    } else if (q.type === 'minmax') {
      questionText = 'Arbore MinMax cu optimizare Alpha-Beta:';
      questionHeight = 45;
    }
    
    doc.roundedRect(20, yPos - 3, pageWidth - 40, questionHeight, 2, 2, 'FD');
    
    doc.setFont('courier', 'normal');
    doc.setFontSize(7);
    doc.setTextColor(226, 232, 240); // #e2e8f0 - light text on dark
    
    if (q.type === 'nash' || q.type === 'strategy' || q.type === 'csp') {
      const questionLines = doc.splitTextToSize(questionText, pageWidth - 50);
      questionLines.slice(0, 10).forEach((line, idx) => {
        doc.text(line, 25, yPos + 2 + (idx * 4));
      });
    } else if (q.type === 'minmax') {
      doc.text('Arbore MinMax cu optimizare Alpha-Beta:', 25, yPos + 2);
      if (q.tree) {
        const treeText = formatTreeForPDF(q.tree);
        const treeLines = doc.splitTextToSize(treeText, pageWidth - 50);
        treeLines.slice(0, 8).forEach((line, idx) => {
          doc.text(line, 25, yPos + 7 + (idx * 4));
        });
      }
    }
    
    yPos += questionHeight + 5;
    
    // Answer section
    doc.setFillColor(247, 250, 252);
    doc.setDrawColor(226, 232, 240);
    doc.roundedRect(20, yPos, pageWidth - 40, 12, 2, 2, 'FD');
    
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    doc.setTextColor(74, 85, 104);
    doc.text('Răspunsul tău:', 25, yPos + 5);
    
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(45, 55, 72);
    const answerText = q.userAnswer || '(necompletat)';
    doc.text(answerText, 25, yPos + 9);
    
    yPos += 17;
    
    // Score section with colored background
    let scoreBg, scoreBorder, scoreText;
    if (score === 100) {
      scoreBg = [198, 246, 213]; // #c6f6d5
      scoreBorder = [154, 230, 180]; // #9ae6b4
      scoreText = [34, 84, 61]; // #22543d
    } else if (score > 0) {
      scoreBg = [254, 243, 199]; // #fef3c7
      scoreBorder = [251, 191, 36]; // #fbbf24
      scoreText = [124, 45, 18]; // #7c2d12
    } else {
      scoreBg = [254, 215, 215]; // #fed7d7
      scoreBorder = [252, 129, 129]; // #fc8181
      scoreText = [116, 42, 42]; // #742a2a
    }
    
    doc.setFillColor(...scoreBg);
    doc.setDrawColor(...scoreBorder);
    doc.setLineWidth(0.5);
    doc.roundedRect(20, yPos, pageWidth - 40, 10, 2, 2, 'FD');
    
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.setTextColor(...scoreText);
    doc.text(`Scor: ${score}%`, 25, yPos + 6);
    
    yPos += 15;
    
    // Feedback
    if (q.result && q.result.feedback) {
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8);
      doc.setTextColor(74, 85, 104);
      const feedbackLines = doc.splitTextToSize(q.result.feedback, pageWidth - 50);
      feedbackLines.slice(0, 3).forEach((line, idx) => {
        if (yPos + (idx * 4) < pageHeight - 30) {
          doc.text(line, 25, yPos + (idx * 4));
        }
      });
      yPos += Math.min(feedbackLines.length * 4, 12) + 5;
    }
    
    // Solution section
    if (yPos > pageHeight - 35) {
      doc.addPage();
      addPageHeader(doc);
      yPos = 45;
    }
    
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    doc.setTextColor(102, 126, 234);
    doc.text('Soluția corectă:', 25, yPos);
    yPos += 6;
    
    // Solution in code box
    doc.setFillColor(249, 249, 249); // #f9f9f9
    doc.setDrawColor(226, 232, 240);
    const solutionText = q.solution?.explanation || 'N/A';
    const solutionLines = doc.splitTextToSize(solutionText, pageWidth - 50);
    const solutionHeight = Math.min(solutionLines.length * 3.5 + 6, 30);
    
    doc.roundedRect(20, yPos - 2, pageWidth - 40, solutionHeight, 2, 2, 'FD');
    
    doc.setFont('courier', 'normal');
    doc.setFontSize(6.5);
    doc.setTextColor(45, 55, 72);
    
    solutionLines.slice(0, 8).forEach((line, idx) => {
      doc.text(line, 25, yPos + 2 + (idx * 3.5));
    });
    
    yPos += solutionHeight + 10;
    
    // Separator line between questions
    if (i < quizQuestions.length - 1 && yPos < pageHeight - 20) {
      doc.setDrawColor(226, 232, 240);
      doc.setLineWidth(0.2);
      doc.line(20, yPos, pageWidth - 20, yPos);
      yPos += 8;
    }
  });
  
  // Footer
  if (yPos > pageHeight - 15) {
    doc.addPage();
  }
  doc.setFontSize(8);
  doc.setTextColor(160, 174, 192);
  doc.text(`Generat pe ${new Date().toLocaleDateString('ro-RO')}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
}

function formatTreeForPDF(node, prefix = '', isLast = true) {
  let result = '';
  const marker = isLast ? '└── ' : '├── ';
  const nodeInfo = node.type === 'LEAF' 
    ? `${node.id} (${node.type}): ${node.value}`
    : `${node.id} (${node.type})`;
  
  result += prefix + marker + nodeInfo + '\n';
  
  if (node.children && node.children.length > 0) {
    const newPrefix = prefix + (isLast ? '    ' : '│   ');
    node.children.forEach((child, i) => {
      result += formatTreeForPDF(child, newPrefix, i === node.children.length - 1);
    });
  }
  
  return result;
}

// Încarcă un quiz salvat pentru rejucare (din profil)
async function loadQuizReplay(quizId) {
  try {
    const resp = await fetch(`api/get_quiz_result.php?id=${encodeURIComponent(quizId)}`);
    if (!resp.ok) {
      alert('Nu am putut încărca quiz-ul salvat. Te rog verifică conexiunea.');
      console.error('Nu am putut încărca quiz-ul salvat');
      return;
    }
    const data = await resp.json();
    if (!data || !data.payload) {
      alert('Date de quiz invalide. Te rog încearcă din nou.');
      console.error('Date de quiz invalide sau lipsă payload');
      return;
    }

    // Configurăm starea pentru replay - EXACT ca pentru un quiz nou
    isReplayMode = true;
    currentQuizId = null; // Nu salvăm peste quiz-ul existent
    quizConfig = Array.isArray(data.payload.config) ? data.payload.config : [];
    
    // Încărcăm întrebările și resetăm complet răspunsurile și rezultatele
    quizQuestions = Array.isArray(data.payload.questions) ? data.payload.questions.map(q => {
      return {
        ...q,
        userAnswer: '',      // Resetează răspunsul utilizatorului
        submitted: false,    // Resetează status de submitare
        result: null         // Resetează rezultatul evaluării
      };
    }) : [];
    
    // Inițializăm array-ul de răspunsuri gol
    quizAnswers = new Array(quizQuestions.length).fill('');
    quizResults = [];
    currentQuestionIndex = 0;
    quizFinished = false;
    timeSpentSeconds = 0;
    
    // Start timer pentru replay
    startQuizTimer();

    // Ascundem zona de configurare și rezultate, arătăm quiz-ul
    const setupSection = document.getElementById('setupSection');
    const quizSection = document.getElementById('quizSection');
    const resultsSection = document.getElementById('resultsSection');
    if (setupSection) setupSection.classList.remove('active');
    if (resultsSection) resultsSection.classList.remove('active');
    if (quizSection) quizSection.classList.add('active');

    // Afișăm prima întrebare exact cum a fost salvată, cu interfață curată
    displayQuestion(0);
    
    console.log(`Quiz ${quizId} încărcat cu ${quizQuestions.length} întrebări pentru reluare.`);
  } catch (e) {
    alert('Eroare la încărcarea quiz-ului: ' + e.message);
    console.error('Eroare la încărcarea quiz-ului salvat:', e);
  }
}

// Initialize on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Funcții pentru cronometru
function startQuizTimer() {
  quizStartTime = Date.now();
  updateTimerDisplay();
  
  // Actualizează afișajul la fiecare secundă
  quizTimerInterval = setInterval(() => {
    timeSpentSeconds = Math.floor((Date.now() - quizStartTime) / 1000);
    updateTimerDisplay();
  }, 1000);
}

function stopQuizTimer() {
  if (quizTimerInterval) {
    clearInterval(quizTimerInterval);
    quizTimerInterval = null;
  }
  if (quizStartTime) {
    timeSpentSeconds = Math.floor((Date.now() - quizStartTime) / 1000);
  }
}

function updateTimerDisplay() {
  const timerEl = document.getElementById('quizTimer');
  if (!timerEl) return;
  
  const hours = Math.floor(timeSpentSeconds / 3600);
  const minutes = Math.floor((timeSpentSeconds % 3600) / 60);
  const seconds = timeSpentSeconds % 60;
  
  let timeStr = '';
  if (hours > 0) {
    timeStr = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  } else {
    timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }
  
  timerEl.textContent = `⏱️ ${timeStr}`;
}

function formatTime(seconds) {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (minutes < 60) {
    return `${minutes}m ${secs}s`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
}