document.addEventListener("DOMContentLoaded", function() {
    let instanciaMetodos = null;
    let instanciaSemanas = null;
    let instanciaClientes = null;
    let instanciaPlanes = null;
    let instanciaEvolucion = null;

    function formatearMoneda(valor) {
        return parseFloat(valor).toLocaleString('de-DE', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function renderizarPaneles(filtro) {
        fetch(`/api/datos-reportes/?filtro=${filtro}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('tarjetaUSD').innerText = `$ ${formatearMoneda(data.tarjetas.usd)}`;
                document.getElementById('tarjetaVES').innerText = `Bs. ${formatearMoneda(data.tarjetas.ves)}`;

                if (instanciaMetodos) instanciaMetodos.destroy();
                if (instanciaSemanas) instanciaSemanas.destroy();
                if (instanciaClientes) instanciaClientes.destroy();
                if (instanciaPlanes) instanciaPlanes.destroy();
                if (instanciaEvolucion) instanciaEvolucion.destroy();

                instanciaMetodos = new Chart(document.getElementById('graficaMetodos').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.ingresos_metodo.labels,
                        datasets: [{
                            label: 'Ingresos ($)',
                            data: data.ingresos_metodo.data,
                            backgroundColor: '#4e73df',
                            hoverBackgroundColor: '#2e59d9',
                            borderColor: '#4e73df',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: { y: { beginAtZero: true } },
                        plugins: { title: { display: true, text: data.ingresos_metodo.titulo } }
                    }
                });

                instanciaSemanas = new Chart(document.getElementById('graficaSemanas').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.ingresos_semanas.labels,
                        datasets: [{
                            label: 'Recaudación ($)',
                            data: data.ingresos_semanas.data,
                            backgroundColor: '#1cc88a',
                            hoverBackgroundColor: '#17a673',
                            borderColor: '#1cc88a',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: { y: { beginAtZero: true } },
                        plugins: { title: { display: true, text: data.ingresos_semanas.titulo } }
                    }
                });

                instanciaClientes = new Chart(document.getElementById('graficaClientes').getContext('2d'), {
                    type: 'pie',
                    data: {
                        labels: data.clientes_estado.labels,
                        datasets: [{
                            data: data.clientes_estado.data,
                            backgroundColor: ['#2ecc71', '#e74c3c', '#f1c40f', '#34495e']
                        }]
                    },
                    options: {
                        responsive: true,
                        radius: '70%',
                        plugins: { title: { display: true, text: data.clientes_estado.titulo } }
                    }
                });

                instanciaPlanes = new Chart(document.getElementById('graficaPlanes').getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: data.planes_vendidos.labels,
                        datasets: [{
                            data: data.planes_vendidos.data,
                            backgroundColor: ['#9b5de5', '#b583f2', '#cca7f8', '#16a085', '#bdc3c7'],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        cutout: '55%',
                        radius: '70%',
                        plugins: { title: { display: true, text: data.planes_vendidos.titulo } }
                    }
                });

                instanciaEvolucion = new Chart(document.getElementById('graficaEvolucion').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.evolucion_ingresos.labels,
                        datasets: [{
                            label: 'Ganancias mensuales ($)',
                            data: data.evolucion_ingresos.data,
                            backgroundColor: '#e67e22',
                            hoverBackgroundColor: '#d35400',
                            borderColor: '#e67e22',
                            borderWidth: 1,
                            maxBarThickness: 40
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { title: { display: true, text: data.evolucion_ingresos.titulo } },
                        scales: {
                            y: { beginAtZero: true, grid: { color: '#e2e8f0' } },
                            x: { grid: { display: false } }
                        }
                    }
                });
            })
            .catch(err => console.error("Error cargando la API de reportes:", err));
    }

    document.getElementById('filtroTemporal').addEventListener('change', function() {
        renderizarPaneles(this.value);
    });

    document.getElementById('btnDescargarPDF').addEventListener('click', function() {
        const filtroActivo = document.getElementById('filtroTemporal').value;
        window.location.href = `/descargar-pdf/?filtro=${filtroActivo}`;
    });

    renderizarPaneles('actualmente');
});
