const ctx1 = document.getElementById('myChart').getContext('2d');
const chart1 = new Chart(ctx1, {
    type: 'line',
    data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez  '],
        datasets: [{
            label: 'Peso médio por mês',
            data: [12, 19, 3, 5, 7, 8, 10, 12, 7, 9, 13, 6],
            borderColor: '#0b55a8',
            tension: 0.2
        },
        {
            label: 'Nº de animais potencialmente doentes por mês',
            data: [2, 4, 17, 21, 23, 22, 15, 14, 10, 4, 6, 8],
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
