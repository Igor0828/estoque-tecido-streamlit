from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import dados

st.set_page_config(page_title="Controle de Tecido", page_icon="🧵", layout="wide")
st.logo("logo.svg")

# ------------------------------------------------------------------ estilo
AZUL_ESC, AZUL, AZUL_MED, AZUL_CLARO = "#1E3A8A", "#2F6BDB", "#6B9BEA", "#BCD3F7"
VERMELHO, AMARELO, CINZA = "#E5484D", "#E8B931", "#8A96A8"
PALETA = [AZUL_ESC, AZUL, AZUL_MED, AZUL_CLARO, "#DCE8FB", CINZA]
CHIPS = {  # status: (fundo, texto)
    "Negativo": ("#FDE8E8", "#C0392B"),
    "Crítico": ("#FFEBD6", "#B45309"),
    "Atenção": ("#FFF6D6", "#8A6D00"),
    "OK": ("#E3F4EA", "#1F7A4D"),
}
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

st.markdown(
    """
    <style>
    .block-container {padding-top: 4.6rem; max-width: 1400px;}
    .g-card {background:#FFFFFF; border:1px solid #E1E8F3; border-radius:16px; padding:16px 18px; height:100%;}
    .g-title {color:#6B7A90; font-size:.72rem; letter-spacing:.07em; text-transform:uppercase; font-weight:600;}
    .g-sub {color:#6B7A90; font-size:.78rem;}
    .g-big {font-size:1.9rem; font-weight:700; color:#12233F; line-height:1.2;}
    .g-row {display:flex; justify-content:space-between; align-items:center; gap:10px; padding:7px 0; border-bottom:1px solid #EBF0F8;}
    .g-row:last-child {border-bottom:none;}
    .g-name {font-weight:600; font-size:.88rem; color:#12233F;}
    .g-chip {display:inline-block; padding:2px 9px; border-radius:999px; font-size:.7rem; font-weight:700;}
    .g-tiles {display:flex; gap:10px; margin-top:10px;}
    .g-tile {flex:1; border-radius:12px; padding:10px 12px;}
    .g-tile b {display:block; font-size:1.05rem;}
    .g-tile span {font-size:.7rem; color:#5A6B85;}
    .g-ico {width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; flex:none;}
    .g-dot {display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:8px;}
    .saude-bar {height:8px; border-radius:6px; position:relative; margin:14px 0 10px 0;
                background:linear-gradient(90deg,#E5484D 0%,#E8B931 50%,#2F9E6B 100%);}
    .saude-bar i {position:absolute; top:-5px; width:3px; height:18px; background:#12233F; border-radius:2px;}
    .g-meter {height:8px; border-radius:6px; background:rgba(255,255,255,.28); overflow:hidden; margin-top:8px;}
    .g-meter i {display:block; height:100%; background:#FFFFFF; border-radius:6px;}
    .g-card-dark {background:linear-gradient(135deg,#1E3A8A,#2F6BDB); color:#FFFFFF; border-radius:14px; padding:14px 16px;}
    .st-key-card_total {background:linear-gradient(145deg,#1E3A8A,#2F6BDB); border-radius:16px; padding:16px 18px; color:#FFFFFF;}
    .st-key-card_total p, .st-key-card_total span, .st-key-card_total div {color:#FFFFFF;}
    .st-key-card_total a {background:rgba(255,255,255,.16); border-radius:999px; padding:2px 10px;}
    [class*="st-key-cardc"] {background:#FFFFFF; border:1px solid #E1E8F3; border-radius:16px; padding:14px 16px;}
    .g-badge {padding:2px 9px; border-radius:999px; font-size:.68rem; font-weight:700; white-space:nowrap;}
    .g-badge.up {background:#E3F4EA; color:#1F7A4D;} .g-badge.down {background:#FDE8E8; color:#C0392B;}
    .g-badge.flat {background:#EBF0F8; color:#5A6B85;} .g-badge.navy {background:#E3E8F6; color:#1E3A8A;} .g-badge.blue {background:#E6EFFD; color:#2457B5;}
    .g-prog {height:7px; background:#EBF0F8; border-radius:6px; overflow:hidden; margin:10px 0 6px 0; display:flex;}
    .g-prog i {display:block; height:100%;}
    .g-kpi {font-size:1.45rem; font-weight:700; color:#12233F; line-height:1.25;}
    h2 {font-size:1.35rem !important;}
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_m(v: float, casas: int = 1) -> str:
    """Formata no padrão brasileiro (1.234,5)."""
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def chip(status: str) -> str:
    bg, fg = CHIPS.get(status, ("#EEE", "#333"))
    return f'<span class="g-chip" style="background:{bg};color:{fg}">{status}</span>'


def estilo(fig, altura=360, legenda=True):
    fig.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=altura, margin=dict(l=8, r=8, t=44, b=8), showlegend=legenda,
        legend=dict(orientation="h", y=-0.12, x=0), font=dict(color="#12233F"), separators=",.",
        title=dict(font=dict(size=13)),
    )
    return fig


def status_chip_df(styler_df, col="Status"):
    cores = {"Negativo": "#C0392B", "Crítico": "#B45309", "Atenção": "#8A6D00", "OK": "#1F7A4D"}
    return styler_df.map(lambda v: f"color:{cores[v]}; font-weight:700" if v in cores else "", subset=[col])


# ------------------------------------------------------------------- páginas
def kpi(titulo, valor, badge, tom, segmentos, sub):
    barras = "".join(f'<i style="width:{max(min(f, 1), 0) * 100:.1f}%;background:{cor}"></i>' for f, cor in segmentos)
    return (f'<div class="g-card"><div class="g-title">{titulo}</div>'
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:6px;margin-top:4px">'
            f'<div class="g-kpi">{valor}</div><span class="g-badge {tom}">{badge}</span></div>'
            f'<div class="g-prog">{barras}</div><div class="g-sub">{sub}</div></div>')


def lista_html(linhas):
    return "".join(linhas)


def pagina_visao():
    hoje = date.today()
    st.markdown(f"## Visão geral  <span class='g-sub'>· {MESES[hoje.month-1].capitalize()} de {hoje.year}</span>",
                unsafe_allow_html=True)
    if vista.empty:
        st.warning("Nenhum artigo encontrado com os filtros atuais."); return

    recebido = vista["Estoque_Mts"].sum(); usado = vista["Cortado_Mts"].sum()
    saldo = vista["Saldo_Mts"].sum(); a_chegar = vista["Pedido_Aberto_Mts"].sum()
    projetado = saldo + a_chegar
    razao = lambda a, b: (a / b) if b else 0.0
    n = len(vista)
    cont = vista["Status"].value_counts()
    n_neg, n_crit, n_aten, n_ok = (int(cont.get(k, 0)) for k in ("Negativo", "Crítico", "Atenção", "OK"))
    sem_pedido = int((vista["Status"].isin(["Negativo", "Crítico"]) & (vista["Pedido_Aberto_Mts"] <= 0)).sum())
    score = round(100 * (n_ok + n_aten * 0.6 + n_crit * 0.25) / n)
    nivel, tom_nivel = ("Bom", "up") if score >= 70 else (("Atenção", "flat") if score >= 40 else ("Crítico", "down"))
    if score < 70 and score >= 40:
        tom_nivel = "blue"

    # ---- faixa de indicadores
    k = st.columns(5)
    k[0].markdown(kpi("EM ESTOQUE", f"{fmt_m(saldo, 0)} m", f"{razao(saldo, recebido):.0%} do recebido", "blue",
                      [(razao(saldo, recebido), AZUL)], f"de {fmt_m(recebido, 0)} m recebidos"), unsafe_allow_html=True)
    k[1].markdown(kpi("A CHEGAR", f"{fmt_m(a_chegar, 0)} m", f"+{razao(a_chegar, saldo):.0%} do estoque", "blue",
                      [(razao(a_chegar, projetado), AZUL_CLARO)], "pedidos em aberto"), unsafe_allow_html=True)
    k[2].markdown(kpi("PROJETADO", f"{fmt_m(projetado, 0)} m", "estoque + a chegar", "flat",
                      [(razao(saldo, projetado), AZUL), (razao(a_chegar, projetado), AZUL_CLARO)], f"{n} artigos"),
                  unsafe_allow_html=True)
    k[3].markdown(kpi("USADO", f"{fmt_m(usado, 0)} m", f"{razao(usado, recebido):.0%} do recebido", "navy",
                      [(razao(usado, recebido), AZUL_ESC)], f"falta usar {fmt_m(saldo, 0)} m"), unsafe_allow_html=True)
    k[4].markdown(
        f'<div class="g-card"><div class="g-title">SAÚDE DO ESTOQUE</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px">'
        f'<div class="g-kpi">{score}<span class="g-sub"> /100</span></div><span class="g-badge {tom_nivel}">{nivel}</span></div>'
        f'<div class="saude-bar" style="margin:12px 0 8px 0"><i style="left:{score}%"></i></div>'
        f'<div class="g-sub">{n_neg} negativos · {n_crit} críticos · {sem_pedido} sem pedido</div></div>',
        unsafe_allow_html=True)
    st.caption("Nota de saúde: OK pesa 100%, Atenção 60%, Crítico 25% e Negativo 0%.")

    # ---- gráficos
    c1, c2 = st.columns([1.5, 1])
    with c1:
        with st.container(key="cardc_barras"):
            st.markdown('<div class="g-title">METROS POR FORNECEDOR: USADO, EM ESTOQUE E A CHEGAR</div>', unsafe_allow_html=True)
            f = vista.groupby("Fornecedor").agg(
                Usado=("Cortado_Mts", "sum"), Estoque=("Saldo_Mts", lambda s: s.clip(lower=0).sum()),
                Chegar=("Pedido_Aberto_Mts", "sum"))
            f["Total"] = f.sum(axis=1)
            f = f.sort_values("Total")
            fig = go.Figure()
            for nome, col, cor in (("Usado", "Usado", AZUL_ESC), ("Em estoque", "Estoque", AZUL), ("A chegar", "Chegar", AZUL_CLARO)):
                fig.add_bar(y=f.index, x=f[col], name=nome, orientation="h", marker_color=cor,
                            texttemplate="%{x:,.0f}", textposition="inside", insidetextanchor="middle",
                            textfont=dict(color="#1E3A8A" if nome == "A chegar" else "#FFFFFF", size=10),
                            hovertemplate="%{y}<br>" + nome + ": %{x:,.1f} m<extra></extra>")
            fig.add_trace(go.Scatter(x=f["Total"], y=f.index, mode="text", showlegend=False, hoverinfo="skip",
                                     text=[f"{fmt_m(t, 0)} m" for t in f["Total"]], textposition="middle right",
                                     textfont=dict(size=10, color="#5A6B85")))
            fig.update_layout(barmode="stack", uniformtext_minsize=9, uniformtext_mode="hide")
            fig.update_xaxes(range=[0, f["Total"].max() * 1.18], tickformat=",.0f", showgrid=True, gridcolor="#EBF0F8")
            fig.update_yaxes(tickfont=dict(size=11))
            fig.update_layout(legend=dict(orientation="h", y=1.08, x=0))
            st.plotly_chart(estilo(fig, max(330, 34 * len(f) + 90)), width="stretch")
    with c2:
        with st.container(key="cardc_rosca"):
            st.markdown('<div class="g-title">DISTRIBUIÇÃO POR FORNECEDOR</div>', unsafe_allow_html=True)
            metrica = st.segmented_control("Mostrar", ["Em estoque", "A chegar", "Usado"], default="Em estoque",
                                           key="rosca_metrica", label_visibility="collapsed") or "Em estoque"
            serie = {"Em estoque": vista["Saldo_Mts"].clip(lower=0), "A chegar": vista["Pedido_Aberto_Mts"],
                     "Usado": vista["Cortado_Mts"]}[metrica]
            s = serie.groupby(vista["Fornecedor"]).sum().sort_values(ascending=False)
            s = s[s > 0]
            if s.empty:
                st.info("Sem metros para mostrar nesta visão.")
            else:
                topo = s.head(5).copy()
                if len(s) > 5:
                    topo["Outros"] = s.iloc[5:].sum()
                total = topo.sum()
                fig = go.Figure(go.Pie(labels=list(topo.index), values=list(topo.values), hole=0.70, sort=False,
                                       marker=dict(colors=PALETA, line=dict(color="#fff", width=2)), textinfo="none",
                                       hovertemplate="%{label}<br>%{value:,.0f} m (%{percent})<extra></extra>"))
                fig.add_annotation(text=f"<span style='font-size:11px;color:#6B7A90'>{metrica}</span><br>"
                                        f"<b style='font-size:19px'>{fmt_m(total, 0)} m</b>", showarrow=False)
                st.plotly_chart(estilo(fig, 230, legenda=False), width="stretch")
                leg = "".join(
                    f'<div class="g-row"><span class="g-name" style="font-weight:500"><span class="g-dot" style="background:{PALETA[i % len(PALETA)]}"></span>{nome[:22]}</span>'
                    f'<span class="g-name">{fmt_m(v, 0)} m <span class="g-sub">{v / total:.0%}</span></span></div>'
                    for i, (nome, v) in enumerate(topo.items()))
                st.markdown(leg, unsafe_allow_html=True)

    st.write("")
    # ---- listas
    e1, e2 = st.columns(2)
    with e1:
        aten = vista[vista["Status"] != "OK"].sort_values("Saldo_Mts").head(6)
        html = ""
        for r in aten.itertuples():
            tag = ('<span class="g-chip" style="background:#FDE8E8;color:#C0392B;margin-left:6px">sem pedido</span>'
                   if r.Pedido_Aberto_Mts <= 0 else "")
            html += (f'<div class="g-row"><div><div class="g-name">{r.Artigo[:30]}</div><div class="g-sub">{r.Fornecedor[:24]}</div></div>'
                     f'<div style="text-align:right">{chip(r.Status)}{tag}<div class="g-sub">saldo {fmt_m(r.Saldo_Mts, 0)} m</div></div></div>')
        st.markdown('<div class="g-card"><span class="g-title">ATENÇÃO: SALDO BAIXO OU NEGATIVO</span>'
                    + (html or '<div class="g-sub" style="padding:10px 0">Nenhum artigo em atenção.</div>')
                    + '<div class="g-sub" style="margin-top:8px">Lista completa na página Artigos.</div></div>', unsafe_allow_html=True)
    with e2:
        cores = ["#1E3A8A", "#2F6BDB", "#6B9BEA", "#4B5F8A", "#3B82F6", "#8A96A8"]
        html = ""
        for i, r in enumerate(vista[vista["Pedido_Aberto_Mts"] > 0].sort_values("Pedido_Aberto_Mts", ascending=False).head(6).itertuples()):
            html += (f'<div class="g-row"><div style="display:flex;gap:10px;align-items:center">'
                     f'<div class="g-ico" style="background:{cores[i % 6]};color:#fff;border-radius:8px">{r.Artigo[:2].upper()}</div>'
                     f'<div><div class="g-name">{r.Artigo[:30]}</div><div class="g-sub">{r.Fornecedor[:24]} · saldo {fmt_m(r.Saldo_Mts, 0)} m</div></div></div>'
                     f'<div class="g-name" style="color:#2F6BDB">+{fmt_m(r.Pedido_Aberto_Mts, 0)} m</div></div>')
        st.markdown('<div class="g-card"><span class="g-title">MAIORES PEDIDOS A CHEGAR</span>'
                    + (html or '<div class="g-sub" style="padding:10px 0">Nenhum pedido em aberto.</div>') + '</div>',
                    unsafe_allow_html=True)


def pagina_artigos():
    st.markdown("## Artigos")
    if vista.empty:
        st.warning("Nenhum artigo encontrado com os filtros atuais."); return
    modo = st.segmented_control("Visualização", ["Tabela", "Barras"], default="Tabela", key="modo_art",
                                label_visibility="collapsed") or "Tabela"

    if modo == "Tabela":
        ver_por = st.radio("Agrupar por", ["Artigo", "Fornecedor"], horizontal=True)
        cols = {"Saldo_Mts": "Em_estoque", "Pedido_Aberto_Mts": "A_chegar", "Cortado_Mts": "Usado"}
        base = vista.rename(columns=cols)
        if ver_por == "Fornecedor":
            lista = base.groupby(["Categoria", "Fornecedor"], as_index=False).agg(
                Artigos=("Artigo", "count"), Em_estoque=("Em_estoque", "sum"), A_chegar=("A_chegar", "sum"), Usado=("Usado", "sum"))
        else:
            lista = base[["Categoria", "Fornecedor", "Artigo", "Status", "Em_estoque", "A_chegar", "Usado"]].copy()
        rec = lista["Em_estoque"] + lista["Usado"]
        lista["Pct_Usado"] = (lista["Usado"] / rec).where(rec > 0).clip(upper=1)
        lista = lista.sort_values([c for c in ["Fornecedor", "Artigo"] if c in lista.columns])
        st.caption(f"{len(lista)} linhas · em estoque **{fmt_m(lista['Em_estoque'].sum())} m** · "
                   f"a chegar **{fmt_m(lista['A_chegar'].sum())} m** · usado **{fmt_m(lista['Usado'].sum())} m**")
        teto = lambda c: float(max(lista[c].quantile(0.95), 1))
        tabela = status_chip_df(lista.style) if "Status" in lista.columns else lista.style
        st.dataframe(tabela, hide_index=True, width="stretch", column_config={
            "Em_estoque": st.column_config.ProgressColumn("Em estoque (m)", format="%.1f", min_value=0, max_value=teto("Em_estoque")),
            "A_chegar": st.column_config.ProgressColumn("A chegar (m)", format="%.1f", min_value=0, max_value=teto("A_chegar")),
            "Usado": st.column_config.ProgressColumn("Usado (m)", format="%.1f", min_value=0, max_value=teto("Usado")),
            "Pct_Usado": st.column_config.ProgressColumn("% do limite usado", format="percent", min_value=0, max_value=1),
        })
        st.caption("As barras de metros usam como máximo o percentil 95, para não achatar os artigos menores. "
                   "Saldo negativo aparece sem barra.")
        st.download_button("Baixar listagem (CSV)", lista.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                           file_name="listagem_metros.csv", mime="text/csv")
        return

    # ---- modo Barras: todos os artigos
    c1, c2 = st.columns([2, 1])
    grafico = c1.segmented_control("Gráfico", ["Consumo do limite", "Metros por artigo"], default="Consumo do limite",
                                   key="grafico_barras", label_visibility="collapsed") or "Consumo do limite"
    qtd = c2.selectbox("Quantos artigos", ["Todos", 20, 40, 60], key="qtd_barras", label_visibility="collapsed")
    b = vista.copy()
    b["Pct"] = (b["Cortado_Mts"] / b["Estoque_Mts"]).where(b["Estoque_Mts"] > 0, 0.0)
    if grafico == "Consumo do limite":
        st.caption("Limite = metros recebidos (estoque + usado). Passou de 100% = trecho vermelho escuro.")
        d = b.sort_values(["Pct", "Cortado_Mts"], ascending=False)
        d = d if qtd == "Todos" else d.head(int(qtd))
        rot = [f"{a} ({p:.0%})" for a, p in zip(d["Artigo"], d["Pct"])]
        fig = go.Figure()
        for nome, vals, cor in (("Usado", d["Pct"].clip(upper=1), AZUL_ESC), ("Restante", (1 - d["Pct"]).clip(lower=0), "#DCE8FB"),
                                ("Acima do limite", (d["Pct"] - 1).clip(lower=0), VERMELHO)):
            fig.add_bar(y=rot, x=vals, name=nome, orientation="h", marker_color=cor,
                        customdata=d[["Cortado_Mts", "Estoque_Mts", "Saldo_Mts"]].values,
                        hovertemplate="%{y}<br>Usado: %{customdata[0]:,.1f} m de %{customdata[1]:,.1f} m"
                                      "<br>Saldo: %{customdata[2]:,.1f} m<extra>" + nome + "</extra>")
        fig.update_layout(barmode="stack", legend=dict(orientation="h", y=1.02, x=0))
        fig.update_xaxes(tickformat=".0%", rangemode="tozero"); fig.update_yaxes(autorange="reversed", tickfont=dict(size=10))
        st.plotly_chart(estilo(fig, max(420, 24 * len(d) + 120)), width="stretch")
    else:
        b["Total"] = b["Cortado_Mts"] + b["Saldo_Mts"].clip(lower=0) + b["Pedido_Aberto_Mts"]
        d = b.sort_values("Total", ascending=False)
        d = d if qtd == "Todos" else d.head(int(qtd))
        fig = go.Figure()
        for nome, vals, cor in (("Usado", d["Cortado_Mts"], AZUL_ESC), ("Em estoque", d["Saldo_Mts"].clip(lower=0), AZUL),
                                ("A chegar", d["Pedido_Aberto_Mts"], AZUL_CLARO)):
            fig.add_bar(y=d["Artigo"], x=vals, name=nome, orientation="h", marker_color=cor,
                        hovertemplate="%{y}<br>%{x:,.1f} m<extra>" + nome + "</extra>")
        fig.update_layout(barmode="stack", legend=dict(orientation="h", y=1.02, x=0))
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=10)); fig.update_xaxes(title="Metros", tickformat=",.0f")
        st.plotly_chart(estilo(fig, max(420, 24 * len(d) + 120)), width="stretch")


def pagina_baixas():
    st.markdown("## Baixas")
    esq, dir_ = st.columns([1, 1.6])
    with esq:
        with st.container(key="cardc_form"):
            st.markdown('<div class="g-title">REGISTRAR BAIXA POR CORTE</div>', unsafe_allow_html=True)
            if "msg_baixa" in st.session_state:
                st.success(st.session_state.pop("msg_baixa"))
            opcoes = estoque.sort_values(["Fornecedor", "Artigo"])
            rotulos = {r.ID_Artigo: f"{r.Artigo} — {r.Fornecedor} (saldo {fmt_m(r.Saldo_Mts)} m)" for r in opcoes.itertuples()}
            with st.form("form_baixa", clear_on_submit=True):
                id_escolhido = st.selectbox("Artigo", list(rotulos), format_func=rotulos.get)
                metros = st.number_input("Metros cortados", min_value=0.0, step=10.0, format="%.1f")
                data_corte = st.date_input("Data do corte")
                forcar = st.checkbox("Confirmar mesmo que ultrapasse o saldo")
                enviado = st.form_submit_button("Registrar baixa")
            if enviado:
                saldo_atual = float(estoque.loc[estoque["ID_Artigo"] == id_escolhido, "Saldo_Mts"].iloc[0])
                if metros <= 0:
                    st.error("Informe uma quantidade de metros maior que zero.")
                elif metros > saldo_atual and not forcar:
                    st.warning(f"A baixa ({fmt_m(metros)} m) é maior que o saldo ({fmt_m(saldo_atual)} m). "
                               "Marque a confirmação para registrar mesmo assim.")
                else:
                    dados.registrar_baixa(id_escolhido, metros, data_corte)
                    st.session_state["msg_baixa"] = f"Baixa de {fmt_m(metros)} m registrada."
                    st.rerun()
    datadas = baixas.dropna(subset=["Data"]).merge(artigos[["ID_Artigo", "Artigo", "Fornecedor"]], on="ID_Artigo")
    datadas = datadas[datadas["ID_Artigo"].isin(vista["ID_Artigo"])]
    with dir_:
        with st.container(key="cardc_14d"):
            st.markdown('<div class="g-title">BAIXAS NOS ÚLTIMOS 14 DIAS</div>', unsafe_allow_html=True)
            hoje = pd.Timestamp.today().normalize()
            dias = pd.date_range(hoje - pd.Timedelta(days=13), hoje)
            ult14 = datadas[(datadas["Data"] >= dias[0]) & (datadas["Data"] <= hoje + pd.Timedelta(days=1))]
            if ult14.empty:
                st.info("Nenhuma baixa com data nos últimos 14 dias. As baixas antigas da planilha não têm data; "
                        "as novas, registradas ao lado, aparecem aqui.")
            else:
                serie = ult14.groupby(ult14["Data"].dt.normalize())["Metros"].sum().reindex(dias, fill_value=0.0)
                fig = px.bar(x=serie.index.strftime("%d/%m"), y=serie.values, labels={"x": "", "y": "Metros cortados"})
                fig.update_traces(marker_color=AZUL)
                st.plotly_chart(estilo(fig, 260, legenda=False), width="stretch")
    st.write("")
    st.markdown("**Últimas movimentações**")
    if datadas.empty:
        st.info("Ainda não há movimentações com data. Registre uma baixa ao lado.")
    else:
        ult = datadas.sort_values(["Data", "Num_Baixa"], ascending=False).head(15)
        st.dataframe(ult[["Data", "Artigo", "Fornecedor", "Metros", "Num_Baixa"]], hide_index=True, width="stretch",
                     column_config={"Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                                    "Metros": st.column_config.NumberColumn("Metros", format="%.1f"),
                                    "Num_Baixa": st.column_config.NumberColumn("Nº da baixa", format="%d")})
    sem = int(baixas[baixas["ID_Artigo"].isin(vista["ID_Artigo"])]["Data"].isna().sum())
    if sem:
        st.caption(f"{sem} baixas antigas não têm data e não entram nos blocos acima.")


def pagina_qualidade():
    st.markdown("## Qualidade dos dados")
    neg = estoque[estoque["Saldo_Mts"] < 0][["Fornecedor", "Artigo", "Estoque_Mts", "Cortado_Mts", "Saldo_Mts"]]
    st.markdown(f"**Saldo negativo ({len(neg)})** — cortes maiores que o estoque registrado")
    st.dataframe(neg, hide_index=True, width="stretch")
    inf = estoque[estoque["Fornecedor_Inferido"] == "Sim"][["Categoria", "Fornecedor", "Artigo"]]
    st.markdown(f"**Fornecedor deduzido pela posição na planilha ({len(inf)})** — confirmar")
    st.dataframe(inf, hide_index=True, width="stretch")
    st.markdown(f"**Baixas sem data:** {int(baixas['Data'].isna().sum())} de {len(baixas)}")


# ---------------------------------------------------------------- navegação
PG = {
    "visao": st.Page(pagina_visao, title="Visão geral", icon=":material/dashboard:", url_path="visao-geral", default=True),
    "artigos": st.Page(pagina_artigos, title="Artigos", icon=":material/list_alt:", url_path="artigos"),
    "baixas": st.Page(pagina_baixas, title="Baixas", icon=":material/content_cut:", url_path="baixas"),
    "qualidade": st.Page(pagina_qualidade, title="Qualidade dos dados", icon=":material/fact_check:", url_path="qualidade"),
}
pg = st.navigation({
    "Menu principal": [PG["visao"], PG["artigos"]],
    "Operação": [PG["baixas"]],
    "Análises": [PG["qualidade"]],
})

# ---------------------------------------------------------- filtros (topo)
artigos = dados.carregar_artigos()
barra1, barra2, barra3 = st.columns([2.2, 3, 1.1], vertical_alignment="center")
with barra1:
    categoria = st.segmented_control("Categoria", ["Todas", "LYCRA", "100%"], default="Todas",
                                     label_visibility="collapsed", key="categoria") or "Todas"
with barra2:
    busca = st.text_input("Buscar", placeholder="Buscar artigo ou fornecedor", label_visibility="collapsed", key="busca")
with barra3:
    with st.popover("Filtros", icon=":material/tune:"):
        fornecedores = st.multiselect("Fornecedor", sorted(artigos["Fornecedor"].unique()))
        limite_critico = st.number_input("Crítico abaixo de (m)", min_value=0, value=300, step=50)
        limite_atencao = st.number_input("Atenção abaixo de (m)", min_value=0, value=1000, step=100)

baixas = dados.carregar_baixas()
estoque = dados.montar_estoque(artigos, baixas, limite_critico, limite_atencao)
estoque["Pedido_Aberto_Mts"] = estoque["Pedido_Aberto_Mts"].fillna(0.0)
estoque["Projetado_Mts"] = estoque["Saldo_Mts"] + estoque["Pedido_Aberto_Mts"]

filtro = pd.Series(True, index=estoque.index)
if categoria != "Todas":
    filtro &= estoque["Categoria"] == categoria
if fornecedores:
    filtro &= estoque["Fornecedor"].isin(fornecedores)
if busca:
    filtro &= (estoque["Artigo"].str.contains(busca, case=False, na=False)
               | estoque["Fornecedor"].str.contains(busca, case=False, na=False))
vista = estoque[filtro]

pg.run()
