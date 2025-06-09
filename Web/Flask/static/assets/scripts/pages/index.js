// Chart instances
const charts = {
    weight: null,
    trend: null,
    breed: null,
    means: null,
    risk: null,
};

// Initialize charts
function initializeCharts() {
    // Means Chart (Average Weight)
    const ctx1 = document.getElementById("means").getContext("2d");
    charts.means = createLineChart(ctx1, {
        label: "Peso médio",
        data: [0],
        backgroundColor: "#0b00a6",
        borderColor: "#0b55a8",
    });

    // Risk Chart (Potentially Sick Animals)
    const ctx2 = document.getElementById("risk").getContext("2d");
    charts.risk = createLineChart(ctx2, {
        label: "Nº de animais potencialmente doentes",
        data: [0],
        backgroundColor: "#AA2222",
        borderColor: "#FF4444",
    });
}

// Helper function to create line charts with consistent styling
function createLineChart(
    context,
    { label, data, backgroundColor, borderColor }
) {
    return new Chart(context, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label,
                    data,
                    backgroundColor,
                    borderColor,
                    tension: 0.2,
                },
            ],
        },
        options: getChartOptions(),
    });
}

// Common chart options
function getChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                grid: {
                    color: "#909090",
                    borderColor: "rgba(200, 200, 200, 0.8)",
                },
                ticks: { color: "#ffffff" },
                title: { color: "#ffffff" },
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: "#909090",
                    borderColor: "rgba(200, 200, 200, 0.8)",
                },
                ticks: { color: "#ffffff" },
                title: { color: "#ffffff" },
            },
        },
        plugins: {
            legend: {
                labels: { color: "#ffffff" },
            },
        },
    };
}

// Update chart data
function updateChartData(chart, labels, data) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update();
}

// Formatting helpers
const formatters = {
    number: (num) => (num ? num.toLocaleString() : "0"),
    weight: (num) =>
        num ? num.toLocaleString({ maximumFractionDigits: 2 }) : "0",
    percent: (num) =>
        num ? num.toLocaleString({ maximumFractionDigits: 2 }) + "%" : "0%",
    date: (dateStr) => new Date(dateStr).toLocaleDateString(),
};

// Dashboard data functions
const dashboard = {
    setMeansData(data) {
        const labels = data.map((e) =>
            e.month_name.substring(0, 3).toUpperCase()
        );
        const weights = data.map((e) => e.avg_weight);
        updateChartData(charts.means, labels, weights);
    },

    setHealthMetricsData(data) {
        const labels = data.map((e) =>
            e.month_name.substring(0, 3).toUpperCase()
        );
        const risk = data.map((e) => e.total_at_risk);
        updateChartData(charts.risk, labels, risk);
    },

    setSummaryData(data) {
        const summaryContainer = document.querySelector(".summary");
        const cards = [
            {
                bg: "bg-blue-600",
                icon: "<i class='fa-solid fa-cow'></i>",
                label: "Total de Animais",
                value: `${data.total_animals} animal(is)`,
            },
            {
                bg: "bg-green-600",
                icon: "<i class='fa-solid fa-heart-pulse'></i>",
                label: "Animais Saudáveis",
                value: `${data.healthy_animals} animal(is)`,
            },
            {
                bg: "bg-yellow-600",
                icon: "<i class='fa-solid fa-triangle-exclamation'></i>",
                label: "Animais em Alerta",
                value: `${data.warning_animals} animal(is)`,
            },
            {
                bg: "bg-red-600",
                icon: "<i class='fa-solid fa-skull-crossbones'></i>",
                label: "Animais Críticos",
                value: `${data.critical_animals} animal(is)`,
            },
            {
                bg: "bg-purple-600",
                icon: "<i class='fa-solid fa-clipboard-list'></i>",
                label: "Saúde Geral",
                value: `${data.health_status}%`,
            },
        ];

        summaryContainer.innerHTML = cards
            .map(
                (card) => `
        <div class="${
            card.bg
        } h-32 p-4 text-white flex flex-col justify-between rounded-lg">
          <div class="flex items-center">
            <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 ${
                card.icon.includes("url")
                    ? card.icon
                    : "flex items-center justify-center"
            }">${!card.icon.includes("url") ? card.icon : ""}</div>
            <span class="text-sm">${card.label}</span>
          </div>
          <span class="text-2xl font-bold font-montserrat truncate">${
              card.value
          }</span>
        </div>
      `
            )
            .join("");
    },

    async fetchPeriodicAnalysis() {
        const startDate = document.getElementById("start-date").value;
        const endDate = document.getElementById("end-date").value;

        if (!startDate || !endDate) {
            alert("Por favor, selecione ambas as datas");
            return;
        }

        const contentDiv = document.getElementById("periodic-analysis-content");

        try {
            contentDiv.innerHTML = `
          <div class="flex justify-center items-center py-8" id="loading-indicator">
            <div class="loader"></div>
            <span class="ml-2 text-gray-300">Carregando análise...</span>
          </div>
        `;

            const response = await fetch("/api/periodic_analysis", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate,
                }),
            });

            if (!response.ok) throw new Error(await response.text());
            this.renderAnalysisResults(await response.json());
        } catch (error) {
            console.error("Error:", error);
            contentDiv.innerHTML = `
          <div class="bg-red-900/20 border border-red-700 rounded p-4 text-red-300">
            Erro ao carregar análise: ${error.message}
          </div>
        `;
        }
    },

    renderAnalysisResults(data) {
        const contentDiv = document.getElementById("periodic-analysis-content");

        contentDiv.innerHTML = `
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4 mb-4">
          ${this.renderMetricCard(
              "Período",
              `
            ${formatters.date(data.period.start)} - ${formatters.date(
                  data.period.end
              )}
          `,
              `${data.weight.measurements} pesagens em ${data.period.days} dias`
          )}
          
          ${this.renderMetricCard(
              "Animais",
              formatters.number(data.animals.total),
              `
            ${formatters.number(
                data.animals.underweight
            )} abaixo (${formatters.percent(
                  data.animals.underweight_percentage
              )})
          `
          )}
          
          ${this.renderMetricCard(
              "Peso Médio",
              `${formatters.weight(data.weight.average)} kg`,
              `
            Min: ${formatters.weight(
                data.weight.minimum
            )} kg / Max: ${formatters.weight(data.weight.maximum)} kg
          `
          )}
          
          ${this.renderMetricCard(
              "Tendência",
              "",
              `
            <div class="flex justify-between mt-2 text-sm">
              <div class="text-center">
                <p class="text-green-400 font-bold">${formatters.number(
                    data.trends.gaining
                )}</p>
                <p class="text-gray-400 text-[10px]">Ganho</p>
              </div>
              <div class="text-center">
                <p class="text-yellow-400 font-bold">${formatters.number(
                    data.trends.stable
                )}</p>
                <p class="text-gray-400 text-[10px]">Estável</p>
              </div>
              <div class="text-center">
                <p class="text-red-400 font-bold">${formatters.number(
                    data.trends.losing
                )}</p>
                <p class="text-gray-400 text-[10px]">Perda</p>
              </div>
            </div>
          `
          )}
        </div>
  
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition">
            <h3 class="text-gray-300 text-sm mb-3 font-semibold">Distribuição de Peso</h3>
            <div class="h-56"><canvas id="weight-chart"></canvas></div>
          </div>
          
          <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition">
            <h3 class="text-gray-300 text-sm mb-3 font-semibold">Distribuição por Raça</h3>
            <div class="h-56"><canvas id="breed-chart"></canvas></div>
          </div>
        </div>
        
        <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition mb-4">
          <h3 class="text-gray-300 text-sm mb-3 font-semibold">Uso das Balanças</h3>
          <div class="h-56"><canvas id="scale-chart"></canvas></div>
        </div>
      `;

        this.renderWeightChart(data);
        this.renderBreedChart(data.breeds);
        this.renderScaleChart(data.scales);
    },

    renderMetricCard(title, value, description) {
        return `
        <div class="bg-gray-800 p-3 rounded-xl shadow-md hover:bg-gray-700 transition">
          <h3 class="text-gray-400 text-xs mb-1 uppercase tracking-wide">${title}</h3>
          <p class="text-lg font-bold text-white">${value}</p>
          <p class="text-gray-400 text-xs mt-1">${description}</p>
        </div>
      `;
    },

    renderWeightChart(data) {
        if (charts.weight) charts.weight.destroy();

        charts.weight = this.createBarChart("weight-chart", {
            labels: ["Mínimo", "Médio", "Máximo"],
            data: [
                data.weight.minimum,
                data.weight.average,
                data.weight.maximum,
            ],
            colors: [
                "rgba(75, 192, 192, 0.7)",
                "rgba(54, 162, 235, 0.7)",
                "rgba(255, 99, 132, 0.7)",
            ],
            label: "Peso (kg)",
        });
    },

    renderBreedChart(breedData) {
        if (charts.breed) charts.breed.destroy();

        const sortedData = [...breedData].sort((a, b) => b.count - a.count);
        const topBreeds = sortedData.slice(0, 5);

        charts.breed = new Chart(
            document.getElementById("breed-chart").getContext("2d"),
            {
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
                            labels: { color: "#D1D5DB" },
                        },
                    },
                },
            }
        );
    },

    renderScaleChart(scaleData) {
        if (charts.trend) charts.trend.destroy();

        const sortedData = [...scaleData].sort((a, b) => b.usage - a.usage);

        charts.trend = this.createBarChart("scale-chart", {
            labels: sortedData.map((item) => item.uid),
            data: sortedData.map((item) => item.usage),
            colors: "rgba(79, 70, 229, 0.7)",
            label: "Uso",
        });
    },

    createBarChart(elementId, { labels, data, colors, label }) {
        return new Chart(document.getElementById(elementId).getContext("2d"), {
            type: "bar",
            data: {
                labels,
                datasets: [
                    {
                        label,
                        data,
                        backgroundColor: colors,
                        borderColor: Array.isArray(colors)
                            ? colors.map((c) => c.replace("0.7", "1"))
                            : colors.replace("0.7", "1"),
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
                        ticks: { color: "#D1D5DB" },
                        grid: { color: "#374151" },
                    },
                    x: {
                        ticks: { color: "#D1D5DB" },
                        grid: { display: false },
                    },
                },
                plugins: { legend: { display: false } },
            },
        });
    },

    update() {
        // Initial load
        this.fetchPeriodicAnalysis();

        // Fetch data and update charts
        fetch("/api/means")
            .then((res) => res.json())
            .then((data) => this.setMeansData(data));

        fetch("/api/health_metrics")
            .then((res) => res.json())
            .then((data) => this.setHealthMetricsData(data));

        fetch("/api/health_status")
            .then((res) => res.json())
            .then((data) => this.setSummaryData(data));
    },
};

// MQTT Client
const mqttClient = mqtt.connect("wss://broker.hivemq.com:8884/mqtt");

mqttClient.on("connect", () => {
    mqttClient.subscribe("cow8/measurements");
});

mqttClient.on("message", () => {
    dashboard.update();
});

// Initialize everything
function init() {
    // Initialize date inputs with default range (last 30 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 30);

    document.getElementById("start-date").valueAsDate = startDate;
    document.getElementById("end-date").valueAsDate = endDate;

    // Analyze button handler
    document
        .getElementById("analyze-btn")
        .addEventListener("click", () => dashboard.fetchPeriodicAnalysis());

    initializeCharts();
    dashboard.update();
}

init();
