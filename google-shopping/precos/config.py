"""Ajustes de comportamento. Mude aqui se precisar."""

QTD_OFERTAS            = 3       # quantas ofertas mais baratas trazer por item
FILTRAR_TITULO         = True    # descarta anúncios cujo título não tem a maioria das palavras do item
PULAR_JA_CONCLUIDOS    = True    # não refaz itens que já estão OK na aba de resultado
PAUSA_ENTRE_BUSCAS_SEG = (4, 9)  # pausa aleatória (mín, máx) entre buscas – reduz risco de captcha
MOSTRAR_NAVEGADOR      = True    # True: abre o Chrome na tela e permite resolver o captcha
ESPERA_MAX_CAPTCHA_SEG = 300     # tempo para você resolver o captcha antes de desistir
