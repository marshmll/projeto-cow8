const ctx1 = document.getElementById('means').getContext('2d');
const chart1 = new Chart(ctx1, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Peso médio',
            data: [0],
            backgroundColor: '#0b00a6',
            borderColor: '#0b55a8',
            tension: 0.1
        }],
    },
    options: {
        scales: {
            x: {
                grid: {
                    color: '#909090',
                    borderColor: 'rgba(200, 200, 200, 0.8)',
                },
                ticks: {
                    color: "#ffffff"
                },
                title: {
                    color: "#ffffff"
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: '#909090',
                    borderColor: 'rgba(200, 200, 200, 0.8)'
                },
                ticks: {
                    color: "#ffffff"
                },
                title: {
                    color: "#ffffff"
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: "#ffffff"
                }
            }
        }
    }
});

const ctx2 = document.getElementById('risk').getContext('2d');
const chart2 = new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Nº de animais potencialmente doentes',
            data: [0],  
            borderColor: '#FF4444',
            backgroundColor: '#AA2222',
            tension: 0.1
        }],
    },
    options: {
        scales: {
            x: {
                grid: {
                    color: '#909090',
                    borderColor: 'rgba(200, 200, 200, 0.8)',
                },
                ticks: {
                    color: "#ffffff"
                },
                title: {
                    color: "#ffffff"
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: '#909090',
                    borderColor: 'rgba(200, 200, 200, 0.8)'
                },
                ticks: {
                    color: "#ffffff"
                },
                title: {
                    color: "#ffffff"
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: "#ffffff"
                }
            }
        }
    }
});

const client = mqtt.connect('wss://broker.emqx.io:8084/mqtt');

client.on("connect", () => {
    console.log("Connected to broker");

    client.subscribe("flask/peso_medio");
    client.subscribe("flask/animais_doentes");
});

client.on("message", (topic, message) => {
    // const data = parseInt(message);

    // if (topic === "flask/peso_medio") {
    //     peso_medio_mensal.push(data);
    //     if (peso_medio_mensal.length > 12) peso_medio_mensal.shift();
    //     chart1.data.datasets[0].data = peso_medio_mensal;
    // }

    // if (topic === "flask/animais_doentes") {
    //     animais_doentes_mensal.push(data);
    //     if (animais_doentes_mensal.length > 12) animais_doentes_mensal.shift();
    //     chart1.data.datasets[1].data = animais_doentes_mensal;
    // }

    // chart1.update();
});

function setChartMeansData(data) {
    const labels = data.map(element => element.month_name.substring(0, 3).toUpperCase());
    const weights = data.map(element => element.avg_weight);

    chart1.data.labels = labels;
    chart1.data.datasets[0].data = weights

    chart1.update();
}

function setChartHealthMetricsData(data) {
    const labels = data.map(element => element.month_name.substring(0, 3).toUpperCase());
    const risk = data.map(element => element.total_at_risk);

    chart2.data.labels = labels;
    chart2.data.datasets[0].data = risk

    chart2.update();
}

function setSummaryData(data) {
    const html = `
        <div class="summary__item">
            <div class="summary__title">
                <div class="summary__icon summary__icon--total"></div>
                <span class="summary__subject">Animais Registrados</span>
            </div>
            <span class="summary__value">${data.total_animals} animais</span>
        </div>
        <div class="summary__item">
            <div class="summary__title">
                <div class="summary__icon summary__icon--health"></div>
                <span class="summary__subject">Animais Saudáveis</span>
            </div>
            <span class="summary__value">${data.healthy_animals} animais</span>
        </div>
        <div class="summary__item">
            <div class="summary__title">
                <div class="summary__icon summary__icon--health"></div>
                <span class="summary__subject">Animais em Estado de Alerta</span>
            </div>
            <span class="summary__value">${data.warning_animals} animais</span>
        </div>
        <div class="summary__item">
            <div class="summary__title">
                <div class="summary__icon summary__icon--health"></div>
                <span class="summary__subject">Animais em Estado Crítico</span>
            </div>
            <span class="summary__value">${data.critical_animals} animais</span>
        </div>
        <div class="summary__item">
            <div class="summary__title">
                <div class="summary__icon summary__icon--health"></div>
                <span class="summary__subject">Condição Geral de Saúde</span>
            </div>
            <span class="summary__value">${data.health_status}%</span>
        </div>
    `;

    document.querySelector(".summary").innerHTML = html;
}

fetch("means").then(res => res.json()).then(data => {
    setChartMeansData(data);
});

fetch("health_metrics").then(res => res.json()).then(data => {
    setChartHealthMetricsData(data);
});

fetch("health_status").then(res => res.json()).then(data => {
    setSummaryData(data);
});
