export function showScaleDetails(scale) {
    const modalBody = document.querySelector(".modal-body");
    modalBody.innerHTML = `
        <div class="space-y-4">
            <div class="pb-2 border-b border-gray-200">
                <h4 class="text-lg font-semibold text-gray-800">Detalhes Módulo de Pesagem</h4>
                <p class="text-sm text-gray-500">ID: #<span class="font-mono">${
                    scale.id
                }</span></p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <p class="text-sm font-medium text-gray-500">UID do Módulo</p>
                    <p class="mt-1 text-gray-800 font-mono bg-gray-50 p-2 rounded">${
                        scale.uid
                    }</p>
                </div>

                <div>
                    <p class="text-sm font-medium text-gray-500">Cadastrado em</p>
                    <p class="mt-1 text-gray-800">${new Date(
                        scale.datahora_registro
                    ).toLocaleString()}</p>
                </div>

                <div>
                    <p class="text-sm font-medium text-gray-500">Status</p>
                    <div class="mt-1">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColorClass(
                            scale.status
                        )}">
                            ${scale.status}
                        </span>
                    </div>
                </div>

                <div>
                    <p class="text-sm font-medium text-gray-500">Última Calibragem</p>
                    <p class="mt-1 text-gray-800">${
                        scale.ultima_calibragem
                            ? new Date(scale.ultima_calibragem).toLocaleString()
                            : "Nunca"
                    }</p>
                </div>
            </div>

            <div>
                <p class="text-sm font-medium text-gray-500">Observações</p>
                <div class="mt-1 p-3 bg-gray-50 rounded-lg">${
                    scale.observacoes || "Não há."
                }</div>
            </div>

            <div class="pt-2 border-t border-gray-200">
                <div class="flex items-center">
                    <span class="relative flex h-3 w-3 mr-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full ${
                            scale.status === "Online"
                                ? "bg-green-400"
                                : "bg-gray-400"
                        } opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-3 w-3 ${
                            scale.status === "Online"
                                ? "bg-green-500"
                                : "bg-gray-500"
                        }"></span>
                    </span>
                    <p class="text-sm text-gray-600">
                        ${
                            scale.status === "Online"
                                ? "Atualmente Online"
                                : "Atualmente Offline"
                        }
                        <span class="text-gray-400 text-xs ml-2">(Última comunicação: ${
                            scale.ultima_comunicacao
                                ? new Date(
                                      scale.ultima_comunicacao
                                  ).toLocaleTimeString()
                                : "N/A"
                        })</span>
                    </p>
                </div>
            </div>
        </div>
    `;
}

function getStatusColorClass(status) {
    const statusClasses = {
        Online: "bg-green-100 text-green-800",
        Offline: "bg-yellow-100 text-yellow-800",
        Erro: "bg-red-100 text-red-800",
    };
    return statusClasses[status] || "bg-gray-100 text-gray-800";
}
