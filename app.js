(function () {
  const el = (sel) => document.querySelector(sel);
  const elAll = (sel) => Array.from(document.querySelectorAll(sel));

  const groupSelect = el('#classGroup');
  const subclassPills = el('#subclassPills');
  const charLevel = el('#charLevel');
  const charLevelLabel = el('#charLevelLabel');
  const skillsGrid = el('#skillsGrid');
  const dnaGrid = el('#dnaGrid');
  const pointsSkills = el('#pointsSkills');
  const pointsDNA = el('#pointsDNA');
  const pointsHint = el('#pointsHint');
  const tooltip = el('#tooltip');
  const btnReset = el('#btnReset');

  let data = null; // loaded JSON
  let currentGroupId = null; // race id
  let currentJobId = null;   // first job id
  let currentSubclassId = null; // second job (spec) id
  let allocated = { skills: {}, dna: {} };

  const norm = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');

  // Basic dependency and points rules (approximation of original calculator)
  // Skill points available per character level (from archived calculator.js)
  const LEVEL_POINTS = [
    0,1,2,3,4,5,6,7,8,11,12,13,14,15,16,17,18,19,20,23,24,25,26,27,28,29,30,31,32,35,36,37,38,39,40,41,42,43,44,47,48,49,50,51,52,53,54,55,56,60,61,62,63,64,65,66,67,68,69,73,74,75,76,77,78,79,80,81,82,85,86,87,88,89,90,91,92,93,94,97,98,99,100,101,102,103,104,105,106,109
  ];
  const MAX_LEVEL = 90;
  const BASE_DNA_POINTS = 55; // from archived calculator.js
  const STARTER_SKILL_POINTS = 1; // free points at level 1 so you can allocate basics

  function getSkillPointsCap() {
    const lvl = Math.max(1, Math.min(MAX_LEVEL, parseInt(charLevel.value || '1', 10)));
    const idx = Math.max(0, Math.min(LEVEL_POINTS.length - 1, lvl - 1));
    const base = LEVEL_POINTS[idx] || 0;
    return base + (lvl === 1 ? STARTER_SKILL_POINTS : 0);
  }

  function countAllocated(map) {
    let sum = 0;
    for (const k in map) sum += map[k] || 0;
    return sum;
  }

  // Requirements handling — supports several shapes:
  // - req: [{id: '25100', level: 3}, ...]
  // - requires: [["25100",3], 26000]
  // - req: "25100:3"
  function normalizeRequirements(reqVal) {
    if (!reqVal) return [];
    const out = [];
    const push = (id, level) => {
      if (!id) return;
      const sid = String(id);
      const lvl = Math.max(1, parseInt(level || '1', 10));
      out.push({ id: sid, level: lvl });
    };
    const arr = Array.isArray(reqVal) ? reqVal : [reqVal];
    for (const r of arr) {
      if (!r && r !== 0) continue;
      if (typeof r === 'object' && !Array.isArray(r)) {
        push(r.id ?? r.skillId ?? r[0], r.level ?? r.lv ?? r[1] ?? 1);
      } else if (Array.isArray(r)) {
        push(r[0], r[1] ?? 1);
      } else if (typeof r === 'string') {
        const m = r.match(/^(\d+)(?::(\d+))?$/);
        if (m) push(m[1], m[2] ?? 1);
      } else if (typeof r === 'number') {
        push(r, 1);
      }
    }
    return out;
  }

  function buildDependencyIndex(specId) {
    const skills = data.skills[specId] || [];
    const requiresById = {};
    const dependentsById = {};
    for (const s of skills) {
      const sid = String(s.id);
      const req = normalizeRequirements(s.req || s.requires);
      if (req.length) requiresById[sid] = req;
      for (const r of req) {
        const arr = (dependentsById[r.id] = dependentsById[r.id] || []);
        if (!arr.includes(sid)) arr.push(sid);
      }
    }
    return { requiresById, dependentsById };
  }

  function loadJSON() {
    fetch('./data.json?_=' + Date.now())
      .then((r) => r.json())
      .then((json) => {
        data = json;
        initUI();
      })
      .catch(() => {
        data = { groups: [], jobs: {}, skills: {} };
        initUI();
      });
  }

  function initUI() {
    // Populate race select
    groupSelect.innerHTML = '';
    data.groups.forEach((g, idx) => {
      const opt = document.createElement('option');
      opt.value = g.id;
      opt.textContent = g.name;
      groupSelect.appendChild(opt);
      if (idx === 0) currentGroupId = g.id;
    });

    groupSelect.addEventListener('change', () => {
      currentGroupId = groupSelect.value;
      renderSubclassPills();
    });

    charLevel.addEventListener('input', () => {
      charLevelLabel.textContent = 'Level ' + charLevel.value;
      updatePoints();
    });

    renderSubclassPills();
    charLevel.dispatchEvent(new Event('input'));
  }

  function renderSubclassPills() {
    subclassPills.innerHTML = '';
    const jobs = data.jobs[currentGroupId] || [];
    // First-job pills bar
    const jobBar = document.createElement('div');
    jobs.forEach((job, jidx) => {
      const pill = document.createElement('button');
      pill.className = 'pill' + (jidx === 0 ? ' active' : '');
      pill.textContent = job.name;
      pill.addEventListener('click', () => {
        currentJobId = job.id;
        allocated = { skills: {}, dna: {} };
        jobBar.querySelectorAll('.pill').forEach((p) => p.classList.remove('active'));
        pill.classList.add('active');
        renderSpecs(job);
      });
      jobBar.appendChild(pill);
      if (jidx === 0) currentJobId = job.id;
    });
    subclassPills.appendChild(jobBar);

    const initialJob = jobs.find((j) => j.id === currentJobId) || jobs[0];
    if (initialJob) renderSpecs(initialJob);

    function renderSpecs(job) {
      const old = subclassPills.querySelector('.specs-row');
      if (old) old.remove();
      const row = document.createElement('div');
      row.className = 'specs-row';
      (job.specs || []).forEach((sc, idx) => {
        const pill = document.createElement('button');
        pill.className = 'pill' + (idx === 0 ? ' active' : '');
        pill.textContent = sc.name;
        pill.addEventListener('click', () => {
          currentSubclassId = sc.id;
          allocated = { skills: {}, dna: {} };
          row.querySelectorAll('.pill').forEach((p) => p.classList.remove('active'));
          pill.classList.add('active');
          renderSkills();
        });
        row.appendChild(pill);
        if (idx === 0) currentSubclassId = sc.id;
      });
      subclassPills.appendChild(row);
      renderSkills();
    }
  }

  function formatTooltipContent(entry) {
    const info = entry.info || {};
    const prog = entry.progression || {};
    const desc = entry.desc || '';

    const kv = (k, v) => v ? `<div class=\"tt-k\">${k}</div><div class=\"tt-v\">${v}</div>` : '';

    let grid = '';
    grid += kv('Type', info.type);
    grid += kv('Cast', info.cast_time);
    grid += kv('Cooldown', info.cooldown);
    grid += kv('Range', info.range);
    if (Array.isArray(info.weapons) && info.weapons.length) {
      grid += kv('Weapons', info.weapons.join(', '));
    }
    // Show a hint from progression if exists
    if (prog['mp consumption']) grid += kv('MP (L1)', prog['mp consumption'][0]);
    if (prog['damage']) grid += kv('Damage (L1)', prog['damage'][0]);

    return `
      <div class=\"tt-title\">${entry.name}</div>
      ${desc ? `<div class=\"tt-desc\">${desc}</div>` : ''}
      ${grid ? `<div class=\"tt-grid\">${grid}</div>` : ''}
    `;
  }

  function showTooltip(html, x, y) {
    if (!tooltip) return;
    tooltip.innerHTML = html;
    tooltip.classList.add('visible');
    tooltip.setAttribute('aria-hidden', 'false');
    // Position with offset
    const pad = 12;
    const rect = tooltip.getBoundingClientRect();
    let left = x + pad;
    let top = y + pad;
    const vw = window.innerWidth, vh = window.innerHeight;
    if (left + rect.width > vw - 8) left = vw - rect.width - 8;
    if (top + rect.height > vh - 8) top = vh - rect.height - 8;
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
  }
  function hideTooltip() {
    if (!tooltip) return;
    tooltip.classList.remove('visible');
    tooltip.setAttribute('aria-hidden', 'true');
  }

  function attachTooltipHandlers(nameEl, entry) {
    const handler = (ev) => {
      const html = formatTooltipContent(entry);
      showTooltip(html, ev.clientX, ev.clientY);
    };
    nameEl.addEventListener('mouseenter', handler);
    nameEl.addEventListener('mousemove', handler);
    nameEl.addEventListener('mouseleave', hideTooltip);
    nameEl.addEventListener('focus', (ev) => {
      const rect = nameEl.getBoundingClientRect();
      showTooltip(formatTooltipContent(entry), rect.right, rect.top);
    });
    nameEl.addEventListener('blur', hideTooltip);
    nameEl.setAttribute('tabindex', '0');
  }

  function buildReverseDependencyMap(specId) {
    const skills = data.skills[specId] || [];
    const dependents = {}; // key: skillId -> array of dependent skillIds
    for (const s of skills) {
      const reqs = s.requires || {};
      for (const k in reqs) {
        const r = reqs[k];
        if (r && r.id) {
          const arr = (dependents[String(r.id)] = dependents[String(r.id)] || []);
          if (!arr.includes(String(s.id))) arr.push(String(s.id));
        }
      }
    }
    return dependents;
  }

  function unmetRequirementsMessage(s, charLvl) {
    const lines = [];
    const cap = getSkillPointsCap();
    const used = countAllocated(allocated.skills);
    const cur = allocated.skills[s.id] || 0;

    if (used >= cap) lines.push('Not enough skill points');
    if (cur >= (s.maxLevel || 10)) lines.push('Already at max level');

    // level req
    const reqArr = Array.isArray(s.lvlReq) ? s.lvlReq : null;
    const nextLevel = cur + 1;
    if (reqArr) {
      const needLevel = reqArr[Math.max(0, Math.min(reqArr.length - 1, nextLevel - 1))];
      if (typeof needLevel === 'number' && charLvl < needLevel) {
        lines.push(`Requires character level ${needLevel}`);
      }
    }
    // skill reqs
    const reqs = s.requires || {};
    for (const key in reqs) {
      const r = reqs[key];
      if (!r) continue;
      // Resolve by id or name
      let target = null;
      if (r.id) {
        target = (data.skills[currentSubclassId] || []).find(x => String(x.id) === String(r.id));
      } else if (r.name) {
        const n = norm(r.name);
        target = (data.skills[currentSubclassId] || []).find(x => norm(x.name) === n);
        if (target && !r.id) r.id = target.id; // cache id for future checks
      }
      const have = r.id ? (allocated.skills[r.id] || 0) : 0;
      if (target) {
        if (have < (r.level || 1)) lines.push(`Requires ${target.name} Lv.${r.level || 1}`);
      } else if (r.name) {
        lines.push(`Requires ${r.name} Lv.${r.level || 1}`);
      }
    }
    return lines;
  }

  function renderSkills() {
    const skills = data.skills[currentSubclassId] || [];
    skillsGrid.innerHTML = '';
    const depIndex = buildDependencyIndex(currentSubclassId);
    const requiresById = depIndex.requiresById;
    const dependentsById = depIndex.dependentsById;
    const reverseDeps = buildReverseDependencyMap(currentSubclassId);

    // helper to find card element by skill id or name
    function findCardEl(predicate) {
      return Array.from(skillsGrid.children).find(card => {
        const n = card.querySelector('.skill-name');
        return n && predicate(n.textContent.trim());
      });
    }
    function findCardElBySkillId(skillId) {
      const target = (data.skills[currentSubclassId] || []).find(s => String(s.id) === String(skillId));
      if (!target) return null;
      return findCardEl(name => name === target.name);
    }
    function findCardElBySkillName(name) {
      const n = norm(name);
      return findCardEl(txt => norm(txt) === n);
    }

    function flashRequirementByAny(r) {
      let card = null;
      if (r && r.id) card = findCardElBySkillId(r.id);
      if (!card && r && r.name) card = findCardElBySkillName(r.name);
      if (!card) return;
      card.classList.add('need-highlight');
      setTimeout(() => card.classList.remove('need-highlight'), 900);
    }

    function canIncrease(s) {
      // Points cap
      const cap = getSkillPointsCap();
      const used = countAllocated(allocated.skills);
      if (used >= cap) return false;
      // Max level
      const cur = allocated.skills[s.id] || 0;
      if (cur >= (s.maxLevel || 10)) return false;
      
      // Character level gating from wiki: s.lvlReq is an array per skill level
      const charLvl = Math.max(1, Math.min(MAX_LEVEL, parseInt(charLevel.value || '1', 10)));
      const reqArr = Array.isArray(s.lvlReq) ? s.lvlReq : null;
      if (reqArr) {
        const nextLevel = cur + 1;
        const needLevel = reqArr[Math.max(0, Math.min(reqArr.length - 1, nextLevel - 1))];
        if (typeof needLevel === 'number' && charLvl < needLevel) return false;
      }
      
      // Job/Skill prerequisites from wiki
      const reqs = s.requires || {};
      for (const key in reqs) {
        const r = reqs[key];
        if (r.id) { // Skill requirement
          const have = allocated.skills[r.id] || 0;
          if (have < (r.level || 1)) return false; // unmet
        } else if (r.level && r.name) { // Job requirement
          // Check against current job and character level.
          if (charLvl < r.level) return false;
        }
      }

      return true;
    }

    function canDecrease(s) {
      const cur = allocated.skills[s.id] || 0;
      if (cur <= 0) return false;
      const newLevel = cur - 1;
      // Check allocated dependents; allow decrease if newLevel still satisfies their required level
      const dependents = (reverseDeps[String(s.id)] || []).map(id => String(id));
      for (const depId of dependents) {
        const depCur = allocated.skills[depId] || 0;
        if (depCur <= 0) continue; // not invested
        // Find requirement object inside dependent referencing s
        const dependentSkill = (skills || []).find(x => String(x.id) === depId);
        if (!dependentSkill) continue;
        let reqLevelNeeded = 0;
        const reqs = dependentSkill.requires || {};
        for (const k in reqs) {
          const r = reqs[k];
          if (!r) continue;
          if ((r.id && String(r.id) === String(s.id)) || (r.name && norm(r.name) === norm(s.name))) {
            reqLevelNeeded = Math.max(reqLevelNeeded, r.level || 1);
          }
        }
        if (newLevel < reqLevelNeeded) {
          return false; // would break this dependent
        }
      }
      return true;
    }
    skills.forEach((s) => {
      const card = document.createElement('div');
      card.className = 'skill-card';
      const name = document.createElement('div');
      name.className = 'skill-name';
      name.textContent = s.name;
      attachTooltipHandlers(name, s);
      const ctrl = document.createElement('div');
      ctrl.className = 'skill-ctrl';
      const dec = document.createElement('button');
      dec.textContent = '-';
      dec.setAttribute('aria-label', 'Decrease ' + s.name);
      const badge = document.createElement('span');
      badge.className = 'skill-level';
      badge.textContent = (allocated.skills[s.id] || 0) + ' / ' + (s.maxLevel || 10);
      const inc = document.createElement('button');
      inc.textContent = '+';
      inc.setAttribute('aria-label', 'Increase ' + s.name);

      dec.addEventListener('click', () => {
        if (!canDecrease(s)) return;
        const cur = allocated.skills[s.id] || 0;
        if (cur > 0) allocated.skills[s.id] = cur - 1;
        if (allocated.skills[s.id] === 0) delete allocated.skills[s.id];
        badge.textContent = (allocated.skills[s.id] || 0) + ' / ' + (s.maxLevel || 10);
        updatePoints();
      });
      inc.addEventListener('click', (ev) => {
        const charLvl = Math.max(1, Math.min(MAX_LEVEL, parseInt(charLevel.value || '1', 10)));
        if (!canIncrease(s)) {
          const lines = unmetRequirementsMessage(s, charLvl);
          if (lines.length) {
            showTooltip(`<div class=\"tt-title\">Requirements</div><div class=\"tt-desc\">${lines.join('<br/>')}</div>`, ev.clientX, ev.clientY);
            // flash any required skills by id or name
            const reqs = s.requires || {};
            for (const k in reqs) flashRequirementByAny(reqs[k]);
            setTimeout(hideTooltip, 1500);
          }
          return;
        }
        const cur = allocated.skills[s.id] || 0;
        allocated.skills[s.id] = cur + 1;
        badge.textContent = (allocated.skills[s.id] || 0) + ' / ' + (s.maxLevel || 10);
        updatePoints();
      });

      ctrl.appendChild(dec);
      ctrl.appendChild(badge);
      ctrl.appendChild(inc);
      card.appendChild(name);
      card.appendChild(ctrl);
      skillsGrid.appendChild(card);
    });
    updatePoints();

    // Render DNA
    const dna = (data.dna && data.dna[currentSubclassId]) ? data.dna[currentSubclassId] : [];
    dnaGrid.innerHTML = '';
    dna.forEach((d) => {
      const card = document.createElement('div');
      card.className = 'skill-card';
      const name = document.createElement('div');
      name.className = 'skill-name';
      name.textContent = d.name;
      attachTooltipHandlers(name, d);
      const ctrl = document.createElement('div');
      ctrl.className = 'skill-ctrl';
      const dec = document.createElement('button');
      dec.textContent = '-';
      dec.setAttribute('aria-label', 'Decrease ' + d.name);
      const badge = document.createElement('span');
      badge.className = 'skill-level';
      badge.textContent = (allocated.dna[d.id] || 0) + ' / ' + (d.maxLevel || 10);
      const inc = document.createElement('button');
      inc.textContent = '+';
      inc.setAttribute('aria-label', 'Increase ' + d.name);

      dec.addEventListener('click', () => {
        const cur = allocated.dna[d.id] || 0;
        if (cur > 0) allocated.dna[d.id] = cur - 1;
        if (allocated.dna[d.id] === 0) delete allocated.dna[d.id];
        badge.textContent = (allocated.dna[d.id] || 0) + ' / ' + (d.maxLevel || 10);
        updatePoints();
      });
      inc.addEventListener('click', () => {
        const cur = allocated.dna[d.id] || 0;
        if (cur < (d.maxLevel || 10)) allocated.dna[d.id] = cur + 1;
        badge.textContent = (allocated.dna[d.id] || 0) + ' / ' + (d.maxLevel || 10);
        updatePoints();
      });

      ctrl.appendChild(dec);
      ctrl.appendChild(badge);
      ctrl.appendChild(inc);
      card.appendChild(name);
      card.appendChild(ctrl);
      dnaGrid.appendChild(card);
    });
  }

  function updatePoints() {
    // Simple placeholder logic: 1 point per skill level, 1 per DNA level
    const skillPoints = Object.values(allocated.skills).reduce((a, b) => a + b, 0);
    const dnaPoints = Object.values(allocated.dna).reduce((a, b) => a + b, 0);
    const cap = getSkillPointsCap();
    pointsSkills.textContent = 'Skills: ' + skillPoints + ' / ' + cap;
    pointsDNA.textContent = 'DNA: ' + dnaPoints;
    if (pointsHint) {
      if (cap === 0) {
        pointsHint.textContent = 'No skill points at current level. Increase level to allocate.';
      } else if (skillPoints >= cap) {
        pointsHint.textContent = 'Skill point cap reached. Increase level or reduce other skills.';
      } else {
        pointsHint.textContent = 'Skill requirements enabled. Some skills require a certain level or other skills.';
      }
    }
  }

  // Reset allocation button
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      allocated = { skills: {}, dna: {} };
      renderSkills();
      updatePoints();
      hideTooltip();
    });
  }

  // Global hide tooltip on scroll/resize/escape
  window.addEventListener('scroll', hideTooltip, { passive: true });
  window.addEventListener('resize', hideTooltip);
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') hideTooltip(); });

  loadJSON();
})();


