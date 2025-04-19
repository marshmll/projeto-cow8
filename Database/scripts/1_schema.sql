CREATE DATABASE IF NOT EXISTS cow8_db;
USE cow8_db;

CREATE TABLE IF NOT EXISTS Usuario (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(120) NOT NULL,
    nome_completo TEXT NOT NULL,
    email VARCHAR(200),
    pfp_url TEXT,
    datahora_registro DATETIME NOT NULL DEFAULT NOW(),
    status VARCHAR(50) NOT NULL DEFAULT 'Ativo',
    privilegios VARCHAR(50) NOT NULL DEFAULT 'Usuário',
    `key` TEXT NOT NULL,
    salt TEXT NOT NULL,
    UNIQUE(username, email)
);

CREATE TABLE IF NOT EXISTS DadosAnimal (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    raca VARCHAR(50) NOT NULL,
    peso_medio NUMERIC(7, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS Animal (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    uid TEXT NOT NULL,
    sexo CHAR(1) NOT NULL,
    id_dados_animal INT,
    FOREIGN KEY (id_dados_animal) REFERENCES DadosAnimal(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ControlePesagem (
    id_animal INT NOT NULL,
    datahora_pesagem DATETIME NOT NULL DEFAULT NOW(),
    medicao_peso NUMERIC(7, 2) NOT NULL,
    observacoes TEXT NULL,
    PRIMARY KEY (id_animal, datahora_pesagem),
    FOREIGN KEY (id_animal) REFERENCES Animal(id)
        ON DELETE CASCADE
);
