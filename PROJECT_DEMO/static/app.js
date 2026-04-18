// SOUMISSION.DZ — SPA vanilla JS
// Auth + router + dashboard + coffre + refs + AO + kanban + facturation
'use strict';

const API = '';  // meme origine
const TOK_KEY = 'sdz_token';
const ME_KEY = 'sdz_me';

const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];

let token = sessionStorage.getItem(TOK_KEY);
let me = JSON.parse(sessionStorage.getItem(ME_KEY) || 'null');

// ---------- API helper ----------
async function api(path, opts={}) {
  const headers = opts.headers || {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!(opts.body instanceof FormData) && opts.body) headers['Content-Type'] = 'application/json';
  const r = await fetch(API + path, {...opts, headers});
  if (r.status === 401) { logout(); throw new Error('Auth expiree'); }
  const text = await r.text();
  let body;
  try { body = text ? JSON.parse(text) : null; } catch { body = text; }
  if (!r.ok) {
    const msg = body?.detail || `HTTP ${r.status}`;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
  return body;
}

function toast(msg, ms=3000) {
  const t = $('#toast');
  t.textContent = msg;
  t.hidden = false;
  setTimeout(() => t.hidden = true, ms);
}

// ---------- Auth ----------
function logout() {
  sessionStorage.removeItem(TOK_KEY);
  sessionStorage.removeItem(ME_KEY);
  token = null; me = null;
  showLogin();
}

function setSession(t, meData) {
  token = t; me = meData;
  sessionStorage.setItem(TOK_KEY, t);
  sessionStorage.setItem(ME_KEY, JSON.stringify(meData));
}

function showLogin() {
  $('#topbar').hidden = true;
  $$('#app > section').forEach(s => s.hidden = (s.id !== 'view-login'));
}

function showApp() {
  $('#topbar').hidden = false;
  $$('#app > section').forEach(s => s.hidden = (s.id === 'view-login'));
  $('#user-label').textContent = `${me.username} — ${me.organisation_nom} (${me.role})`;
  navigate(location.hash.slice(1) || 'dashboard');
}

// ---------- Login form ----------
$$('.tab').forEach(tab => tab.addEventListener('click', () => {
  $$('.tab').forEach(t => t.classList.remove('active'));
  tab.classList.add('active');
  $$('.tab-content').forEach(c => { c.classList.remove('active'); c.hidden = true; });
  const target = $(`#form-${tab.dataset.tab}`);
  target.classList.add('active'); target.hidden = false;
}));

$('#form-login').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    const r = await api('/auth/login', {
      method: 'POST', body: JSON.stringify(Object.fromEntries(fd))
    });
    token = r.access_token;
    const meData = await api('/auth/me', { headers: {Authorization: `Bearer ${token}`} });
    setSession(token, meData);
    showApp();
  } catch (err) {
    const errBox = $('#login-error');
    errBox.textContent = err.message;
    errBox.hidden = false;
  }
});

$('#form-signup-ent').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  try {
    const r = await api('/signup/entreprise', {method:'POST', body: JSON.stringify(fd)});
    token = r.access_token;
    const meData = await api('/auth/me');
    setSession(token, meData);
    showApp();
    toast('Compte cree avec succes');
  } catch (err) { $('#login-error').textContent = err.message; $('#login-error').hidden = false; }
});

$('#form-signup-cab').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  try {
    const r = await api('/signup/cabinet', {method:'POST', body: JSON.stringify(fd)});
    token = r.access_token;
    const meData = await api('/auth/me');
    setSession(token, meData);
    showApp();
    toast('Cabinet cree avec succes');
  } catch (err) { $('#login-error').textContent = err.message; $('#login-error').hidden = false; }
});

$('#btn-logout').addEventListener('click', logout);

// ---------- Router ----------
const routes = {};
function register(name, fn) { routes[name] = fn; }

async function navigate(name) {
  $$('#app > section').forEach(s => s.hidden = (s.id !== `view-${name}`));
  $$('#topbar nav a').forEach(a => a.classList.toggle('active', a.dataset.route === name));
  if (routes[name]) {
    try { await routes[name](); }
    catch (err) { toast('Erreur : ' + err.message); }
  }
}
window.addEventListener('hashchange', () => navigate(location.hash.slice(1) || 'dashboard'));

// ---------- DASHBOARD ----------
register('dashboard', async () => {
  const c = $('#dashboard-content');
  c.innerHTML = '<div class="card">Chargement…</div>';
  const [docs, alertes, refs, aos, factures] = await Promise.all([
    api('/coffre/documents').catch(() => []),
    api('/coffre/alertes').catch(() => []),
    api('/references').catch(() => []),
    api('/ao').catch(() => []),
    api('/factures').catch(() => []),
  ]);
  c.innerHTML = `
    <div class="kpi-grid">
      <div class="kpi"><div class="value">${docs.length}</div><div class="label">Documents</div></div>
      <div class="kpi"><div class="value ${alertes.length ? 'danger' : ''}">${alertes.length}</div><div class="label">Alertes expir.</div></div>
      <div class="kpi"><div class="value">${refs.length}</div><div class="label">References</div></div>
      <div class="kpi"><div class="value">${aos.length}</div><div class="label">AO actifs</div></div>
      <div class="kpi"><div class="value">${factures.length}</div><div class="label">Factures</div></div>
    </div>
    ${alertes.length ? `
      <div class="card">
        <h2>Alertes d'expiration</h2>
        <table>
          <thead><tr><th>Type</th><th>Date expiration</th><th>Jours</th><th>Seuil</th></tr></thead>
          <tbody>
            ${alertes.map(a => `<tr>
              <td>${a.type_code}</td>
              <td>${a.date_expiration}</td>
              <td>${a.jours_restants < 0 ? '<span class="danger">Expire</span>' : a.jours_restants + 'j'}</td>
              <td><span class="badge badge-${a.seuil === '7j' || a.seuil === 'expire' ? 'danger' : 'warn'}">${a.seuil}</span></td>
            </tr>`).join('')}
          </tbody>
        </table>
      </div>` : ''}
    <div class="card">
      <h2>Comptes de demonstration</h2>
      <p class="muted small">Disponibles apres bootstrap. Mot de passe : <code>Demo12345</code></p>
      <ul>
        <li><b>brahim@alpha-btph.dz</b> — Cas 1 entreprise (donnees pre-remplies)</li>
        <li><b>kamel@batipro-setif.dz</b>, <b>amine@hydra-etudes.dz</b>, <b>nadia@omega-fournitures.dz</b>, <b>omar@sud-travaux.dz</b></li>
        <li><b>mourad@cabinet-mourad.dz</b> — Cas 2 cabinet</li>
        <li><b>admin@soumission.dz</b> / <b>Admin12345</b> — admin plateforme</li>
      </ul>
    </div>
  `;
});

// ---------- COFFRE ----------
register('coffre', async () => {
  const c = $('#coffre-content');
  c.innerHTML = '<div class="card">Chargement…</div>';
  const [types, docs] = await Promise.all([api('/coffre/types'), api('/coffre/documents')]);
  c.innerHTML = `
    <div class="card">
      <h2>Ajouter un document</h2>
      <form id="upload-doc">
        <div class="flex">
          <select name="type_code" required style="flex:2">
            ${types.map(t => `<option value="${t.code}">${t.code} — ${t.libelle}</option>`).join('')}
          </select>
          <input type="date" name="date_expiration" placeholder="Date expiration" style="flex:1">
          <input type="file" name="file" accept=".pdf" required style="flex:2">
        </div>
        <button class="btn-primary" type="submit">Uploader</button>
      </form>
    </div>
    <div class="card">
      <h2>Documents (${docs.length})</h2>
      ${docs.length ? `
      <table>
        <thead><tr><th>Type</th><th>Fichier</th><th>Taille</th><th>Expiration</th><th>Actions</th></tr></thead>
        <tbody>
          ${docs.map(d => `<tr>
            <td>${d.type_code}</td>
            <td>${d.filename}</td>
            <td>${(d.size_bytes/1024).toFixed(1)} Ko</td>
            <td>${d.date_expiration || '—'}</td>
            <td class="actions">
              <a class="btn-secondary" href="/coffre/documents/${d.id}/download" target="_blank"
                 onclick="downloadAuth(event, this)">Telecharger</a>
              <button class="btn-danger" onclick="delDoc(${d.id})">Supprimer</button>
            </td>
          </tr>`).join('')}
        </tbody>
      </table>` : '<p class="empty">Aucun document. Uploadez le premier.</p>'}
    </div>
  `;
  $('#upload-doc').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await api('/coffre/documents', {method:'POST', body: fd});
      toast('Document ajoute');
      navigate('coffre');
    } catch (err) { toast('Erreur : ' + err.message); }
  });
});

window.delDoc = async (id) => {
  if (!confirm('Supprimer ce document ?')) return;
  try { await api(`/coffre/documents/${id}`, {method:'DELETE'}); toast('Supprime'); navigate('coffre'); }
  catch (e) { toast(e.message); }
};
window.downloadAuth = async (e, link) => {
  e.preventDefault();
  const url = link.getAttribute('href');
  const r = await fetch(url, {headers: {Authorization: `Bearer ${token}`}});
  if (!r.ok) { toast('Erreur telechargement'); return; }
  const blob = await r.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = link.dataset.filename || 'document.pdf';
  a.click();
};

// ---------- REFS ----------
register('refs', async () => {
  const c = $('#refs-content');
  const refs = await api('/references');
  c.innerHTML = `
    <div class="card">
      <h2>Nouvelle reference</h2>
      <form id="add-ref">
        <label>Objet du marche <input name="objet" required minlength="3"></label>
        <div class="flex">
          <label style="flex:2">Maitre d'ouvrage <input name="maitre_ouvrage"></label>
          <label style="flex:1">Annee <input type="number" name="annee" min="1990" max="2100"></label>
        </div>
        <div class="flex">
          <label style="flex:1">Montant DA <input type="number" name="montant_da" min="0"></label>
          <label style="flex:1">Type travaux <input name="type_travaux"></label>
        </div>
        <button class="btn-primary" type="submit">Ajouter</button>
      </form>
    </div>
    <div class="card">
      <h2>Vos references (${refs.length})</h2>
      ${refs.length ? `
      <table>
        <thead><tr><th>Objet</th><th>MO</th><th>Annee</th><th>Montant</th><th>Type</th><th></th></tr></thead>
        <tbody>${refs.map(r => `<tr>
          <td>${r.objet}</td><td>${r.maitre_ouvrage || '—'}</td><td>${r.annee || '—'}</td>
          <td>${r.montant_da ? r.montant_da.toLocaleString('fr-FR') + ' DA' : '—'}</td>
          <td>${r.type_travaux || '—'}</td>
          <td><button class="btn-danger" onclick="delRef(${r.id})">×</button></td>
        </tr>`).join('')}</tbody>
      </table>` : '<p class="empty">Aucune reference.</p>'}
    </div>
  `;
  $('#add-ref').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = Object.fromEntries(new FormData(e.target));
    for (const k of ['annee', 'montant_da']) if (fd[k] === '') delete fd[k]; else fd[k] = +fd[k];
    if (!fd.maitre_ouvrage) delete fd.maitre_ouvrage;
    if (!fd.type_travaux) delete fd.type_travaux;
    try { await api('/references', {method:'POST', body: JSON.stringify(fd)}); navigate('refs'); }
    catch (err) { toast(err.message); }
  });
});

window.delRef = async (id) => {
  if (!confirm('Supprimer cette reference ?')) return;
  await api(`/references/${id}`, {method:'DELETE'}); navigate('refs');
};

// ---------- AO + AUDIT ----------
register('ao', async () => {
  const c = $('#ao-content');
  const aos = await api('/ao');
  c.innerHTML = `
    <div class="card">
      <h2>Importer un AO depuis un PDF</h2>
      <form id="import-ao">
        <input type="file" name="file" accept=".pdf" required>
        <button class="btn-primary" type="submit">Importer + extraire</button>
      </form>
    </div>
    <div class="card">
      <h2>Creer un AO manuellement</h2>
      <form id="add-ao">
        <label>Reference <input name="reference"></label>
        <label>Objet <input name="objet" required minlength="3"></label>
        <div class="flex">
          <label style="flex:2">Maitre d'ouvrage <input name="maitre_ouvrage"></label>
          <label style="flex:1">Wilaya <input name="wilaya_code" maxlength="3"></label>
        </div>
        <div class="flex">
          <label style="flex:1">Date limite <input type="date" name="date_limite"></label>
          <label style="flex:1">Budget DA <input type="number" name="budget_estime_da"></label>
          <label style="flex:1">Qualification <input name="qualification_requise_cat" maxlength="10"></label>
        </div>
        <button class="btn-primary" type="submit">Creer l'AO</button>
      </form>
    </div>
    <div class="card">
      <h2>Vos appels d'offres (${aos.length})</h2>
      ${aos.length ? `
      <table>
        <thead><tr><th>Ref</th><th>Objet</th><th>MO</th><th>Wilaya</th><th>Date limite</th><th>Budget</th><th></th></tr></thead>
        <tbody>${aos.map(a => `<tr>
          <td>${a.reference || '—'}</td><td>${a.objet}</td><td>${a.maitre_ouvrage || '—'}</td>
          <td>${a.wilaya_code || '—'}</td><td>${a.date_limite || '—'}</td>
          <td>${a.budget_estime_da ? a.budget_estime_da.toLocaleString('fr-FR') + ' DA' : '—'}</td>
          <td class="actions">
            <button class="btn-secondary" onclick="auditAo(${a.id})">Auditer</button>
            <button class="btn-secondary" onclick="genMemo(${a.id})">Memoire</button>
          </td>
        </tr>`).join('')}</tbody>
      </table>` : '<p class="empty">Aucun AO.</p>'}
    </div>
    <div id="audit-result"></div>
  `;

  $('#add-ao').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = Object.fromEntries(new FormData(e.target));
    for (const k of ['budget_estime_da']) if (fd[k] === '') delete fd[k]; else fd[k] = +fd[k];
    Object.keys(fd).forEach(k => fd[k] === '' && delete fd[k]);
    try { await api('/ao', {method:'POST', body: JSON.stringify(fd)}); navigate('ao'); }
    catch (err) { toast(err.message); }
  });

  $('#import-ao').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      const r = await api('/ao/import-pdf', {method:'POST', body: fd});
      toast(`AO importe. Champs extraits: ${r.champs_extraits.join(', ') || 'aucun'}`);
      navigate('ao');
    } catch (err) { toast(err.message); }
  });
});

window.auditAo = async (id) => {
  try {
    const a = await api(`/ao/${id}/audit`);
    const target = $('#audit-result');
    target.innerHTML = `
      <div class="card">
        <h2>Audit — Score <span class="score">${a.score}</span> — ${a.verdict_global.toUpperCase()}</h2>
        <p>OK: <b class="ok">${a.total_ok}</b> &nbsp; Warning: <b class="warn">${a.total_warning}</b> &nbsp; Danger: <b class="danger">${a.total_danger}</b></p>
        <div class="rule-list">
          ${a.regles.map(r => `<div class="rule-item">
            <span class="rule-icon ${r.verdict}">${r.verdict === 'ok' ? '✓' : r.verdict === 'warning' ? '!' : '×'}</span>
            <div>
              <b>${r.libelle}</b> (poids ${r.poids}, ${r.categorie})<br>
              <span class="muted small">${r.message}</span>
              ${r.action ? `<br><span class="warn small">→ ${r.action}</span>` : ''}
            </div>
          </div>`).join('')}
        </div>
      </div>
    `;
    target.scrollIntoView({behavior:'smooth'});
  } catch (e) { toast(e.message); }
};

window.genMemo = async (id) => {
  const r = await fetch(`/memoire/generer?ao_id=${id}`, {headers: {Authorization: `Bearer ${token}`}});
  if (!r.ok) { toast('Erreur'); return; }
  const blob = await r.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `memoire_AO_${id}.docx`;
  a.click();
};

// ---------- DOSSIERS / KANBAN ----------
register('dossiers', async () => {
  const c = $('#dossiers-content');
  c.innerHTML = '<div class="card">Chargement…</div>';
  let kanban;
  try { kanban = await api('/dossiers/kanban'); }
  catch { c.innerHTML = '<div class="empty">Endpoint kanban indisponible.</div>'; return; }
  const cols = ['a_faire', 'en_cours', 'a_valider', 'termine'];
  const labels = {a_faire:'A faire', en_cours:'En cours', a_valider:'A valider', termine:'Termine'};
  c.innerHTML = `
    <div class="kanban">
      ${cols.map(s => `<div class="kanban-col"><h3>${labels[s]}</h3>
        ${(kanban[s] || []).map(d => `
          <div class="kanban-card">
            <div class="title">${d.nom}</div>
            <div class="meta">Etape : ${d.etape_actuelle}${d.score_audit ? ' · Score ' + d.score_audit : ''}</div>
          </div>`).join('') || '<p class="muted small">vide</p>'}
      </div>`).join('')}
    </div>
  `;
});

// ---------- CHIFFRAGE (prix + simulateur + templates) ----------
register('chiffrage', async () => {
  const c = $('#chiffrage-content');
  c.innerHTML = '<div class="card">Chargement du catalogue…</div>';
  const [articles, templates] = await Promise.all([
    api('/prix/articles'),
    api('/templates'),
  ]);

  // On groupe les articles par categorie pour l'affichage
  const categories = {};
  for (const a of articles) {
    (categories[a.categorie] = categories[a.categorie] || []).push(a);
  }

  c.innerHTML = `
    <div class="tabs">
      <button class="tab active" data-chtab="simulateur">Simulateur DQE</button>
      <button class="tab" data-chtab="templates">Templates chiffres</button>
      <button class="tab" data-chtab="catalogue">Catalogue (${articles.length} articles)</button>
    </div>

    <div id="chtab-simulateur" class="chtab active">
      <div class="card">
        <h2>Simulateur de prix</h2>
        <p class="muted small">Ajoutez des postes, saisissez vos prix proposes, le simulateur
        compare aux fourchettes observees sur le marche algerien et vous alerte si vous etes
        hors-fourchette.</p>
        <table id="sim-table">
          <thead><tr>
            <th style="width:36%">Article</th>
            <th style="width:16%">Quantite</th>
            <th style="width:16%">Prix propose (DA)</th>
            <th style="width:16%">Moy. marche</th>
            <th style="width:10%">Ecart</th>
            <th style="width:6%"></th>
          </tr></thead>
          <tbody id="sim-rows"></tbody>
          <tfoot>
            <tr>
              <td colspan="2" class="muted small">Total propose</td>
              <td id="sim-total-propose" style="font-weight:bold">—</td>
              <td class="muted small">Total reference</td>
              <td id="sim-total-ref">—</td>
              <td id="sim-ecart-global"></td>
            </tr>
          </tfoot>
        </table>
        <div class="flex" style="margin-top:1em">
          <button class="btn-secondary" id="btn-add-poste">+ Ajouter un poste</button>
          <div class="spacer"></div>
          <button class="btn-primary" id="btn-simuler">Simuler</button>
          <button class="btn-secondary" id="btn-export-csv">Exporter CSV</button>
        </div>
      </div>
    </div>

    <div id="chtab-templates" class="chtab" hidden>
      <div class="card">
        <h2>Chiffrage depuis un template</h2>
        <p class="muted small">Selectionnez un template (DQE de reference), saisissez votre
        budget cible, les quantites sont adaptees proportionnellement.</p>
        <div class="flex">
          <select id="tpl-code" style="flex:2">
            ${templates.map(t => `<option value="${t.code}">${t.nom} (ref ${t.budget_reference_da.toLocaleString('fr-FR')} DA)</option>`).join('')}
          </select>
          <input type="number" id="tpl-budget" placeholder="Budget cible DA" style="flex:1" min="1">
          <button class="btn-primary" id="btn-chiffrer">Chiffrer</button>
        </div>
        <div id="tpl-result"></div>
      </div>
    </div>

    <div id="chtab-catalogue" class="chtab" hidden>
      <div class="card">
        <h2>Catalogue de prix BTPH</h2>
        <input id="cat-search" placeholder="🔍 Filtrer par code, libelle ou categorie…" style="margin-bottom:1em">
        <table>
          <thead><tr>
            <th>Categorie</th><th>Code</th><th>Libelle</th><th>Unite</th>
            <th>Min</th><th>Moyen</th><th>Max</th>
          </tr></thead>
          <tbody id="cat-rows">
            ${Object.entries(categories).sort().map(([cat, arts]) =>
              arts.map((a, i) => `<tr data-search="${(a.code + ' ' + a.libelle + ' ' + a.categorie).toLowerCase()}">
                ${i === 0 ? `<td rowspan="${arts.length}" style="vertical-align:top"><b>${cat}</b></td>` : ''}
                <td><code>${a.code}</code></td>
                <td>${a.libelle}</td>
                <td class="muted">${a.unite}</td>
                <td>${a.prix_min_da.toLocaleString('fr-FR')}</td>
                <td><b>${a.prix_moy_da.toLocaleString('fr-FR')}</b></td>
                <td>${a.prix_max_da.toLocaleString('fr-FR')}</td>
              </tr>`).join('')
            ).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;

  // Tabs internes
  $$('#view-chiffrage .tab').forEach(b => b.addEventListener('click', () => {
    $$('#view-chiffrage .tab').forEach(t => t.classList.remove('active'));
    b.classList.add('active');
    $$('#view-chiffrage .chtab').forEach(p => p.hidden = true);
    $(`#chtab-${b.dataset.chtab}`).hidden = false;
  }));

  // Recherche catalogue
  $('#cat-search').addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    $$('#cat-rows tr').forEach(tr => {
      tr.style.display = !q || (tr.dataset.search || '').includes(q) ? '' : 'none';
    });
  });

  // Simulateur : gestion des lignes
  function renderSimRow() {
    const tr = document.createElement('tr');
    const articlesOptions = articles.map(a =>
      `<option value="${a.code}">${a.code} — ${a.libelle} (${a.unite})</option>`).join('');
    tr.innerHTML = `
      <td><select class="sim-art">${articlesOptions}</select></td>
      <td><input type="number" class="sim-qte" value="1" min="0.01" step="0.01"></td>
      <td><input type="number" class="sim-prix" placeholder="Prix propose" min="0"></td>
      <td class="sim-moy muted">—</td>
      <td class="sim-ecart">—</td>
      <td><button class="btn-danger sim-del">×</button></td>
    `;
    // Initialise l'affichage de la moyenne quand on change d'article
    const refreshMoy = () => {
      const code = tr.querySelector('.sim-art').value;
      const art = articles.find(a => a.code === code);
      tr.querySelector('.sim-moy').textContent = art ? art.prix_moy_da.toLocaleString('fr-FR') : '—';
    };
    tr.querySelector('.sim-art').addEventListener('change', refreshMoy);
    tr.querySelector('.sim-del').addEventListener('click', () => tr.remove());
    refreshMoy();
    $('#sim-rows').appendChild(tr);
  }

  $('#btn-add-poste').addEventListener('click', renderSimRow);

  // Pre-remplir 2 lignes d'exemple
  renderSimRow();
  renderSimRow();
  if ($$('#sim-rows tr').length >= 2) {
    const rows = $$('#sim-rows tr');
    rows[0].querySelector('.sim-art').value = 'GRO002';
    rows[0].querySelector('.sim-art').dispatchEvent(new Event('change'));
    rows[0].querySelector('.sim-qte').value = 100;
    rows[0].querySelector('.sim-prix').value = 28000;
    rows[1].querySelector('.sim-art').value = 'VRD005';
    rows[1].querySelector('.sim-art').dispatchEvent(new Event('change'));
    rows[1].querySelector('.sim-qte').value = 50;
    rows[1].querySelector('.sim-prix').value = 17000;
  }

  $('#btn-simuler').addEventListener('click', async () => {
    const postes = $$('#sim-rows tr').map(tr => {
      const code = tr.querySelector('.sim-art').value;
      const qte = parseFloat(tr.querySelector('.sim-qte').value) || 0;
      const prix = parseInt(tr.querySelector('.sim-prix').value) || 0;
      return { article_code: code, quantite: qte, prix_propose_da: prix, _tr: tr };
    }).filter(p => p.quantite > 0 && p.prix_propose_da > 0);

    if (!postes.length) { toast('Ajoutez au moins un poste avec quantite et prix.'); return; }

    try {
      const res = await api('/prix/simuler', {
        method: 'POST',
        body: JSON.stringify({ postes: postes.map(({_tr, ...p}) => p) }),
      });
      res.postes.forEach((p, i) => {
        const tr = postes[i]._tr;
        const ecartCell = tr.querySelector('.sim-ecart');
        const cls = p.verdict === 'ok' ? 'ok'
                  : p.verdict === 'hors_fourchette' ? 'danger' : 'warn';
        const sign = p.ecart_vs_moy_pct > 0 ? '+' : '';
        ecartCell.innerHTML = `<span class="badge badge-${cls === 'ok' ? 'ok' : cls === 'danger' ? 'danger' : 'warn'}">${sign}${p.ecart_vs_moy_pct}% ${p.verdict}</span>`;
      });
      $('#sim-total-propose').textContent = res.montant_total_propose_da.toLocaleString('fr-FR') + ' DA';
      $('#sim-total-ref').textContent = res.montant_total_reference_da.toLocaleString('fr-FR') + ' DA';
      const globalCls = Math.abs(res.ecart_global_pct) < 5 ? 'ok' : Math.abs(res.ecart_global_pct) < 15 ? 'warn' : 'danger';
      $('#sim-ecart-global').innerHTML = `<span class="badge badge-${globalCls}">${res.ecart_global_pct > 0 ? '+' : ''}${res.ecart_global_pct}%</span>`;
      // Stocker pour l'export CSV
      window._simResult = res;
      toast('Simulation calculee');
    } catch (err) { toast(err.message); }
  });

  $('#btn-export-csv').addEventListener('click', () => {
    const res = window._simResult;
    if (!res) { toast('Lancez une simulation avant d\'exporter.'); return; }
    const rows = [
      ['Code', 'Libelle', 'Quantite', 'Prix propose DA', 'Prix moyen DA', 'Ecart %', 'Verdict'],
      ...res.postes.map(p => [p.article_code, p.libelle, p.quantite, p.prix_propose_da, p.prix_moy_da, p.ecart_vs_moy_pct, p.verdict]),
      [],
      ['TOTAL propose', '', '', res.montant_total_propose_da, '', '', ''],
      ['TOTAL reference', '', '', '', res.montant_total_reference_da, '', ''],
      ['Ecart global', '', '', '', '', res.ecart_global_pct + '%', ''],
    ];
    const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(';')).join('\r\n');
    const blob = new Blob(['\ufeff' + csv], {type: 'text/csv;charset=utf-8'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `simulation_prix_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    toast('CSV telecharge');
  });

  // Templates : chiffrage
  $('#btn-chiffrer').addEventListener('click', async () => {
    const code = $('#tpl-code').value;
    const budget = parseInt($('#tpl-budget').value) || 0;
    if (budget < 1) { toast('Saisissez un budget cible.'); return; }
    try {
      const r = await api(`/templates/${code}/chiffrer`, {
        method: 'POST', body: JSON.stringify({budget_cible_da: budget})
      });
      window._tplResult = r;
      $('#tpl-result').innerHTML = `
        <h3 style="margin-top:1.5em">${r.nom}</h3>
        <p>Budget cible : <b>${r.budget_cible_da.toLocaleString('fr-FR')} DA</b>
           — Montant calcule : <b class="${r.montant_calcule_da <= r.budget_cible_da * 1.05 ? 'ok' : 'warn'}">${r.montant_calcule_da.toLocaleString('fr-FR')} DA</b></p>
        <table>
          <thead><tr><th>Code</th><th>Libelle</th><th>Unite</th><th>Quantite</th><th>P.U.</th><th>Total</th></tr></thead>
          <tbody>
            ${r.postes.map(p => `<tr>
              <td><code>${p.article_code}</code></td>
              <td>${p.libelle}</td>
              <td class="muted">${p.unite}</td>
              <td>${p.quantite.toLocaleString('fr-FR')}</td>
              <td>${p.prix_unitaire_da.toLocaleString('fr-FR')}</td>
              <td><b>${p.total_da.toLocaleString('fr-FR')}</b></td>
            </tr>`).join('')}
          </tbody>
        </table>
        <button class="btn-secondary" onclick="exportTplCsv()" style="margin-top:0.8em">Exporter CSV</button>
        <button class="btn-primary" onclick="importerDansSim()" style="margin-top:0.8em">Importer ces postes dans le simulateur</button>
      `;
    } catch (err) { toast(err.message); }
  });
});

window.exportTplCsv = () => {
  const r = window._tplResult;
  if (!r) return;
  const rows = [
    ['Code', 'Libelle', 'Unite', 'Quantite', 'Prix unitaire DA', 'Total DA'],
    ...r.postes.map(p => [p.article_code, p.libelle, p.unite, p.quantite, p.prix_unitaire_da, p.total_da]),
    [],
    ['', '', '', '', 'TOTAL', r.montant_calcule_da],
  ];
  const csv = rows.map(x => x.map(c => `"${String(c).replace(/"/g, '""')}"`).join(';')).join('\r\n');
  const blob = new Blob(['\ufeff' + csv], {type: 'text/csv;charset=utf-8'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `chiffrage_${r.code}_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
};

window.importerDansSim = () => {
  const r = window._tplResult;
  if (!r) return;
  // Bascule sur l'onglet simulateur
  $$('#view-chiffrage .tab').forEach(t => t.classList.remove('active'));
  $$('#view-chiffrage .tab')[0].classList.add('active');
  $$('#view-chiffrage .chtab').forEach(p => p.hidden = true);
  $('#chtab-simulateur').hidden = false;

  // Reinitialiser les lignes
  $('#sim-rows').innerHTML = '';
  r.postes.forEach(p => {
    const tr = document.createElement('tr');
    const articlesOptions = `<option value="${p.article_code}" selected>${p.article_code} — ${p.libelle}</option>`;
    tr.innerHTML = `
      <td><input value="${p.article_code}" readonly></td>
      <td><input type="number" class="sim-qte" value="${p.quantite}" min="0.01" step="0.01"></td>
      <td><input type="number" class="sim-prix" value="${p.prix_unitaire_da}" min="0"></td>
      <td class="sim-moy muted">${p.prix_unitaire_da.toLocaleString('fr-FR')}</td>
      <td class="sim-ecart">—</td>
      <td><button class="btn-danger sim-del">×</button></td>
    `;
    // Simuler une cellule .sim-art cachee pour compatibilite avec btn-simuler
    const hiddenSel = document.createElement('select');
    hiddenSel.className = 'sim-art';
    hiddenSel.style.display = 'none';
    hiddenSel.innerHTML = `<option value="${p.article_code}" selected></option>`;
    tr.querySelector('td:first-child').appendChild(hiddenSel);
    tr.querySelector('.sim-del').addEventListener('click', () => tr.remove());
    $('#sim-rows').appendChild(tr);
  });
  toast('Postes importes dans le simulateur');
};

// ---------- ASSISTANCE (catalogue + mes missions) ----------
register('assistance', async () => {
  const c = $('#assistance-content');
  c.innerHTML = '<div class="card">Chargement…</div>';
  const [prestations, missions] = await Promise.all([
    api('/assistance/prestations'),
    api('/missions').catch(() => []),
  ]);

  c.innerHTML = `
    <div class="card">
      <h2>Catalogue de prestations</h2>
      <p class="muted small">Un assistant agree de la plateforme intervient a votre place,
      sous mandat signe.</p>
      <table>
        <thead><tr><th>Code</th><th>Prestation</th><th>Delai</th><th>Prix HT</th><th>TTC (TVA 19%)</th><th></th></tr></thead>
        <tbody>${prestations.map(p => `<tr>
          <td><code>${p.code}</code></td>
          <td>${p.nom}<br><span class="muted small">${p.description}</span></td>
          <td>${p.delai_max_jours}j</td>
          <td>${p.prix_ht_da.toLocaleString('fr-FR')} DA</td>
          <td><b>${Math.round(p.prix_ht_da * 1.19).toLocaleString('fr-FR')} DA</b></td>
          <td><button class="btn-primary" onclick="demanderMission('${p.code}', '${p.nom.replace(/'/g, '\\\'')}')">Demander</button></td>
        </tr>`).join('')}</tbody>
      </table>
    </div>
    <div class="card">
      <h2>Mes missions (${missions.length})</h2>
      ${missions.length ? `<table>
        <thead><tr><th>#</th><th>Statut</th><th>Prestation</th><th>TTC</th><th>Creee le</th><th></th></tr></thead>
        <tbody>${missions.map(m => `<tr>
          <td>#${m.id}</td>
          <td><span class="badge badge-${missionBadge(m.statut)}">${m.statut}</span></td>
          <td>${m.prestation_code || '—'}</td>
          <td>${(m.prix_ttc_da || 0).toLocaleString('fr-FR')} DA</td>
          <td>${m.created_at ? m.created_at.slice(0,10) : '—'}</td>
          <td>${m.statut === 'brouillon'
            ? `<button class="btn-primary" onclick="signerMandat(${m.id})">Signer le mandat</button>`
            : m.statut === 'livree'
            ? `<button class="btn-primary" onclick="validerMission(${m.id})">Valider</button>`
            : ''}</td>
        </tr>`).join('')}</tbody>
      </table>` : '<p class="empty">Aucune mission.</p>'}
    </div>
  `;
});

function missionBadge(statut) {
  if (statut === 'validee') return 'ok';
  if (statut === 'en_cours' || statut === 'livree') return 'warn';
  if (statut === 'contestee') return 'danger';
  return 'warn';
}

window.demanderMission = async (code, nom) => {
  const brief = prompt(`Brief pour la prestation "${nom}" (10 caracteres minimum) :`,
                       `Demande d'assistance pour ${nom}. Precisions : `);
  if (!brief || brief.length < 10) return;
  try {
    await api('/missions', {
      method: 'POST',
      body: JSON.stringify({prestation_code: code, brief}),
    });
    toast('Mission creee au statut brouillon');
    navigate('assistance');
  } catch (e) { toast(e.message); }
};

window.signerMandat = async (id) => {
  if (!confirm('Signer electroniquement le mandat de representation ?')) return;
  try {
    await api(`/missions/${id}/signer-mandat`, {
      method: 'POST',
      body: JSON.stringify({accepte: true, valide_jours: 7}),
    });
    toast('Mandat signe, assistant affecte');
    navigate('assistance');
  } catch (e) { toast(e.message); }
};

window.validerMission = async (id) => {
  const note = prompt('Note sur 5 (1=mauvais, 5=excellent) :', '5');
  if (!note) return;
  const commentaire = prompt('Commentaire (optionnel) :', '');
  try {
    await api(`/missions/${id}/valider`, {
      method: 'POST',
      body: JSON.stringify({note: parseInt(note), commentaire: commentaire || ''}),
    });
    toast('Mission validee, assistant paye (mode mock)');
    navigate('assistance');
  } catch (e) { toast(e.message); }
};

// ---------- FACTURATION ----------
register('facturation', async () => {
  const c = $('#facturation-content');
  c.innerHTML = '<div class="card">Chargement…</div>';
  const [plans, abos, factures] = await Promise.all([
    api('/plans'), api('/abonnements'), api('/factures'),
  ]);
  c.innerHTML = `
    <div class="card">
      <h2>Plans tarifaires</h2>
      <table>
        <thead><tr><th>Code</th><th>Nom</th><th>Mensuel</th><th>Annuel (-10%)</th><th></th></tr></thead>
        <tbody>${plans.map(p => `<tr>
          <td><b>${p.code}</b></td><td>${p.nom}</td>
          <td>${p.prix_mensuel_da.toLocaleString('fr-FR')} DA</td>
          <td>${p.prix_annuel_da.toLocaleString('fr-FR')} DA</td>
          <td class="actions">
            <button class="btn-primary" onclick="souscrire('${p.code}', 'mensuel')">Souscrire mensuel</button>
          </td>
        </tr>`).join('')}</tbody>
      </table>
    </div>
    <div class="card">
      <h2>Vos abonnements (${abos.length})</h2>
      ${abos.length ? `<table>
        <thead><tr><th>Plan</th><th>Periodicite</th><th>Debut</th><th>Fin</th><th>Statut</th><th>Montant</th></tr></thead>
        <tbody>${abos.map(a => `<tr>
          <td>${a.plan_code}</td><td>${a.periodicite}</td>
          <td>${a.debut}</td><td>${a.fin || '—'}</td>
          <td><span class="badge badge-${a.statut === 'actif' ? 'ok' : 'warn'}">${a.statut}</span></td>
          <td>${a.montant_da.toLocaleString('fr-FR')} DA</td>
        </tr>`).join('')}</tbody>
      </table>` : '<p class="empty">Aucun abonnement.</p>'}
    </div>
    <div class="card">
      <h2>Vos factures (${factures.length})</h2>
      ${factures.length ? `<table>
        <thead><tr><th>N°</th><th>Date</th><th>Libelle</th><th>HT</th><th>TTC</th><th>Statut</th><th></th></tr></thead>
        <tbody>${factures.map(f => `<tr>
          <td>${f.numero}</td><td>${f.date_emission}</td><td>${f.libelle}</td>
          <td>${f.prix_ht_da.toLocaleString('fr-FR')}</td>
          <td><b>${f.prix_ttc_da.toLocaleString('fr-FR')}</b></td>
          <td><span class="badge badge-${f.statut === 'payee' ? 'ok' : 'warn'}">${f.statut}</span></td>
          <td class="actions">
            <button class="btn-secondary" onclick="dlFacture(${f.id}, '${f.numero}')">PDF</button>
            ${f.statut !== 'payee' ? `<button class="btn-primary" onclick="payerFacture(${f.id})">Payer</button>` : ''}
          </td>
        </tr>`).join('')}</tbody>
      </table>` : '<p class="empty">Aucune facture.</p>'}
    </div>
  `;
});

window.souscrire = async (code, periodicite) => {
  try {
    await api('/abonnements', {method:'POST', body: JSON.stringify({plan_code: code, periodicite})});
    toast('Abonnement cree');
    navigate('facturation');
  } catch (e) { toast(e.message); }
};
window.dlFacture = async (id, num) => {
  const r = await fetch(`/factures/${id}/pdf`, {headers: {Authorization: `Bearer ${token}`}});
  const blob = await r.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = `${num}.pdf`; a.click();
};
window.payerFacture = async (id) => {
  if (!confirm('Confirmer le paiement (mode mock Edahabia) ?')) return;
  await api(`/factures/${id}/payer`, {method:'POST', body: JSON.stringify({mode_paiement: 'edahabia'})});
  toast('Paiement enregistre');
  navigate('facturation');
};

// ---------- BOOT ----------
(async () => {
  if (token) {
    try { me = await api('/auth/me'); setSession(token, me); showApp(); }
    catch { logout(); }
  } else {
    showLogin();
  }
})();
