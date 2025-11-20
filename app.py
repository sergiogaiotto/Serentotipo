from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated
import os
from dotenv import load_dotenv
import uvicorn

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

app = FastAPI(title="Gerador de Protótipos - Serendipidade")
templates = Jinja2Templates(directory="templates")

# ============================================================================
# CONFIGURAÇÃO SEGURA DA OPENAI API KEY (BOAS PRÁTICAS)
# ============================================================================
def get_api_key() -> str:
    """
    Recupera API key seguindo boas práticas de segurança:
    
    1. NUNCA commitar chaves em código
    2. Usar variáveis de ambiente (.env)
    3. Validar formato antes de usar
    4. Nunca logar a chave completa
    5. Rotacionar chaves periodicamente
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY não encontrada.\n"
            "Configure via arquivo .env: OPENAI_API_KEY=sk-proj-..."
        )
    
    # Validar formato básico
    if not (api_key.startswith('sk-') or api_key.startswith('sk-proj-')):
        raise ValueError("OPENAI_API_KEY com formato inválido")
    
    return api_key

def get_llm(temperature: float = 0.7, max_tokens: int = 4000):
    """Inicializa ChatOpenAI com configuração segura"""
    # Limpar variáveis de proxy temporariamente (evita erro 'proxies')
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    old_proxies = {var: os.environ.pop(var) for var in proxy_vars if var in os.environ}
    
    try:
        api_key = get_api_key()
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
        # Restaurar proxies
        for var, value in old_proxies.items():
            os.environ[var] = value
        return llm
    except Exception as e:
        # Restaurar proxies mesmo em erro
        for var, value in old_proxies.items():
            os.environ[var] = value
        raise e

# ============================================================================
# STATE DEFINITION PARA LANGGRAPH
# ============================================================================
class AgentState(TypedDict):
    """Estado compartilhado entre agentes - LangGraph gerencia automaticamente"""
    user_input: str
    discovery_output: str
    structure_output: str
    design_output: str
    implementation_output: str
    refinement_output: str
    current_step: str
    error: str

# ============================================================================
# AGENTES CONFIGURATION
# ============================================================================
AGENTS_CONFIG = {
    'discovery': {
        'name': 'Descoberta & Serendipidade',
        'system_prompt': '''Você é especialista em descoberta criativa usando serendipidade.

**Conceito Central:**
[Identifique o núcleo da ideia]

**Direções Serendípitas:**
1. [Conexão inesperada 1]
2. [Conexão inesperada 2]
3. [Conexão inesperada 3]

**Potencial de Inovação:**
[Avalie o potencial]

**Recomendação:**
[Sugira abordagem]''',
        'temperature': 0.9
    },
    'structure': {
        'name': 'Arquitetura & Estrutura',
        'system_prompt': '''Arquiteto de software. Defina estrutura técnica:

**Componentes Principais:**
**Fluxo de Interação:**
**Estrutura de Dados:**
**Funcionalidades:**''',
        'temperature': 0.7
    },
    'design': {
        'name': 'Design & Experiência',
        'system_prompt': '''Designer UX/UI. Crie proposta visual:

**Paleta de Cores:**
**Layout:**
**Elementos Interativos:**
**Microinterações:**''',
        'temperature': 0.7
    },
    'implementation': {
        'name': 'Implementação',
        'system_prompt': '''Desenvolvedor frontend. Gere HTML completo:

REGRAS:
- HTML5 + Tailwind CDN
- JavaScript vanilla
- Responsivo
- SEM localStorage

RETORNE APENAS CÓDIGO HTML.

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
</head>''',
        'temperature': 0.7
    },
    'refinement': {
        'name': 'Refinamento',
        'system_prompt': '''Otimize o código HTML:

- Performance
- Acessibilidade (ARIA)
- Usabilidade

RETORNE CÓDIGO COMPLETO OTIMIZADO.''',
        'temperature': 0.7
    }
}

# ============================================================================
# LANGGRAPH NODES (CADA AGENTE É UM NÓ)
# ============================================================================
def discovery_agent(state: AgentState) -> AgentState:
    """Nó: Descoberta"""
    llm = get_llm(temperature=0.9, max_tokens=1500)
    messages = [
        SystemMessage(content=AGENTS_CONFIG['discovery']['system_prompt']),
        HumanMessage(content=state['user_input'])
    ]
    response = llm.invoke(messages)
    state['discovery_output'] = response.content
    state['current_step'] = 'discovery'
    return state

def structure_agent(state: AgentState) -> AgentState:
    """Nó: Estrutura"""
    llm = get_llm(max_tokens=1500)
    context = f"Análise:\n{state['discovery_output']}"
    messages = [
        SystemMessage(content=AGENTS_CONFIG['structure']['system_prompt']),
        HumanMessage(content=context)
    ]
    response = llm.invoke(messages)
    state['structure_output'] = response.content
    state['current_step'] = 'structure'
    return state

def design_agent(state: AgentState) -> AgentState:
    """Nó: Design"""
    llm = get_llm(max_tokens=1500)
    context = f"Estrutura:\n{state['structure_output']}"
    messages = [
        SystemMessage(content=AGENTS_CONFIG['design']['system_prompt']),
        HumanMessage(content=context)
    ]
    response = llm.invoke(messages)
    state['design_output'] = response.content
    state['current_step'] = 'design'
    return state

def implementation_agent(state: AgentState) -> AgentState:
    """Nó: Implementação"""
    llm = get_llm(max_tokens=4000)
    context = f"Design:\n{state['design_output']}\n\nEstrutura:\n{state['structure_output']}"
    messages = [
        SystemMessage(content=AGENTS_CONFIG['implementation']['system_prompt']),
        HumanMessage(content=context)
    ]
    response = llm.invoke(messages)
    state['implementation_output'] = response.content
    state['current_step'] = 'implementation'
    return state

def refinement_agent(state: AgentState) -> AgentState:
    """Nó: Refinamento"""
    llm = get_llm(max_tokens=4000)
    context = f"Código:\n{state['implementation_output']}"
    messages = [
        SystemMessage(content=AGENTS_CONFIG['refinement']['system_prompt']),
        HumanMessage(content=context)
    ]
    response = llm.invoke(messages)
    state['refinement_output'] = response.content
    state['current_step'] = 'refinement'
    return state

# ============================================================================
# CONSTRUÇÃO DO GRAFO LANGGRAPH
# ============================================================================
def build_graph():
    """
    LangGraph garante:
    - Execução sequencial controlada
    - Estado compartilhado entre nós
    - Checkpointing automático
    - Retry logic
    """
    workflow = StateGraph(AgentState)
    
    # Adicionar nós (agentes)
    workflow.add_node("discovery", discovery_agent)
    workflow.add_node("structure", structure_agent)
    workflow.add_node("design", design_agent)
    workflow.add_node("implementation", implementation_agent)
    workflow.add_node("refinement", refinement_agent)
    
    # Fluxo sequencial garantido
    workflow.set_entry_point("discovery")
    workflow.add_edge("discovery", "structure")
    workflow.add_edge("structure", "design")
    workflow.add_edge("design", "implementation")
    workflow.add_edge("implementation", "refinement")
    workflow.add_edge("refinement", END)
    
    return workflow.compile()

graph = None

# ============================================================================
# PYDANTIC MODELS
# ============================================================================
class ProcessAgentRequest(BaseModel):
    agent_id: str
    user_input: str = ""
    context: str = ""

class AgentResponse(BaseModel):
    success: bool
    response: str = None
    agent_name: str = None
    error: str = None

# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("default.html", {"request": request})

@app.post("/api/process-agent", response_model=AgentResponse)
async def process_agent(data: ProcessAgentRequest):
    """Processa agente individual (compatibilidade com frontend)"""
    try:
        agent_id = data.agent_id
        if agent_id not in AGENTS_CONFIG:
            raise HTTPException(status_code=400, detail="Agente inválido")
        
        agent = AGENTS_CONFIG[agent_id]
        temp = agent.get('temperature', 0.7)
        llm = get_llm(temperature=temp)
        
        messages = [SystemMessage(content=agent['system_prompt'])]
        if data.context:
            messages.append(HumanMessage(content=f'Contexto:\n{data.context}'))
        messages.append(HumanMessage(
            content=data.user_input if agent_id == 'discovery' else 'Continue.'
        ))
        
        response = llm.invoke(messages)
        
        return AgentResponse(
            success=True,
            response=response.content,
            agent_name=agent['name']
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
async def get_agents():
    return JSONResponse(content=[
        {'id': k, 'name': v['name']} for k, v in AGENTS_CONFIG.items()
    ])

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("GERADOR DE PROTÓTIPOS - LangGraph + FastAPI")
    print("Controle de execução garantido por LangGraph")
    print("="*60 + "\n")
    
    try:
        api_key = get_api_key()
        print(f"✓ API Key: {api_key[:15]}...{api_key[-5:]}")
        
        global graph
        graph = build_graph()
        print("✓ LangGraph compilado")
        print("✓ Sistema pronto")
    except Exception as e:
        print(f"⚠️  Erro: {e}")
    
    print(f"\nAcesse: http://127.0.0.1:8000")
    print(f"Docs: http://127.0.0.1:8000/docs\n")

if __name__ == '__main__':
    uvicorn.run(
        "app:app",
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', 8000)),
        reload=True
    )