# Atividade-Testes-Automatizados-da-API-de-Tarefas

# Documentação da Suíte de Testes — API de Tarefas

## 1. Descrição

A suíte de testes desenvolvida cobre de forma abrangente todas as regras de negócio e restrições técnicas estabelecidas para a API de Tarefas, totalizando 19 casos de teste (CT-01 a CT-19). As validações foram divididas em cinco grandes módulos funcionais:

* **Autenticação (CT-01 a CT-03):** Garante que o endpoint `/auth/login` emita corretamente tokens do tipo `bearer` para credenciais preenchidas e rejeite requisições que omitam campos obrigatórios (`username` ou `password`) retornando o status esperado `422 Unprocessable Entity`.
* **Criar Tarefa (CT-04 a CT-09):** Valida os limites do modelo Pydantic (`TarefaCreate`). Testa o comportamento de campos opcionais (descrição nula), bloqueia títulos vazios ou que excedam o limite máximo de 200 caracteres, e assegura que, independentemente do payload enviado, o status padrão de inicialização seja estritamente `"pendente"`.
* **Listar Tarefas (CT-10 e CT-11):** Garante a consistência do repositório em dois estados cruciais — retornando uma lista vazia (`[]`) quando não há dados e listando corretamente os objetos após a criação de novos registros.
* **Buscar Tarefa por ID (CT-12 a CT-14):** Assegura que consultas a IDs existentes devolvam o objeto correto, que IDs inexistentes retornem `404 Not Found` e que entradas inválidas na URL (como strings alfanuméricas no lugar do ID inteiro) sejam interceptadas com `422`.
* **Deletar Tarefa (CT-15 a CT-19):** Valida a camada de segurança e controle de acesso da API. Garante o bloqueio `401 Unauthorized` para requisições anônimas ou com tokens corrompidos, valida a exclusão com sucesso (`204 No Content`) para usuários autenticados e certifica que o recurso deletado torna-se imediatamente inacessível para consultas subsequentes.

**Por que essas escolhas?** Esses cenários foram escolhidos para cobrir tanto o "caminho feliz" (fluxos de sucesso que o usuário espera) quanto os caminhos de exceção (erros de digitação, ataques sem token ou estouros de limite). Testar as respostas de erro garante que a API falhe de forma graciosa e segura, impedindo comportamentos imprevistos ou brechas de segurança.

---

## 2. Como Executar

Siga os passos abaixo para preparar o ambiente e rodar a suíte de testes localmente no Windows:

1. **Abra o terminal** na raiz do projeto (`Atividade-Testes-Automatizados-da-API-de-Tarefas`).
2. **Ative o seu ambiente virtual** (Venv):
   ```powershell
   .\venv\Scripts\activate
3. **Certifique-se de que todas as dependências estão devidamente instaladas executando**:
    ```powerShell
    pip install fastapi pytest passlib python-jose[cryptography] httpx
4. **Execute o comando do pytest** apontando para o arquivo de testes com os parâmetros de verbosidade:
    ```owerShell
    python -m pytest -v -s tests/test_api.py

## 3. Saída Esperada

Ao executar os comandos acima, a saída gerada pelo pytest no terminal deverá indicar o sucesso absoluto de todos os 19 casos coletados, conforme o log abaixo:

====================================================== test session starts ======================================================
platform win32 -- Python 3.14.3, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: C:\Users\jesus\Documents\Area_de_trabalho_nova\2026.1\BANCO DE DADOS\project\Atividade-Testes-Automatizados-da-API-de-Tarefas
configfile: pyproject.toml
plugins: anyio-4.13.0
collected 19 items

tests/test_api.py::test_ct01_login_valido PASSED                                                                           [  5%]
tests/test_api.py::test_ct02_login_sem_username PASSED                                                                     [ 10%]
tests/test_api.py::test_ct03_login_sem_password PASSED                                                                     [ 15%]
tests/test_api.py::test_ct04_criar_tarefa_com_dados_validos PASSED                                                         [ 21%]
tests/test_api.py::test_ct05_criar_tarefa_sem_descricao PASSED                                                             [ 26%]
tests/test_api.py::test_ct06_criar_tarefa_com_titulo_vazio PASSED                                                          [ 31%]
tests/test_api.py::test_ct07_criar_tarefa_sem_campo_titulo PASSED                                                          [ 36%]
tests/test_api.py::test_ct08_criar_tarefa_com_titulo_acima_do_limite PASSED                                                [ 42%]
tests/test_api.py::test_ct09_status_inicial_da_tarefa_criada PASSED                                                        [ 47%]
tests/test_api.py::test_ct10_listar_tarefas_com_repositorio_vazio PASSED                                                   [ 52%]
tests/test_api.py::test_ct11_listar_tarefas_apos_criacao PASSED                                                            [ 57%]
tests/test_api.py::test_ct12_buscar_tarefa_existente PASSED                                                                [ 63%]
tests/test_api.py::test_ct13_buscar_tarefa_com_id_inexistente PASSED                                                       [ 68%]
tests/test_api.py::test_ct14_buscar_tarefa_com_id_nao_numerico PASSED                                                      [ 73%]
tests/test_api.py::test_ct15_deletar_tarefa_sem_token PASSED                                                               [ 78%]
tests/test_api.py::test_ct16_deletar_tarefa_com_token_invalido PASSED                                                      [ 84%]
tests/test_api.py::test_ct17_deletar_tarefa_existente_com_token_valido PASSED                                              [ 89%]
tests/test_api.py::test_ct18_deletar_tarefa_inexistente_com_token_valido PASSED                                            [ 94%]
tests/test_api.py::test_ct19_tarefa_deletada_nao_pode_ser_encontrada_depois PASSED                                         [[100%]]

====================================================== 19 passed in 0.52s =======================================================

## 4. Dificuldades Encontradas

A principal dificuldade encontrada durante o desenvolvimento destes testes esteve relacionada ao isolamento do estado físico da API e à concorrência interna do ciclo de coleta de testes do pytest. Como os dados da aplicação estão estruturados de forma volátil dentro de um dicionário global em memória (_tarefas), as alterações realizadas por testes de escrita ou deleção geravam efeitos colaterais imediatos nos testes subsequentes, provocando falhas em cascata induzidas pela quebra de ordem cronológica. Se o caso de teste de listagem vazia rodasse após a criação de uma tarefa, ele falharia incorretamente por herdar lixo de memória.

Para solucionar esse problema técnico de forma elegante e garantir a independência mútua exigida pela atividade, foi estruturada uma fixture global no Pytest configurada com autouse=True. Essa função intercepta o ciclo de vida imediatamente anterior a cada caso de teste individual, realiza uma importação direta do escopo interno de módulos da aplicação (src.tarefas.app) e invoca comandos de limpeza forçada (.clear()) nas variáveis em memória RAM, reiniciando o ponteiro sequencial _proximo_id para 1. Adicionalmente, enfrentou-se um problema sintático pontual com operadores de atribuição por expressão (:=) durante a escrita rápida de asserts condicionais de status de rede, o qual foi mitigado simplificando a validação para asserções booleanas diretas padrão do ecossistema Python. Esse conjunto de processos garantiu um ambiente controlado e perfeitamente isolado para a validação precisa de cada cenário.