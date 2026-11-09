"""Estrutura fixa do template DDL. Só mude se o template mudar."""

ABA_ORIGEM      = "Entrega"
MAX_LINHAS_ATE_CABECALHO = 10        # o cabeçalho é procurado nas primeiras linhas da aba
ABA_DESTINO     = "Google Shopping"  # criada automaticamente se não existir

VALOR_NAO_SELECIONADO = "No"


class ColunaOrigem:
    """Cabeçalhos lidos da aba Entrega (localizados pelo nome, não pela letra)."""
    SELECIONADO = "Selecionado?"
    ITEM_ID     = "Item ID"
    ITEM_NAME   = "Item Name"
    SHOP_NAME   = "Shop Name"
    FINAL_PRICE = "Final Price"

    @classmethod
    def todas(cls):
        return [cls.SELECIONADO, cls.ITEM_ID, cls.ITEM_NAME, cls.SHOP_NAME, cls.FINAL_PRICE]


COLUNAS_DESTINO = [
    "Item ID", "Item Name", "Shop Name", "Final Price (Shopee)",
    "Posição", "Preço Google (R$)", "Loja", "Título do anúncio", "Link",
    "Status", "Atualizado em",
]


class Status:
    OK            = "OK"
    SEM_RESULTADO = "SEM RESULTADO"
    BLOQUEADO     = "BLOQUEADO (captcha)"
    PENDENTE      = "PENDENTE"   # não buscado porque o Google bloqueou antes
    ERRO          = "ERRO"
