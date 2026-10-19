"""
Script de Teste Automatizado de Ponta a Ponta para a API Ello Mineiro.
Valida:
1. Health check (GET /health)
2. Proteção de Mutabilidade (Subtópico 3.2):
   - Bloqueio 403 para scripts externos sem X-API-Key
   - Bloqueio 403 para chave inválida
   - Sucesso para script externo com X-API-Key válida
   - Sucesso transparente para front-end na mesma origem (Sec-Fetch-Site: same-origin / Origin)
3. Cadastro com TODOS os campos opcionais preenchidos (genero, cpf, rg, data_nasc, telefone, telefone_sec)
4. Cadastro com TODOS os campos opcionais NÃO preenchidos (None / null na tabela Usuarios)
5. Integridade atômica com endereço obrigatório (422) e duplicidade (409)
6. Autenticação, emissão e consumo de cookie HttpOnly 'access_token' (/me)
7. Rate Limiting por IP (RNF07) com HTTP 429 Too Many Requests
"""

import os
import random
from fastapi.testclient import TestClient
from app.main import app
from app.security_guards import rate_limiter

client = TestClient(app)
API_KEY_LOCAL = os.getenv("API_KEY", "ello_priv_key_local_dev_2026")
HEADER_API_KEY = {"X-API-Key": API_KEY_LOCAL}
HEADER_SAME_ORIGIN = {"Sec-Fetch-Site": "same-origin", "Origin": "http://testserver"}


def gerar_digitos_aleatorios(qtd: int) -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(qtd)])


def gerar_cpf_valido() -> str:
    """Gera um CPF matematicamente válido com os dois dígitos verificadores do módulo 11."""
    nove_digitos = [random.randint(0, 9) for _ in range(9)]
    soma1 = sum(nove_digitos[i] * (10 - i) for i in range(9))
    resto1 = (soma1 * 10) % 11
    d1 = 0 if resto1 in (10, 11) else resto1
    dez_digitos = nove_digitos + [d1]
    soma2 = sum(dez_digitos[i] * (11 - i) for i in range(10))
    resto2 = (soma2 * 10) % 11
    d2 = 0 if resto2 in (10, 11) else resto2
    return "".join(map(str, dez_digitos + [d2]))


def executar_testes():
    print("=" * 70)
    print("INICIANDO BATERIA COMPLETA DE TESTES DE SEGURANÇA E API E BANCO LOCAL")
    print("=" * 70)

    # 1. Health check
    print("\n[1/11] Testando GET /health...")
    res_health = client.get("/health")
    print(f"Status: {res_health.status_code} | Resposta: {res_health.json()}")
    assert res_health.status_code == 200, "Health check falhou!"

    # 2. Mutabilidade: Bloqueio para chamada externa sem X-API-Key (403 Forbidden)
    print("\n[2/11] Testando bloqueio 403 em chamada externa sem X-API-Key e sem mesma origem...")
    res_bloqueio = client.post("/api/auth/register", json={"user_login": "teste_bloq"})
    print(f"Status: {res_bloqueio.status_code} | Resposta: {res_bloqueio.json()}")
    assert res_bloqueio.status_code == 403, "API deveria barrar chamada externa sem chave com 403!"

    # 3. Mutabilidade: Bloqueio com chave de API incorreta (403 Forbidden)
    print("\n[3/11] Testando bloqueio 403 com X-API-Key inválida...")
    res_chave_invalida = client.post(
        "/api/auth/register",
        json={"user_login": "teste_bloq"},
        headers={"X-API-Key": "chave_totalmente_errada_123"}
    )
    print(f"Status: {res_chave_invalida.status_code} | Resposta: {res_chave_invalida.json()}")
    assert res_chave_invalida.status_code == 403, "API deveria barrar chave inválida com 403!"

    # 4. Cadastro novo COMPLETO (com todos os campos opcionais preenchidos) via X-API-Key
    login_completo = f"aluno_full_{random.randint(1000, 9999)}"
    cpf_valido_full = gerar_cpf_valido()
    rg_aleatorio = f"MG{gerar_digitos_aleatorios(7)}"

    payload_completo = {
        "user_login": login_completo,
        "email": f"{login_completo}@escola.com",
        "senha": "SenhaForte123!",
        "nome": "Aluno Teste Completo da Silva",
        "genero": "Masculino",
        "cpf": cpf_valido_full,
        "rg": rg_aleatorio,
        "data_nasc": "2001-08-20",
        "telefone": "31988887777",
        "telefone_sec": "31977776666",
        "endereco": {
            "tipo": "Residencial",
            "cep": "30110000",
            "rua": "Av. Afonso Pena",
            "numero": "1000",
            "bairro": "Centro",
            "complemento": "Apto 302",
            "cidade": "Belo Horizonte",
            "uf": "MG"
        }
    }

    print(f"\n[4/11] Testando POST /api/auth/register com TODOS os campos preenchidos ({login_completo})...")
    res_reg_full = client.post("/api/auth/register", json=payload_completo, headers=HEADER_API_KEY)
    print(f"Status: {res_reg_full.status_code} | Resposta: {res_reg_full.json()}")
    assert res_reg_full.status_code == 201, "Cadastro com todos os campos preenchidos falhou!"

    # 5. Cadastro com campos opcionais NÃO PREENCHIDOS (genero, data_nasc, telefones = None) e CPF/RG OBRIGATÓRIOS
    login_vazio = f"aluno_vazio_{random.randint(1000, 9999)}"
    cpf_valido_vazio = gerar_cpf_valido()
    rg_valido_vazio = f"SP{gerar_digitos_aleatorios(7)}"

    payload_nao_preenchidos = {
        "user_login": login_vazio,
        "email": f"{login_vazio}@escola.com",
        "senha": "SenhaForte123!",
        "nome": "Usuario Sem Opcionais",
        "genero": None,
        "cpf": cpf_valido_vazio,
        "rg": rg_valido_vazio,
        "data_nasc": None,
        "telefone": None,
        "telefone_sec": None,
        "endereco": {
            "tipo": "Residencial",
            "cep": "30110000",
            "rua": "Rua da Bahia",
            "numero": "500",
            "bairro": "Centro",
            "complemento": None,
            "cidade": "Belo Horizonte",
            "uf": "MG"
        }
    }

    print(f"\n[5/11] Testando POST /api/auth/register com campos opcionais NÃO preenchidos e CPF/RG obrigatórios ({login_vazio})...")
    res_reg_vazio = client.post("/api/auth/register", json=payload_nao_preenchidos, headers=HEADER_API_KEY)
    print(f"Status: {res_reg_vazio.status_code} | Resposta: {res_reg_vazio.json()}")
    assert res_reg_vazio.status_code == 201, "Cadastro com campos opcionais vazios falhou!"

    # 6. Cadastro transparente simulando o Front-end oficial do site (mesma origem, zero atrito)
    login_front = f"front_{random.randint(1000, 9999)}"
    payload_front = payload_completo.copy()
    payload_front["user_login"] = login_front
    payload_front["email"] = f"{login_front}@escola.com"
    payload_front["cpf"] = gerar_cpf_valido()
    payload_front["rg"] = f"MG{gerar_digitos_aleatorios(7)}"

    print(f"\n[6/11] Testando POST /api/auth/register simulando front-end legítimo (mesma origem, zero atrito)...")
    res_front = client.post("/api/auth/register", json=payload_front, headers=HEADER_SAME_ORIGIN)
    print(f"Status: {res_front.status_code} | Resposta: {res_front.json()}")
    assert res_front.status_code == 201, "Cadastro de mesma origem pelo front-end falhou!"

    # 7. Rejeição de Cadastro SEM Endereço e SEM CPF/RG (422 Unprocessable Entity)
    print("\n[7/11] Testando rejeição de cadastro SEM endereço e SEM CPF obrigatório (422)...")
    payload_sem_endereco = payload_completo.copy()
    payload_sem_endereco["user_login"] = f"sem_end_{random.randint(1000, 9999)}"
    payload_sem_endereco["email"] = f"{payload_sem_endereco['user_login']}@escola.com"
    payload_sem_endereco["cpf"] = None
    payload_sem_endereco["endereco"] = None
    res_sem_end = client.post("/api/auth/register", json=payload_sem_endereco, headers=HEADER_API_KEY)
    print(f"Status: {res_sem_end.status_code} | Resposta: {res_sem_end.json()}")
    assert res_sem_end.status_code == 422, "API permitiu cadastro sem endereço ou sem CPF!"


    # 8. Teste de Duplicidade (409 Conflict)
    print("\n[8/11] Testando detecção de duplicidade (409 Conflict)...")
    res_dup = client.post("/api/auth/register", json=payload_completo, headers=HEADER_API_KEY)
    print(f"Status: {res_dup.status_code} | Resposta: {res_dup.json()}")
    assert res_dup.status_code == 409, "Duplicidade não foi barrada!"

    # 9. Login e Emissão do Cookie HttpOnly para o usuário com campos vazios
    print("\n[9/11] Testando POST /api/auth/login para usuário com campos vazios...")
    payload_login = {
        "identificador": login_vazio,
        "senha": "SenhaForte123!"
    }
    res_login = client.post("/api/auth/login", json=payload_login, headers=HEADER_API_KEY)
    print(f"Status: {res_login.status_code} | Resposta: {res_login.json()}")
    assert res_login.status_code == 200, "Login falhou!"

    cookie_token = res_login.cookies.get("access_token")
    print(f"Cookie 'access_token' emitido pelo servidor? {'SIM' if cookie_token else 'NAO'}")
    assert cookie_token is not None, "Cookie HttpOnly não foi emitido!"

    # 10. Consulta à rota protegida /api/me validando que campos opcionais são None
    print("\n[10/11] Testando GET /api/me e verificando integridade dos campos não preenchidos...")
    res_me = client.get("/api/me", cookies={"access_token": cookie_token})
    assert res_me.status_code == 200, "Consulta a /api/me falhou!"
    dados_me = res_me.json()
    assert dados_me["user_login"] == login_vazio
    assert dados_me["cpf"] == cpf_valido_vazio, "cpf obrigatório não confere!"
    assert dados_me["rg"] == rg_valido_vazio, "rg obrigatório não confere!"
    assert dados_me["genero"] is None, "genero opcional deveria ser None!"
    assert dados_me["data_nasc"] is None, "data_nasc opcional deveria ser None!"
    assert dados_me["telefone"] is None, "telefone opcional deveria ser None!"
    assert dados_me["telefone_sec"] is None, "telefone_sec opcional deveria ser None!"
    assert len(dados_me["enderecos"]) == 1, "Usuário deveria ter exatamente 1 endereço vinculado!"
    print("Dados retornados validados: CPF e RG obrigatórios presentes, campos opcionais são None e endereço está ativo.")


    res_logout = client.post("/api/auth/logout", headers=HEADER_API_KEY)
    assert res_logout.status_code == 200, "Logout falhou!"
    print("Logout efetuado com sucesso!")

    # 11. Rate Limiting por IP (RNF07)
    print("\n[11/11] Testando Rate Limiting por IP (RNF07 - disparando requisições até 429 Too Many Requests)...")
    rate_limiter.reset()
    bloqueou_429 = False
    for i in range(12):  # Limite de login é 10 por minuto
        r = client.post(
            "/api/auth/login",
            json={"identificador": "teste_rate", "senha": "123"},
            headers=HEADER_API_KEY
        )
        if r.status_code == 429:
            bloqueou_429 = True
            print(f"Rate Limiting acionado com sucesso na tentativa {i + 1}: {r.json()}")
            assert "Retry-After" in r.headers, "Header 'Retry-After' não foi incluído na resposta 429!"
            break

    assert bloqueou_429, "Rate limiter não retornou 429 Too Many Requests após estourar o limite!"

    print("\n" + "=" * 70)
    print("TODOS OS 11 TESTES DE SEGURANÇA, API E BANCO PASSARAM COM 100% DE SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    executar_testes()
