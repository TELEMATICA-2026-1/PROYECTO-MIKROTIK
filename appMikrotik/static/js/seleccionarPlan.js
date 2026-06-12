
    document.addEventListener('DOMContentLoaded', function() {
        // se Obtienen referencias a los elementos del formulario
        const planSelect = document.querySelector('#id_idPlan');
        const precioInput = document.querySelector('#id_plan_precioUSD');
        const subidaInput = document.querySelector('#id_plan_velocidad_subida');
        const bajadaInput = document.querySelector('#id_plan_velocidad_bajada');

        function actualizarDatosPlan() {
            // se obtiene la opción seleccionada y se actualizan los campos de precio y velocidades con los datos almacenados en los atributos data- de la opción seleccionada
            const opcion = planSelect?.selectedOptions?.[0];
            precioInput.value = opcion?.dataset?.preciousd || '';
            subidaInput.value = opcion?.dataset?.velocidadSubida || '';
            bajadaInput.value = opcion?.dataset?.velocidadBajada || '';
        }

        // se Agrega un event listener al select de planes para actualizar los datos cada vez que se cambie la selección, y también se llama a la función una vez al cargar la página para mostrar los datos del plan seleccionado por defecto
        if (planSelect) {
            planSelect.addEventListener('change', actualizarDatosPlan);
            actualizarDatosPlan();
        }
    });
