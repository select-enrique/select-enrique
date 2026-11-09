"""Leitura dos itens na aba Entrega e gravação do resultado."""

from datetime import datetime

import gspread

from .modelos import Item
from .template import (ABA_DESTINO, ABA_ORIGEM, COLUNAS_DESTINO, LINHA_CABECALHO,
                       VALOR_NAO_SELECIONADO, ColunaOrigem, Status)


def localizar_colunas(cabecalho, nomes):
    """Devolve {nome: índice} e avisa claramente se alguma coluna sumiu do template."""
    cabecalho_limpo = [c.strip() for c in cabecalho]
    faltando = [n for n in nomes if n not in cabecalho_limpo]
    if faltando:
        raise ValueError(f"Coluna(s) não encontrada(s) na linha {LINHA_CABECALHO} da aba "
                         f"'{ABA_ORIGEM}': {faltando}")
    return {n: cabecalho_limpo.index(n) for n in nomes}


def texto_para_numero(texto):
    """'1,234.56' -> 1234.56. Se não for número, devolve o texto original."""
    try:
        return float(texto.replace(",", ""))
    except ValueError:
        return texto.strip()


def esta_selecionado(valor):
    valor = valor.strip()
    return bool(valor) and valor != VALOR_NAO_SELECIONADO


def ler_itens_selecionados(planilha):
    """Itens com 'Selecionado?' preenchido e diferente de 'No', sem repetir Item ID."""
    linhas = planilha.worksheet(ABA_ORIGEM).get_values()
    cabecalho, dados = linhas[LINHA_CABECALHO - 1], linhas[LINHA_CABECALHO:]
    col = localizar_colunas(cabecalho, ColunaOrigem.todas())

    itens = {}
    for linha in dados:
        linha = linha + [""] * (len(cabecalho) - len(linha))
        item_id = linha[col[ColunaOrigem.ITEM_ID]].strip()
        if item_id and item_id not in itens and esta_selecionado(linha[col[ColunaOrigem.SELECIONADO]]):
            itens[item_id] = Item(
                item_id=item_id,
                nome=linha[col[ColunaOrigem.ITEM_NAME]].strip(),
                loja_shopee=linha[col[ColunaOrigem.SHOP_NAME]].strip(),
                preco_shopee=texto_para_numero(linha[col[ColunaOrigem.FINAL_PRICE]]),
            )
    return list(itens.values())


def obter_aba_destino(planilha):
    try:
        return planilha.worksheet(ABA_DESTINO)
    except gspread.WorksheetNotFound:
        return planilha.add_worksheet(ABA_DESTINO, rows=1000, cols=len(COLUNAS_DESTINO))


def ler_linhas_concluidas(aba_destino):
    """Linhas de execuções anteriores cujo item terminou com status OK."""
    linhas = aba_destino.get_values(value_render_option="UNFORMATTED_VALUE")[1:]
    i_status = COLUNAS_DESTINO.index("Status")
    return [l for l in linhas if len(l) > i_status and l[i_status] == Status.OK]


def resultado_para_linhas(resultado):
    """Uma linha por oferta; se não houver oferta, uma linha só com o status."""
    item = resultado.item
    base = [item.item_id, item.nome, item.loja_shopee, item.preco_shopee]
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    if not resultado.ofertas:
        return [base + ["", "", "", "", "", resultado.status, agora]]
    return [base + [pos, o.preco, o.loja, o.titulo, o.link, resultado.status, agora]
            for pos, o in enumerate(resultado.ofertas, start=1)]


def gravar_resultados(aba_destino, linhas):
    aba_destino.clear()
    # RAW mantém o Item ID como texto (sem virar notação científica)
    aba_destino.update([COLUNAS_DESTINO] + linhas, value_input_option="RAW")
    aba_destino.format("A1:K1", {"textFormat": {"bold": True}})
    aba_destino.freeze(rows=1)
