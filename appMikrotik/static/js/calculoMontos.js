// Se obtienen las referencias a los campos de entrada para el monto en dólares, el monto en bolívares y la tasa del día
  const usdEntrada = document.getElementById('id_montoUSD');
  const bsEntrada = document.getElementById('monto_bs');
  const tasaEntrada = document.getElementById('id_tasa');

  // Función para convertir una cadena de texto a un número decimal, manejando comas como separadores decimales y eliminando espacios
  function pasar_Decimal(value) {
    if (!value) return 0;
    return parseFloat(value.toString().replace(/\s+/g, '').replace(',', '.')) || 0;
  }

  // Función para limpiar la entrada del usuario, permitiendo solo números y un punto decimal, y ajustando la posición del cursor después de la limpieza
  function sanitizeNumericInput(input) {
    if (!input) return;
    let val = input.value || '';
    const cursor = input.selectionStart || 0;

    // reemplazar comas por puntos
    val = val.replace(/,/g, '.');

    // remover caracteres no numéricos excepto el punto
    val = val.replace(/[^0-9.]/g, '');

    // permitir solo un punto decimal
    const firstDot = val.indexOf('.');
    if (firstDot !== -1) {
      val = val.slice(0, firstDot + 1) + val.slice(firstDot + 1).replace(/\./g, '');
    }

    input.value = val;

    // ajustar la posición del cursor después de la limpieza
    const newPos = Math.min(cursor, val.length);
    try { input.setSelectionRange(newPos, newPos); } catch (e) { /* ignore */ }
  }

  // Función para formatear un número a una cadena con dos decimales, asegurando que se use un punto como separador decimal
  function formatoDecimal(value) {
    return Number(value).toFixed(2).toString().replace(',', '.');
  }

  // Función para calcular el monto en bolívares a partir del monto en dólares y la tasa del día, actualizando el campo de bolívares
  function CambioUsd() {
    const usd = pasar_Decimal(usdEntrada.value);
    const tasa = pasar_Decimal(tasaEntrada.value);
    bsEntrada.value = tasa > 0 ? formatoDecimal(usd * tasa) : '';
  }


  // Función para calcular el monto en dólares a partir del monto en bolívares y la tasa del día, actualizando el campo de dólares
  function CambioBs() {
    const bs = pasar_Decimal(bsEntrada.value);
    const tasa = pasar_Decimal(tasaEntrada.value);
    usdEntrada.value = tasa > 0 ? formatoDecimal(bs / tasa) : '';
  }

  // Variable para rastrear cuál campo fue editado por última vez, para determinar qué cálculo realizar al cambiar la tasa del día
  let campoEditado = null;

  // Agregar event listeners a los campos de entrada para detectar cambios y realizar los cálculos correspondientes.
  usdEntrada?.addEventListener('input', () => {
    sanitizeNumericInput(usdEntrada);
    campoEditado = 'usd';
    CambioUsd();
  });

  // Agregar un event listener en el campo de bolívares, para realizar el cálculo cuando el usuario termine de editar el campo
  bsEntrada?.addEventListener('input', () => {
    sanitizeNumericInput(bsEntrada);
    campoEditado = 'bs';
    CambioBs();
  });

  bsEntrada?.addEventListener('change', () => {
    sanitizeNumericInput(bsEntrada);
    campoEditado = 'bs';
    CambioBs();
  });

  // Agregar un event listener en el campo de tasa del día, para recalcular los montos en dólares o bolívares según el último campo editado
  tasaEntrada?.addEventListener('input', () => {
    sanitizeNumericInput(tasaEntrada);
    if (campoEditado === 'bs') {
      CambioBs();
    } else {
      CambioUsd();
    }
  });

  // Limpiar los campos de entrada al cargar la página para evitar mostrar valores anteriores, y resetear la variable de campo editado
  document.addEventListener('DOMContentLoaded', () => {
    if (usdEntrada) usdEntrada.value = '';
    if (bsEntrada) bsEntrada.value = '';
    campoEditado = null;
  });

