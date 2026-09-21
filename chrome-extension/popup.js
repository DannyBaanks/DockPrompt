(() => {
  const $ = (id) => document.getElementById(id);

  const geometryEl = $('geometry');
  const geometryResult = $('geometryResult');
  const screenFrame = $('screenFrame');
  const screenWorkarea = $('screenWorkarea');
  const screenDock = $('screenDock');
  const lblRes = $('lblRes');
  const lblEdge = $('lblEdge');
  const lblDockRegion = $('lblDockRegion');
  const lblDockArea = $('lblDockArea');

  const dropZone = $('dropZone');
  const fileInput = $('fileInput');
  const imagePreview = $('imagePreview');
  const imageThumb = $('imageThumb');
  const imageName = $('imageName');
  const imageSize = $('imageSize');
  const imageRemove = $('imageRemove');

  const effectGroup = $('effectGroup');
  const cmdSection = $('cmdSection');
  const cmdTabs = $('cmdTabs');
  const cmdBody = $('cmdBody');
  const cmdCopy = $('cmdCopy');
  const terminalTitle = $('terminalTitle');
  const terminalHint = $('terminalHint');
  const readyMeta = $('readyMeta');
  const toast = $('toast');

  const step1 = $('step1');
  const step2 = $('step2');
  const step3 = $('step3');

  let geo = {};
  let currentImage = null;
  let currentEffect = 'blur';
  let currentTab = 'prompt';
  let currentOutput = '';

  geometryEl.value = localStorage.getItem('dockprompt_geometry') || '';

  function num(v) {
    return Number.isFinite(v) ? v : undefined;
  }

  function parseGeometry(text) {
    const out = {};

    for (const rawLine of text.split(/\r?\n/)) {
      const line = rawLine.trim();
      let m;

      m = line.match(/^Session:\s*(.+)$/i);
      if (m) out.session = m[1].trim();

      m = line.match(/^Desktop:\s*(.+)$/i);
      if (m) out.desktop = m[1].trim();

      m = line.match(/^Display:\s*(\d+)\s*[x×]\s*(\d+)$/i);
      if (m) { out.sw = +m[1]; out.sh = +m[2]; }

      m = line.match(/^Workarea:\s*(-?\d+)\s*,\s*(-?\d+)\s+(\d+)\s*[x×]\s*(\d+)$/i);
      if (m) { out.wx = +m[1]; out.wy = +m[2]; out.ww = +m[3]; out.wh = +m[4]; }

      m = line.match(/^Dock:\s*([a-z_-]+)$/i);
      if (m) out.edge = m[1].toLowerCase();

      m = line.match(/^Dock region:\s*x=(-?\d+)\s+y=(-?\d+)\s+w=(\d+)\s+h=(\d+)$/i);
      if (m) { out.dx = +m[1]; out.dy = +m[2]; out.dw = +m[3]; out.dh = +m[4]; }
    }

    if (!out.edge && hasDock(out)) out.edge = inferEdge(out);
    return out;
  }

  function hasDisplay(g) {
    return Number.isFinite(g.sw) && g.sw > 0 && Number.isFinite(g.sh) && g.sh > 0;
  }

  function hasDock(g) {
    return hasDisplay(g) && [g.dx, g.dy, g.dw, g.dh].every(Number.isFinite) && g.dw > 0 && g.dh > 0;
  }

  function inferEdge(g) {
    if (!hasDock(g)) return 'custom';
    const tol = 1;
    if (Math.abs((g.dy + g.dh) - g.sh) <= tol && g.dw >= g.sw - tol) return 'bottom';
    if (Math.abs(g.dy) <= tol && g.dw >= g.sw - tol) return 'top';
    if (Math.abs(g.dx) <= tol && g.dh >= g.sh - tol) return 'left';
    if (Math.abs((g.dx + g.dw) - g.sw) <= tol && g.dh >= g.sh - tol) return 'right';
    return 'custom';
  }

  function setPanelState(panel, state) {
    panel.dataset.state = state;
  }

  function pct(value, total) {
    if (!total) return 0;
    return Math.max(0, Math.min(100, (value / total) * 100));
  }

  function renderGeometry() {
    geo = parseGeometry(geometryEl.value);
    const valid = hasDock(geo);

    geometryEl.classList.toggle('valid', valid);
    geometryResult.classList.toggle('visible', valid);
    setPanelState(step1, valid ? 'done' : 'active');
    setPanelState(step2, valid ? (currentImage ? 'done' : 'active') : 'idle');
    setPanelState(step3, valid && currentImage ? 'active' : 'idle');

    if (!valid) {
      renderOutput();
      return;
    }

    screenFrame.style.aspectRatio = `${geo.sw} / ${geo.sh}`;

    if ([geo.wx, geo.wy, geo.ww, geo.wh].every(Number.isFinite)) {
      screenWorkarea.style.display = 'block';
      screenWorkarea.style.left = `${pct(geo.wx, geo.sw)}%`;
      screenWorkarea.style.top = `${pct(geo.wy, geo.sh)}%`;
      screenWorkarea.style.width = `${pct(geo.ww, geo.sw)}%`;
      screenWorkarea.style.height = `${pct(geo.wh, geo.sh)}%`;
    } else {
      screenWorkarea.style.display = 'none';
    }

    screenDock.style.left = `${pct(geo.dx, geo.sw)}%`;
    screenDock.style.top = `${pct(geo.dy, geo.sh)}%`;
    screenDock.style.width = `${pct(geo.dw, geo.sw)}%`;
    screenDock.style.height = `${pct(geo.dh, geo.sh)}%`;

    lblRes.textContent = `${geo.sw}×${geo.sh}`;
    lblEdge.textContent = geo.edge || 'custom';
    lblDockRegion.textContent = `${geo.dx},${geo.dy}`;
    lblDockArea.textContent = `${geo.dw}×${geo.dh}`;

    renderOutput();
  }

  geometryEl.addEventListener('input', () => {
    localStorage.setItem('dockprompt_geometry', geometryEl.value);
    renderGeometry();
  });

  function openPicker() {
    fileInput.click();
  }

  dropZone.addEventListener('click', openPicker);
  dropZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      openPicker();
    }
  });
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  });
  fileInput.addEventListener('change', () => {
    const file = fileInput.files?.[0];
    if (file) handleFile(file);
  });

  function handleFile(file) {
    if (!file.type.startsWith('image/')) {
      showToast('Choose an image file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        currentImage = {
          name: file.name,
          width: img.naturalWidth,
          height: img.naturalHeight,
          type: file.type,
          dataUrl: e.target.result,
        };

        imageThumb.src = e.target.result;
        imageName.textContent = currentImage.name;
        imageSize.textContent = `${currentImage.width}×${currentImage.height}`;
        imagePreview.classList.add('visible');
        dropZone.style.display = 'none';
        setPanelState(step2, 'done');
        setPanelState(step3, 'active');
        renderOutput();
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  imageRemove.addEventListener('click', () => {
    currentImage = null;
    fileInput.value = '';
    imageThumb.removeAttribute('src');
    imagePreview.classList.remove('visible');
    dropZone.style.display = '';
    setPanelState(step2, hasDock(geo) ? 'active' : 'idle');
    setPanelState(step3, 'idle');
    renderOutput();
  });

  effectGroup.addEventListener('click', (e) => {
    const btn = e.target.closest('.effect');
    if (!btn) return;
    effectGroup.querySelectorAll('.effect').forEach((b) => b.classList.toggle('active', b === btn));
    currentEffect = btn.dataset.effect;
    renderOutput();
  });

  cmdTabs.addEventListener('click', (e) => {
    const tab = e.target.closest('.tab');
    if (!tab) return;
    cmdTabs.querySelectorAll('.tab').forEach((t) => t.classList.toggle('active', t === tab));
    currentTab = tab.dataset.tab;
    renderOutput();
  });

  function outputName() {
    if (!currentImage) return 'wallpaper_final.png';
    const stem = currentImage.name.replace(/\.[^.]+$/, '');
    return `${stem}_dockprompt.png`;
  }

  function aiPrompt() {
    const action = currentEffect === 'blur'
      ? 'Apply a blur effect'
      : currentEffect === 'darken'
        ? 'Darken the image'
        : 'Apply a subtle color tint';

    const source = currentImage
      ? `${currentImage.width}×${currentImage.height}`
      : 'unknown resolution';

    return [
      'Edit the attached wallpaper for this Linux desktop.',
      '',
      `FINAL CANVAS: exactly ${geo.sw}×${geo.sh} pixels.`,
      `SOURCE IMAGE: ${source}.`,
      '',
      'The dock region below is expressed only in FINAL-CANVAS coordinates:',
      `x=${geo.dx}`,
      `y=${geo.dy}`,
      `width=${geo.dw}`,
      `height=${geo.dh}`,
      `edge=${geo.edge || inferEdge(geo)}`,
      '',
      `${action} only inside that exact rectangle.`,
      'Preserve everything outside the rectangle.',
      'Do not infer, rescale, double, halve, or reinterpret the dock dimensions from the source image resolution.',
      `The dock height in the FINAL ${geo.sw}×${geo.sh} canvas is exactly ${geo.dh}px.`,
      '',
      'Do not add desktop UI, icons, panels, windows, text, taskbars, or controls.',
      'The attached image is the wallpaper source, not a screenshot to recreate.',
      'Do not crop or recompose the source unless required to reach the final canvas; preserve the complete composition whenever possible.',
      'Keep the boundary of the edited region hard and geometrically exact: no feathering or gradient outside the dock rectangle.',
      '',
      'Pixel alignment with the real Linux dock is more important than how the isolated wallpaper looks without the dock on top.',
    ].join('\n');
  }

  function applyCommand() {
    return [
      `# ${geo.sw}×${geo.sh} | dock ${geo.edge || inferEdge(geo)} x=${geo.dx} y=${geo.dy} w=${geo.dw} h=${geo.dh}`,
      `dockprompt apply "${currentImage.name}" --effect ${currentEffect} -o "${outputName()}"`,
    ].join('\n');
  }

  function inspectCommand() {
    return [
      '# Run this on the Linux host that owns the dock geometry:',
      'dockprompt inspect',
      '',
      '# Include source-image metadata:',
      `dockprompt inspect "${currentImage.name}"`,
    ].join('\n');
  }

  function renderOutput() {
    const ready = hasDock(geo) && !!currentImage;
    cmdSection.classList.toggle('visible', ready);
    if (!ready) return;

    readyMeta.textContent = `${geo.dw}×${geo.dh}px · ${currentEffect}`;

    if (currentTab === 'apply') {
      currentOutput = applyCommand();
      terminalTitle.textContent = 'terminal';
      terminalHint.textContent = 'Deterministic post-process on the Linux host.';
    } else if (currentTab === 'inspect') {
      currentOutput = inspectCommand();
      terminalTitle.textContent = 'inspect.sh';
      terminalHint.textContent = 'Re-run after changing monitor, scaling, dock size, or dock edge.';
    } else {
      currentOutput = aiPrompt();
      terminalTitle.textContent = 'prompt.txt';
      terminalHint.textContent = 'Paste this prompt together with the wallpaper into your image model.';
    }

    cmdBody.textContent = currentOutput;
  }

  async function writeClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (_) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      const ok = document.execCommand('copy');
      ta.remove();
      return ok;
    }
  }

  cmdCopy.addEventListener('click', async () => {
    if (!currentOutput) return;
    const ok = await writeClipboard(currentOutput);
    if (!ok) {
      showToast('Copy failed');
      return;
    }
    cmdCopy.textContent = 'copied';
    cmdCopy.classList.add('ok');
    showToast('Copied');
    setTimeout(() => {
      cmdCopy.textContent = 'copy';
      cmdCopy.classList.remove('ok');
    }, 1300);
  });

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(() => toast.classList.remove('show'), 1400);
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.close();
  });

  renderGeometry();
})();
