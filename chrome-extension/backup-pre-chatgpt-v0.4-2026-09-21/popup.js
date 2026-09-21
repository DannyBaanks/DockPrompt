(() => {
  // ── Elements ──
  const geometryEl = document.getElementById('geometry');
  const screenPreview = document.getElementById('screenPreview');
  const screenFrame = document.getElementById('screenFrame');
  const screenWorkarea = document.getElementById('screenWorkarea');
  const screenDock = document.getElementById('screenDock');
  const lblRes = document.getElementById('lblRes');
  const lblDockH = document.getElementById('lblDockH');
  const lblDockY = document.getElementById('lblDockY');
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const imagePreview = document.getElementById('imagePreview');
  const imageThumb = document.getElementById('imageThumb');
  const imageName = document.getElementById('imageName');
  const imageSize = document.getElementById('imageSize');
  const imageRemove = document.getElementById('imageRemove');
  const effectGroup = document.getElementById('effectGroup');
  const cmdSection = document.getElementById('cmdSection');
  const cmdBody = document.getElementById('cmdBody');
  const cmdCopy = document.getElementById('cmdCopy');
  const cmdTabs = document.getElementById('cmdTabs');
  const toast = document.getElementById('toast');
  const step1 = document.getElementById('step1');
  const step2 = document.getElementById('step2');
  const step3 = document.getElementById('step3');

  let geo = {};
  let currentEffect = 'blur';
  let currentImageName = null;
  let currentTab = 'apply';

  // ── Geometry ──
  geometryEl.value = localStorage.getItem('dockprompt_geometry') || '';

  geometryEl.addEventListener('input', () => {
    localStorage.setItem('dockprompt_geometry', geometryEl.value);
    parseAndRender();
  });

  function parseGeometry(text) {
    const r = {};
    for (const line of text.split('\n')) {
      const d = line.match(/Display:\s*(\d+)x(\d+)/i);
      if (d) { r.sw = +d[1]; r.sh = +d[2]; }
      const dr = line.match(/Dock region:\s*x=(\d+)\s*y=(\d+)\s*w=(\d+)\s*h=(\d+)/i);
      if (dr) { r.dx = +dr[1]; r.dy = +dr[2]; r.dw = +dr[3]; r.dh = +dr[4]; }
      const de = line.match(/Dock:\s*(\w+)/i);
      if (de && !dr) r.edge = de[1];
    }
    return r;
  }

  function parseAndRender() {
    geo = parseGeometry(geometryEl.value);
    const valid = geo.sw && geo.dy !== undefined;

    // Textarea state
    geometryEl.classList.toggle('parsed', valid);
    step1.classList.toggle('active', !valid);
    step1.classList.toggle('done', valid);

    // Mini screen preview
    if (valid) {
      screenPreview.classList.add('visible');
      const scale = 100 / geo.sw;
      const sh = geo.sh * scale;

      // Workarea
      const waTop = (geo.dy - (geo.sh - geo.sh)) * scale || 0;
      const waLeft = (geo.dx || 0) * scale;
      const waW = (geo.dw || geo.sw) * scale;
      const waH = (geo.dh || (geo.sh - geo.dy)) * scale;

      screenFrame.style.height = sh + '%';
      screenWorkarea.style.cssText = `top:0;left:0;width:100%;height:calc(100% - ${geo.dh * scale}%);`;

      // Dock at bottom
      screenDock.style.cssText = `bottom:0;left:0;width:100%;height:${geo.dh * scale}%;`;

      lblRes.textContent = `${geo.sw}x${geo.sh}`;
      lblDockH.textContent = `${geo.dh}px`;
      lblDockY.textContent = geo.dy;
    } else {
      screenPreview.classList.remove('visible');
    }

    // Step 2 activation
    if (valid && !currentImageName) {
      step2.classList.add('active');
    } else if (!valid) {
      step2.classList.remove('active');
    }

    generateCommand();
  }

  // ── Image drop ──
  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
  });

  imageRemove.addEventListener('click', () => {
    currentImageName = null;
    imagePreview.classList.remove('visible');
    dropZone.style.display = '';
    step2.classList.add('active');
    step2.classList.remove('done');
    generateCommand();
  });

  function handleFile(file) {
    if (!file.type.startsWith('image/')) return;
    currentImageName = file.name;
    const reader = new FileReader();
    reader.onload = (e) => {
      imageThumb.src = e.target.result;
      const img = new Image();
      img.onload = () => {
        imageName.textContent = file.name;
        imageSize.textContent = `${img.width}×${img.height}`;
        imagePreview.classList.add('visible');
        dropZone.style.display = 'none';
        step2.classList.remove('active');
        step2.classList.add('done');
        if (geo.sw) step3.classList.add('active');
        generateCommand();
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // ── Effects ──
  effectGroup.addEventListener('click', (e) => {
    const btn = e.target.closest('.effect-btn');
    if (!btn) return;
    effectGroup.querySelectorAll('.effect-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentEffect = btn.dataset.effect;
    generateCommand();
  });

  // ── Command tabs ──
  cmdTabs.addEventListener('click', (e) => {
    const tab = e.target.closest('.cmd-tab');
    if (!tab) return;
    cmdTabs.querySelectorAll('.cmd-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentTab = tab.dataset.tab;
    generateCommand();
  });

  // ── Command generation ──
  function generateCommand() {
    const valid = geo.sw && geo.dy !== undefined;
    if (!valid || !currentImageName) {
      cmdSection.classList.remove('visible');
      return;
    }

    const inputName = currentImageName.replace(/\.[^.]+$/, '');
    const outputName = `${inputName}_final.png`;

    let lines = [];
    if (currentTab === 'apply') {
      lines = [
        { type: 'comment', text: `# ${geo.sw}×${geo.sh} canvas | dock y=${geo.dy} h=${geo.dh}px | effect=${currentEffect}` },
        { type: 'command', text: `dockprompt apply "${currentImageName}" --effect ${currentEffect} -o "${outputName}"` },
      ];
    } else if (currentTab === 'prompt') {
      lines = [
        { type: 'comment', text: '# Full prompt for ChatGPT / image model:' },
        { type: 'command', text: `dockprompt "${currentImageName}" --effect ${currentEffect}` },
        { type: 'comment', text: '' },
        { type: 'comment', text: '# Copy the output above and paste it with your image into ChatGPT.' },
        { type: 'comment', text: '# Then run apply on the result:' },
        { type: 'command', text: `dockprompt apply <chatgpt_output.png> --effect ${currentEffect} -o "${outputName}"` },
      ];
    } else if (currentTab === 'inspect') {
      lines = [
        { type: 'comment', text: '# Run this on your Linux host to get geometry:' },
        { type: 'command', text: 'dockprompt inspect' },
        { type: 'comment', text: '' },
        { type: 'comment', text: '# Or with image info:' },
        { type: 'command', text: `dockprompt inspect "${currentImageName}"` },
      ];
    }

    // Typewriter render
    cmdBody.innerHTML = '';
    lines.forEach((line) => {
      const span = document.createElement('span');
      if (line.type === 'comment') {
        span.className = 'comment';
        span.textContent = line.text + '\n';
      } else {
        span.innerHTML = `<span class="prompt">$ </span><span class="command">${escHtml(line.text)}</span>\n`;
      }
      cmdBody.appendChild(span);
    });

    cmdSection.classList.add('visible');
  }

  function escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  // ── Copy ──
  cmdCopy.addEventListener('click', () => {
    const text = cmdBody.textContent;
    navigator.clipboard.writeText(text).then(() => {
      cmdCopy.textContent = 'copied!';
      cmdCopy.classList.add('copied');
      showToast('Copied to clipboard');
      setTimeout(() => {
        cmdCopy.textContent = 'copy';
        cmdCopy.classList.remove('copied');
      }, 1500);
    });
  });

  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 1500);
  }

  // ── Keyboard shortcuts ──
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.close();
  });

  // ── Init ──
  parseAndRender();
})();
