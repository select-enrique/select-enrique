# Google Shopping – 3 ofertas mais baratas (template DDL)

Notebook do Google Colab que lê os itens **selecionados** da aba **Entrega** do template DDL, busca cada um no **Google Shopping (Brasil)** e grava as **3 ofertas mais baratas** numa aba nova, **Google Shopping**, na mesma planilha.

## Como usar
1. Abra `google_shopping_mais_baratos.ipynb` no [Google Colab](https://colab.research.google.com) (Arquivo → Fazer upload de notebook).
2. Na célula **⚙️ Configuração**, cole o link da planilha (cada campanha tem um link diferente, mas o template é o mesmo).
3. **Ambiente de execução → Executar tudo** e autorize sua conta Google.

## Regras
- Busca as linhas com `Selecionado?` preenchido e diferente de `No`.
- Variações com o mesmo `Item ID` são buscadas uma única vez, usando o `Item Name`.
- As colunas são localizadas pelo **nome do cabeçalho** (linha 4), não pela letra. Se o template mudar, ajuste só a célula "Estrutura do template".
- A aba **Entrega** não é alterada.

## Resultado (aba `Google Shopping`)
| Item ID | Item Name | Shop Name | Final Price (Shopee) | Posição | Preço Google (R$) | Loja | Título do anúncio | Link | Status | Atualizado em |
|---|---|---|---|---|---|---|---|---|---|---|

## Organização do código
| Célula | Responsabilidade |
|---|---|
| Configuração | Único lugar que o usuário altera |
| Estrutura do template | Nomes de abas, colunas e status |
| Modelos de dados | `Item`, `Oferta`, `ResultadoBusca` |
| Planilha | Ler itens selecionados e gravar resultado |
| Busca | Abrir o Google Shopping e extrair ofertas |
| Orquestração | Juntar tudo, pular itens concluídos e tratar o captcha |

## Limitações
- É raspagem direta: o Google pode pedir **captcha**. A busca para e os itens restantes ficam `PENDENTE`. Rode de novo mais tarde; os itens `OK` são mantidos.
- Se o Google mudar o layout, pode ser preciso ajustar `JS_EXTRAIR_CARDS`.
- Alguns links são do próprio Google (anúncio ou página do produto) e redirecionam para a loja.
- Nomes muito longos da Shopee podem reduzir os resultados. Se aparecer muito `SEM RESULTADO`, teste `FILTRAR_TITULO = False`.
