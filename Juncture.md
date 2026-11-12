<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Juncture — Guitar Toolkit</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }
  
  body {
    background-color: #09090b;
    color: #e4e4e7;
    font-family: 'IBM Plex Mono', monospace;
    padding: 2rem 1rem;
    display: flex;
    justify-content: center;
  }

  .container {
    width: 100%;
    max-width: 800px;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  /* HEADER */
  .header { margin-bottom: 0.5rem; }
  .eyebrow {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #71717a;
    margin-bottom: 0.5rem;
  }
  .title {
    font-size: 3.5rem;
    font-weight: 600;
    line-height: 1;
    letter-spacing: -0.02em;
    color: #fafafa;
  }
  .title span { color: #a3e635; } /* Neon green */
  
  .status-bar {
    background: #121212;
    border: 1px solid #27272a;
    padding: 0.6rem 1rem;
    border-radius: 4px;
    font-size: 0.75rem;
    color: #a1a1aa;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  .status-dot {
    width: 6px; height: 6px;
    background: #a3e635;
    border-radius: 50%;
    box-shadow: 0 0 8px #a3e635;
  }

  /* CARDS */
  .card {
    background: #121212;
    border: 1px solid #27272a;
    border-radius: 6px;
    padding: 1.25rem;
  }
  .card-label {
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #71717a;
    margin-bottom: 0.75rem;
    display: flex;
    justify-content: space-between;
  }

  /* INPUTS */
  textarea, input[type="text"], select {
    width: 100%;
    background: #18181b;
    border: 1px solid #27272a;
    color: #fafafa;
    font-family: 'IBM Plex Mono', monospace;
    padding: 0.75rem;
    border-radius: 4px;
    font-size: 0.85rem;
    outline: none;
    transition: border-color 0.2s;
  }
  textarea:focus, input[type="text"]:focus, select:focus {
    border-color: #a3e635;
  }
  textarea { resize: vertical; min-height: 60px; }
  
  .grid-3 {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 1rem;
    margin-top: 1rem;
  }
  .input-group { display: flex; flex-direction: column; gap: 0.4rem; }
  .input-group label {
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #71717a;
  }

  /* PILLS */
  .category { margin-bottom: 1.25rem; }
  .category:last-child { margin-bottom: 0; }
  .category-label {
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #71717a;
    margin-bottom: 0.5rem;
  }
  .pill-group { display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .pill {
    background: #18181b;
    border: 1px solid #27272a;
    color: #a1a1aa;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.5rem 0.8rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }
  .pill:hover { border-color: #52525b; }
  .pill.active {
    background: #1a2e05;
    border-color: #a3e635;
    color: #a3e635;
  }
  .pill .conf { font-size: 0.55rem; opacity: 0.7; border: 1px solid currentColor; padding: 1px 3px; border-radius: 2px; }

  /* CREDITS */
  .credits-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  .checkbox-row {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    font-size: 0.75rem;
    color: #a1a1aa;
    line-height: 1.4;
  }
  .checkbox-row input[type="checkbox"] {
    accent-color: #a3e635;
    width: 16px; height: 16px;
    margin-top: 2px;
    cursor: pointer;
  }

  /* GENERATE BTN */
  .btn-generate {
    background: #a3e635;
    color: #09090b;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    width: 100%;
    padding: 1rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: transform 0.1s, background 0.2s;
  }
  .btn-generate:hover { background: #bef264; }
  .btn-generate:active { transform: scale(0.99); }
  .btn-generate:disabled { opacity: 0.5; cursor: not-allowed; }

  /* OUTPUT */
  .output-header {
    font-size: 0.75rem;
    color: #71717a;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
  }
  canvas {
    width: 100%;
    height: 180px;
    background: #000;
    border: 1px solid #27272a;
    border-radius: 4px;
    display: block;
  }
  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 0.75rem;
    font-size: 0.7rem;
    color: #a1a1aa;
  }
  .legend-item { display: flex; align-items: center; gap: 0.35rem; }
  .legend-dot { width: 8px; height: 8px; border-radius: 2px; }
  
  .save-row {
    display: flex;
    gap: 0.75rem;
    margin-top: 1rem;
  }
  .btn-save {
    flex: 1;
    background: transparent;
    border: 1px solid #a3e635;
    color: #a3e635;
    padding: 0.75rem;
    font-family: inherit;
    font-size: 0.8rem;
    font-weight: 500;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.15s;
  }
  .btn-save:hover { background: #1a2e05; }
  .hidden { display: none; }
</style>
</head>
<body>

<div class="container">
  <!-- HEADER -->
  <header class="header">
    <div class="eyebrow">Juncture Neural · Focus</div>
    <div class="title"><span>Junc</span>ture</div>
  </header>

  <div class="status-bar">
    <div class="status-dot"></div>
    <span>ENGINE ONLINE · KARPLUS-STRONG (LOCAL DSP)</span>
  </div>

  <!-- PROMPT -->
  <div class="card">
    <div class="card-label">Prompt</div>
    <textarea id="prompt" placeholder="mid-tempo funk riff in E minor, clean tone, palm mutes"></textarea>
    
    <div class="grid-3">
      <div class="input-group">
        <label>Tone Model</label>
        <select id="amp">
          <option value="clean">Fender Clean [M]</option>
          <option value="breakup">Edge of Breakup [E]</option>
          <option value="ambient">Ambient Shimmer [X]</option>
        </select>
      </div>
      <div class="input-group">
        <label>Tempo (BPM)</label>
        <input type="number" id="tempo" value="96" min="40" max="240">
      </div>
      <div class="input-group">
        <label>Seed</label>
        <input type="number" id="seed" value="42">
      </div>
    </div>
  </div>

  <!-- INSTRUMENTS -->
  <div class="card">
    <div class="card-label">
      <span>Guitar Roles</span>
      <span id="selection-count">3 OF 8 MAX SELECTED</span>
    </div>

    <div class="category">
      <div class="category-label">Lead</div>
      <div class="pill-group">
        <button class="pill active" data-role="lead" data-conf="M">Pentatonic Solo <span class="conf">M</span></button>
        <button class="pill" data-role="lead" data-conf="X">Shred Arp <span class="conf">X</span></button>
        <button class="pill" data-role="lead" data-conf="E">Melodic Lead <span class="conf">E</span></button>
      </div>
    </div>

    <div class="category">
      <div class="category-label">Rhythm</div>
      <div class="pill-group">
        <button class="pill active" data-role="rhythm" data-conf="M">Power Chords <span class="conf">M</span></button>
        <button class="pill" data-role="rhythm" data-conf="M">Open Chords <span class="conf">M</span></button>
        <button class="pill" data-role="rhythm" data-conf="E">Palm Mutes <span class="conf">E</span></button>
      </div>
    </div>

    <div class="category">
      <div class="category-label">Bass</div>
      <div class="pill-group">
        <button class="pill active" data-role="bass" data-conf="M">Root Notes <span class="conf">M</span></button>
        <button class="pill" data-role="bass" data-conf="X">Walking Bass <span class="conf">X</span></button>
      </div>
    </div>

    <div class="category">
      <div class="category-label">Drums</div>
      <div class="pill-group">
        <button class="pill" data-role="drums" data-conf="M">Rock Kit <span class="conf">M</span></button>
        <button class="pill" data-role="drums" data-conf="M">Funk Kit <span class="conf">M</span></button>
      </div>
    </div>
  </div>

  <!-- CREDITS -->
  <div class="card">
    <div class="card-label">Credits & Terms · Before You Generate</div>
    <div class="credits-grid">
      <div class="input-group">
        <label>Session Name (Required)</label>
        <input type="text" id="session-name" placeholder="Juncture Riff 01">
      </div>
      <div class="input-group">
        <label>Credited Names (Comma Separated)</label>
        <input type="text" id="credits" placeholder="Your Name">
      </div>
    </div>
    <label class="checkbox-row">
      <input type="checkbox" id="agree">
      <span>I agree to the credit terms. Everyone named has agreed to be credited, and this is the session name I am submitting.</span>
    </label>
  </div>

  <button class="btn-generate" id="generate-btn" disabled>Generate</button>

  <!-- OUTPUT -->
  <div class="output hidden" id="output-panel">
    <div class="output-header">
      <span id="gen-status">Done · 0 bytes</span>
      <span id="gen-prompt-display">Funk riff in E minor...</span>
    </div>
    
    <canvas id="piano-roll" width="800" height="180"></canvas>
    
    <div class="legend" id="legend"></div>
    
    <div class="save-row">
      <button class="btn-save" id="save-midi">Save Session.mid</button>
      <button class="btn-save" id="save-wav">Save Session.wav</button>
    </div>
  </div>
</div>

<script>
  // UI Logic
  const pills = document.querySelectorAll('.pill');
  const countEl = document.getElementById('selection-count');
  const generateBtn = document.getElementById('generate-btn');
  const agreeBox = document.getElementById('agree');
  const sessionInput = document.getElementById('session-name');
  
  const MAX_PILLS = 8;

  function updatePills() {
    const active = document.querySelectorAll('.pill.active');
    countEl.textContent = `${active.length} OF ${MAX_PILLS} MAX SELECTED`;
    
    if (active.length >= MAX_PILLS) {
      pills.forEach(p => {
        if (!p.classList.contains('active')) p.disabled = true;
      });
    } else {
      pills.forEach(p => p.disabled = false);
    }
  }

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      if (!pill.classList.contains('active') && document.querySelectorAll('.pill.active').length >= MAX_PILLS) return;
      pill.classList.toggle('active');
      updatePills();
    });
  });

  function checkGenerateState() {
    generateBtn.disabled = !(agreeBox.checked && sessionInput.value.trim().length > 0);
  }

  agreeBox.addEventListener('change', checkGenerateState);
  sessionInput.addEventListener('input', checkGenerateState);

  // Canvas & Generation Logic
  const canvas = document.getElementById('piano-roll');
  const ctx = canvas.getContext('2d');
  const outputPanel = document.getElementById('output-panel');
  const genStatus = document.getElementById('gen-status');
  const legendEl = document.getElementById('legend');
  const promptDisplay = document.getElementById('gen-prompt-display');

  const COLORS = {
    lead: '#a3e635',   // Green
    rhythm: '#f97316', // Orange
    bass: '#a855f7',   // Purple
    drums: '#3b82f6'   // Blue
  };

  generateBtn.addEventListener('click', () => {
    generateBtn.textContent = 'Generating...';
    generateBtn.disabled = true;
    
    // Simulate processing delay
    setTimeout(() => {
      outputPanel.classList.remove('hidden');
      promptDisplay.textContent = document.getElementById('prompt').value || "Custom riff";
      
      const activePills = Array.from(document.querySelectorAll('.pill.active')).map(p => ({
        role: p.dataset.role,
        name: p.textContent.replace(/ [MEX]/, '').trim() // Strip confidence tag
      }));

      generatePianoRoll(activePills);
      
      // Fake byte count for the "Done" status
      const fakeBytes = Math.floor(Math.random() * 2000) + 1500;
      genStatus.textContent = `Done · ${fakeBytes} bytes`;
      
      generateBtn.textContent = 'Generate';
      generateBtn.disabled = false;
    }, 600);
  });

  function generatePianoRoll(activePills) {
    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid lines
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 8; i++) {
      const x = (canvas.width / 8) * i;
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }

    legendEl.innerHTML = '';
    const rowHeight = canvas.height / 6;
    let currentRow = 0;

    activePills.forEach(pill => {
      if (currentRow >= 6) return; // Max 6 visual rows
      
      const color = COLORS[pill.role] || '#fff';
      
      // Draw fake notes for this instrument
      const noteCount = Math.floor(Math.random() * 20) + 15;
      for (let i = 0; i < noteCount; i++) {
        const x = Math.random() * (canvas.width - 20);
        const y = (currentRow * rowHeight) + (Math.random() * (rowHeight - 10));
        const w = Math.random() * 25 + 5;
        const h = 4;

        ctx.fillStyle = color;
        ctx.fillRect(x, y, w, h);
      }
      
      // Add to legend
      const legendItem = document.createElement('div');
      legendItem.className = 'legend-item';
      legendItem.innerHTML = `<div class="legend-dot" style="background:${color}"></div> ${pill.name} · ${noteCount}`;
      legendEl.appendChild(legendItem);
      
      currentRow++;
    });
  }

  // Initialize
  updatePills();
</script>
</body>
</html>
