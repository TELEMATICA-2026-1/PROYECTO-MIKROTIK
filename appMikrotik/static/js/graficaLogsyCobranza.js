document.addEventListener("DOMContentLoaded", function() {
        // LLamado para cargar el numero de clientes según su estado
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

        // llamado para cargar los datos de los graficos 
        fetch('api/graficos-dashboard/') 
            .then(response => response.json())
            .then(data => {
                
                // 1. Gráfica de Líneas - Histórico de Logs
                const ctxLogs = document.getElementById('graficaLogsDash').getContext('2d');
                new Chart(ctxLogs, {
                    type: 'line',
                    data: {
                        labels: data.historico_logs.labels,
                        datasets: [
                            {
                                label: 'Éxitos',        //Linea de Exitos
                                data: data.historico_logs.exitos,
                                borderColor: '#10b981', 
                                backgroundColor: '#10b981',
                                tension: 0.4, // Genera el efecto de curva suave
                                borderWidth: 3,
                                pointRadius: 4,
                                pointBackgroundColor: '#10b981'
                            },
                            {
                                label: 'Errores',       //Linea de Errores 
                                data: data.historico_logs.errores,
                                borderColor: '#ef4444', 
                                backgroundColor: '#ef4444',
                                tension: 0.4, // Curva suave
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

                // 2. Gráfica de Dona - Estado de Cobranzas
                const estadoCobranzas = Object.keys(data.estado_cobranzas);         //Obtiene las categorias de estado
                const valoresCobranzas = Object.values(data.estado_cobranzas);      //Obtiene la cantidad de cliente por estado 

                // Se llevan los datos a porcentajes 
                const total = valoresCobranzas.reduce((a, b) => a + b, 0) || 1;
                const porcentajes = valoresCobranzas.map(v => Math.round((v / total) * 100));

                // Diccionario para mapear la etiquetas del estado del cliente 
                const etiquetasCambio = {
                    'Solvente': 'Clientes al día',
                    'Pendiente': 'Clientes morosos'
                };

                const etiquetasCobranzas = estadoCobranzas.map((estado, i) =>
                    `${etiquetasCambio[estado] || estado} (${porcentajes[i]}%)`
                );

                // Se usan los porcentajes como datos del gráfico para que la dona muestre proporciones
                const datosGrafica = porcentajes;

                //Se establecen los colores que rellenan la dona en base al estado de los clientes 
                const coloresCobranzas = estadoCobranzas.map(estado => {
                    const est = estado.toLowerCase();
                    if (est.includes('solvente')) return '#3b82f6';
                    if (est.includes('pendiente')) return '#ef4444';
                    return '#95a5a6';
                });

                // Obtener el contexto del canvas antes de crear la gráfica
                const ctxCobranzas = document.getElementById('graficaCobranzasDash').getContext('2d');

                new Chart(ctxCobranzas, {
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
                            legend: { position: 'top', labels: { 
                                color: '#111827',
                                padding: 20, 
                                usePointStyle: true, 
                                pointStyle: 'circle',
                                font: { 
                                size: 15,
                                family: "Arial",
                                weight: 'bold'}
                              } },
                            tooltip: {
                                callbacks: {
                                    // mostrar también el conteo absoluto en el tooltip
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

            })
            .catch(error => console.error('Error al cargar los gráficos del dashboard:', error));
    });