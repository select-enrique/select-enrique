"""Login na conta Google pelo navegador (OAuth)."""

from pathlib import Path

import gspread

PASTA_PROJETO     = Path(__file__).resolve().parent.parent
ARQUIVO_CREDENCIAIS = PASTA_PROJETO / "credentials.json"   # baixado do Google Cloud (ver README)
ARQUIVO_TOKEN       = PASTA_PROJETO / "token.json"         # criado sozinho no 1º login


def conectar_google_sheets():
    """Na 1ª vez abre o navegador para login; depois reutiliza o token salvo."""
    if not ARQUIVO_CREDENCIAIS.exists():
        raise FileNotFoundError(
            f"Arquivo '{ARQUIVO_CREDENCIAIS.name}' não encontrado em {PASTA_PROJETO}.\n"
            "Siga o passo 'Configuração do login' no README.")
    return gspread.oauth(credentials_filename=str(ARQUIVO_CREDENCIAIS),
                         authorized_user_filename=str(ARQUIVO_TOKEN))


def abrir_planilha(cliente, url_ou_id):
    if url_ou_id.startswith("http"):
        return cliente.open_by_url(url_ou_id)
    return cliente.open_by_key(url_ou_id)
