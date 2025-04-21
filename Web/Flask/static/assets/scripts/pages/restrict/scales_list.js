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
                  ).toString()}">
                      <span>Reg. em ${new Date(
                          scale.datahora_registro
                      ).toLocaleDateString()}</span>
                  </div>
                  <div class="${
                      scale.status == "Banido"
                          ? "bg-red-600/70"
                          : "bg-blue-600/70"
                  } text-white px-2 py-1 rounded text-xs whitespace-nowrap">
                      ${scale.status}
                  </div>
              </div>
  
              <!-- Right Section - Actions -->
              <div class="flex justify-center sm:justify-end gap-2 flex-shrink-0">
                  <button class="w-6 h-6 bg-green-600 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Editar Balança ${
                      scale.uid
                  }" uid="${scale.uid}">
                    <i class="fa-solid fa-pen-to-square"></i>
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

    document.querySelectorAll(".btn-delete").forEach((button) => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();
            const doDelete = confirm(
                "Deseja deletar a balança selecionada? Esta ação não poderá ser desfeita."
            );

            if (!doDelete) return;

            const uid = e.target.getAttribute("uid");
            e.target.classList.add("cursor-wait", "opacity-75");

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
