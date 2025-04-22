import { openModal } from "../../modal.js";

function setScalesListData(data) {
    const scalesList = document.querySelector(".scales-list");
    let html = "";

    data.forEach((scale) => {
        html += `
          <li class="bg-gray-700 w-full rounded-lg flex flex-col md:flex-row items-stretch md:items-center p-3 text-white text-sm gap-3 md:gap-4">
              <!-- Left Section - User Info -->
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
  
              <!-- Middle Section - Details -->
              <div class="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 min-w-0 flex-1">
                  <div class="text-gray-300 text-xs sm:text-sm truncate min-w-0" title="${new Date(
                      scale.datahora_registro
                  ).toLocaleString()}">
                      <span>Cad. em ${new Date(
                          scale.datahora_registro
                      ).toLocaleDateString()}</span>
                  </div>
                  <div class="${
                      scale.status == "Operacional" ? "bg-blue-600/70" : ""
                  }
                  ${scale.status == "Desativado" ? "bg-yellow-600/70" : ""}
                  ${scale.status == "Erro" ? "bg-red-600/70" : ""}
                  
                  text-white px-2 py-1 rounded text-xs whitespace-nowrap">
                      ${scale.status}
                  </div>
              </div>
  
              <!-- Right Section - Actions -->
              <div class="flex justify-center sm:justify-end gap-2 flex-shrink-0">
                  <button class="btn-details w-6 h-6 bg-green-600 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Ver Detalhes ${
                      scale.uid
                  }" uid="${scale.uid}">
                    <i class="fa-solid fa-circle-info"></i>
                  </button>
                  <button class="btn-ban w-6 h-6 bg-orange-500 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Ativar/Desativar Balança ${
                      scale.uid
                  }" uid="${scale.uid}">
                    <i class="fa-solid fa-power-off"></i>
                  </button>
                  <button class="btn-delete w-6 h-6 bg-red-600 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Deletar Balança ${
                      scale.uid
                  }" uid="${scale.uid}">
                    <i class="fa-solid fa-trash"></i>
                  </button>
              </div>
          </li>
      `;
    });

    scalesList.innerHTML = html;

    document.querySelectorAll(".btn-details").forEach((button) => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();

            const uid = button.getAttribute("uid");
            let scale = await fetch("/api/scales/" + uid).then((res) =>
                res.json()
            );

            document.querySelector(".modal-body").innerHTML = `
                <div class="space-y-4">
                <!-- Header with Scale ID -->
                <div class="pb-2 border-b border-gray-200">
                    <h4 class="text-lg font-semibold text-gray-800">
                        Detalhes Módulo de Pesagem
                    </h4>
                    <p class="text-sm text-gray-500">
                        ID: #<span class="font-mono">${scale.id}</span>
                    </p>
                </div>

                <!-- Key Information Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Scale UID -->
                    <div>
                        <p class="text-sm font-medium text-gray-500">
                            UID do Módulo
                        </p>
                        <p
                            class="mt-1 text-gray-800 font-mono bg-gray-50 p-2 rounded"
                        >
                            ${scale.uid}
                        </p>
                    </div>

                    <!-- Registration Date -->
                    <div>
                        <p class="text-sm font-medium text-gray-500">
                            Cadastrado em
                        </p>
                        <p class="mt-1 text-gray-800">${new Date(
                            scale.datahora_registro
                        ).toLocaleString()}</p>
                    </div>

                    <!-- Status with colored badge -->
                    <div>
                        <p class="text-sm font-medium text-gray-500">Status</p>
                        <div class="mt-1">
                            <span
                                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                ${
                                    scale.status === "Operacional"
                                        ? "bg-green-100 text-green-800"
                                        : ""
                                }
                                 ${
                                     scale.status === "Desativado"
                                         ? "bg-yellow-100 text-yellow-800"
                                         : ""
                                 }
                                ${
                                    scale.status === "Erro"
                                        ? "bg-red-100 text-red-800"
                                        : ""
                                }"
                            >
                                ${scale.status}
                            </span>
                        </div>
                    </div>

                    <!-- Last Calibration Date -->
                    <div>
                        <p class="text-sm font-medium text-gray-500">
                            Última Calibragem
                        </p>
                        <p class="mt-1 text-gray-800">${
                            scale.ultima_calibragem
                                ? new Date(
                                      scale.ultima_calibragem
                                  ).toLocaleString()
                                : "Nunca"
                        }</p>
                    </div>
                </div>

                <!-- Observations Section -->
                <div>
                    <p class="text-sm font-medium text-gray-500">
                        Observations
                    </p>
                    <div class="mt-1 p-3 bg-gray-50 rounded-lg">
                        ${scale.observacoes || "Não há."}
                    </div>
                </div>

                <!-- Connection Status -->
                <div class="pt-2 border-t border-gray-200">
                    <div class="flex items-center">
                        <span class="relative flex h-3 w-3 mr-2">
                            <span
                                class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"
                            ></span>
                            <span
                                class="relative inline-flex rounded-full h-3 w-3 bg-green-500"
                            ></span>
                        </span>
                        <p class="text-sm text-gray-600">
                            Atualmente Online
                            <span class="text-gray-400 text-xs ml-2"
                                >(Latência: 100ms)</span
                            >
                        </p>
                    </div>
                </div>
            </div>
            `;
            openModal();
        });
    });

    document.querySelectorAll(".btn-delete").forEach((button) => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();
            const doDelete = confirm(
                "Deseja deletar a balança selecionada? Esta ação não poderá ser desfeita."
            );

            if (!doDelete) return;

            const uid = button.getAttribute("uid");
            button.classList.add("cursor-wait", "opacity-75");

            try {
                const response = await fetch("/api/scales/delete/" + uid);
                if (response.ok) {
                    const updatedscales = await fetch("/api/scales/all").then(
                        (res) => res.json()
                    );
                    setScalesListData(updatedscales);
                } else {
                    alert("Ocorreu um erro ao tentar deletar a balança.");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Ocorreu um erro na comunicação com o servidor.");
            } finally {
                e.target.classList.remove("cursor-wait", "opacity-75");
            }
        });
    });
}

// Load initial data
fetch("/api/scales/all")
    .then((res) => res.json())
    .then((data) => setScalesListData(data))
    .catch((error) => {
        console.error("Error loading scales:", error);
        document.querySelector(".scales-list").innerHTML = `
              <li class="text-red-400 text-center py-4">
                  Erro ao carregar lista de balanças
              </li>
          `;
    });
