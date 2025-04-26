import { openModal } from "../modal.js";
import { showScaleDetails } from "./restrict/scale_details.js";
import { showScaleCommands } from "./restrict/scale_commands.js";
import { showScaleBroadcastCommands } from "./restrict/scale_broadcast.js";

// Cache DOM elements
const scalesList = document.querySelector(".scales-list");

const client = mqtt.connect("wss://broker.emqx.io:8084/mqtt");

client.on("connect", () => {
    console.log("Connected to broker");
    client.subscribe("cow8/status");
});

client.on("message", (topic, message) => {
    fetchScales()
        .then(setScalesListData)
        .catch((error) => {
            console.error("Error loading scales:", error);
            scalesList.innerHTML = createErrorState();
        });
});

export default client;

export function setScalesListData(data) {
    let html = data.map((scale) => createScaleListItem(scale)).join("");
    scalesList.innerHTML = html || createErrorState();

    setupEventListeners();
}

function createScaleListItem(scale) {
    return `
        <li class="bg-gray-700 w-full rounded-lg flex flex-col md:flex-row items-stretch md:items-center p-3 text-white text-sm gap-3 md:gap-4">
            <div class="flex flex-col sm:flex-row items-center gap-3 min-w-0 flex-1">
                <div class="min-w-0 text-center sm:text-left">
                    <p class="font-medium truncate" title="Balança ${
                        scale.uid
                    }">
                        Balança ${scale.uid}
                    </p>
                    <p class="text-gray-300 text-xs truncate">
                        Id: ${scale.id}
                    </p>
                </div>
            </div>

            <div class="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 min-w-0 flex-1">
                <div class="text-gray-300 text-xs sm:text-sm truncate min-w-0" 
                     title="${new Date(
                         scale.datahora_registro
                     ).toLocaleString()}">
                    <span>Cad. em ${new Date(
                        scale.datahora_registro
                    ).toLocaleDateString()}</span>
                </div>
                <div class="${getStatusColorClass(
                    scale.status
                )} text-white px-2 py-1 rounded text-xs whitespace-nowrap">
                    ${scale.status}
                </div>
            </div>

            <div class="flex justify-center sm:justify-end gap-2 flex-shrink-0">
                <button class="btn-details w-6 h-6 bg-green-500 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Ver Detalhes ${
                    scale.uid
                }" uid="${scale.uid}">
                    <i class="fa-solid fa-circle-info"></i>
                </button>
                <button class="btn-commands w-6 h-6 bg-gray-800 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Painel de Comandos da Balança ${
                    scale.uid
                }" uid="${scale.uid}">
                    <i class="fa-solid fa-terminal"></i>
                </button>
            </div>
        </li>
    `;
}

function getStatusColorClass(status) {
    const statusClasses = {
        Online: "bg-blue-600/70",
        Offline: "bg-yellow-600/70",
        Erro: "bg-red-600/70",
    };
    return statusClasses[status] || "bg-gray-600/70";
}

function setupEventListeners() {
    document
        .querySelector(".broadcast")
        .addEventListener("click", handleBroadcastClick);

    document.querySelectorAll(".btn-details").forEach((button) => {
        button.addEventListener("click", handleDetailsClick);
    });

    document.querySelectorAll(".btn-commands").forEach((button) => {
        button.addEventListener("click", handleCommandsClick);
    });

    document.querySelectorAll(".btn-delete").forEach((button) => {
        button.addEventListener("click", handleDeleteClick);
    });
}

function handleBroadcastClick(e) {
    e.preventDefault();
    showScaleBroadcastCommands();
    openModal();
}

async function handleDetailsClick(e) {
    e.preventDefault();
    const uid = e.currentTarget.getAttribute("uid");
    const scale = await fetchScaleDetails(uid);
    showScaleDetails(scale);
    openModal();
}

async function handleCommandsClick(e) {
    e.preventDefault();
    const uid = e.currentTarget.getAttribute("uid");
    const scale = await fetchScaleDetails(uid);
    showScaleCommands(scale);
    openModal();
}

async function handleDeleteClick(e) {
    e.preventDefault();
    const button = e.currentTarget;
    const uid = button.getAttribute("uid");

    if (
        !confirm(
            "Deseja deletar a balança selecionada? Esta ação não poderá ser desfeita."
        )
    ) {
        return;
    }

    button.classList.add("cursor-wait", "opacity-75");

    try {
        await deleteScale(uid);
        const updatedScales = await fetchScales();
        setScalesListData(updatedScales);
    } catch (error) {
        console.error("Error deleting scale:", error);
        alert("Ocorreu um erro ao tentar deletar a balança.");
    } finally {
        button.classList.remove("cursor-wait", "opacity-75");
    }
}

// API Functions
async function fetchScales() {
    const response = await fetch("/api/scales/all");
    return response.json();
}

async function fetchScaleDetails(uid) {
    const response = await fetch(`/api/scales/${uid}`);
    return response.json();
}

async function deleteScale(uid) {
    const response = await fetch(`/api/scales/delete/${uid}`, {
        method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to delete scale");
    return response.json();
}

function createErrorState() {
    return `
        <li class="text-red-400 text-center py-4">
            Erro ao carregar lista de balanças
        </li>
    `;
}

// Initialize
fetchScales()
    .then(setScalesListData)
    .catch((error) => {
        console.error("Error loading scales:", error);
        scalesList.innerHTML = createErrorState();
    });
