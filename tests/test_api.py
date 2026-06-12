import pytest
from fastapi.testclient import TestClient

# Importamos o app e as variáveis globais para poder resetar o estado da memória
from src.tarefas.app import app
import src.tarefas.app as app_module

client = TestClient(app)

@pytest.fixture(autouse=True)
def resetar_estado_api():
    """
    Fixture executada automaticamente antes de CADA teste.
    Garante a independência dos testes limpando o repositório em memória.
    """
    app_module._tarefas.clear()
    app_module._proximo_id = 1
    yield


# ==============================================================================
# MÓDULO: AUTENTICAÇÃO
# ==============================================================================

def test_ct01_login_valido():
    """
    Cenário: O cliente envia username e password preenchidos via form.
    Verifica se o login retorna status 200, um token não vazio e o tipo 'bearer'.
    """
    resposta = client.post('/auth/login', data={'username': 'aluno', 'password': 'senha123'})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert 'access_token' in dados
    assert dados['access_token'] != ""
    assert dados['token_type'] == 'bearer'


def test_ct02_login_sem_username():
    """
    Cenário: Formulário incompleto — campo obrigatório ausente.
    Verifica se a ausência do username resulta em status HTTP 422.
    """
    resposta = client.post('/auth/login', data={'password': 'senha123'})
    assert resposta.status_code == 422


def test_ct03_login_sem_password():
    """
    Cenário: Formulário incompleto — campo obrigatório ausente.
    Verifica se a ausência do password resulta em status HTTP 422.
    """
    resposta = client.post('/auth/login', data={'username': 'aluno'})
    assert resposta.status_code == 422


# ==============================================================================
# MÓDULO: CRIAR TAREFA
# ==============================================================================

def test_ct04_criar_tarefa_com_dados_validos_com_descricao():
    """
    Cenário: Cliente envia titulo e descricao preenchidos.
    Verifica criação com sucesso (201) e correspondência exata dos dados e tipo de ID.
    """
    payload = {"titulo": "Estudar pytest", "descricao": "Ler a documentação"}
    resposta = client.post('/tarefas', json=payload)
    assert resposta.status_code == 201
    dados = resposta.json()
    assert isinstance(dados['id'], int)
    assert dados['titulo'] == payload['titulo']
    assert dados['descricao'] == payload['descricao']
    assert dados['status'] == 'pendente'


def test_ct05_criar_tarefa_sem_descricao_campo_opcional():
    """
    Cenário: A descrição é opcional — deve ser aceita sem ela.
    Verifica se a tarefa é criada com sucesso e se a descrição retorna nula (None).
    """
    payload = {"titulo": "Tarefa sem descricao"}
    resposta = client.post('/tarefas', json=payload)
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados['descricao'] is None


def test_ct06_criar_tarefa_com_titulo_vazio():
    """
    Cenário: O título não pode ser uma string vazia (min_length=1).
    Verifica se o envio de string vazia gera um erro HTTP 422.
    """
    payload = {"titulo": ""}
    resposta = client.post('/tarefas', json=payload)
    assert resposta.status_code == 422


def test_ct07_criar_tarefa_sem_campo_titulo():
    """
    Cenário: O título é obrigatório.
    Verifica se a ausência do campo de título resulta em erro HTTP 422.
    """
    payload = {"descricao": "sem titulo"}
    resposta = client.post('/tarefas', json=payload)
    assert resposta.status_code == 422


def test_ct08_criar_tarefa_com_titulo_acima_do_limite_201():
    """
    Cenário: Limite máximo do título é 200 caracteres.
    Verifica se o envio de um título com 201 caracteres falha com HTTP 422.
    """
    payload = {"titulo": "A" * 201}
    resposta = client.post('/tarefas', json=payload)
    assert resposta.status_code == 422


def test_ct09_status_inicial_da_tarefa_criada_e_pendente():
    """
    Cenário: Independentemente do que o cliente envie, o status inicial é sempre 'pendente'.
    Verifica se o campo status é implicitamente setado de forma correta pela API.
    """
    payload = {"titulo": "Validar Status Inicial", "descricao": "Ignorar qualquer outro status"}
    resposta = client.post('/tarefas', json=payload)
    assert resposta.status_code == 201
    assert resposta.json()['status'] == 'pendente'


# ==============================================================================
# MÓDULO: LISTAR TAREFAS
# ==============================================================================

def test_ct10_listar_tarefas_com_repositorio_vazio():
    """
    Cenário: Nenhuma tarefa foi criada ainda.
    Verifica se a rota de listagem retorna uma lista totalmente vazia [] com status 200.
    """
    resposta = client.get('/tarefas')
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_ct11_listar_tarefas_apos_criacao():
    """
    Cenário: Uma tarefa é criada e depois a listagem é consultada.
    Verifica se a lista retornada passa a conter elementos após um cadastro bem-sucedido.
    """
    payload = {"titulo": "Tarefa Listável"}
    client.post('/tarefas', json=payload)
    
    resposta = client.get('/tarefas')
    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 1
    assert dados[0]['titulo'] == payload['titulo']


# ==============================================================================
# MÓDULO: BUSCAR TAREFA POR ID
# ==============================================================================

def test_ct12_buscar_tarefa_existente():
    """
    Cenário: A tarefa existe no repositório.
    Verifica se ao capturar o ID dinâmico criado e buscá-lo, a API retorna o registro correto (200).
    """
    criacao = client.post('/tarefas', json={"titulo": "Tarefa Especifica"})
    tarefa_id = criacao.json()['id']
    
    resposta = client.get(f'/tarefas/{tarefa_id}')
    assert resposta.status_code == 200
    assert resposta.json()['id'] == tarefa_id


def test_ct13_buscar_tarefa_com_id_inexistente():
    """
    Cenário: Nenhuma tarefa com aquele ID existe.
    Verifica se a busca por um identificador fora do escopo retorna HTTP 404.
    """
    resposta = client.get('/tarefas/99999')
    assert resposta.status_code == 404
    assert resposta.json()['detail'] == 'Tarefa não encontrada'


def test_ct14_buscar_tarefa_com_id_nao_numerico():
    """
    Cenário: O parâmetro tarefa_id deve ser um inteiro.
    Verifica se o envio de uma string alfanumérica na URL causa rejeição de tipo HTTP 422.
    """
    resposta = client.get('/tarefas/abc')
    assert resposta.status_code == 422


# ==============================================================================
# MÓDULO: DELETAR TAREFA
# ==============================================================================

def test_ct15_deletar_tarefa_sem_token():
    """
    Cenário: A rota exige autenticação — sem token, deve ser negada.
    Verifica se a omissão completa do cabeçalho de autorização resulta em HTTP 401.
    """
    resposta = client.delete('/tarefas/1')
    assert resposta.status_code == 401


def test_ct16_deletar_tarefa_com_token_invalido():
    """
    Cenário: Token forjado ou corrompido não deve ser aceito.
    Verifica se um token com formato ou assinatura incorreta resulta em HTTP 401.
    """
    headers = {"Authorization": "Bearer token-invalido"}
    resposta = client.delete('/tarefas/1', headers=headers)
    assert resposta.status_code == 401


def test_ct17_deletar_tarefa_existente_com_token_valido():
    """
    Cenário: Fluxo completo: autenticar, criar tarefa, deletar.
    Verifica se a deleção retorna HTTP 204 e nenhum conteúdo no corpo da resposta.
    """
    # 1. Login para pegar o Token
    login_resp = client.post('/auth/login', data={'username': 'aluno', 'password': 'senha123'})
    token = login_resp.json()['access_token']
    
    # 2. Criar a tarefa a ser excluída
    criacao = client.post('/tarefas', json={"titulo": "Tarefa Deletável"})
    tarefa_id = criacao.json()['id']
    
    # 3. Deletar usando o Header correto
    headers = {"Authorization": f"Bearer {token}"}
    resposta = client.delete(f'/tarefas/{tarefa_id}', headers=headers)
    assert resposta.status_code == 204
    assert resposta.text == ""


def test_ct18_deletar_tarefa_inexistente_com_token_valido():
    """
    Cenário: Token válido, mas o recurso não existe.
    Verifica se um usuário autenticado recebe HTTP 404 ao tentar apagar ID fantasma.
    """
    login_resp = client.post('/auth/login', data={'username': 'aluno', 'password': 'senha123'})
    token = login_resp.json()['access_token']
    
    headers = {"Authorization": f"Bearer {token}"}
    resposta = client.delete('/tarefas/99999', headers=headers)
    assert resposta.status_code == 404


def test_ct19_tarefa_deletada_nao_pode_ser_encontrada_depois():
    """
    Cenário: Após a deleção, o recurso não deve mais existir.
    Verifica se uma busca subsequente (GET) à exclusão resulta em HTTP 404.
    """
    login_resp = client.post('/auth/login', data={'username': 'aluno', 'password': 'senha123'})
    token = login_resp.json()['access_token']
    
    criacao = client.post('/tarefas', json={"titulo": "Tarefa Efemera"})
    tarefa_id = criacao.json()['id']
    
    headers = {"Authorization": f"Bearer {token}"}
    client.delete(f'/tarefas/{tarefa_id}', headers=headers)
    
    # Tentativa de busca
    busca = client.get(f'/tarefas/{tarefa_id}')
    assert busca.status_code == 404