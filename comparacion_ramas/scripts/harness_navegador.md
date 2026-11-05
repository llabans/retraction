# Consultas del harness en el navegador (rama 3)

Bloques que Claude ejecutó con la extensión Claude in Chrome (`javascript_tool`) en la pestaña de una API pública. Se guardan como Markdown porque se pegan en la consola; no forman parte de ningún paquete.

```js
// Rama 3 (IA con herramientas): consultas ejecutadas en el navegador del investigador
// mediante la extensión Claude in Chrome (javascript_tool), porque el contenedor de
// Claude no tiene salida a E-utilities, Europe PMC ni OpenAlex.
// Cada bloque se pegó tal cual en la consola de la pestaña; los resultados se
// devolvieron en fragmentos de <=950 caracteres (límite de salida de la herramienta)
// y se verificaron con n y suma de identificadores (ver decodificar_delta36.py).
// Fechas de ejecución: 2026-11-04/05 (UTC). Sin claves de API.

// ---------- P1: PubMed E-utilities (esearch) ----------
// Texto libre en título/resumen de artículos con tipo "Retracted Publication".
async function p1() {
  const E = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&tool=retracciones_ecas_r3';
  const q = '"Retracted Publication"[pt] AND (randomized[tiab] OR randomised[tiab] OR randomly[tiab] OR placebo[tiab] OR trial[tiab] OR assigned[tiab]) AND 1800/01/01:2023/08/07[dp]';
  const r = await fetch(E + '&retmax=10000&term=' + encodeURIComponent(q)).then(r => r.json());
  window.P1 = r.esearchresult.idlist;
  return { count: r.esearchresult.count, translation: r.esearchresult.querytranslation };
}

// Codificación compacta para sacar la lista del navegador: PMIDs ordenados,
// diferencias sucesivas en base 36, separadas por coma, en fragmentos de 950.
function encodeDelta36(ids) {
  const a = ids.map(Number).sort((x, y) => x - y);
  let prev = 0;
  const s = a.map(v => { const d = (v - prev).toString(36); prev = v; return d; }).join(',');
  const chunks = [];
  for (let i = 0; i < s.length; i += 950) chunks.push(s.slice(i, i + 950));
  return { n: a.length, sum: a.reduce((x, y) => x + y, 0), chunks };
}

// ---------- Fecha de la nota para candidatos de P1 sin registro en RW ----------
// efetch XML -> CommentsCorrections RefType="RetractionIn" -> esummary de la nota.
async function fechasNota(ids) {
  const B = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/', T = '&tool=retracciones_ecas_r3';
  const map = {};
  for (let i = 0; i < ids.length; i += 100) {
    const x = await fetch(B + 'efetch.fcgi?db=pubmed&retmode=xml' + T + '&id=' + ids.slice(i, i + 100).join(',')).then(r => r.text());
    const doc = new DOMParser().parseFromString(x, 'text/xml');
    for (const a of doc.querySelectorAll('PubmedArticle')) {
      const p = a.querySelector('MedlineCitation > PMID').textContent;
      map[p] = [...a.querySelectorAll('CommentsCorrections[RefType="RetractionIn"] PMID')].map(e => e.textContent);
    }
    await new Promise(r => setTimeout(r, 400));
  }
  const notices = [...new Set(Object.values(map).flat())], nd = {};
  for (let i = 0; i < notices.length; i += 150) {
    const j = await fetch(B + 'esummary.fcgi?db=pubmed&retmode=json' + T + '&id=' + notices.slice(i, i + 150).join(',')).then(r => r.json());
    for (const k of j.result.uids) nd[k] = j.result[k].sortpubdate || j.result[k].pubdate;
    await new Promise(r => setTimeout(r, 400));
  }
  return Object.entries(map).map(([p, rs]) => {
    const ds = rs.map(n => nd[n]).filter(Boolean).sort();
    return [p, rs[0] || '', ds[0] || ''];
  });
}

// ---------- P2: Europe PMC ----------
async function p2() {
  const EP = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=lite&query=';
  const q = 'PUB_TYPE:"Retracted Publication" AND (TITLE_ABS:(randomized OR randomised OR randomly OR placebo OR trial OR assigned)) AND PUB_YEAR:[1800 TO 2023]';
  const all = await fetch(EP + encodeURIComponent(q) + '&pageSize=1').then(r => r.json());
  const extra = await fetch(EP + encodeURIComponent(q + ' AND NOT SRC:MED') + '&pageSize=100').then(r => r.json());
  return { version: all.version, total: all.hitCount, notInMedline: extra.hitCount };
}

// ---------- P3: OpenAlex ----------
// La búsqueda de texto anónima estaba suspendida (HTTP 503) y el paginado por cursor
// exige clave (HTTP 401). Desviación: se usan solo filtros (sin búsqueda), paginado
// por página (máx. 10 000 por consulta, por eso se parte por año) y se aplica el
// filtro de términos de ensayo al título en el navegador.
const TRIAL_RE = /randomi[sz]|\btrial\b|placebo|randomly|assigned/i;
async function p3(hasPmid, yearSlices) {
  const base = 'is_retracted:true,primary_topic.domain.id:4,has_pmid:' + hasPmid + ',publication_year:';
  const rows = [];
  for (const s of yearSlices) {
    for (let p = 1; p <= 50; p++) {
      const r = await fetch('https://api.openalex.org/works?per-page=200&page=' + p +
        '&select=id,doi,ids,title,publication_year&filter=' + encodeURIComponent(base + s));
      if (r.status !== 200) break;
      const j = await r.json();
      rows.push(...j.results);
      if (j.results.length < 200) break;
      await new Promise(z => setTimeout(z, 150));
    }
  }
  return rows.filter(x => TRIAL_RE.test(x.title || ''));
}
// Llamadas usadas: p3(false, ['<2024']) y p3(true, ['<2011','2011-2015','2016-2018','2019-2020','2021','2022','2023']).

// ---------- Verificación cruzada de un registro (Crossref + OpenAlex) ----------
async function verificar(doi) {
  const cr = await fetch('https://api.crossref.org/works/' + doi).then(r => r.json());
  const oa = await fetch('https://api.openalex.org/works/doi:' + doi + '?select=id,is_retracted,type,title,publication_year').then(r => r.json());
  return { crossref_title: cr.message.title, crossref_updated_by: cr.message['updated-by'] || null, openalex: oa };
}
```
