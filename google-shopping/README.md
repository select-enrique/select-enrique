# Google Shopping – 3 ofertas mais baratas

Notebook do Google Colab que lê uma lista de itens numa **Google Sheets**, busca cada item no **Google Shopping (Brasil)** e grava as **3 ofertas mais baratas** de cada um numa aba `Resultados`.

## Como usar
1. Abra `google_shopping_mais_baratos.ipynb` no [Google Colab](https://colab.research.google.com) (Arquivo → Fazer upload de notebook, ou abrir direto do GitHub).
2. Na planilha, crie uma aba `Itens` com o cabeçalho `Item` e um nome de produto por linha (ex.: `Kit Principia Essencial`).
3. Na célula **⚙️ Configuração**, cole o link da planilha.
4. **Ambiente de execução → Executar tudo** e autorize sua conta Google.

## Resultado (aba `Resultados`)
| Item | Posição | Preço (R$) | Loja | Título do anúncio | Link | Status |
|---|---|---|---|---|---|---|

## Limitações
- É raspagem direta: o Google pode mostrar **captcha** após muitas buscas. O item fica `BLOQUEADO`; espere alguns minutos e rode a célula 4 de novo (itens já `OK` são pulados).
- Se o Google mudar o layout da página, a extração pode precisar de ajuste (função `EXTRAIR_JS`).
- Alguns links podem ser do próprio Google (anúncio ou página do produto), que redirecionam para a loja.
- `FILTRAR_TITULO = True` descarta anúncios cujo título não contém a maioria das palavras do item (evita produtos errados). Desligue se estiver vindo `SEM RESULTADO` demais.
