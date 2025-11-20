# Gerador de Protótipos com Serendipidade

Aplicação multiagentes para criação de protótipos funcionais em HTML/JavaScript/Tailwind CSS.

## Arquitetura

**Backend:** FastAPI + OpenAI API  
**Frontend:** HTML + JavaScript + Tailwind CSS  
**Padrão:** Multiagentes com context propagation

## Estrutura de Arquivos

```
projeto/
├── .env                    # Configurações (API keys)
├── app.py                  # Backend FastAPI
├── requirements.txt        # Dependências Python
├── templates/
│   └── default.html       # Frontend
```

## Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar .env

Edite o arquivo `.env` e insira sua OpenAI API key:

```bash
OPENAI_API_KEY=sk-proj-sua-chave-aqui
HOST=127.0.0.1
PORT=8000
```

### 3. Executar aplicação

```bash
# Opção 1: Diretamente
python app.py

# Opção 2: Via uvicorn
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### 4. Acessar no navegador

```
Interface: http://127.0.0.1:8000
Docs API: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
```

## Arquitetura FastAPI

### Endpoints

**GET /**
- Renderiza interface principal
- Template: `templates/default.html`

**POST /api/process-agent**
- Processa requisição de agente específico
- Body:
```json
{
  "agent_id": "discovery",
  "user_input": "Descrição da ideia",
  "context": "Contexto acumulado"
}
```
- Response:
```json
{
  "success": true,
  "response": "Resposta do agente",
  "agent_name": "Nome do Agente"
}
```

**GET /api/agents**
- Lista todos agentes disponíveis
- Response: Array de objetos com `id` e `name`

### Modelos Pydantic

**ProcessAgentRequest:**
- `agent_id`: str (obrigatório)
- `user_input`: str (opcional)
- `context`: str (opcional)

**AgentResponse:**
- `success`: bool
- `response`: str | None
- `agent_name`: str | None
- `error`: str | None

## Agentes Disponíveis

### 1. Discovery (Descoberta & Serendipidade)
- Temperature: 0.9
- Max Tokens: 1500
- Função: Análise serendípita da ideia

### 2. Structure (Arquitetura & Estrutura)
- Temperature: 0.7
- Max Tokens: 1500
- Função: Definição de arquitetura técnica

### 3. Design (Design & Experiência)
- Temperature: 0.7
- Max Tokens: 1500
- Função: Proposta visual e UX

### 4. Implementation (Implementação)
- Temperature: 0.7
- Max Tokens: 4000
- Função: Geração de código HTML/JS/Tailwind

### 5. Refinement (Refinamento)
- Temperature: 0.7
- Max Tokens: 4000
- Função: Otimização e acessibilidade

## Vantagens do FastAPI

✅ **Performance superior** - Baseado em Starlette (async)  
✅ **Documentação automática** - Swagger UI e ReDoc  
✅ **Validação de dados** - Via Pydantic  
✅ **Type hints nativos** - Melhor IDE support  
✅ **Async/await** - Suporte nativo a operações assíncronas  
✅ **Padrões modernos** - OpenAPI 3.0, JSON Schema  

## Diferenças Flask → FastAPI

| Aspecto | Flask | FastAPI |
|---------|-------|---------|
| Port padrão | 5000 | 8000 |
| Decorador rota | `@app.route()` | `@app.get()` / `@app.post()` |
| Templates | `render_template()` | `templates.TemplateResponse()` |
| Request body | `request.json` | `Pydantic model` |
| Response | `jsonify()` | Return dict direto |
| Docs | Manual | Automático (/docs) |
| Async | Via extensões | Nativo |

## Fluxo de Operação

1. Usuário descreve ideia inicial
2. Agent Discovery analisa e sugere direções serendípitas
3. Agent Structure define arquitetura técnica
4. Agent Design cria proposta visual
5. Agent Implementation gera código HTML funcional
6. Agent Refinement otimiza código final
7. Download imediato do protótipo pronto

## Características Técnicas

- Single-file HTML output com Tailwind CDN
- Sem dependências de localStorage/sessionStorage
- Context propagation entre agentes
- Temperature diferenciada por especialização
- Validação automática com Pydantic
- Documentação interativa (Swagger)
- Hot reload em desenvolvimento

## Requisitos

- Python 3.8+
- OpenAI API key ativa
- Navegador moderno (Chrome/Firefox/Safari)

## Troubleshooting

**Erro: "OpenAI não inicializada"**
- Verifique se o arquivo `.env` existe
- Confirme que `OPENAI_API_KEY` está preenchida
- API key deve começar com `sk-proj-` ou `sk-`

**Erro: "Port already in use"**
- Altere a porta no `.env`: `PORT=8001`
- Ou mate o processo: `lsof -ti:8000 | xargs kill -9` (Mac/Linux)

**Erro: "Template not found"**
- Certifique-se que existe pasta `templates/`
- Arquivo `default.html` deve estar dentro de `templates/`

## Documentação Interativa

Acesse `http://127.0.0.1:8000/docs` para:
- Testar endpoints diretamente
- Ver schemas de request/response
- Gerar código cliente
- Exportar OpenAPI spec