// Deshabilitar el botón antes de la solicitud
document.body.addEventListener('htmx:beforeRequest', function() {
    const btn = document.getElementById('btnLeer');
    const btnText = document.getElementById('btnText');
    btn.disabled = true;
    btnText.textContent = 'Extrayendo historial de navegadores ...';
});

// Deshabilitar el botón después de la solicitud
document.body.addEventListener('htmx:afterRequest', function() {
    const btn = document.getElementById('btnLeer');
    const btnText = document.getElementById('btnText');
    btn.disabled = false;
    btnText.textContent = 'Leer Historial de Navegadores';
});
