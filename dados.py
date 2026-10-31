"""Camada de dados do app.

Hoje lê de um Excel e grava as novas baixas em um CSV. Para trocar por Firebase
(ou outro banco), basta reescrever as três funções públicas deste arquivo:
carregar_artigos, carregar_baixas e registrar_baixa.
"""
from datetime import date, datetime
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).parent
XLSX = PASTA / "base_estoque_tecido.xlsx"
LOG = PASTA / "baixas_registradas.csv"
COLUNAS_BAIXA = ["ID_Artigo", "Num_Baixa", "Metros", "Data"]


def carregar_artigos() -> pd.DataFrame:
    return pd.read_excel(XLSX, sheet_name="Artigos")


def carregar_baixas() -> pd.DataFrame:
    """Baixas históricas (Excel) + baixas registradas pelo app (CSV)."""
    historico = pd.read_excel(XLSX, sheet_name="Baixas")
    historico["Data"] = pd.to_datetime(historico["Data"], errors="coerce")
    if LOG.exists():
        novas = pd.read_csv(LOG, parse_dates=["Data"])[COLUNAS_BAIXA]
        return pd.concat([historico[COLUNAS_BAIXA], novas], ignore_index=True)
    return historico[COLUNAS_BAIXA]


def registrar_baixa(id_artigo: str, metros: float, data: date) -> None:
    baixas = carregar_baixas()
    anteriores = baixas.loc[baixas["ID_Artigo"] == id_artigo, "Num_Baixa"]
    numero = int(anteriores.max()) + 1 if len(anteriores) else 1
    linha = pd.DataFrame(
        [{
            "ID_Artigo": id_artigo,
            "Num_Baixa": numero,
            "Metros": float(metros),
            "Data": pd.Timestamp(data),
            "Registrado_em": datetime.now().isoformat(timespec="seconds"),
        }]
    )
    linha.to_csv(LOG, mode="a", header=not LOG.exists(), index=False)


def montar_estoque(
    artigos: pd.DataFrame, baixas: pd.DataFrame, limite_critico: float, limite_atencao: float
) -> pd.DataFrame:
    cortado = baixas.groupby("ID_Artigo")["Metros"].sum().rename("Cortado_Mts")
    df = artigos.merge(cortado, on="ID_Artigo", how="left")
    df["Cortado_Mts"] = df["Cortado_Mts"].fillna(0.0)
    df["Saldo_Mts"] = df["Estoque_Mts"] - df["Cortado_Mts"]
    df["Pct_Consumido"] = (df["Cortado_Mts"] / df["Estoque_Mts"]).where(df["Estoque_Mts"] > 0)

    def status(saldo: float) -> str:
        if saldo < 0:
            return "Negativo"
        if saldo < limite_critico:
            return "Crítico"
        if saldo < limite_atencao:
            return "Atenção"
        return "OK"

    df["Status"] = df["Saldo_Mts"].apply(status)
    return df
