# 🧵 Estoque de Tecido

Painel em Streamlit para acompanhar o estoque de tecidos de uma confecção de jeans e registrar a baixa de metros a cada corte.

## O que faz
Painel com visual de app financeiro: menu azul na lateral, cartões brancos e barra de filtros no topo (categoria, busca e filtros avançados com fornecedor e limites de status).

- **Visão geral:** indicadores (em estoque, a chegar, projetado, usado e saúde do estoque), metros por fornecedor em barras empilhadas (usado, em estoque e a chegar), rosca com seletor (em estoque, a chegar ou usado), lista de atenção e maiores pedidos a chegar.
- **Artigos:** todos os artigos em tabela, com barras em cada coluna de metros (em estoque, a chegar, usado), % do limite usado, status colorido, agrupamento por artigo ou fornecedor e download em CSV. A visualização **Barras** mostra todos os artigos em barras horizontais: consumo do limite ou metros por artigo.
- **Baixas:** formulário para registrar baixa por corte (com aviso quando passa do saldo), baixas dos últimos 14 dias e últimas movimentações.
- **Qualidade dos dados:** saldos negativos, fornecedores deduzidos e baixas sem data.

## Como rodar
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura
| Arquivo | Função |
|---|---|
| `app.py` | Interface (Streamlit + Plotly), páginas e tema |
| `.streamlit/config.toml` | Cores do tema (azul e branco) |
| `logo.svg` | Logo do menu |
| `dados.py` | Leitura, cálculo de saldo/status e gravação das baixas |
| `base_estoque_tecido.xlsx` | Base de dados (abas `Artigos` e `Baixas`) |
| `baixas_registradas.csv` | Criado pelo app ao registrar novas baixas |

Saldo = `Estoque_Mts` (total recebido) − soma das baixas. Os limites de status (padrão 300 m e 1.000 m) ficam em Filtros, no topo.
A nota de saúde dá peso 100% aos artigos OK, 60% a Atenção, 25% a Crítico e 0% a Negativo.

## Próximos passos
- Trocar o CSV por Firebase/Firestore para vários usuários registrarem baixas ao mesmo tempo. Basta reescrever `carregar_baixas` e `registrar_baixa` em `dados.py`.
- Evolução do consumo no tempo, quando as baixas tiverem data.
- Autenticação simples para quem pode registrar baixa.

> Os dados do exemplo devem ser anonimizados antes de publicar o repositório.
