const USE_PROXY = true;          
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
    levelLabel.className = "tree-level-label";
    const levelType = levelNodes[0]?.type || "MAX";
    levelLabel.textContent = levelType;
    levelDiv.appendChild(levelLabel);
    
    const nodesContainer = document.createElement("div");
    nodesContainer.style.display = "flex";
    nodesContainer.style.justifyContent = "center";
    nodesContainer.style.alignItems = "center";
    nodesContainer.style.gap = `${horizontalSpacing}px`;
    nodesContainer.style.width = "100%";
    nodesContainer.style.flexWrap = "nowrap";
    nodesContainer.style.paddingLeft = "80px"; 
    
    levelNodes.forEach((nodeInfo, nodeIndex) => {
      const nodeDiv = document.createElement("div");
      const isVisited = nodeInfo.visited;
      const nodeType = nodeInfo.type.toLowerCase();
      
      let className = 'tree-node';
      if (nodeType === 'max') className += ' max';
      else if (nodeType === 'min') className += ' min';
      else if (nodeType === 'leaf') className += ' leaf';
      if (isVisited) className += ' visited';
      
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
                  console.warn(`Invalid coordinates for line from ${parentInfo.id} to ${nodeInfo.id}`);
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

async function loadQuestion() {
  try {
    const depth = document.getElementById("depth").value;
    const branching = document.getElementById("branching").value;
    const valueMin = document.getElementById("valueMin").value;
    const valueMax = document.getElementById("valueMax").value;
    const seed = document.getElementById("seed").value;
    const q = await callGenerate(depth, branching, valueMin, valueMax, seed);
    currentPayload = q;
    
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


function solveMinMaxAlphaBeta(depth, branching, leaves) {
  let visitedIndices = [];
  let log = [];
  let leafPos = 0;

  function minmax(level, maximizingPlayer, alpha, beta) {
    if (level === depth - 1) {
      const value = leaves[leafPos];
      visitedIndices.push(leafPos);
      log.push(
        `Frunză #${leafPos}: valoare=${value}, α=${alpha}, β=${beta}`
      );
      leafPos++;
      return value;
    }

    if (maximizingPlayer) {
      let value = -Infinity;
      log.push(`MAX la nivel ${level}, α=${alpha}, β=${beta}`);
      for (let i = 0; i < branching; i++) {
        const childVal = minmax(level + 1, false, alpha, beta);
        value = Math.max(value, childVal);
        alpha = Math.max(alpha, value);
        log.push(`  → copil ${i}: value=${value}, α=${alpha}, β=${beta}`);
        if (beta <= alpha) {
          log.push(`  ❌ tăiere (beta cut-off) la copilul ${i}`);
          break;
        }
      }
      return value;
    } else {
      let value = Infinity;
      log.push(`MIN la nivel ${level}, α=${alpha}, β=${beta}`);
      for (let i = 0; i < branching; i++) {
        const childVal = minmax(level + 1, true, alpha, beta);
        value = Math.min(value, childVal);
        beta = Math.min(beta, value);
        log.push(`  → copil ${i}: value=${value}, α=${alpha}, β=${beta}`);
        if (beta <= alpha) {
          log.push(`  ❌ tăiere (alpha cut-off) la copilul ${i}`);
          break;
        }
      }
      return value;
    }
  }

  const rootValue = minmax(0, true, -Infinity, Infinity);
  return {
    rootValue,
    visitedLeaves: visitedIndices.length,
    log: log.join("\n")
  };
}

let customDepthInput, customBranchingInput, customLeavesInput,
    customHint, solveCustomBtn, customResult, customSolution;

function initCustomExercise() {
  customDepthInput = document.getElementById("customDepth");
  customBranchingInput = document.getElementById("customBranching");
  customLeavesInput = document.getElementById("customLeaves");
  customHint = document.getElementById("customHint");
  solveCustomBtn = document.getElementById("solveCustomBtn");
  customResult = document.getElementById("customResult");
  customSolution = document.getElementById("customSolution");

  if (!customDepthInput || !customBranchingInput || !customLeavesInput || !solveCustomBtn) {
    return;
  }

  function updateCustomHint() {
    const d = parseInt(customDepthInput.value, 10);
    const b = parseInt(customBranchingInput.value, 10);
    if (!isNaN(d) && !isNaN(b) && d >= 2 && b >= 2) {
      const leavesCount = Math.pow(b, d - 1);
      if (customHint) {
        customHint.textContent =
          `Trebuie să introduci exact ${leavesCount} valori de frunză (arbore complet cu ${d} niveluri și factor ${b}).`;
      }
    } else if (customHint) {
      customHint.textContent = "";
    }
  }

  customDepthInput.addEventListener("input", updateCustomHint);
  customBranchingInput.addEventListener("input", updateCustomHint);
  updateCustomHint();

  solveCustomBtn.addEventListener("click", () => {
    const d = parseInt(customDepthInput.value, 10);
    const b = parseInt(customBranchingInput.value, 10);

    if (isNaN(d) || isNaN(b) || d < 2 || b < 2) {
      if (customResult) {
        customResult.textContent = "Te rog completează corect adâncimea și factorul de ramificare.";
        customResult.style.color = "red";
      }
      return;
    }

    const expectedLeaves = Math.pow(b, d - 1);

    const parts = customLeavesInput.value
      .split(/[\s,;]+/)
      .filter(x => x.trim().length > 0);

    if (parts.length !== expectedLeaves) {
      if (customResult) {
        customResult.textContent =
          `Număr incorect de frunze: ai introdus ${parts.length}, dar pentru acest arbore ai nevoie de ${expectedLeaves}.`;
        customResult.style.color = "red";
      }
      if (customSolution) customSolution.textContent = "";
      return;
    }

    const leaves = parts.map(Number);
    if (leaves.some(v => Number.isNaN(v))) {
      if (customResult) {
        customResult.textContent = "Toate valorile frunzelor trebuie să fie numere (int/float).";
        customResult.style.color = "red";
      }
      if (customSolution) customSolution.textContent = "";
      return;
    }

    try {
      const { rootValue, visitedLeaves, log } = solveMinMaxAlphaBeta(d, b, leaves);
      if (customResult) {
        customResult.textContent =
          `Valoarea din rădăcină: ${rootValue}, frunze vizitate: ${visitedLeaves}.`;
        customResult.style.color = "green";
      }
      if (customSolution) customSolution.textContent = log;
    } catch (e) {
      console.error(e);
      if (customResult) {
        customResult.textContent = "A apărut o eroare la calcul. Verifică datele introduse.";
        customResult.style.color = "red";
      }
      if (customSolution) customSolution.textContent = e?.message || "";
    }
  });
}


function setMode(mode) {
  const solveSection = document.getElementById("solveSection");
  const customSection = document.getElementById("customSection");
  const buttons = document.querySelectorAll(".mode-btn");

  if (!solveSection || !customSection) {
    return;
  }

  if (mode === "solve") {
    solveSection.style.display = "";
    customSection.style.display = "none";
  } else if (mode === "custom") {
    solveSection.style.display = "none";
    customSection.style.display = "";
  }

  buttons.forEach(btn => {
    if (btn.dataset.mode === mode) {
      btn.classList.add("active-mode");
    } else {
      btn.classList.remove("active-mode");
    }
  });
}

function initPage() {
  const genBtn = document.getElementById("genBtn");
  const gradeBtn = document.getElementById("gradeBtn");
  if (genBtn) genBtn.addEventListener("click", loadQuestion);
  if (gradeBtn) gradeBtn.addEventListener("click", gradeAnswer);

  initCustomExercise();

  const modeButtons = document.querySelectorAll(".mode-btn");
  modeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const mode = btn.dataset.mode;
      setMode(mode);
    });
  });

  setMode("solve");
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPage);
} else {
  initPage();
}
