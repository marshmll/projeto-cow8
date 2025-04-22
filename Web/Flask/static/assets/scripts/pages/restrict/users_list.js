function setUsersListData(data) {
    const usersList = document.querySelector(".users-list");
    let html = "";

    data.forEach((user) => {
        html += `
        <li class="bg-gray-700 w-full rounded-lg flex flex-col md:flex-row items-stretch md:items-center p-3 text-white text-sm gap-3 md:gap-4">
            <!-- Left Section - User Info -->
            <div class="flex flex-col sm:flex-row items-center gap-3 min-w-0 flex-1">
                <div class="flex-shrink-0 w-10 h-10 border border-gray-500 bg-contain bg-center bg-no-repeat bg-[url(${
                    user.pfp_url || "/static/assets/images/default.jpg"
                })] rounded-full"></div>
                <div class="min-w-0 text-center sm:text-left">
                    <p class="font-medium truncate" title="${
                        user.nome_completo
                    }">
                        ${user.nome_completo}
                    </p>
                    <p class="text-gray-300 text-xs truncate">
                        ${user.privilegios}
                    </p>
                </div>
            </div>

            <!-- Middle Section - Details -->
            <div class="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 min-w-0 flex-1">
                <div class="text-gray-300 text-xs sm:text-sm truncate min-w-0" title="${new Date(
                    user.datahora_registro
                ).toLocaleString()}">
                    <span>Reg. em ${new Date(
                        user.datahora_registro
                    ).toLocaleDateString()}</span>
                </div>
                <div class="${
                    user.status == "Banido" ? "bg-red-600/70" : "bg-blue-600/70"
                } text-white px-2 py-1 rounded text-xs whitespace-nowrap">
                    ${user.status}
                </div>
                <div class="text-gray-300 text-xs sm:text-sm truncate min-w-0 flex-1" title="${
                    user.email
                }">
                    ${user.email}
                </div>
            </div>

            <!-- Right Section - Actions -->
            <div class="flex justify-center sm:justify-end gap-2 flex-shrink-0">
                <button class="btn-edit w-6 h-6 bg-green-600 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Editar ${
                    user.username
                }" username="${user.username}">
                    <i class="fa-solid fa-user-pen"></i>
                </button>
                <button class="btn-ban w-6 h-6 bg-orange-500 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Banir/Desbanir ${
                    user.username
                }" username="${user.username}">
                    <i class="fa-solid fa-ban"></i>
                </button>
                <button class="btn-delete w-6 h-6 bg-red-600 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Deletar ${
                    user.username
                }" username="${user.username}">
                    <i class="fa-solid fa-user-xmark"></i>
                </button>
            </div>
        </li>
    `;
    });

    usersList.innerHTML = html;

    document.querySelectorAll(".btn-ban").forEach((button) => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();
            const username = e.target.getAttribute("username");
            e.target.classList.add("cursor-wait", "opacity-75");

            try {
                const response = await fetch("/api/users/ban/" + username);
                if (response.ok) {
                    const updatedUsers = await fetch("/api/users/all").then(
                        (res) => res.json()
                    );
                    setUsersListData(updatedUsers);
                } else {
                    alert(
                        "Ocorreu um erro ao tentar banir/desbanir o usuário."
                    );
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Ocorreu um erro na comunicação com o servidor.");
            } finally {
                e.target.classList.remove("cursor-wait", "opacity-75");
            }
        });
    });

    document.querySelectorAll(".btn-delete").forEach((button) => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();
            const doDelete = confirm(
                "Deseja deletar o usuário selecionado? Esta ação não poderá ser desfeita."
            );

            if (!doDelete) return;

            const username = e.target.getAttribute("username");
            e.target.classList.add("cursor-wait", "opacity-75");

            try {
                const response = await fetch("/api/users/delete/" + username);
                if (response.ok) {
                    const updatedUsers = await fetch("/api/users/all").then(
                        (res) => res.json()
                    );
                    setUsersListData(updatedUsers);
                } else {
                    alert("Ocorreu um erro ao tentar deletar o usuário.");
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
fetch("/api/users/all")
    .then((res) => res.json())
    .then((data) => setUsersListData(data))
    .catch((error) => {
        console.error("Error loading users:", error);
        document.querySelector(".users-list").innerHTML = `
            <li class="text-red-400 text-center py-4">
                Erro ao carregar lista de usuários
            </li>
        `;
    });
