let peso_medio_mensal = [0];
let animais_doentes_mensal = [0];

const client = mqtt.connect('wss://broker.emqx.io:8084/mqtt');

client.on("connect", function () {
    console.log("Connected to broker");

    client.subscribe("flask/peso_medio");
    client.subscribe("flask/animais_doentes");
});

client.on("message", function (topic, message) {
    const data = parseInt(message);

    if (topic === "flask/peso_medio") {
        peso_medio_mensal.push(data);
        if (peso_medio_mensal.length > 12) peso_medio_mensal.shift();
        chart1.data.datasets[0].data = peso_medio_mensal;
    }

    if (topic === "flask/animais_doentes") {
        animais_doentes_mensal.push(data);
        if (animais_doentes_mensal.length > 12) animais_doentes_mensal.shift();
        chart1.data.datasets[1].data = animais_doentes_mensal;
    }

    chart1.update();
});



const ctx1 = document.getElementById('myChart').getContext('2d');
const chart1 = new Chart(ctx1, {
    type: 'line',
    data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez  '],
        datasets: [{
            label: 'Peso médio por mês',
            data: peso_medio_mensal,
            borderColor: '#0b55a8',
            tension: 0.2
        },
        {
            label: 'Nº de animais potencialmente doentes por mês',
            data: animais_doentes_mensal,
            borderColor: '#FF0000',
            tension: 0.2
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
