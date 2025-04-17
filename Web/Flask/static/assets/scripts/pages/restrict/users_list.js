
function setUsersListData(data) {
    let html = ''

    for (let user of data) {
        html += `
        <li class="user">
            <div class="user__left">
                <div class="user__pfp"></div>
                <div class="user__info">
                    <span title="${user.nome_completo}">${user.nome_completo}</span>
                    <span>${user.privilegios}</span>
                </div>
            </div>
            <div class="user__middle">
                <div class="user__creation">
                    <span title="${new Date(user.datahora_registro).toString()}">Reg. em ${new Date(user.datahora_registro).toLocaleDateString()}</span>
                </div>
                <div class="user__status ${user.status == "Banido" ? "user__status--banned" : ""}">
                    <span>${user.status}</span>
                </div>
                <div class="user__email" title="${user.email}">
                    <span>${user.email}</span>
                </div>
            </div>
            <div class="user__right">
                <button class="user__button user__button--edit" title="Editar"></button>
                <button class="user__button user__button--ban-toggle" username="${user.username}" title="Banir/Desbanir"></button>
                <button class="user__button user__button--delete" title="Deletar"></button>
            </div>
        </li>
        `
    }

    document.querySelector(".users").innerHTML = html;

    for (let button of document.querySelectorAll(".user__button--ban-toggle")) {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const username = e.target.getAttribute('username');
            e.target.style.cursor = "wait";

            fetch('/api/users/ban/' + username)
                .then(res => {
                    if (res.status == 200) {
                        e.target.style.cursor = "wait";
                        fetch('/api/users/all').then(res => res.json()).then(data => setUsersListData(data));
                    }
                    else {
                        alert("Ocorreu um erro ao tentar banir/desbanir o usuário.");
                    }
                })
        })
    }
}


fetch('/api/users/all').then(res => res.json()).then(data => setUsersListData(data));