-- Backup do banco estudio_tatuagem
-- Gerado conforme a Aula 2 do curso

CREATE DATABASE IF NOT EXISTS estudio_tatuagem;
USE estudio_tatuagem;

-- Níveis de experiência dos tatuadores (Júnior, Pleno, Sênior)
CREATE TABLE IF NOT EXISTS senioridade (
    idsenioridade INT AUTO_INCREMENT PRIMARY KEY,
    nome          VARCHAR(50) NOT NULL
);

-- Estilos de tatuagem (Blackwork, Aquarela, etc.)
CREATE TABLE IF NOT EXISTS estilo (
    idestilo  INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL
);

-- Tatuadores do estúdio
CREATE TABLE IF NOT EXISTS tatuador (
    idtatuador      INT AUTO_INCREMENT PRIMARY KEY,
    nometatuador    VARCHAR(100) NOT NULL,
    cpf             CHAR(11)     NOT NULL UNIQUE,
    email           VARCHAR(100),
    telefone        VARCHAR(20),
    datacontratacao DATE,
    idsenioridade   INT NOT NULL,
    FOREIGN KEY (idsenioridade) REFERENCES senioridade(idsenioridade)
);

-- Quais estilos cada tatuador domina (relação N:N)
CREATE TABLE IF NOT EXISTS tatuador_estilo (
    idtatuador INT  NOT NULL,
    idestilo   INT  NOT NULL,
    dataestilo DATE,
    PRIMARY KEY (idtatuador, idestilo),
    FOREIGN KEY (idtatuador) REFERENCES tatuador(idtatuador),
    FOREIGN KEY (idestilo)   REFERENCES estilo(idestilo)
);

-- Clientes do estúdio
CREATE TABLE IF NOT EXISTS cliente (
    idcliente    INT AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    cpf          CHAR(11)     NOT NULL UNIQUE,
    telefone     VARCHAR(20),
    datacadastro DATE,
    cidade       VARCHAR(100),
    uf           CHAR(2)
);

-- Agendamentos de sessões
CREATE TABLE IF NOT EXISTS agendamento (
    idagendamento     INT AUTO_INCREMENT PRIMARY KEY,
    idcliente         INT            NOT NULL,
    idtatuador        INT            NOT NULL,
    dataagendamento   DATE           NOT NULL,
    horaagendamento   TIME           NOT NULL,
    descricaotatuagem TEXT,
    desenhoaprovado   VARCHAR(255),
    valortatuagem     DECIMAL(10,2),
    status            ENUM('pendente','confirmado','concluido','cancelado') NOT NULL DEFAULT 'pendente',
    FOREIGN KEY (idcliente)  REFERENCES cliente(idcliente),
    FOREIGN KEY (idtatuador) REFERENCES tatuador(idtatuador)
);

INSERT INTO senioridade (nome) VALUES ('Júnior'), ('Pleno'), ('Sênior');

INSERT INTO estilo (descricao) VALUES ('Blackwork'), ('Aquarela'), ('Realismo'), ('Old School');

INSERT INTO tatuador (nometatuador, cpf, email, telefone, datacontratacao, idsenioridade) VALUES
    ('Lucas Mendes', '11111111111', 'lucas@estudio.com', '11999990001', '2020-03-01', 3),
    ('Carla Souza',  '22222222222', 'carla@estudio.com', '11999990002', '2022-06-15', 2),
    ('Pedro Lima',   '33333333333', 'pedro@estudio.com', '11999990003', '2024-01-10', 1);

INSERT INTO tatuador_estilo (idtatuador, idestilo, dataestilo) VALUES
    (1, 1, '2020-03-01'),
    (1, 3, '2021-05-10'),
    (2, 2, '2022-06-15'),
    (3, 4, '2024-01-10');

INSERT INTO cliente (nome, cpf, telefone, datacadastro, cidade, uf) VALUES
    ('Ana Silva',   '44444444444', '11988880001', '2024-01-15', 'São Paulo',      'SP'),
    ('Bruno Costa', '55555555555', '31988880002', '2024-03-22', 'Belo Horizonte', 'MG');

INSERT INTO agendamento (idcliente, idtatuador, dataagendamento, horaagendamento, descricaotatuagem, valortatuagem, status) VALUES
    (1, 1, '2025-05-10', '14:00', 'Mandala no braço',       350.00, 'pendente'),
    (2, 2, '2025-05-11', '10:00', 'Rosa aquarela no ombro', 200.00, 'pendente');
