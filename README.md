# 🐄 MVP Cow8 - Pesagem Semi-Automatizada de Gado

> Sistema inteligente para pesagem semi-automatizada de bovinos, equinos e outros animais de criação.

## 📌 Visão Geral

O **MVP Cow8** é um sistema que visa otimizar a rotina de pesagem de animais em propriedades rurais por meio da automação e digitalização dos processos. Utilizando tecnologias como sensores NFC, balanças eletrônicas e uma interface web com inteligência artificial, o projeto busca garantir o bem-estar animal e melhorar a produtividade na pecuária.

---

## 🚩 Problema

A pesagem manual ainda é comum em pequenas e médias propriedades rurais, o que traz diversos problemas:

- Necessidade de mão de obra especializada;
- Estresse nos animais;
- Erros humanos na coleta e no registro de dados;
- Dificuldade no monitoramento da saúde dos animais.

---

## 🚀 Solução Proposta

Desenvolvimento de um sistema semi-automatizado com as seguintes funcionalidades:

- Identificação individual via **tags NFC**;
- Pesagem automática com **portões motorizados** e **balança eletrônica**;
- Registro de dados em **banco de dados MySQL**;
- Interface web desenvolvida em **Flask**;
- Navegação via **chat com inteligência artificial** para facilitar o uso por qualquer produtor.

---

## 🎥 Demonstrações

[Componente IoT](https://www.youtube.com/watch?v=pZCwRlHaOyU&t=2s&pp=0gcJCbEJAYcqIYzv)

[Componente Web](https://www.youtube.com/watch?v=nLt2YAsHN0E&t=13s)

[Persistência de dados, segurança e controle de acesso](https://www.youtube.com/watch?v=rGcEcjEHR5Q)

---

## 🔧 Tecnologias Envolvidas

### 🖥️ Software

- Python (Flask)
- SQLAlchemy
- MySQL
- MQTT (Broker EMQX)
- HTML, CSS, JavaScript
- Docker (opcional)
- LLM Chat (para navegação intuitiva)

### 🔌 Hardware

- ESP32
- Sensor NFC RFID-RC522 *
- Tags NFC Mifare 13.56 MHz *
- Células de carga 50kg *
- Módulo HX711
- Servo motores
- Buzzer passivo
- Protoboard *

> *Itens marcados com asterisco são usados apenas para prototipação.

---

## 📈 Resultados Esperados

- Redução de erros humanos
- Monitoramento eficiente da saúde e nutrição animal
- Acesso remoto e em tempo real via web
- Interface acessível para usuários sem conhecimento técnico
- Base de dados histórica para análises e decisões estratégicas

---

## 📅 Cronograma do Projeto

O desenvolvimento está dividido nas seguintes fases:

1. Planejamento e aquisição de componentes
2. Desenvolvimento de hardware e software
3. Integração e testes
4. Implementação e validação

![Cronograma](https://raw.githubusercontent.com/marshmll/projeto-cow8/refs/heads/main/Docs/cronograma.png)

---

## 🤖 Diretrizes para Uso de IA

Durante a elaboração do projeto e da documentação, foi utilizada a IA Chat DeepSeek V3 para verificação gramatical e validação de dados. O conteúdo final foi revisado e editado manualmente pelos autores.

---

## 👥 Autores

- Renan da Silva Oliveira Andrade – `renan.silva3@pucpr.edu.br`
- Ricardo Lucas Kucek – `ricardo.kucek@pucpr.edu.br`
- Pedro Senes Velloso Ribeiro – `pedro.senes@pucpr.edu.br`
- Riscala Miguel Fadel Neto – `riscala.neto@pucpr.edu.br`
- Victor Valerio Fadel – `victor.fadel@pucpr.edu.br`

---

## 📬 Contato

Para dúvidas, contribuições ou sugestões, entre em contato com qualquer um dos autores por e-mail.

---

## 📄 Licença

Este projeto é de caráter educacional e está sujeito às diretrizes da Pontifícia Universidade Católica do Paraná (PUCPR).

