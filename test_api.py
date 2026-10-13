"""
Script de Teste Automatizado de Ponta a Ponta para a API Ello Mineiro.
Executa os cenários do Passo 3 definidos no Guia de Ambiente e Execução:
1. Health check (ping da API + verificação do Banco MySQL)
2. Cadastro de novo usuário com perfil padrão 'Usuario' e endereço (201 Created)
3. Tentativa de cadastro duplicado com mesmo login/email (409 Conflict)
4. Autenticação e emissão do cookie HttpOnly 'access_token' (200 OK)
5. Consulta à rota protegida /api/me usando o cookie (200 OK)
6. Logout e destruição da sessão (200 OK)
"""

import random
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def executar_testes():
    print("=" * 60)
    print("INICIANDO BATERIA DE TESTES DA API E BANCO LOCAL (XAMPP)")
    print("=" * 60)

    # 1. Health check
    print("\n[1/6] Testando GET /health...")
    res_health = client.get("/health")
    print(f"Status: {res_health.status_code}")
    print(f"Resposta: {res_health.json()}")
    assert res_health.status_code == 200, "Health check falhou!"

    # 2. Cadastro novo
    login_aleatorio = f"aluno_{random.randint(1000, 9999)}"
    email_aleatorio = f"{login_aleatorio}@escola.com"

    payload_cadastro = {
        "user_login": login_aleatorio,
        "email": email_aleatorio,
        "senha": "SenhaForte123!",
        "nome": "Aluno Teste da Silva",
        "telefone": "31988887777",
        "endereco": {
            "tipo": "Residencial",
            "cep": "30110000",
            "rua": "Av. Afonso Pena",
            "numero": "1000",
            "bairro": "Centro",
            "cidade": "Belo Horizonte",
            "uf": "MG"
        }
    }

    print(f"\n[2/7] Testando POST /api/auth/register com login '{login_aleatorio}' e endereço completo...")
    res_reg = client.post("/api/auth/register", json=payload_cadastro)
    print(f"Status: {res_reg.status_code}")
    print(f"Resposta: {res_reg.json()}")
    assert res_reg.status_code == 201, "Cadastro falhou!"

    # 3. Teste de Rejeição de Cadastro SEM Endereço (422 Unprocessable Entity)
    print("\n[3/7] Testando tentativa de cadastro SEM endereço (deve retornar 422 Unprocessable Entity)...")
    payload_sem_endereco = payload_cadastro.copy()
    payload_sem_endereco["user_login"] = f"sem_end_{random.randint(1000, 9999)}"
    payload_sem_endereco["email"] = f"{payload_sem_endereco['user_login']}@escola.com"
    payload_sem_endereco["endereco"] = None
    res_sem_end = client.post("/api/auth/register", json=payload_sem_endereco)
    print(f"Status: {res_sem_end.status_code}")
    print(f"Resposta: {res_sem_end.json()}")
    assert res_sem_end.status_code == 422, "API permitiu cadastro sem endereço!"

    # 4. Teste de Duplicidade (409 Conflict)
    print("\n[4/7] Testando duplicidade com o mesmo payload (deve retornar 409 Conflict)...")
    res_dup = client.post("/api/auth/register", json=payload_cadastro)
    print(f"Status: {res_dup.status_code}")
    print(f"Resposta: {res_dup.json()}")
    assert res_dup.status_code == 409, "Duplicidade não foi barrada!"

    # 4. Login com identificador e senha
    print(f"\n[4/6] Testando POST /api/auth/login...")
    payload_login = {
        "identificador": login_aleatorio,
        "senha": "SenhaForte123!"
    }
    res_login = client.post("/api/auth/login", json=payload_login)
    print(f"Status: {res_login.status_code}")
    print(f"Resposta: {res_login.json()}")
    assert res_login.status_code == 200, "Login falhou!"

    cookie_token = res_login.cookies.get("access_token")
    print(f"Cookie 'access_token' emitido pelo servidor? {'SIM' if cookie_token else 'NAO'}")
    assert cookie_token is not None, "Cookie HttpOnly não foi emitido!"

    # 5. Consulta a /api/me com o cookie recebido
    print("\n[5/6] Testando rota protegida GET /api/me com cookie de sessão...")
    res_me = client.get("/api/me", cookies={"access_token": cookie_token})
    print(f"Status: {res_me.status_code}")
    print(f"Resposta: {res_me.json()}")
    assert res_me.status_code == 200, "Consulta a /api/me falhou!"
    assert res_me.json()["user_login"] == login_aleatorio
    assert res_me.json()["permissao_nome"] == "Usuario"
    assert len(res_me.json()["enderecos"]) > 0

    # 6. Logout
    print("\n[6/6] Testando POST /api/auth/logout...")
    res_logout = client.post("/api/auth/logout")
    print(f"Status: {res_logout.status_code}")
    print(f"Resposta: {res_logout.json()}")
    assert res_logout.status_code == 200, "Logout falhou!"

    print("\n" + "=" * 60)
    print("TODOS OS 6 TESTES DA API PASSARAM COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    executar_testes()
