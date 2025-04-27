export function showScaleCommands(scale) {
    const modalBody = document.querySelector(".modal-body");
    modalBody.innerHTML = `
        <div class="scale-control-board space-y-4">
            <div class="pb-2 border-b border-gray-200">
                <h4 class="text-lg font-semibold text-gray-800">Controle da Balança</h4>
                <p class="text-sm text-gray-500">UID: <span class="font-mono">${
                    scale.uid
                }</span></p>
            </div>

            <div class="grid grid-cols-2 gap-3 mb-4">
                <div class="status-indicator p-2 rounded-lg bg-gray-50">
                    <p class="text-xs text-gray-500">Status Atual</p>
                    <div class="flex items-center mt-1">
                        <span class="status-dot h-3 w-3 rounded-full mr-2 ${
                            scale.status === "Online"
                                ? "bg-green-500"
                                : "bg-gray-400"
                        }"></span>
                        <span class="text-sm font-medium">${scale.status}</span>
                    </div>
                </div>
                <div class="connection-indicator p-2 rounded-lg bg-gray-50">
                    <p class="text-xs text-gray-500">Conexão</p>
                    <div class="flex items-center mt-1">
                        <span class="relative flex h-3 w-3 mr-2">
                            <span class="animate-ping absolute inline-flex h-full w-full rounded-full ${
                                getStatusStyles(scale.status).pingColor
                            } opacity-75"></span>
                            <span class="relative inline-flex rounded-full h-3 w-3 ${
                                getStatusStyles(scale.status).dotColor
                            }"></span>
                        </span>
                        <span class="text-sm font-medium ${
                            getStatusStyles(scale.status).textColor
                        }">
                            ${getStatusStyles(scale.status).label}
                        </span>
                    </div>
                </div>
            </div>

            <div class="command-grid grid grid-cols-2 gap-3">
                ${createCommandButton(
                    "TARE",
                    "Tara",
                    "fa-balance-scale",
                    "blue",
                    scale.status === "Offline"
                )}
                ${createCommandButton(
                    "ENABLE",
                    "Habilitar",
                    "fa-power-off",
                    "green",
                    scale.status === "Offline"
                )}
                ${createCommandButton(
                    "DISABLE",
                    "Desabilitar",
                    "fa-ban",
                    "yellow",
                    scale.status === "Offline"
                )}
                ${createCommandButton(
                    "POWEROFF",
                    "Desligar",
                    "fa-plug",
                    "red",
                    scale.status === "Offline"
                )}
            </div>

            <div id="additional-commands" class="additional-commands-grid grid grid-cols-2 gap-3 mt-3">
                <!-- Additional commands can be added here -->
            </div>

            <div id="command-feedback" class="feedback-area mt-4 p-3 bg-gray-50 rounded-lg hidden">
                <p class="text-sm text-gray-700"></p>
            </div>
        </div>
    `;

    setupCommandButtons(scale.uid);
}

function getStatusStyles(status) {
    const styles = {
        Online: {
            pingColor: "bg-green-400",
            dotColor: "bg-green-500",
            textColor: "text-green-800",
            label: "Conectado",
        },
        Desabilitado: {
            pingColor: "bg-yellow-400",
            dotColor: "bg-yellow-500",
            textColor: "text-yellow-800",
            label: "Desabilitado",
        },
        Offline: {
            pingColor: "bg-gray-400",
            dotColor: "bg-gray-500",
            textColor: "text-gray-800",
            label: "Offline",
        },
        Erro: {
            pingColor: "bg-red-400",
            dotColor: "bg-red-500",
            textColor: "text-red-800",
            label: "Erro",
        },
    };
    return styles[status] || styles.Offline;
}

function createCommandButton(command, label, icon, color, isDisabled) {
    const colorClasses = {
        blue: "bg-blue-100 hover:bg-blue-200 text-blue-800",
        green: "bg-green-100 hover:bg-green-200 text-green-800",
        yellow: "bg-yellow-100 hover:bg-yellow-200 text-yellow-800",
        red: "bg-red-100 hover:bg-red-200 text-red-800",
    };

    return `
        <button class="command-btn ${colorClasses[color]} ${
        isDisabled ? "opacity-50 cursor-not-allowed" : ""
    }" data-command="${command}" ${isDisabled ? "disabled" : ""}>
            <i class="fas ${icon}" style="font-size: 20px; margin-bottom: 8px;"></i>
            <span style="font-size: 14px; font-weight: 500;">${label}</span>
        </button>
    `;
}

function setupCommandButtons(scaleUid) {
    document.querySelectorAll(".command-btn").forEach((button) => {
        button.addEventListener("click", async (e) => {
            if (button.disabled) return;

            const command = button.getAttribute("data-command");
            const feedback = document.getElementById("command-feedback");

            button.classList.add("cursor-wait", "opacity-75");
            feedback.classList.remove("hidden");
            feedback.querySelector(
                "p"
            ).textContent = `Enviando comando ${command}...`;

            try {
                const response = await sendScaleCommand(scaleUid, command);
                feedback.querySelector("p").textContent =
                    response.message || "Comando enviado com sucesso!";

                // Refresh scale status if needed
                if (["enable", "disable", "power_off"].includes(command)) {
                    setTimeout(refreshScaleStatus, 2000);
                }
            } catch (error) {
                feedback.querySelector(
                    "p"
                ).textContent = `Erro ao enviar comando: ${error.message}`;
            } finally {
                button.classList.remove("cursor-wait", "opacity-75");
            }
        });
    });
}

async function sendScaleCommand(scaleUid, command) {
    const feedback = document.getElementById("command-feedback");
    feedback.classList.remove("hidden");
    feedback.querySelector("p").textContent = `Enviando comando ${command}...`;

    try {
        const response = await fetch(
            `/api/scales/${scaleUid}/command/${command}`
        );

        if (!response.ok) throw new Error(await response.text());

        const result = await response.json();
        feedback.querySelector("p").textContent =
            result.message || "Comando executado";

        // Auto-refresh after important commands
        if (["ENABLE", "DISABLE", "POWEROFF", "TARE"].includes(command)) {
            setTimeout(refreshScaleStatus, 2000);
        }

        return result;
    } catch (error) {
        feedback.querySelector("p").textContent = `Erro: ${error.message}`;
        throw error;
    }
}
async function refreshScaleStatus() {
    const modalBody = document.querySelector(".modal-body");
    const feedback =
        document.getElementById("command-feedback") ||
        document.createElement("div"); // Fallback if no feedback element

    // Determine if we're in details view or commands view
    const isCommandsView =
        modalBody.querySelector(".scale-control-board") !== null;
    const scaleUid =
        modalBody.querySelector(".font-mono")?.textContent ||
        modalBody.dataset.scaleUid;

    if (!scaleUid) {
        console.error("No scale ID found for refresh");
        return;
    }

    try {
        // Show loading state
        if (feedback) {
            feedback.classList.remove("hidden");
            feedback.querySelector("p").textContent = "Atualizando status...";
        }

        // Fetch updated scale data
        let response = await fetch(`/api/scales/${scaleUid}`);
        if (!response.ok) throw new Error("Failed to fetch scale data");

        const scale = await response.json();

        // Update the appropriate view
        if (isCommandsView) {
            showScaleCommands(scale); // Refresh commands view
        } else {
            showScaleDetails(scale); // Refresh details view
        }

        // Show success feedback briefly
        if (feedback) {
            feedback.querySelector("p").textContent =
                "Status atualizado com sucesso";
            setTimeout(() => feedback.classList.add("hidden"), 2000);
        }
    } catch (error) {
        console.error("Error refreshing scale status:", error);
        if (feedback) {
            feedback.querySelector(
                "p"
            ).textContent = `Erro ao atualizar: ${error.message}`;
            setTimeout(() => feedback.classList.add("hidden"), 3000);
        }
    }
}
