// Espera a que el DOM esté listo para ejecutar el código cuando la página cargue.
document.addEventListener('DOMContentLoaded', function () {

    const toastElement = document.getElementById('loginToast');

    // Si  existe el toast o  viene de un error de login, muestra el toast.
    if (!toastElement || toastElement.getAttribute('data-login-error') !== 'true') {
        return;
    }

    // Obtiene el botón de cerrar dentro del toast.
    const closeButton = toastElement.querySelector('.btn-close');

    // Función para mostrar el toast.
    const showToast = function () {
        toastElement.classList.remove('d-none');
        toastElement.classList.add('show');
        toastElement.setAttribute('aria-hidden', 'false');
        toastElement.style.display = 'block';
    };

    // Función para ocultar el toast.
    const hideToast = function () {
        toastElement.classList.remove('show');
        toastElement.classList.add('d-none');
        toastElement.setAttribute('aria-hidden', 'true');
        toastElement.style.display = 'none';
    };

    // Si existe el botón de cerrar, al hacer clic se oculta el toast.
    if (closeButton) {
        closeButton.addEventListener('click', function (event) {
            event.preventDefault();
            hideToast();
        });
    }

    // Muestra el toast al cargar la página.
    showToast();

    // Después de 5 segundos, el toast se oculta automáticamente.
    setTimeout(hideToast, 5000);
});
