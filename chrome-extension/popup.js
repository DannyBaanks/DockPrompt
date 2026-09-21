(() => {
  const geometryEl = document.getElementById('geometry');
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const preview = document.getElementById('preview');
  const imageInfo = document.getElementById('imageInfo');
  const effectBtns = document.getElementById('effectBtns');
  const cmdBox = document.getElementById('cmdBox');
  const cmdText = document.getElementById('cmdText');
  const copyBtn = document.getElementById('copyBtn');
  const status = document.getElementById('status');

  let currentEffect = 'blur';
  let currentImageName = null;

  // Restore geometry from localStorage
  geometryEl.value = localStorage.getItem('dockprompt_geometry') || '';
  geometryEl.addEventListener('input', () => {
    localStorage.setItem('dockprompt_geometry', geometryEl.value);
    generateCommand();
  });

  // Effect buttons
  effectBtns.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    effectBtns.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentEffect = btn.dataset.effect;
    generateCommand();
  });

  // Drop zone
  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
  });

  function handleFile(file) {
    if (!file.type.startsWith('image/')) {
      status.textContent = 'not an image file';
      return;
    }
    currentImageName = file.name;
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
      preview.style.display = 'block';
      const img = new Image();
      img.onload = () => {
        imageInfo.textContent = `${img.width}×${img.height} — ${file.name}`;
        generateCommand();
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  function parseGeometry(text) {
    const result = {};
    for (const line of text.split('\n')) {
      const display = line.match(/Display:\s*(\d+)x(\d+)/i);
      if (display) { result.screenW = parseInt(display[1]); result.screenH = parseInt(display[2]); }

      const dockRegion = line.match(/Dock region:\s*x=(\d+)\s*y=(\d+)\s*w=(\d+)\s*h=(\d+)/i);
      if (dockRegion) {
        result.dockX = parseInt(dockRegion[1]);
        result.dockY = parseInt(dockRegion[2]);
        result.dockW = parseInt(dockRegion[3]);
        result.dockH = parseInt(dockRegion[4]);
      }

      const dockEdge = line.match(/Dock:\s*(\w+)/i);
      if (dockEdge && !dockRegion) { result.dockEdge = dockEdge[1]; }
    }
    return result;
  }

  function generateCommand() {
    const geo = parseGeometry(geometryEl.value);
    if (!geo.screenW || geo.dockY === undefined) {
      cmdBox.style.display = 'none';
      status.textContent = geometryEl.value.trim() ? 'could not parse geometry' : '';
      return;
    }
    if (!currentImageName) {
      cmdBox.style.display = 'none';
      status.textContent = 'drop an image first';
      return;
    }

    const inputName = currentImageName.replace(/\.[^.]+$/, '');
    const outputName = `${inputName}_final.png`;

    const cmd = [
      `# ${geo.screenW}x${geo.screenH} canvas, dock at y=${geo.dockY} h=${geo.dockH}`,
      `dockprompt apply "${currentImageName}" --effect ${currentEffect} -o "${outputName}"`,
    ].join('\n');

    cmdText.textContent = cmd;
    cmdBox.style.display = 'block';
    status.textContent = `ready — ${geo.screenW}x${geo.screenH}, dock y=${geo.dockY}`;
  }

  // Copy button
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(cmdText.textContent).then(() => {
      copyBtn.textContent = 'copied!';
      copyBtn.classList.add('copied');
      setTimeout(() => { copyBtn.textContent = 'copy'; copyBtn.classList.remove('copied'); }, 1500);
    });
  });

  // Generate on load if we have data
  generateCommand();
})();
