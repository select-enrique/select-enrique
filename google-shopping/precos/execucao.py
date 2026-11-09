"""Orquestra a leitura da planilha, a busca e a gravação do resultado."""

import random
import time

from playwright.sync_api import sync_playwright

from .busca import USER_AGENT, BloqueioDoGoogle, buscar_item
from .config import (FILTRAR_TITULO, MOSTRAR_NAVEGADOR, PAUSA_ENTRE_BUSCAS_SEG,
                     PULAR_JA_CONCLUIDOS, QTD_OFERTAS)
from .modelos import ResultadoBusca
from .planilha import (gravar_resultados, ler_itens_selecionados, ler_linhas_concluidas,
                       obter_aba_destino, resultado_para_linhas)
from .template import ABA_DESTINO, Status


def abrir_navegador(playwright):
    navegador = playwright.chromium.launch(
        headless=not MOSTRAR_NAVEGADOR, args=["--disable-blink-features=AutomationControlled"])
    contexto = navegador.new_context(
        locale="pt-BR", user_agent=USER_AGENT, viewport={"width": 1366, "height": 900})
    return navegador, contexto.new_page()


def buscar_todos(itens):
    """Busca item a item. Se o Google bloquear, os restantes ficam PENDENTES."""
    resultados = []
    with sync_playwright() as playwright:
        navegador, pagina = abrir_navegador(playwright)
        for posicao, item in enumerate(itens, start=1):
            try:
                resultado = buscar_item(pagina, item, QTD_OFERTAS, FILTRAR_TITULO)
            except BloqueioDoGoogle:
                resultados.append(ResultadoBusca(item, Status.BLOQUEADO))
                resultados += [ResultadoBusca(i, Status.PENDENTE) for i in itens[posicao:]]
                print(f"Google bloqueou na busca {posicao}. Espere alguns minutos e rode de novo.")
                break
            resultados.append(resultado)
            print(f"[{posicao}/{len(itens)}] {resultado.status:<14} {item.nome[:70]}")
            time.sleep(random.uniform(*PAUSA_ENTRE_BUSCAS_SEG))
        navegador.close()
    return resultados


def ordenar_como_na_origem(linhas, itens):
    ordem = {item.item_id: i for i, item in enumerate(itens)}
    return sorted(linhas, key=lambda l: (ordem.get(str(l[0]), len(ordem)), str(l[4])))


def separar_pendentes(itens, aba_destino):
    """Devolve (linhas já concluídas a manter, itens que ainda precisam de busca)."""
    if not PULAR_JA_CONCLUIDOS:
        return [], itens
    ids_selecionados = {item.item_id for item in itens}
    mantidas = [l for l in ler_linhas_concluidas(aba_destino) if str(l[0]) in ids_selecionados]
    ids_concluidos = {str(l[0]) for l in mantidas}
    return mantidas, [item for item in itens if item.item_id not in ids_concluidos]


def executar(planilha):
    itens = ler_itens_selecionados(planilha)
    aba_destino = obter_aba_destino(planilha)
    linhas_mantidas, pendentes = separar_pendentes(itens, aba_destino)

    print(f"{len(itens)} itens selecionados | {len(itens) - len(pendentes)} já concluídos | "
          f"{len(pendentes)} para buscar\n")
    resultados = buscar_todos(pendentes)

    linhas_novas = [linha for r in resultados for linha in resultado_para_linhas(r)]
    gravar_resultados(aba_destino, ordenar_como_na_origem(linhas_mantidas + linhas_novas, itens))
    print(f"\nPronto! Resultado gravado na aba '{ABA_DESTINO}'.")
