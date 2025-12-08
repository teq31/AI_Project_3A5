const USE_PROXY = true;          // true = chem PHP proxy (fără CORS); false = chem direct FastAPI
const API = "http://127.0.0.1:8000";

let currentPayload = null;

async function callGenerate(depth, branching, valueMin, valueMax, seed) {
  if (USE_PROXY) {
    const url = `api/proxy_minmax_generate.php?depth=${depth}&branching=${branching}&valueMin=${valueMin}&valueMax=${valueMax}${seed!==''?`&seed=${seed}`:''}`;
    const r = await fetch(url);
    return await r.json();
  } else {
    const url = `${API}/minmax/generate?depth=${depth}&branching_factor=${branching}&value_min=${valueMin}&value_max=${valueMax}${seed!==''?`&seed=${seed}`:''}`;
    const r = await fetch(url);
    return await r.json();
  }
}

async function callGrade(payload, answer) {
  const body = JSON.stringify({ payload, answer });
  if (USE_PROXY) {
    const r = await fetch("api/proxy_minmax_grade.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body
    });
    return await r.json();
  } else {
    const r = await fetch(`${API}/minmax/grade`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body
    });
    return await r.json();
  }
}

function drawTree(treeData, visitedLeaves = []) {
  const container = document.getElementById("treeVisualization");
  if (!container) {
    console.error("Tree visualization container not found!");
    return;
  }
  
  container.innerHTML = "";
  
  if (!treeData) {
    console.error("Tree data is missing!");
    return;
  }
  
  console.log("Drawing tree:", treeData, "Visited leaves:", visitedLeaves);
  
  // Construiește structura nivelurilor
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
  
  // Calculează spacing adaptiv
  const maxNodesPerLevel = Math.max(...levels.map(level => level.length));
  const nodeWidth = 80;
  const horizontalSpacing = Math.max(50, Math.min(100, 900 / Math.max(maxNodesPerLevel, 1)));
  const verticalSpacing = 100;
  
  // Creează container pentru arbore
  const treeWrapper = document.createElement("div");
  treeWrapper.className = "tree-wrapper";
  treeWrapper.style.position = "relative";
  treeWrapper.style.width = "100%";
  treeWrapper.style.minHeight = `${levels.length * verticalSpacing}px`;
  treeWrapper.style.padding = "20px";
  
  // Creează SVG pentru linii
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
  
  // Desenează fiecare nivel
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
    
    // Eticheta nivelului pe stânga (poziționată absolut)
    const levelLabel = document.createElement("div");
    levelLabel.className = "tree-level-label";
    const levelType = levelNodes[0]?.type || "MAX";
    levelLabel.textContent = levelType;
    levelDiv.appendChild(levelLabel);
    
    // Container pentru noduri - centrat
    const nodesContainer = document.createElement("div");
    nodesContainer.style.display = "flex";
    nodesContainer.style.justifyContent = "center";
    nodesContainer.style.alignItems = "center";
    nodesContainer.style.gap = `${horizontalSpacing}px`;
    nodesContainer.style.width = "100%";
    nodesContainer.style.flexWrap = "nowrap";
    nodesContainer.style.paddingLeft = "80px"; // Spațiu pentru etichetă
    
    levelNodes.forEach((nodeInfo, nodeIndex) => {
      const nodeDiv = document.createElement("div");
      const isVisited = nodeInfo.visited;
      const nodeType = nodeInfo.type.toLowerCase();
      
      // Construiește clasa corect
      let className = 'tree-node';
      if (nodeType === 'max') className += ' max';
      else if (nodeType === 'min') className += ' min';
      else if (nodeType === 'leaf') className += ' leaf';
      if (isVisited) className += ' visited';
      
      nodeDiv.className = className;
      nodeDiv.id = `node-${nodeInfo.id}`;
      nodeDiv.style.position = "relative";
      nodeDiv.style.flexShrink = "0";
      
      // Doar ID-ul nodului
      const labelDiv = document.createElement("div");
      labelDiv.className = "tree-node-label";
      labelDiv.textContent = nodeInfo.id;
      
      // Doar valoarea (fără "?")
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
  
  // Adaugă SVG și wrapper-ul în container
  treeWrapper.appendChild(svg);
  container.appendChild(treeWrapper);
  
  // Desenează liniile după ce nodurile sunt poziționate
  // Folosim requestAnimationFrame pentru a ne asigura că toate elementele sunt renderate
  requestAnimationFrame(() => {
    setTimeout(() => {
      try {
        const wrapperRect = treeWrapper.getBoundingClientRect();
        const svgWidth = Math.max(wrapperRect.width, maxNodesPerLevel * (nodeWidth + horizontalSpacing) + 40);
        const svgHeight = levels.length * verticalSpacing + 40;
        
        svg.setAttribute("width", svgWidth);
        svg.setAttribute("height", svgHeight);
        svg.setAttribute("viewBox", `0 0 ${svgWidth} ${svgHeight}`);
        
        // Desenează liniile pentru fiecare nivel
        levels.forEach((levelNodes, levelIndex) => {
          if (levelIndex === 0) return; // skip root level
          
          levelNodes.forEach((nodeInfo) => {
            const childElement = document.getElementById(`node-${nodeInfo.id}`);
            if (!childElement) return;
            
            // Găsește părintele
            const parentInfo = Array.from(nodeMap.values()).find(n => 
              n.children && n.children.some(c => c.id === nodeInfo.id)
            );
            
            if (parentInfo) {
              const parentElement = document.getElementById(`node-${parentInfo.id}`);
              if (parentElement) {
                // Recalculează pozițiile pentru a fi siguri că sunt corecte
                const parentRect = parentElement.getBoundingClientRect();
                const childRect = childElement.getBoundingClientRect();
                
                // Calculează pozițiile relative la wrapper
                // Punctul de pornire: centrul orizontal, exact la marginea de jos a nodului părinte
                const x1 = parentRect.left + parentRect.width / 2 - wrapperRect.left;
                const y1 = parentRect.top + parentRect.height - wrapperRect.top;
                
                // Punctul de sosire: centrul orizontal, exact la marginea de sus a nodului copil
                // Extindem linia mai jos pentru a atinge efectiv nodul (ținând cont de border de 2px)
                const x2 = childRect.left + childRect.width / 2 - wrapperRect.left;
                // Calculăm poziția exactă a marginii de sus a nodului (ținând cont de border)
                // getBoundingClientRect() include border-ul, deci trebuie să adăugăm mai mult pentru a atinge efectiv
                const borderWidth = 2; // border-ul nodului
                const y2 = childRect.top - wrapperRect.top + borderWidth + 4; // +4px pentru a atinge efectiv nodul
                
                // Verifică că avem coordonate valide
                if (isNaN(x1) || isNaN(y1) || isNaN(x2) || isNaN(y2)) {
                  console.warn(`Invalid coordinates for line from ${parentInfo.id} to ${nodeInfo.id}`);
                  return;
                }
                
                // Creează linia care conectează exact marginile nodurilor
                // Extindem linia puțin mai jos pentru a se asigura că atinge nodul copil
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", x1);
                line.setAttribute("y1", y1);
                line.setAttribute("x2", x2);
                line.setAttribute("y2", y2);
                line.setAttribute("stroke", "#333");
                line.setAttribute("stroke-width", "2.5");
                line.setAttribute("stroke-linecap", "round");
                // Asigură-te că linia se extinde până la marginea efectivă a nodului
                line.setAttribute("stroke-linejoin", "round");
                svg.appendChild(line);
              }
            }
          });
        });
      } catch (error) {
        console.error("Error drawing tree lines:", error);
      }
    }, 200); // Mărit timpul de așteptare pentru a se asigura că toate elementele sunt renderate
  });
}

async function loadQuestion() {
  try {
    const depth = document.getElementById("depth").value;
    const branching = document.getElementById("branching").value;
    const valueMin = document.getElementById("valueMin").value;
    const valueMax = document.getElementById("valueMax").value;
    const seed = document.getElementById("seed").value;
    const q = await callGenerate(depth, branching, valueMin, valueMax, seed);
    currentPayload = q;
    
    // Desenează arborele vizual
    const treeContainer = document.getElementById("treeVisualization");
    if (treeContainer && q.tree) {
      drawTree(q.tree, q.solution.visited_leaves || []);
    } else {
      console.error("Tree container or tree data missing", { treeContainer, hasTree: !!q.tree });
    }
    
    const solutionEl = document.getElementById("solution");
    if (solutionEl) {
      solutionEl.textContent = q.solution.explanation;
    }
    
    const resultEl = document.getElementById("result");
    if (resultEl) {
      resultEl.innerHTML = "";
    }
    
    const answerEl = document.getElementById("answer");
    if (answerEl) {
      answerEl.value = "";
    }
  } catch (error) {
    console.error("Error loading question:", error);
    alert("Eroare la încărcarea întrebării: " + error.message);
  }
}

async function gradeAnswer() {
  if (!currentPayload) {
    alert("Te rog generează mai întâi o întrebare!");
    return;
  }
  const answerEl = document.getElementById("answer");
  if (!answerEl) {
    console.error("Answer input not found!");
    return;
  }
  const answer = answerEl.value.trim();
  if (!answer) {
    alert("Te rog introdu un răspuns!");
    return;
  }
  try {
    const res = await callGrade(currentPayload, answer);
    const resultEl = document.getElementById("result");
    if (resultEl) {
      resultEl.innerHTML = `<strong>Scor: ${res.score}%</strong><br>${res.feedback}`;
    } else {
      console.error("Result element not found!");
    }
  } catch (error) {
    console.error("Error grading answer:", error);
    alert("Eroare la evaluarea răspunsului: " + error.message);
  }
}

// Așteaptă ca DOM-ul să fie complet încărcat
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    const genBtn = document.getElementById("genBtn");
    const gradeBtn = document.getElementById("gradeBtn");
    if (genBtn) genBtn.addEventListener("click", loadQuestion);
    if (gradeBtn) gradeBtn.addEventListener("click", gradeAnswer);
    // Nu încărca automat întrebarea la start
  });
} else {
  const genBtn = document.getElementById("genBtn");
  const gradeBtn = document.getElementById("gradeBtn");
  if (genBtn) genBtn.addEventListener("click", loadQuestion);
  if (gradeBtn) gradeBtn.addEventListener("click", gradeAnswer);
}

