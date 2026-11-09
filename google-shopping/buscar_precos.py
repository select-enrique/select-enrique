"""Uso:  python buscar_precos.py "LINK_DA_PLANILHA"

Lê os itens selecionados da aba Entrega e grava as ofertas mais baratas
do Google Shopping na aba "Google Shopping" da mesma planilha.
"""

import argparse
import sys

from precos.autenticacao import abrir_planilha, conectar_google_sheets
from precos.execucao import executar


def ler_argumentos():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("planilha", help="link (ou ID) da Google Sheets no template DDL")
    return parser.parse_args()


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # acentos no terminal do Windows
    argumentos = ler_argumentos()
    planilha = abrir_planilha(conectar_google_sheets(), argumentos.planilha)
    print(f"Planilha: {planilha.title}\n")
    executar(planilha)


if __name__ == "__main__":
    main()
