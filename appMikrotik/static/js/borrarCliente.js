// Script para manejar la lógica del modal de confirmación de eliminación/desactivación de cliente

document.addEventListener('DOMContentLoaded', function () {
    var modal = document.getElementById('confirmarBorradoModal');
    if (!modal) return;

    modal.addEventListener('show.bs.modal', function (event) {
        // El botón que disparó el modal
        var button = event.relatedTarget;
        if (!button) return;

        // Obtener la URL de eliminación y el nombre del cliente desde los atributos data del botón
        var rutaBorrado = button.getAttribute('data-delete-url');
        var clienteNombre = button.getAttribute('data-client-name');

        // Configurar el formulario del modal con la URL de eliminación y mostrar el nombre del cliente
        var form = modal.querySelector('#confirmarBorradoForm');
        var campoNombre = modal.querySelector('#confirmarBorradoClienteNombre');

        // Actualizar el formulario y el texto del modal
        if (form && rutaBorrado) {
            form.action = rutaBorrado;
        }
        if (campoNombre) {
            campoNombre.textContent = clienteNombre || '';
        }
    });
});