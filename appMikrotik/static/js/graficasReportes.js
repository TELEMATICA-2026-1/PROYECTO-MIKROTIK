// Llamado asíncrono a tu API unificada
    fetch('/api/datos-reportes/')
        .then(response => response.json())
        .then(data => {
            
            // 1. Gráfica de Barras - Métodos de Pago
            new Chart(document.getElementById('graficaMetodos'), {
                type: 'bar',
                data: {
                    labels: data.ingresos_metodo.labels,
                    datasets: [{
                        label: 'Monto Recaudado ($)',
                        data: data.ingresos_metodo.data,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: data.ingresos_metodo.titulo } } }
            });

            // 2. Gráfica de Torta - Estado de Clientes
            new Chart(document.getElementById('graficaClientes'), {
                type: 'pie',
                data: {
                    labels: data.clientes_estado.labels,
                    datasets: [{
                        data: data.clientes_estado.data,
                        backgroundColor: ['#2ecc71', '#e74c3c', '#f1c40f', '#34495e']
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: data.clientes_estado.titulo } } }
            });

            // 3. Gráfica de Dona - Planes Populares
            new Chart(document.getElementById('graficaPlanes'), {
                type: 'doughnut',
                data: {
                    labels: data.planes_populares.labels,
                    datasets: [{
                        data: data.planes_populares.data,
                        backgroundColor: ['#9b59b6', '#3498db', '#1abc9c', '#e67e22']
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: data.planes_populares.titulo } } }
            });

            // 4. Gráfica de Líneas - Evolución Mensual
            new Chart(document.getElementById('graficaMensual'), {
                type: 'line',
                data: {
                    labels: data.ingresos_mensuales.labels,
                    datasets: [{
                        label: 'Ganancias mensuales ($)',
                        data: data.ingresos_mensuales.data,
                        borderColor: '#e67e22',
                        backgroundColor: 'rgba(230, 126, 34, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: data.ingresos_mensuales.titulo } } }
            });

            // 5. Gráfica de Área Polar - Logs de Errores
            new Chart(document.getElementById('graficaLogs'), {
                type: 'polarArea',
                data: {
                    labels: data.metricas_logs.labels,
                    datasets: [{
                        data: data.metricas_logs.data,
                        backgroundColor: ['rgba(231, 76, 60, 0.7)', 'rgba(241, 196, 15, 0.7)', 'rgba(52, 152, 219, 0.7)']
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: data.metricas_logs.titulo } } }
            });

        })
        .catch(error => console.error('Error al mapear las gráficas:', error));