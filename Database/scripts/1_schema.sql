CREATE DATABASE IF NOT EXISTS cow8_db;
USE cow8_db;

CREATE TABLE IF NOT EXISTS DadosAnimal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    raca VARCHAR(50) NOT NULL,
    peso_medio NUMERIC(7, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS Animal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid TEXT NOT NULL,
    sexo CHAR(1) NOT NULL,
    id_dados_animal INT,
    FOREIGN KEY (id_dados_animal) REFERENCES DadosAnimal(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ControlePesagem (
    id_animal INT NOT NULL,
    datahora_pesagem DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    medicao_peso NUMERIC(7, 2) NOT NULL,
    observacoes TEXT NULL,
    PRIMARY KEY (id_animal, datahora_pesagem),
    FOREIGN KEY (id_animal) REFERENCES Animal(id)
        ON DELETE CASCADE
);
