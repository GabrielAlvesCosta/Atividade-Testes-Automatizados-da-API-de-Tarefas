from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse 
from fastapi.security import OAuth2PasswordRequestForm
from .modelos import TarefaCreate, TarefaResponse, StatusTarefa
from .auth import verificar_token, criar_token

app = FastAPI(title='API de Tarefas')

@app.get('/', include_in_schema=False)
def raiz():
    return RedirectResponse(url='/docs')

_tarefas: dict[int, dict] = {}

_proximo_id = 1

@app.post('/auth/login', tags=['auth'])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = criar_token({'sub': form_data.username, 'role': 'user'})
    return {'access_token': token, 'token_type': 'bearer'}

@app.get('/tarefas', response_model=list[TarefaResponse], tags=['tarefas'])
def listar_tarefas():
    return list(_tarefas.values())

@app.post('/tarefas', response_model=TarefaResponse, status_code=201, tags=['tarefas'])
def criar_tarefa(tarefa: TarefaCreate):
    global _proximo_id
    nova = {
        'id': _proximo_id,
        'titulo': tarefa.titulo,
        'descricao': tarefa.descricao,
        'status': StatusTarefa.pendente
    }
    _tarefas[_proximo_id] = nova
    _proximo_id += 1
    return nova

@app.get('/tarefas/{tarefa_id}', response_model=TarefaResponse, tags=['tarefas'])
def buscar_tarefa(tarefa_id: int):
    if tarefa_id not in _tarefas:
        raise HTTPException(status_code=404, detail='Tarefa não encontrada')
    return _tarefas[tarefa_id]

@app.delete('/tarefas/{tarefa_id}', status_code=204, tags=['tarefas'])
def deletar_tarefa(tarefa_id: int, usuario=Depends(verificar_token)):
    if tarefa_id not in _tarefas:
        raise HTTPException(status_code=404, detail='Tarefa não encontrada')
    del _tarefas[tarefa_id]