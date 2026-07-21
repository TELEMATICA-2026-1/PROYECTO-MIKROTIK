document.addEventListener("DOMContentLoaded", function() {
        const filtroTemporal = document.getElementById('filtroTemporal');
        let graficoLogs = null;
        let graficoCobranzas = null;

        function renderizarGraficoLogs(data) {
            const ctxLogs = document.getElementById('graficaLogsDash').getContext('2d');

            if (graficoLogs) {
                graficoLogs.destroy();
            }

            graficoLogs = new Chart(ctxLogs, {
                type: 'line',
                data: {
                    labels: data.historico_logs.labels,
                    datasets: [
                        {
                            label: 'Éxitos',
                            data: data.historico_logs.exitos,
                            borderColor: '#10b981',
                            backgroundColor: '#10b981',
                            tension: 0.4,
                            borderWidth: 3,
                            pointRadius: 4,
                            pointBackgroundColor: '#10b981'
                        },
                        {
                            label: 'Errores',
                            data: data.historico_logs.errores,
                            borderColor: '#ef4444',
                            backgroundColor: '#ef4444',
                            tension: 0.4,
                            borderWidth: 3,
                            pointRadius: 4,
                            pointBackgroundColor: '#ef4444'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(0, 0, 0, 0.15)' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        function renderizarGraficoCobranzas(data) {
            const estadoCobranzas = Object.keys(data.estado_cobranzas);
            const valoresCobranzas = Object.values(data.estado_cobranzas);
            const total = valoresCobranzas.reduce((a, b) => a + b, 0) || 1;
            const porcentajes = valoresCobranzas.map(v => Math.round((v / total) * 100));

            const etiquetasCambio = {
                'Solvente': 'Clientes al día',
                'Pendiente': 'Clientes morosos'
            };

            const etiquetasCobranzas = estadoCobranzas.map((estado, i) =>
                `${etiquetasCambio[estado] || estado} (${porcentajes[i]}%)`
            );

            const datosGrafica = porcentajes;
            const coloresCobranzas = estadoCobranzas.map(estado => {
                const est = estado.toLowerCase();
                if (est.includes('solvente')) return '#3b82f6';
                if (est.includes('pendiente')) return '#ef4444';
                return '#95a5a6';
            });

            const ctxCobranzas = document.getElementById('graficaCobranzasDash').getContext('2d');

            if (graficoCobranzas) {
                graficoCobranzas.destroy();
            }

            graficoCobranzas = new Chart(ctxCobranzas, {
                type: 'doughnut',
                data: {
                    labels: etiquetasCobranzas,
                    datasets: [{
                        data: datosGrafica,
                        backgroundColor: coloresCobranzas,
                        borderWidth: 3,
                        borderColor: '#ffffff',
                        borderRadius: 7,
                        hoverOffset: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '55%',
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: '#111827',
                                padding: 20,
                                usePointStyle: true,
                                pointStyle: 'circle',
                                font: {
                                    size: 15,
                                    family: 'Arial',
                                    weight: 'bold'
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const i = context.dataIndex;
                                    const count = valoresCobranzas[i];
                                    const pct = porcentajes[i];
                                    return `${count} clientes (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }

        function cargarGraficoLogs(filtro = 'actualmente') {
            fetch(`api/graficos-dashboard/?filtro=${filtro}`)
                .then(response => response.json())
                .then(data => {
                    renderizarGraficoLogs(data);
                })
                .catch(error => console.error('Error al cargar el gráfico de logs del dashboard:', error));
        }

        function cargarDatosIniciales() {
            fetch('api/graficos-dashboard/?filtro=actualmente')
                .then(response => response.json())
                .then(data => {
                    renderizarGraficoLogs(data);
                    renderizarGraficoCobranzas(data);
                })
                .catch(error => console.error('Error al cargar los gráficos iniciales del dashboard:', error));
        }

        fetch('api/tarjetas-dashboard/')
            .then(response => response.json())
            .then(data => {
                try {
                    document.getElementById('tarjeta-solventes').textContent = data.solventes ?? 0;
                    document.getElementById('tarjeta-exonerados').textContent = data.exonerados ?? 0;
                    document.getElementById('tarjeta-pendientes').textContent = data.pendientes ?? 0;
                    document.getElementById('tarjeta-desconectados').textContent = data.desconectados ?? 0;
                } catch (e) {
                    console.error('Error al actualizar las tarjetas del dashboard:', e);
                }
            })
            .catch(err => console.error('Error al cargar las tarjetas del dashboard:', err));

        cargarDatosIniciales();

        if (filtroTemporal) {
            filtroTemporal.addEventListener('change', function() {
                cargarGraficoLogs(this.value);
            });
        }
    });