const navs = {
    chrome: { nombre: 'Chrome', icono: 'bi-browser-chrome', color: '#4285F4' },
    edge: { nombre: 'Microsoft Edge', icono: 'bi-microsoft', color: '#0078D4' },
    firefox: { nombre: 'Firefox', icono: 'bi-firefox', color: '#FF7139' },
    opera: { nombre: 'Opera', icono: 'bi-browser-safari', color: '#FF1B2D' }
};

function loading(show) {
    const el = id => document.getElementById(id);
    el('btnLeer').disabled = show;
    el('btnText').textContent = show ? 'Leyendo...' : 'Leer Historial de Navegadores';
    el('btnSpinner').classList.toggle('d-none', !show);
}

function renderNavs(resumen) {
    const cont = document.getElementById('navegadoresList');
    cont.innerHTML = Object.entries(resumen).map(([key, info]) => {
        const n = navs[key] || { nombre: key, icono: 'bi-browser', color: '#6B7280' };
        const cls = info.encontrado ? 'border-success border-opacity-25' : 'border-secondary border-opacity-25 bg-light bg-opacity-50';
        return `<div class="card shadow-sm border mb-3 ${cls}">
            <div class="card-body">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center">
                        <i class="bi ${n.icono} fs-3 me-3" style="color: ${n.color}; opacity: 0.8;"></i>
                        <div>
                            <h6 class="mb-1 fw-semibold">${n.nombre}</h6>
                            <small class="text-muted">${info.encontrado ? 'Navegador encontrado' : 'Navegador no encontrado'}</small>
                        </div>
                    </div>
                    <div class="text-end">
                        ${info.encontrado ? `<span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25">${info.insertados} insertados</span><br><small class="text-muted mt-1 d-block">${info.total_leidos} leídos</small>` : `<span class="badge bg-secondary bg-opacity-10 text-secondary border border-secondary border-opacity-25">No disponible</span>`}
                    </div>
                </div>
            </div>
        </div>`;
    }).join('');
    document.getElementById('resultadosContainer').classList.remove('d-none');
}

function stats() {
    fetch('/api/estadisticas').then(r => r.json()).then(d => {
        if (!d.success) return;
        const s = d.estadisticas, c = document.getElementById('statsRow');
        c.innerHTML = `<div class="col-md-4"><div class="card shadow-sm border-0 h-100"><div class="card-body"><p class="text-muted small mb-2">Total de Registros</p><h2 class="mb-0 fw-bold">${s.total.toLocaleString()}</h2></div></div></div>` +
            Object.entries(s.por_navegador).map(([nav, cant]) => {
                const n = navs[nav] || { nombre: nav, color: '#6B7280' };
                return `<div class="col-md-2"><div class="card shadow-sm border-0 h-100" style="border-left: 3px solid ${n.color} !important;"><div class="card-body"><p class="text-muted small mb-2">${n.nombre}</p><h3 class="mb-0 fw-bold">${cant.toLocaleString()}</h3></div></div></div>`;
            }).join('');
        document.getElementById('estadisticasContainer').classList.remove('d-none');
    });
}

async function leerHistorial() {
    loading(true);
    document.getElementById('alertContainer').innerHTML = '';
    document.getElementById('resultadosContainer').classList.add('d-none');
    try {
        const d = await (await fetch('/api/leer-historial', { method: 'POST', headers: { 'Content-Type': 'application/json' } })).json();
        if (d.success) { renderNavs(d.resumen); stats(); }
    } finally { loading(false); }
}

window.addEventListener('DOMContentLoaded', stats);
