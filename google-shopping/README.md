# Google Shopping – 3 ofertas mais baratas (template DDL)

Script Python que lê os itens **selecionados** da aba **Entrega** do template DDL, busca cada um no **Google Shopping (Brasil)** e grava as **3 ofertas mais baratas** na aba **Google Shopping** da mesma planilha.

```
python buscar_precos.py "https://docs.google.com/spreadsheets/d/.../edit"
```

---

## 1. Instalação (uma vez por computador)

1. Instale o **Python 3.10+** em [python.org](https://www.python.org/downloads/). No Windows, marque **"Add Python to PATH"**.
2. Abra a pasta `google-shopping` no **VS Code** (Arquivo → Abrir Pasta).
3. Abra o terminal (**Terminal → Novo Terminal**) e rode:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
playwright install chromium
```

## 2. Configuração do login (uma vez por time)

O script entra na planilha com a **sua conta Google**. Para isso, ele precisa de um arquivo `credentials.json`. Uma pessoa cria esse arquivo e passa para o time:

1. Acesse [console.cloud.google.com](https://console.cloud.google.com) e crie um projeto (ex.: `precos-google-shopping`).
2. **APIs e serviços → Biblioteca**: ative **Google Sheets API** e **Google Drive API**.
3. **APIs e serviços → Tela de consentimento OAuth**:
   - Tipo **Interno**, se a empresa usa Google Workspace. Se não, **Externo**.
   - Preencha nome do app e e-mail.
   - Se escolheu **Externo**, adicione em **Usuários de teste** o e-mail de cada pessoa que vai usar.
4. **APIs e serviços → Credenciais → Criar credenciais → ID do cliente OAuth**:
   - Tipo de aplicativo: **App para computador**.
   - Clique em **Baixar JSON**.
5. Renomeie o arquivo para **`credentials.json`** e coloque-o dentro da pasta `google-shopping`.

> Na 1ª execução, o navegador abre pedindo login no Google. Depois disso, o script salva um `token.json` e não pede mais.
> `credentials.json` e `token.json` estão no `.gitignore`. **Não envie esses arquivos para o GitHub.**

## 3. Uso

1. Na planilha, marque em `Selecionado?` os itens que quer buscar (qualquer valor diferente de `No`). No primeiro teste, use 3 a 5 itens.
2. No terminal do VS Code, com o `.venv` ativo:

```bash
python buscar_precos.py "LINK_DA_PLANILHA"
```

3. Uma janela do Chrome abre e faz as buscas. **Se aparecer captcha, resolva na janela**: a busca continua sozinha (você tem até 5 minutos).
4. No final, confira a aba **Google Shopping** na planilha.

Rodando de novo, os itens já `OK` são mantidos e só os pendentes são buscados.

## Resultado (aba `Google Shopping`)
| Item ID | Item Name | Shop Name | Final Price (Shopee) | Posição | Preço Google (R$) | Loja | Título do anúncio | Link | Status | Atualizado em |
|---|---|---|---|---|---|---|---|---|---|---|

| Status | Significado |
|---|---|
| `OK` | Ofertas encontradas |
| `SEM RESULTADO` | Nenhuma oferta (ou nenhuma passou no filtro de título) |
| `BLOQUEADO (captcha)` | Captcha não resolvido a tempo |
| `PENDENTE` | Não foi buscado por causa do bloqueio. Rode de novo mais tarde |
| `ERRO: ...` | Falha inesperada ao carregar a página |

## Ajustes (`precos/config.py`)
| Opção | Padrão | Para que serve |
|---|---|---|
| `QTD_OFERTAS` | 3 | Quantas ofertas trazer |
| `FILTRAR_TITULO` | True | Descarta anúncios que não batem com o nome do item. Desligue se vier muito `SEM RESULTADO` |
| `MOSTRAR_NAVEGADOR` | True | Mostra o Chrome (permite resolver o captcha) |
| `PAUSA_ENTRE_BUSCAS_SEG` | (4, 9) | Pausa entre buscas |

## Organização do código
| Arquivo | Responsabilidade |
|---|---|
| `buscar_precos.py` | Ponto de entrada (linha de comando) |
| `precos/config.py` | Ajustes de comportamento |
| `precos/template.py` | Nomes de abas, colunas e status do template |
| `precos/modelos.py` | `Item`, `Oferta`, `ResultadoBusca` |
| `precos/autenticacao.py` | Login Google e abertura da planilha |
| `precos/planilha.py` | Ler itens selecionados e gravar o resultado |
| `precos/busca.py` | Pesquisar no Google Shopping e extrair ofertas |
| `precos/execucao.py` | Juntar tudo, pular itens concluídos e tratar o captcha |

## Problemas comuns
- **`credentials.json não encontrado`**: veja a seção 2.
- **`Coluna(s) não encontrada(s)`**: a planilha não segue o template (aba `Entrega`, cabeçalho na linha 4).
- **`403` / sem permissão**: a conta usada no login não tem acesso de edição à planilha.
- **`Acesso bloqueado: app não verificado`**: adicione seu e-mail em **Usuários de teste** (seção 2, passo 3).
