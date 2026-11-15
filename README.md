# API Fila de Atendimento

API feita com FastAPI para o totem de uma fila de atendimento presencial.

## Como rodar

1. Criar o ambiente virtual: `python -m venv venv`
2. Ativar (Windows PowerShell): `venv\Scripts\Activate.ps1`
3. Instalar as dependências: `pip install -r requirements.txt`
4. Rodar: `uvicorn main:app --reload`
5. Abrir a documentação: http://127.0.0.1:8000/docs

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | /fila | Lista os clientes não atendidos |
| GET | /fila/{id} | Busca o cliente pela posição |
| POST | /fila | Adiciona um cliente (nome até 20 caracteres, tipo N ou P) |
| PUT | /fila | Avança a fila (-1 posição) |
| DELETE | /fila/{id} | Remove o cliente da posição |

Autor: [Wellington Alves Da Silva Junior]