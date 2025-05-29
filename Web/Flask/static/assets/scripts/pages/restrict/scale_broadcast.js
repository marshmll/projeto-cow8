export function showScaleBroadcastCommands() {
    const modalBody = document.querySelector(".modal-body");
    modalBody.innerHTML = `
        <div class="scale-control-board space-y-4">
            <div class="pb-2 border-b border-gray-200">
                <h4 class="text-lg font-semibold text-gray-800">Broadcast Balanças</h4>
            </div>

            <div class="command-grid grid grid-cols-2 gap-3">
                ${createCommandButton(
                    "TARE",
                    "Tara",
                    "fa-balance-scale",
                    "blue",
                    false
                )}
                ${createCommandButton(
                    "ENABLE",
                    "Habilitar",
                    "fa-power-off",
                    "green",
                    false
                )}
                ${createCommandButton(
                    "DISABLE",
                    "Desabilitar",
                    "fa-ban",
                    "yellow",
                    false
                )}
                ${createCommandButton(
                    "POWEROFF",
                    "Desligar",
                    "fa-plug",
                    "red",
                    false
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

    setupCommandButtons("ffff");
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
                    response.message || "Comando executado com sucesso";

                // Refresh scale status if needed
                if (["enable", "disable", "power_off"].includes(command)) {
                    setTimeout(refreshScaleStatus, 3000);
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

        return result;
    } catch (error) {
        feedback.querySelector("p").textContent = `Erro: ${error.message}`;
        throw error;
    }
}
