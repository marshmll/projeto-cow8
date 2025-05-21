import { openModal } from "../../modal.js";

function setUsersListData(data) {
    const usersList = document.querySelector(".users-list");
    let html = "";

    data.forEach(([user, role]) => {
        console.log(user);

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
                        ${role.name}
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
                <button class="btn-details w-6 h-6 bg-green-600 rounded cursor-pointer hover:scale-105 transition-transform duration-200" title="Detalhes ${
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

    document.querySelectorAll(".btn-details").forEach((button) => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();
            const username = button.getAttribute("username");
            button.classList.add("cursor-wait", "opacity-75");

            try {
                const response = await fetch("/api/users/" + username);
                if (!response.ok) {
                    alert("Ocorreu um erro ao tentar ver detalhes do usuário.");
                } else {
                    const user = await response.json();
                    showUserDetails(user);
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Ocorreu um erro na comunicação com o servidor.");
            } finally {
                button.classList.remove("cursor-wait", "opacity-75");
            }
        });
    });

    document.querySelectorAll(".btn-ban").forEach((button) => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();
            const username = button.getAttribute("username");
            button.classList.add("cursor-wait", "opacity-75");

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
                button.classList.remove("cursor-wait", "opacity-75");
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

            const username = button.getAttribute("username");
            button.classList.add("cursor-wait", "opacity-75");

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
                button.classList.remove("cursor-wait", "opacity-75");
            }
        });
    });
}

function showUserDetails(user) {
    const modalBody = document.querySelector(".modal-body");
    const modalFooter = document.querySelector(".modal-footer");
    let isEditing = false;

    const renderViewMode = () => {
        modalBody.innerHTML = `
            <div class="space-y-4">
                <!-- Header with profile picture and basic info -->
                <div class="flex items-center space-x-4">
                    <div class="flex-shrink-0">
                        <img class="h-16 w-16 rounded-full object-cover border-2 border-gray-200" 
                             src="${
                                 user.pfp_url ||
                                 "/static/assets/images/default.jpg"
                             }" 
                             alt="${user.username}'s profile picture">
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-gray-800">${
                            user.nome_completo || "No name provided"
                        }</h3>
                        <p class="text-gray-600">@${user.username}</p>
                    </div>
                </div>

                <!-- User details grid -->
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div class="space-y-1">
                        <p class="text-gray-500 font-medium">User ID</p>
                        <p class="text-gray-800 font-mono">${user.id}</p>
                    </div>
                    
                    <div class="space-y-1">
                        <p class="text-gray-500 font-medium">Status</p>
                        <span class="px-2 py-1 rounded-full text-xs font-medium 
                            ${
                                user.status === "Ativo"
                                    ? "bg-green-100 text-green-800"
                                    : user.status === "Banido"
                                    ? "bg-red-100 text-red-800"
                                    : "bg-gray-100 text-gray-800"
                            }">
                            ${user.status}
                        </span>
                    </div>
                    
                    <div class="space-y-1 col-span-2">
                        <p class="text-gray-500 font-medium">Email</p>
                        <p class="text-gray-800 break-all">${
                            user.email || "No email provided"
                        }</p>
                    </div>
                    
                    <div class="space-y-1">
                        <p class="text-gray-500 font-medium">Registrado em</p>
                        <p class="text-gray-800">${new Date(
                            user.datahora_registro
                        ).toLocaleDateString()}</p>
                    </div>
                    
                    <div class="space-y-1">
                        <p class="text-gray-500 font-medium">Privilégios</p>
                        <p class="text-gray-800">${user.privilegios}</p>
                    </div>
                </div>
            </div>
        `;

        modalFooter.innerHTML = `
            <button id="editBtn" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
                Editar
            </button>
        `;

        document.getElementById("editBtn").addEventListener("click", () => {
            isEditing = true;
            renderEditMode();
        });
    };

    const renderEditMode = () => {
        modalBody.innerHTML = `
            <div class="space-y-4">
                <!-- Header with profile picture and basic info -->
                <div class="flex items-center space-x-4">
                    <div class="flex-shrink-0 relative">
                        <img id="pfpPreview" class="h-16 w-16 rounded-full object-cover border-2 border-gray-200" 
                             src="${
                                 user.pfp_url ||
                                 "/static/assets/images/default.jpg"
                             }" 
                             alt="${user.username}'s profile picture">
                        <input type="file" id="pfpUpload" class="hidden" accept="image/*">
                    </div>
                    <div class="flex-1">
                        <div class="space-y-2">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Nome Completo</label>
                                <input type="text" id="fullName" value="${
                                    user.nome_completo || ""
                                }" 
                                       class="p-2 mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Username</label>
                                <input type="text" id="username" value="${
                                    user.username
                                }" 
                                       class="p-2 mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Editable fields -->
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div class="space-y-1 col-span-2">
                        <label class="block text-sm font-medium text-gray-700">URL Foto de Perfil</label>
                        <input type="text" id="pfpUrl" value="${
                            user.pfp_url || ""
                        }" 
                               class="p-2 mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
                    </div>
                    
                    <div class="space-y-1 col-span-2">
                        <label class="block text-sm font-medium text-gray-700">Email</label>
                        <input type="email" id="email" value="${
                            user.email || ""
                        }" 
                               class="p-2 mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
                    </div>
                    
                    <div class="space-y-1 col-span-2">
                        <label class="block text-sm font-medium text-gray-700">Nova Senha (deixe em branco para não alterar)</label>
                        <input type="password" id="newPassword" 
                               class="p-2 mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
                    </div>
                </div>
            </div>
        `;

        modalFooter.innerHTML = `
            <button id="cancelBtn" class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition mr-2">
                Cancelar
            </button>
            <button id="saveBtn" class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition">
                Salvar Alterações
            </button>
        `;

        // Setup event listeners
        document.getElementById("cancelBtn").addEventListener("click", () => {
            isEditing = false;
            renderViewMode();
        });

        document
            .getElementById("saveBtn")
            .addEventListener("click", async () => {
                const updatedData = {
                    nome_completo: document.getElementById("fullName").value,
                    username: document.getElementById("username").value,
                    email: document.getElementById("email").value,
                    pfp_url: document.getElementById("pfpUrl").value,
                    new_password:
                        document.getElementById("newPassword").value ||
                        undefined,
                };

                try {
                    const response = await fetch(
                        `/api/users/update/${user.username}`,
                        {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify(updatedData),
                        }
                    );

                    if (!response.ok) {
                        throw new Error(await response.text());
                    }

                    // Update local user object with new data
                    Object.assign(user, updatedData);
                    isEditing = false;
                    renderViewMode();
                    alert("Alterações salvas com sucesso!");
                    loadUsers();
                } catch (error) {
                    console.error("Error updating user:", error);
                    alert("Erro ao salvar alterações: " + error.message);
                }
            });

        // Image upload preview
        document.getElementById("pfpUrl").addEventListener("input", (e) => {
            document.getElementById("pfpPreview").src =
                e.target.value || "/static/assets/images/default.jpg";
        });

        document.getElementById("pfpUpload").addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    document.getElementById("pfpPreview").src =
                        event.target.result;
                    document.getElementById("pfpUrl").value = ""; // Clear URL field if uploading file
                };
                reader.readAsDataURL(file);
            }
        });
    };

    // Initial render
    renderViewMode();
    openModal();
}

function loadUsers() {
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
}

loadUsers();