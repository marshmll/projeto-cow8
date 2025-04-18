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
        tension: 0.1,
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
  type: "bar",
  data: {
    labels: [],
    datasets: [
      {
        label: "Nº de animais potencialmente doentes",
        data: [0],
        borderColor: "#FF4444",
        backgroundColor: "#AA2222",
        tension: 0.1,
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
                <span class="text-sm">Animais Registrados</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.total_animals} animais</span>
        </div>
        <div class="bg-blue-600 h-32 p-4 text-white flex flex-col justify-between rounded-lg">
            <div class="flex items-center">
                <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 bg-[url('static/assets/images/icons/monitor_heart_white.svg')] bg-center bg-[length:80%] bg-no-repeat"></div>
                <span class="text-sm">Animais Saudáveis</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.healthy_animals} animais</span>
        </div>
        <div class="bg-blue-600 h-32 p-4 text-white flex flex-col justify-between rounded-lg">
            <div class="flex items-center">
                <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 bg-[url('static/assets/images/icons/health_white.svg')] bg-center bg-[length:80%] bg-no-repeat"></div>
                <span class="text-sm">Animais em Alerta</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.warning_animals} animais</span>
        </div>
        <div class="bg-blue-600 h-32 p-4 text-white flex flex-col justify-between rounded-lg">
            <div class="flex items-center">
                <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 bg-[url('static/assets/images/icons/health_white.svg')] bg-center bg-[length:80%] bg-no-repeat"></div>
                <span class="text-sm">Animais Críticos</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.critical_animals} animais</span>
        </div>
        <div class="bg-blue-600 h-32 p-4 text-white flex flex-col justify-between rounded-lg">
            <div class="flex items-center">
                <div class="min-w-7 min-h-7 bg-white/30 rounded mr-4 bg-[url('static/assets/images/icons/monitor_heart_white.svg')] bg-center bg-[length:80%] bg-no-repeat"></div>
                <span class="text-sm">Saúde Geral</span>
            </div>
            <span class="text-2xl font-bold font-montserrat truncate">${data.health_status}%</span>
        </div>
    `;
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
