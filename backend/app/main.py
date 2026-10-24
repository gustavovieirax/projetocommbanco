# ============================================================
# main.py — API do Estúdio de Tatuagem
# Descrição: endpoints para clientes, tatuadores, agendamentos,
#            login, JWT e autenticação.
# Como rodar: uvicorn app.main:app --reload
# ============================================================

from __future__ import annotations

import hashlib
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "estudio_tatuagem.db"))
JWT_SECRET = os.getenv("JWT_SECRET", "projetocombanco-dev-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

security = HTTPBearer(auto_error=False)


class ClienteCreate(BaseModel):
    nome: str = Field(..., min_length=2)
    cpf: str = Field(..., min_length=11, max_length=11)
    telefone: str | None = None
    datacadastro: str | None = None
    cidade: str | None = None
    uf: str | None = None


class ClienteUpdate(ClienteCreate):
    pass


class SenioridadeCreate(BaseModel):
    nome: str = Field(..., min_length=2)


class EstiloCreate(BaseModel):
    descricao: str = Field(..., min_length=2)


class TatuadorCreate(BaseModel):
    nometatuador: str = Field(..., min_length=2)
    cpf: str = Field(..., min_length=11, max_length=11)
    email: str | None = None
    telefone: str | None = None
    datacontratacao: str | None = None
    idsenioridade: int


class AgendamentoCreate(BaseModel):
    idcliente: int
    idtatuador: int
    dataagendamento: str
    horaagendamento: str
    descricaotatuagem: str | None = None
    desenhoaprovado: str | None = None
    valortatuagem: float | None = None
    status: Literal["pendente", "confirmado", "concluido", "cancelado"] = "pendente"


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2)
    email: str = Field(...)
    senha: str = Field(..., min_length=6)


class UsuarioLogin(BaseModel):
    email: str
    senha: str


class LoginResponse(BaseModel):
    acess_token: str
    token_type: str = "bearer"
    usuario: dict[str, Any]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.strip().encode("utf-8")).hexdigest()


def criar_token(email: str) -> str:
    payload = {"sub": email, "exp": datetime.utcnow() + timedelta(hours=8)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def buscar_usuario_por_email(email: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        usuario = conn.execute(
            "SELECT idusuario, nome, email, senha FROM usuario WHERE email = ?",
            (email.lower(),),
        ).fetchone()
        return dict(usuario) if usuario else None


def verificar_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict[str, Any]:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente.")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido.")
        usuario = buscar_usuario_por_email(email)
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuário não encontrado.")
        return usuario
    except jwt.PyJWTError as erro:
        raise HTTPException(status_code=401, detail=f"Token inválido: {erro}") from erro


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS senioridade (
                idsenioridade INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS estilo (
                idestilo INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tatuador (
                idtatuador INTEGER PRIMARY KEY AUTOINCREMENT,
                nometatuador TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                email TEXT,
                telefone TEXT,
                datacontratacao TEXT,
                idsenioridade INTEGER NOT NULL,
                FOREIGN KEY (idsenioridade) REFERENCES senioridade(idsenioridade)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tatuador_estilo (
                idtatuador INTEGER NOT NULL,
                idestilo INTEGER NOT NULL,
                dataestilo TEXT,
                PRIMARY KEY (idtatuador, idestilo),
                FOREIGN KEY (idtatuador) REFERENCES tatuador(idtatuador),
                FOREIGN KEY (idestilo) REFERENCES estilo(idestilo)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cliente (
                idcliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                telefone TEXT,
                datacadastro TEXT,
                cidade TEXT,
                uf TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agendamento (
                idagendamento INTEGER PRIMARY KEY AUTOINCREMENT,
                idcliente INTEGER NOT NULL,
                idtatuador INTEGER NOT NULL,
                dataagendamento TEXT NOT NULL,
                horaagendamento TEXT NOT NULL,
                descricaotatuagem TEXT,
                desenhoaprovado TEXT,
                valortatuagem REAL,
                status TEXT NOT NULL DEFAULT 'pendente',
                FOREIGN KEY (idcliente) REFERENCES cliente(idcliente),
                FOREIGN KEY (idtatuador) REFERENCES tatuador(idtatuador)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usuario (
                idusuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL
            )
            """
        )

        if conn.execute("SELECT COUNT(*) FROM senioridade").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO senioridade (nome) VALUES (?)",
                [("Júnior",), ("Pleno",), ("Sênior",)],
            )

        if conn.execute("SELECT COUNT(*) FROM estilo").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO estilo (descricao) VALUES (?)",
                [("Blackwork",), ("Aquarela",), ("Realismo",), ("Old School",)],
            )

        if conn.execute("SELECT COUNT(*) FROM cliente").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO cliente (nome, cpf, telefone, datacadastro, cidade, uf) VALUES (?, ?, ?, ?, ?, ?)",
                [
                    ("Ana Silva", "44444444444", "11988880001", "2024-01-15", "São Paulo", "SP"),
                    ("Bruno Costa", "55555555555", "31988880002", "2024-03-22", "Belo Horizonte", "MG"),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM tatuador").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO tatuador (nometatuador, cpf, email, telefone, datacontratacao, idsenioridade) VALUES (?, ?, ?, ?, ?, ?)",
                [
                    ("Lucas Mendes", "11111111111", "lucas@estudio.com", "11999990001", "2020-03-01", 3),
                    ("Carla Souza", "22222222222", "carla@estudio.com", "11999990002", "2022-06-15", 2),
                    ("Pedro Lima", "33333333333", "pedro@estudio.com", "11999990003", "2024-01-10", 1),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM tatuador_estilo").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO tatuador_estilo (idtatuador, idestilo, dataestilo) VALUES (?, ?, ?)",
                [
                    (1, 1, "2020-03-01"),
                    (1, 3, "2021-05-10"),
                    (2, 2, "2022-06-15"),
                    (3, 4, "2024-01-10"),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM agendamento").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO agendamento (idcliente, idtatuador, dataagendamento, horaagendamento, descricaotatuagem, valortatuagem, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (1, 1, "2025-05-10", "14:00", "Mandala no braço", 350.00, "pendente"),
                    (2, 2, "2025-05-11", "10:00", "Rosa aquarela no ombro", 200.00, "pendente"),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?)",
                ("Administrador", "admin@estudio.com", hash_senha("admin123")),
            )


app = FastAPI(title="Estúdio de Tatuagem API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    # Verifica se a API está respondendo corretamente
    return {"status": "ok"}


@app.get("/clientes")
def listar_clientes() -> list[dict[str, Any]]:
    # Retorna todos os clientes em ordem alfabética
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM cliente ORDER BY nome").fetchall()
        return [dict(row) for row in rows]


@app.get("/clientes/{id_cliente}")
def buscar_cliente(id_cliente: int) -> dict[str, Any]:
    # Busca um cliente pelo identificador
    with get_connection() as conn:
        cliente = conn.execute("SELECT * FROM cliente WHERE idcliente = ?", (id_cliente,)).fetchone()
        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")
        return dict(cliente)


@app.post("/clientes", status_code=status.HTTP_201_CREATED)
def criar_cliente(dados: ClienteCreate) -> dict[str, Any]:
    # Cria um novo cliente e retorna o registro salvo
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO cliente (nome, cpf, telefone, datacadastro, cidade, uf)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    dados.nome,
                    dados.cpf,
                    dados.telefone,
                    dados.datacadastro,
                    dados.cidade,
                    dados.uf,
                ),
            )
            conn.commit()
            id_cliente = cursor.lastrowid
            return {"idcliente": id_cliente, **dados.model_dump()}
        except sqlite3.IntegrityError as erro:
            raise HTTPException(status_code=400, detail=f"CPF duplicado ou dados inválidos: {erro}") from erro


@app.put("/clientes/{id_cliente}")
def atualizar_cliente(id_cliente: int, dados: ClienteUpdate) -> dict[str, Any]:
    # Atualiza os dados de um cliente existente
    with get_connection() as conn:
        cliente = conn.execute("SELECT * FROM cliente WHERE idcliente = ?", (id_cliente,)).fetchone()
        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")

        conn.execute(
            """
            UPDATE cliente
            SET nome = ?, cpf = ?, telefone = ?, datacadastro = ?, cidade = ?, uf = ?
            WHERE idcliente = ?
            """,
            (
                dados.nome,
                dados.cpf,
                dados.telefone,
                dados.datacadastro,
                dados.cidade,
                dados.uf,
                id_cliente,
            ),
        )
        conn.commit()
        return {"idcliente": id_cliente, **dados.model_dump()}


@app.delete("/clientes/{id_cliente}")
def excluir_cliente(id_cliente: int) -> dict[str, str]:
    # Remove um cliente pelo identificador
    with get_connection() as conn:
        linha = conn.execute("DELETE FROM cliente WHERE idcliente = ?", (id_cliente,)).rowcount
        conn.commit()
        if linha == 0:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")
        return {"mensagem": "Cliente excluído com sucesso."}


@app.get("/senioridades")
def listar_senioridades() -> list[dict[str, Any]]:
    # Retorna os níveis de senioridade cadastrados
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM senioridade ORDER BY nome").fetchall()
        return [dict(row) for row in rows]


@app.post("/senioridades", status_code=status.HTTP_201_CREATED)
def criar_senioridade(dados: SenioridadeCreate) -> dict[str, Any]:
    # Cria um novo nível de senioridade
    with get_connection() as conn:
        cursor = conn.execute("INSERT INTO senioridade (nome) VALUES (?)", (dados.nome,))
        conn.commit()
        return {"idsenioridade": cursor.lastrowid, **dados.model_dump()}


@app.get("/estilos")
def listar_estilos() -> list[dict[str, Any]]:
    # Retorna todos os estilos cadastrados
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM estilo ORDER BY descricao").fetchall()
        return [dict(row) for row in rows]


@app.post("/estilos", status_code=status.HTTP_201_CREATED)
def criar_estilo(dados: EstiloCreate) -> dict[str, Any]:
    # Cria um novo estilo de tatuagem
    with get_connection() as conn:
        cursor = conn.execute("INSERT INTO estilo (descricao) VALUES (?)", (dados.descricao,))
        conn.commit()
        return {"idestilo": cursor.lastrowid, **dados.model_dump()}


@app.get("/tatuadores")
def listar_tatuadores() -> list[dict[str, Any]]:
    # Retorna todos os tatuadores com o nível de senioridade
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT t.*, s.nome AS senioridade
            FROM tatuador t
            LEFT JOIN senioridade s ON s.idsenioridade = t.idsenioridade
            ORDER BY t.nometatuador
            """
        ).fetchall()
        return [dict(row) for row in rows]


@app.post("/tatuadores", status_code=status.HTTP_201_CREATED)
def criar_tatuador(dados: TatuadorCreate) -> dict[str, Any]:
    # Cria um novo tatuador e usa a chave estrangeira de senioridade
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO tatuador (nometatuador, cpf, email, telefone, datacontratacao, idsenioridade)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    dados.nometatuador,
                    dados.cpf,
                    dados.email,
                    dados.telefone,
                    dados.datacontratacao,
                    dados.idsenioridade,
                ),
            )
            conn.commit()
            return {"idtatuador": cursor.lastrowid, **dados.model_dump()}
        except sqlite3.IntegrityError as erro:
            raise HTTPException(status_code=400, detail=f"Tatuador inválido: {erro}") from erro


@app.get("/agendamentos")
def listar_agendamentos() -> list[dict[str, Any]]:
    # Retorna os agendamentos com nome do cliente e do tatuador
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT a.*, c.nome AS nome_cliente, t.nometatuador
            FROM agendamento a
            LEFT JOIN cliente c ON c.idcliente = a.idcliente
            LEFT JOIN tatuador t ON t.idtatuador = a.idtatuador
            ORDER BY a.dataagendamento, a.horaagendamento
            """
        ).fetchall()
        return [dict(row) for row in rows]


@app.post("/agendamentos", status_code=status.HTTP_201_CREATED)
def criar_agendamento(dados: AgendamentoCreate) -> dict[str, Any]:
    # Cria um novo agendamento com cliente, tatuador, data e hora
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO agendamento (
                    idcliente, idtatuador, dataagendamento, horaagendamento,
                    descricaotatuagem, desenhoaprovado, valortatuagem, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dados.idcliente,
                    dados.idtatuador,
                    dados.dataagendamento,
                    dados.horaagendamento,
                    dados.descricaotatuagem,
                    dados.desenhoaprovado,
                    dados.valortatuagem,
                    dados.status,
                ),
            )
            conn.commit()
            return {"idagendamento": cursor.lastrowid, **dados.model_dump()}
        except sqlite3.IntegrityError as erro:
            raise HTTPException(status_code=400, detail=f"Agendamento inválido: {erro}") from erro


@app.post("/usuarios/cadastro", status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(dados: UsuarioCreate) -> dict[str, Any]:
    # Registra um novo usuário com senha criptografada
    email = dados.email.lower().strip()
    senha_criptografada = hash_senha(dados.senha)
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?)",
                (dados.nome, email, senha_criptografada),
            )
            conn.commit()
            return {"idusuario": cursor.lastrowid, "nome": dados.nome, "email": email}
        except sqlite3.IntegrityError as erro:
            raise HTTPException(status_code=400, detail=f"E-mail já cadastrado: {erro}") from erro


@app.post("/login", response_model=LoginResponse)
def login(dados: UsuarioLogin) -> LoginResponse:
    # Valida e-mail e senha para emitir um token JWT
    email = dados.email.lower().strip()
    usuario = buscar_usuario_por_email(email)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    senha_criptografada = hash_senha(dados.senha)
    if usuario["senha"] != senha_criptografada:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    token = criar_token(email)
    return LoginResponse(acess_token=token, usuario={"idusuario": usuario["idusuario"], "nome": usuario["nome"], "email": usuario["email"]})


@app.get("/dashboard")
def dashboard(usuario: dict[str, Any] = Depends(verificar_token)) -> dict[str, Any]:
    # Retorna os dados do usuário autenticado
    return {"mensagem": "Login válido", "usuario": {"idusuario": usuario["idusuario"], "nome": usuario["nome"], "email": usuario["email"]}}
