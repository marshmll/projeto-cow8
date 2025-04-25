INSERT INTO DadosAnimal (raca, peso_medio) VALUES
('Nelore', 500.00),
('Angus', 600.00),
('Brahman', 550.00),
('Hereford', 580.00),
('Girolando', 450.00);

INSERT INTO Balanca (id, uid, status) VALUES
(1, 'f654', 'Offline'),
(2, '89f3', 'Offline'),
(3, '41f5', 'Offline'),
(4, 'c5ab', 'Offline'),
(5, 'faba', 'Offline');

INSERT INTO Animal (uid, sexo, id_dados_animal) VALUES 
('MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=', 'M', 1),
('QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVphYmNkZWZ=', 'F', 2),
('NDA4ZmExMzcyOTBiMmJlMWVjZDA2YWU1MTQ4ZWI1OTk=', 'M', 3),
('Zjc4MGI2YzYxYjNmNDVkY2U5MDRjNDg4YjBhNDRjZjE=', 'F', 4),
('NzVjNTliMmEyMjc1NzYyNWIzYzFkOWUyNDQxNWU4NWE=', 'M', 5);

-- Inserções mensais para 2025 (padrões claros)
-- Janeiro (todos começam com pesos iniciais)
INSERT INTO ControlePesagem (id_animal, id_balanca, datahora_pesagem, medicao_peso, observacoes) VALUES
(1, 1, '2025-01-05 09:00:00', 400.00, 'Peso inicial - saudável'),
(1, 1, '2025-01-20 10:00:00', 410.00, 'Crescimento normal'),
(2, 2, '2025-01-05 09:00:00', 450.00, 'Peso inicial - abaixo do esperado'),
(2, 2, '2025-01-20 10:00:00', 455.00, 'Crescimento lento'),
(3, 3, '2025-01-05 09:00:00', 420.00, 'Peso inicial - crítico'),
(3, 3, '2025-01-20 10:00:00', 415.00, 'Leve perda de peso'),
(4, 4, '2025-01-05 09:00:00', 380.00, 'Peso inicial - saudável'),
(4, 4, '2025-01-20 10:00:00', 390.00, 'Crescimento normal'),
(5, 5, '2025-01-05 09:00:00', 300.00, 'Peso inicial - muito abaixo'),
(5, 5, '2025-01-20 10:00:00', 305.00, 'Crescimento insuficiente'),

-- Fevereiro (padrões se mantêm)
(1, 1, '2025-02-05 09:00:00', 420.00, 'Crescimento consistente'),
(1, 1, '2025-02-20 10:00:00', 430.00, 'Desenvolvimento ideal'),
(2, 2, '2025-02-05 09:00:00', 460.00, 'Abaixo do esperado'),
(2, 2, '2025-02-20 10:00:00', 465.00, 'Crescimento lento'),
(3, 3, '2025-02-05 09:00:00', 410.00, 'Perda de peso'),
(3, 3, '2025-02-20 10:00:00', 405.00, 'Condição piorando'),
(4, 4, '2025-02-05 09:00:00', 400.00, 'Crescimento normal'),
(4, 4, '2025-02-20 10:00:00', 410.00, 'Desenvolvimento saudável'),
(5, 5, '2025-02-05 09:00:00', 310.00, 'Peso muito baixo'),
(5, 5, '2025-02-20 10:00:00', 315.00, 'Crescimento mínimo'),

-- Março (intensificando os padrões)
(1, 1, '2025-03-05 09:00:00', 440.00, 'Excelente desenvolvimento'),
(1, 1, '2025-03-20 10:00:00', 450.00, 'Peso ideal'),
(2, 2, '2025-03-05 09:00:00', 470.00, 'Abaixo do esperado'),
(2, 2, '2025-03-20 10:00:00', 475.00, 'Crescimento abaixo da média'),
(3, 3, '2025-03-05 09:00:00', 400.00, 'Perda de peso acentuada'),
(3, 3, '2025-03-20 10:00:00', 395.00, 'Condição crítica'),
(4, 4, '2025-03-05 09:00:00', 420.00, 'Crescimento normal'),
(4, 4, '2025-03-20 10:00:00', 430.00, 'Saudável'),
(5, 5, '2025-03-05 09:00:00', 320.00, 'Peso crítico'),
(5, 5, '2025-03-20 10:00:00', 325.00, 'Crescimento insuficiente'),

-- Abril (continuando os padrões)
(1, 1, '2025-04-05 09:00:00', 460.00, 'Saudável'),
(1, 1, '2025-04-20 10:00:00', 470.00, 'Peso excelente'),
(2, 2, '2025-04-05 09:00:00', 480.00, 'Em alerta'),
(2, 2, '2025-04-20 10:00:00', 485.00, 'Abaixo da média'),
(3, 3, '2025-04-05 09:00:00', 390.00, 'Perda de peso grave'),
(3, 3, '2025-04-20 10:00:00', 385.00, 'Necessita intervenção'),
(4, 4, '2025-04-05 09:00:00', 440.00, 'Saudável'),
(4, 4, '2025-04-20 10:00:00', 450.00, 'Desenvolvimento ideal'),
(5, 5, '2025-04-05 09:00:00', 330.00, 'Peso muito abaixo'),
(5, 5, '2025-04-20 10:00:00', 335.00, 'Crescimento mínimo'),

-- Padrão continua para os meses subsequentes (Maio-Dezembro) com a mesma lógica:
-- Animal 1: +10kg/mês (saudável)
-- Animal 2: +5kg/mês (alerta)
-- Animal 3: -5kg/mês até tratamento em julho (crítico)
-- Animal 4: +10kg/mês (saudável)
-- Animal 5: +5kg/mês (crítico por estar muito abaixo)

-- Maio
(1, 1, '2025-05-05 09:00:00', 480.00, 'Saudável'),
(1, 1, '2025-05-20 10:00:00', 490.00, 'Peso excelente'),
(2, 2, '2025-05-05 09:00:00', 490.00, 'Em alerta'),
(2, 2, '2025-05-20 10:00:00', 495.00, 'Abaixo da média'),
(3, 3, '2025-05-05 09:00:00', 380.00, 'Condição crítica'),
(3, 3, '2025-05-20 10:00:00', 375.00, 'Perda de peso'),
(4, 4, '2025-05-05 09:00:00', 460.00, 'Saudável'),
(4, 4, '2025-05-20 10:00:00', 470.00, 'Desenvolvimento ideal'),
(5, 5, '2025-05-05 09:00:00', 340.00, 'Peso muito abaixo'),
(5, 5, '2025-05-20 10:00:00', 345.00, 'Crescimento mínimo'),

-- Junho
(1, 1, '2025-06-05 09:00:00', 500.00, 'Saudável'),
(1, 1, '2025-06-20 10:00:00', 510.00, 'Peso excelente'),
(2, 2, '2025-06-05 09:00:00', 500.00, 'Em alerta'),
(2, 2, '2025-06-20 10:00:00', 505.00, 'Abaixo da média'),
(3, 3, '2025-06-05 09:00:00', 370.00, 'Condição crítica'),
(3, 3, '2025-06-20 10:00:00', 365.00, 'Perda de peso'),
(4, 4, '2025-06-05 09:00:00', 480.00, 'Saudável'),
(4, 4, '2025-06-20 10:00:00', 490.00, 'Desenvolvimento ideal'),
(5, 5, '2025-06-05 09:00:00', 350.00, 'Peso muito abaixo'),
(5, 5, '2025-06-20 10:00:00', 355.00, 'Crescimento mínimo'),

-- Julho (Animal 3 inicia tratamento)
(1, 1, '2025-07-05 09:00:00', 520.00, 'Saudável'),
(1, 1, '2025-07-20 10:00:00', 530.00, 'Peso excelente'),
(2, 2, '2025-07-05 09:00:00', 510.00, 'Em alerta'),
(2, 2, '2025-07-20 10:00:00', 515.00, 'Abaixo da média'),
(3, 3, '2025-07-05 09:00:00', 370.00, 'Início de tratamento'),
(3, 3, '2025-07-20 10:00:00', 380.00, 'Primeira melhora'),
(4, 4, '2025-07-05 09:00:00', 500.00, 'Saudável'),
(4, 4, '2025-07-20 10:00:00', 510.00, 'Desenvolvimento ideal'),
(5, 5, '2025-07-05 09:00:00', 360.00, 'Peso muito abaixo'),
(5, 5, '2025-07-20 10:00:00', 365.00, 'Crescimento mínimo'),

-- Agosto (Animal 3 em recuperação)
(1, 1, '2025-08-05 09:00:00', 540.00, 'Saudável'),
(1, 1, '2025-08-20 10:00:00', 550.00, 'Peso excelente'),
(2, 2, '2025-08-05 09:00:00', 520.00, 'Em alerta'),
(2, 2, '2025-08-20 10:00:00', 525.00, 'Abaixo da média'),
(3, 3, '2025-08-05 09:00:00', 390.00, 'Em recuperação'),
(3, 3, '2025-08-20 10:00:00', 400.00, 'Ganho de peso'),
(4, 4, '2025-08-05 09:00:00', 520.00, 'Saudável'),
(4, 4, '2025-08-20 10:00:00', 530.00, 'Desenvolvimento ideal'),
(5, 5, '2025-08-05 09:00:00', 370.00, 'Peso muito abaixo'),
(5, 5, '2025-08-20 10:00:00', 375.00, 'Crescimento mínimo'),

-- Setembro
(1, 1, '2025-09-05 09:00:00', 560.00, 'Saudável'),
(1, 1, '2025-09-20 10:00:00', 570.00, 'Peso excelente'),
(2, 2, '2025-09-05 09:00:00', 530.00, 'Em alerta'),
(2, 2, '2025-09-20 10:00:00', 535.00, 'Abaixo da média'),
(3, 3, '2025-09-05 09:00:00', 410.00, 'Recuperação'),
(3, 3, '2025-09-20 10:00:00', 420.00, 'Melhora contínua'),
(4, 4, '2025-09-05 09:00:00', 540.00, 'Saudável'),
(4, 4, '2025-09-20 10:00:00', 550.00, 'Desenvolvimento ideal'),
(5, 5, '2025-09-05 09:00:00', 380.00, 'Peso muito abaixo'),
(5, 5, '2025-09-20 10:00:00', 385.00, 'Crescimento mínimo'),

-- Outubro 2025 (Animal 3 continua recuperação)
(1, 1, '2025-10-05 09:00:00', 580.00, 'Saudável - peso excelente'),
(1, 1, '2025-10-20 10:00:00', 590.00, 'Desenvolvimento ideal'),
(2, 2, '2025-10-05 09:00:00', 540.00, 'Em alerta - abaixo do esperado'),
(2, 2, '2025-10-20 10:00:00', 545.00, 'Crescimento lento persistente'),
(3, 3, '2025-10-05 09:00:00', 430.00, 'Recuperação acelerada'),
(3, 3, '2025-10-20 10:00:00', 440.00, 'Ganho de peso consistente'),
(4, 4, '2025-10-05 09:00:00', 560.00, 'Saudável - padrão normal'),
(4, 4, '2025-10-20 10:00:00', 570.00, 'Crescimento adequado'),
(5, 5, '2025-10-05 09:00:00', 390.00, 'Peso crítico - intervenção necessária'),
(5, 5, '2025-10-20 10:00:00', 395.00, 'Melhora mínima'),

-- Novembro 2025 (Animal 3 atinge 80% do peso ideal)
(1, 1, '2025-11-05 09:00:00', 600.00, 'Saudável - atingiu peso médio'),
(1, 1, '2025-11-20 10:00:00', 610.00, 'Acima da média'),
(2, 2, '2025-11-05 09:00:00', 550.00, 'Em alerta - ainda abaixo'),
(2, 2, '2025-11-20 10:00:00', 555.00, 'Progresso lento'),
(3, 3, '2025-11-05 09:00:00', 450.00, '80% do peso ideal'),
(3, 3, '2025-11-20 10:00:00', 460.00, 'Mantendo ganho'),
(4, 4, '2025-11-05 09:00:00', 580.00, 'Saudável - padrão excelente'),
(4, 4, '2025-11-20 10:00:00', 590.00, 'Crescimento consistente'),
(5, 5, '2025-11-05 09:00:00', 400.00, 'Ainda crítico'),
(5, 5, '2025-11-20 10:00:00', 405.00, 'Progresso insuficiente'),

-- Dezembro 2025 (Animal 3 quase recuperado, outros padrões mantidos)
(1, 1, '2025-12-05 09:00:00', 620.00, 'Saudável - acima da média'),
(1, 1, '2025-12-20 10:00:00', 630.00, 'Final de ano excelente'),
(2, 2, '2025-12-05 09:00:00', 560.00, 'Em alerta - 93% do esperado'),
(2, 2, '2025-12-20 10:00:00', 565.00, 'Quase aceitável'),
(3, 3, '2025-12-05 09:00:00', 470.00, '85% do peso - quase recuperado'),
(3, 3, '2025-12-20 10:00:00', 480.00, 'Recuperação completa'),
(4, 4, '2025-12-05 09:00:00', 600.00, 'Saudável - peso ideal'),
(4, 4, '2025-12-20 10:00:00', 610.00, 'Desenvolvimento perfeito'),
(5, 5, '2025-12-05 09:00:00', 410.00, 'Ainda abaixo (91%) - monitorar'),
(5, 5, '2025-12-20 10:00:00', 415.00, 'Melhora gradual');