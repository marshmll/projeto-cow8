const ctx1 = document.getElementById("means").getContext("2d");
const chart1 = new Chart(ctx1, {
    type: "line",
    data: {
        labels: [],
        datasets: [
            {
                label: "Peso médio",
                data: [0],
                backgroundColor: "#0b00a6",
                borderColor: "#0b55a8",
                tension: 0.2,
            },
        ],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                grid: {
                    color: "#909090",
                    borderColor: "rgba(200, 200, 200, 0.8)",
                },
                ticks: {
                    color: "#ffffff",
                },
                title: {
                    color: "#ffffff",
                },
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: "#909090",
                    borderColor: "rgba(200, 200, 200, 0.8)",
                },
                ticks: {
                    color: "#ffffff",
                },
                title: {
                    color: "#ffffff",
                },
            },
        },
        plugins: {
            legend: {
                labels: {
                    color: "#ffffff",
                },
            },
        },
    },
});

const ctx2 = document.getElementById("risk").getContext("2d");
const chart2 = new Chart(ctx2, {
    type: "line",
    data: {
        labels: [],
        datasets: [
            {
                label: "Nº de animais potencialmente doentes",
                data: [0],
                borderColor: "#FF4444",
                backgroundColor: "#AA2222",
                tension: 0.2,
            },
        ],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                grid: {
                    color: "#909090",
                    borderColor: "rgba(200, 200, 200, 0.8)",
                },
                ticks: {
                    color: "#ffffff",
                },
                title: {
                    color: "#ffffff",
                },
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: "#909090",
                    borderColor: "rgba(200, 200, 200, 0.8)",
                },
                ticks: {
                    color: "#ffffff",
                },
                title: {
                    color: "#ffffff",
                },
            },
        },
        plugins: {
            legend: {
                labels: {
                    color: "#ffffff",
                },
            },
        },
    },
});

const client = mqtt.connect("wss://broker.emqx.io:8084/mqtt");

client.on("connect", () => {
    console.log("Connected to broker");
    client.subscribe("flask/peso_medio");
    client.subscribe("flask/animais_doentes");
});

client.on("message", (topic, message) => {
    // Handle MQTT messages if needed
});

function setChartMeansData(data) {
    const labels = data.map((element) =>
        element.month_name.substring(0, 3).toUpperCase()
    );
    const weights = data.map((element) => element.avg_weight);

    chart1.data.labels = labels;
    chart1.data.datasets[0].data = weights;
    chart1.update();
}

function setChartHealthMetricsData(data) {
    const labels = data.map((element) =>
        element.month_name.substring(0, 3).toUpperCase()
    );
    const risk = data.map((element) => element.total_at_risk);

    chart2.data.labels = labels;
    chart2.data.datasets[0].data = risk;
    chart2.update();
}

function setSummaryData(data) {
    const summaryContainer = document.querySelector(".summary");

    summaryContainer.innerHTML = `
        <div class="bg-blue-600 h-32 p-4 text-white flex flex-col justify-between rounded-lg">
            <div class="flex items-center">
                <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 bg-[url('static/assets/images/icons/icon_white.svg')] bg-center bg-[length:80%] bg-no-repeat"></div>
                <span class="text-sm">Total de Animais</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.total_animals} animais</span>
        </div>
        <div class="bg-green-600 h-32 p-4 text-white flex flex-col justify-between rounded-lg">
            <div class="flex items-center">
                <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 flex items-center justify-center">
                    <i class="fa-solid fa-heart-pulse"></i>
                </div>
                <span class="text-sm">Animais Saudáveis</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.healthy_animals} animais</span>
        </div>
        <div class="bg-yellow-600 h-32 p-4 text-white flex flex-col justify-between rounded-lg">
            <div class="flex items-center">
                <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 flex items-center justify-center">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                </div>
                <span class="text-sm">Animais em Alerta</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.warning_animals} animais</span>
        </div>
        <div class="bg-red-600 h-32 p-4 text-white flex flex-col justify-between rounded-lg">
            <div class="flex items-center">
                <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 flex items-center justify-center">
                    <i class="fa-solid fa-skull-crossbones"></i>
                </div>
                <span class="text-sm">Animais Críticos</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.critical_animals} animais</span>
        </div>
        <div class="bg-purple-600 h-32 p-4 text-white flex flex-col justify-between rounded-lg">
            <div class="flex items-center">
                <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 flex items-center justify-center">
                    <i class="fa-solid fa-clipboard-list"></i>
                </div>
                <span class="text-sm">Saúde Geral</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.health_status}%</span>
        </div>
    `;
}

// Initialize date inputs with default range (last 30 days)
const endDate = new Date();
const startDate = new Date();
startDate.setDate(endDate.getDate() - 30);

document.getElementById("start-date").valueAsDate = startDate;
document.getElementById("end-date").valueAsDate = endDate;

// Chart instances
let weightChart, trendChart, breedChart;

// Analyze button handler
document
    .getElementById("analyze-btn")
    .addEventListener("click", fetchPeriodicAnalysis);

// Initial load
fetchPeriodicAnalysis();

async function fetchPeriodicAnalysis() {
    const startDate = document.getElementById("start-date").value;
    const endDate = document.getElementById("end-date").value;

    if (!startDate || !endDate) {
        alert("Por favor, selecione ambas as datas");
        return;
    }

    const contentDiv = document.getElementById("periodic-analysis-content");

    try {
        // Show loading
        contentDiv.innerHTML = `
            <div
                class="flex justify-center items-center py-8"
                id="loading-indicator"
            >
                <div class="loader"></div>
                <span class="ml-2 text-gray-300">Carregando análise...</span>
            </div>
        `;

        const response = await fetch("/api/periodic_analysis", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                start_date: startDate,
                end_date: endDate,
            }),
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();
        renderAnalysisResults(data);
    } catch (error) {
        console.error("Error:", error);
        contentDiv.innerHTML = `
            <div class="bg-red-900/20 border border-red-700 rounded p-4 text-red-300">
                Erro ao carregar análise: ${error.message}
            </div>
        `;
    }
}

function renderAnalysisResults(data) {
    const contentDiv = document.getElementById("periodic-analysis-content");

    // Format numbers
    const formatNum = (num) => (num ? num.toLocaleString("pt-BR") : "0");
    const formatWeight = (num) =>
        num ? num.toLocaleString("pt-BR", { maximumFractionDigits: 2 }) : "0";
    const formatPercent = (num) =>
        num
            ? num.toLocaleString("pt-BR", { maximumFractionDigits: 2 }) + "%"
            : "0%";

    // Create metrics cards
    const metricsHtml = `
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4 mb-4">
            <!-- Period Card -->
            <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition">
                <h3 class="text-gray-400 text-xs mb-1 uppercase tracking-wide">Período</h3>
                <p class="text-lg font-bold text-white">
                    ${new Date(data.period.start).toLocaleDateString("pt-BR")} 
                    - ${new Date(data.period.end).toLocaleDateString("pt-BR")}
                </p>
                <p class="text-gray-400 text-xs mt-1">
                    ${data.weight.measurements} pesagens em ${
        data.period.days
    } dias
                </p>
            </div>
            
            <!-- Animals Card -->
            <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition">
                <h3 class="text-gray-400 text-xs mb-1 uppercase tracking-wide">Animais</h3>
                <p class="text-lg font-bold text-white">${formatNum(
                    data.animals.total
                )}</p>
                <p class="text-gray-400 text-xs mt-1">
                    ${formatNum(
                        data.animals.underweight
                    )} abaixo (${formatPercent(
        data.animals.underweight_percentage
    )})
                </p>
            </div>
            
            <!-- Weight Stats Card -->
            <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition">
                <h3 class="text-gray-400 text-xs mb-1 uppercase tracking-wide">Peso Médio</h3>
                <p class="text-lg font-bold text-white">${formatWeight(
                    data.weight.average
                )} kg</p>
                <p class="text-gray-400 text-xs mt-1">
                    Min: ${formatWeight(
                        data.weight.minimum
                    )} kg / Max: ${formatWeight(data.weight.maximum)} kg
                </p>
            </div>
            
            <!-- Trends Card -->
            <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition">
                <h3 class="text-gray-400 text-xs mb-1 uppercase tracking-wide">Tendência</h3>
                <div class="flex justify-between mt-2 text-sm">
                    <div class="text-center">
                        <p class="text-green-400 font-bold">${formatNum(
                            data.trends.gaining
                        )}</p>
                        <p class="text-gray-400 text-[10px]">Ganho</p>
                    </div>
                    <div class="text-center">
                        <p class="text-yellow-400 font-bold">${formatNum(
                            data.trends.stable
                        )}</p>
                        <p class="text-gray-400 text-[10px]">Estável</p>
                    </div>
                    <div class="text-center">
                        <p class="text-red-400 font-bold">${formatNum(
                            data.trends.losing
                        )}</p>
                        <p class="text-gray-400 text-[10px]">Perda</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
            <!-- Weight Distribution Chart -->
            <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition">
                <h3 class="text-gray-300 text-sm mb-3 font-semibold">Distribuição de Peso</h3>
                <div class="h-56">
                    <canvas id="weight-chart"></canvas>
                </div>
            </div>
            
            <!-- Breed Distribution Chart -->
            <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition">
                <h3 class="text-gray-300 text-sm mb-3 font-semibold">Distribuição por Raça</h3>
                <div class="h-56">
                    <canvas id="breed-chart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition mb-4">
            <h3 class="text-gray-300 text-sm mb-3 font-semibold">Uso das Balanças</h3>
            <div class="h-56">
                <canvas id="scale-chart"></canvas>
            </div>
        </div>
    `;

    contentDiv.innerHTML = metricsHtml;

    // Render charts
    renderWeightChart(data);
    renderBreedChart(data.breeds);
    renderScaleChart(data.scales);
}

function renderWeightChart(data) {
    const ctx = document.getElementById("weight-chart").getContext("2d");

    if (weightChart) {
        weightChart.destroy();
    }

    weightChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Mínimo", "Médio", "Máximo"],
            datasets: [
                {
                    label: "Peso (kg)",
                    data: [
                        data.weight.minimum,
                        data.weight.average,
                        data.weight.maximum,
                    ],
                    backgroundColor: [
                        "rgba(75, 192, 192, 0.7)",
                        "rgba(54, 162, 235, 0.7)",
                        "rgba(255, 99, 132, 0.7)",
                    ],
                    borderColor: [
                        "rgba(75, 192, 192, 1)",
                        "rgba(54, 162, 235, 1)",
                        "rgba(255, 99, 132, 1)",
                    ],
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: "#D1D5DB",
                    },
                    grid: {
                        color: "#374151",
                    },
                },
                x: {
                    ticks: {
                        color: "#D1D5DB",
                    },
                    grid: {
                        display: false,
                    },
                },
            },
            plugins: {
                legend: {
                    display: false,
                    labels: {
                        color: "#D1D5DB",
                    },
                },
            },
        },
    });
}

function renderBreedChart(breedData) {
    const ctx = document.getElementById("breed-chart").getContext("2d");

    if (breedChart) {
        breedChart.destroy();
    }

    // Sort by count and take top 5
    const sortedData = [...breedData].sort((a, b) => b.count - a.count);
    const topBreeds = sortedData.slice(0, 5);

    breedChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: topBreeds.map((item) => item.name),
            datasets: [
                {
                    data: topBreeds.map((item) => item.count),
                    backgroundColor: [
                        "rgba(255, 99, 132, 0.7)",
                        "rgba(54, 162, 235, 0.7)",
                        "rgba(255, 206, 86, 0.7)",
                        "rgba(75, 192, 192, 0.7)",
                        "rgba(153, 102, 255, 0.7)",
                    ],
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "right",
                    labels: {
                        color: "#D1D5DB",
                    },
                },
            },
        },
    });
}

function renderScaleChart(scaleData) {
    const ctx = document.getElementById("scale-chart").getContext("2d");

    if (trendChart) {
        trendChart.destroy();
    }

    // Sort by usage
    const sortedData = [...scaleData].sort((a, b) => b.usage - a.usage);

    trendChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: sortedData.map((item) => item.uid),
            datasets: [
                {
                    label: "Uso",
                    data: sortedData.map((item) => item.usage),
                    backgroundColor: "rgba(79, 70, 229, 0.7)",
                    borderColor: "rgba(79, 70, 229, 1)",
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: "#D1D5DB",
                    },
                    grid: {
                        color: "#374151",
                    },
                },
                x: {
                    ticks: {
                        color: "#D1D5DB",
                    },
                    grid: {
                        display: false,
                    },
                },
            },
            plugins: {
                legend: {
                    display: false,
                },
            },
        },
    });
}

// Fetch data and update charts
fetch("/api/means")
    .then((res) => res.json())
    .then((data) => {
        setChartMeansData(data);
    });

fetch("/api/health_metrics")
    .then((res) => res.json())
    .then((data) => {
        setChartHealthMetricsData(data);
    });

fetch("/api/health_status")
    .then((res) => res.json())
    .then((data) => {
        setSummaryData(data);
    });
