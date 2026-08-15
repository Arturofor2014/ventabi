import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Dashboard de Ventas", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #cde2fb;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
        color: #184f95;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_PATH = Path(__file__).parent / "data" / "ventas.xlsx"

# --- Paleta (fija, validada para accesibilidad — ver skill dataviz) ---
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
GOOD, CRITICAL, MUTED = "#0ca30c", "#d03b3b", "#898781"
INK, GRID, BASELINE = "#0b0b0b", "#e1e0d9", "#c3c2b7"
FONT = dict(family="system-ui, -apple-system, Segoe UI, sans-serif", color=INK, size=13)

REGION_ORDER = ["Chiriqui", "Colon", "Panama Este", "Panama Oeste"]
REGION_COLORS = {r: CATEGORICAL[i] for i, r in enumerate(REGION_ORDER)}


def style_fig(fig, height=380, show_legend=True):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=FONT,
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None),
    )
    fig.update_xaxes(showgrid=False, linecolor=BASELINE, ticks="outside", tickcolor=BASELINE, title=None)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig


@st.cache_data(show_spinner="Cargando datos del Excel...")
def load_data():
    ventas = pd.read_excel(DATA_PATH, sheet_name="Ventas")
    productos = pd.read_excel(DATA_PATH, sheet_name="Productos")
    clientes = pd.read_excel(DATA_PATH, sheet_name="Clientes")
    presupuesto = pd.read_excel(DATA_PATH, sheet_name="Presupuesto")

    ventas["Fecha"] = pd.to_datetime(ventas["Fecha"])
    presupuesto["Fecha"] = pd.to_datetime(presupuesto["Fecha"])
    clientes["Fecha_Primera_Compra"] = pd.to_datetime(clientes["Fecha_Primera_Compra"])

    ventas["Monto_Venta"] = ventas["Cantidad"] * ventas["Precio_Unitario"]
    ventas = ventas.merge(productos, on="ID_Producto", how="left")
    ventas = ventas.merge(clientes, on="ID_Cliente", how="left")

    return ventas, productos, clientes, presupuesto


ventas, productos, clientes, presupuesto = load_data()

# ----------------------------- Sidebar: filtros -----------------------------
st.sidebar.header("Filtros")

min_date, max_date = ventas["Fecha"].min().date(), ventas["Fecha"].max().date()
date_range = st.sidebar.date_input(
    "Rango de fechas", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start, end = pd.to_datetime(min_date), pd.to_datetime(max_date)

regiones = st.sidebar.multiselect("Región", REGION_ORDER, default=REGION_ORDER)
categorias = st.sidebar.multiselect(
    "Categoría", sorted(productos["Categoria"].unique()), default=sorted(productos["Categoria"].unique())
)
vendedores = st.sidebar.multiselect(
    "Vendedor", sorted(ventas["Vendedor"].unique()), default=sorted(ventas["Vendedor"].unique())
)

df = ventas[
    (ventas["Fecha"] >= start)
    & (ventas["Fecha"] <= end)
    & (ventas["Region"].isin(regiones))
    & (ventas["Categoria"].isin(categorias))
    & (ventas["Vendedor"].isin(vendedores))
].copy()

st.title("📊 Dashboard de Ventas — Panel Solar (Panamá)")
st.caption(f"Datos del {min_date} al {max_date}. Fuente: Modelo Ventas DAX - PowerBI.xlsx")

if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# ----------------------------------- KPIs -----------------------------------
ventas_totales = df["Monto_Venta"].sum()
num_transacciones = df["ID_Venta"].nunique()
ticket_promedio = ventas_totales / num_transacciones if num_transacciones else 0
clientes_distintos = df["ID_Cliente"].nunique()

presu_filtrado = presupuesto[
    (presupuesto["Fecha"] >= start.replace(day=1)) & (presupuesto["Fecha"] <= end) & (presupuesto["Region"].isin(regiones))
]
presupuesto_total = presu_filtrado["Presupuesto"].sum()
cumplimiento = ventas_totales / presupuesto_total if presupuesto_total else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Ventas Totales", f"${ventas_totales:,.0f}")
c2.metric("# Transacciones", f"{num_transacciones:,}")
c3.metric("Ticket Promedio", f"${ticket_promedio:,.0f}")
c4.metric("Clientes Distintos", f"{clientes_distintos:,}")
c5.metric("Cumplimiento Presupuesto", f"{cumplimiento:.0%}")

st.divider()

tab_resumen, tab_presupuesto, tab_clientes, tab_productos, tab_vendedores = st.tabs(
    ["Resumen", "Presupuesto", "Clientes", "Productos", "Vendedores"]
)

# --------------------------------- Resumen -----------------------------------
with tab_resumen:
    monthly = df.groupby(df["Fecha"].dt.to_period("M"))["Monto_Venta"].sum().reset_index()
    monthly["Periodo"] = monthly["Fecha"]
    monthly["AnioMesStr"] = monthly["Periodo"].astype(str)
    monthly = monthly.sort_values("Periodo")

    st.subheader("Tendencia mensual de ventas")
    fig = px.line(monthly, x="AnioMesStr", y="Monto_Venta", markers=True)
    fig.update_traces(line=dict(width=2, color=CATEGORICAL[0]), marker=dict(size=8, color=CATEGORICAL[0]))
    fig.update_yaxes(title="Ventas Totales ($)")
    st.plotly_chart(style_fig(fig, show_legend=False), use_container_width=True)

    st.subheader("Crecimiento interanual (YoY %)")
    st.caption("Compara cada mes contra el mismo mes del año anterior, dentro de los filtros activos.")
    yoy_src = monthly.set_index("Periodo")["Monto_Venta"]
    yoy_rows = []
    for period, value in yoy_src.items():
        prev_period = period - 12
        if prev_period in yoy_src.index and yoy_src[prev_period] != 0:
            growth = (value - yoy_src[prev_period]) / yoy_src[prev_period]
            yoy_rows.append({"AnioMesStr": str(period), "YoY": growth})
    if yoy_rows:
        yoy = pd.DataFrame(yoy_rows)
        colors = np.where(yoy["YoY"] >= 0, GOOD, CRITICAL)
        fig = go.Figure(go.Bar(x=yoy["AnioMesStr"], y=yoy["YoY"], marker_color=colors))
        fig.update_yaxes(title="Crecimiento YoY", tickformat=".0%")
        st.plotly_chart(style_fig(fig, show_legend=False), use_container_width=True)
    else:
        st.info("No hay suficiente histórico (se necesita el mismo mes del año anterior) para calcular YoY con los filtros actuales.")

# -------------------------------- Presupuesto ---------------------------------
with tab_presupuesto:
    st.subheader("Ventas reales vs. presupuesto por región")
    bp = df.groupby("Region", as_index=False)["Monto_Venta"].sum().rename(columns={"Monto_Venta": "Ventas Reales"})
    presu_g = presu_filtrado.groupby("Region", as_index=False)["Presupuesto"].sum()
    comp = pd.DataFrame({"Region": REGION_ORDER}).merge(bp, on="Region", how="left").merge(presu_g, on="Region", how="left").fillna(0)
    comp["Cumplimiento"] = comp.apply(lambda r: r["Ventas Reales"] / r["Presupuesto"] if r["Presupuesto"] else 0, axis=1)

    fig = go.Figure()
    fig.add_bar(name="Ventas Reales", x=comp["Region"], y=comp["Ventas Reales"], marker_color=CATEGORICAL[0])
    fig.add_bar(name="Presupuesto", x=comp["Region"], y=comp["Presupuesto"], marker_color=MUTED)
    fig.update_layout(barmode="group")
    fig.update_yaxes(title="$")
    st.plotly_chart(style_fig(fig), use_container_width=True)

    st.dataframe(
        comp.assign(**{
            "Ventas Reales": comp["Ventas Reales"].map(lambda v: f"${v:,.0f}"),
            "Presupuesto": comp["Presupuesto"].map(lambda v: f"${v:,.0f}"),
            "Cumplimiento": comp["Cumplimiento"].map(lambda v: f"{v:.0%}"),
        }),
        hide_index=True,
        use_container_width=True,
    )

# ---------------------------------- Clientes -----------------------------------
with tab_clientes:
    st.subheader("Top 10 clientes por ventas")
    top_clientes = (
        df.groupby("Cliente", as_index=False)["Monto_Venta"].sum().sort_values("Monto_Venta", ascending=False).head(10)
    )
    fig = px.bar(top_clientes.sort_values("Monto_Venta"), x="Monto_Venta", y="Cliente", orientation="h")
    fig.update_traces(marker_color=CATEGORICAL[0])
    fig.update_xaxes(title="Ventas Totales ($)")
    st.plotly_chart(style_fig(fig, show_legend=False, height=420), use_container_width=True)

    st.subheader("Clientes nuevos vs. recurrentes por mes")
    st.caption("Un cliente es 'nuevo' en el mes de su primera compra registrada (Clientes[Fecha_Primera_Compra]).")
    df_month = df.assign(AnioMes=df["Fecha"].dt.to_period("M"))
    primera_compra_periodo = clientes.set_index("ID_Cliente")["Fecha_Primera_Compra"].dt.to_period("M")

    rows = []
    for periodo, grupo in df_month.groupby("AnioMes"):
        ids = set(grupo["ID_Cliente"].unique())
        nuevos = sum(1 for cid in ids if primera_compra_periodo.get(cid) == periodo)
        rows.append({"AnioMes": str(periodo), "Nuevos": nuevos, "Recurrentes": len(ids) - nuevos})
    nvr = pd.DataFrame(rows).sort_values("AnioMes")

    fig = go.Figure()
    fig.add_bar(name="Nuevos", x=nvr["AnioMes"], y=nvr["Nuevos"], marker_color=CATEGORICAL[0])
    fig.add_bar(name="Recurrentes", x=nvr["AnioMes"], y=nvr["Recurrentes"], marker_color=CATEGORICAL[1])
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title="# Clientes")
    st.plotly_chart(style_fig(fig), use_container_width=True)

# --------------------------------- Productos -----------------------------------
with tab_productos:
    st.subheader("Ventas por categoría de producto")
    cat_orden = sorted(productos["Categoria"].unique())
    cat_colors = {c: CATEGORICAL[i % len(CATEGORICAL)] for i, c in enumerate(cat_orden)}
    cat_sales = df.groupby("Categoria", as_index=False)["Monto_Venta"].sum()
    fig = px.bar(
        cat_sales, x="Categoria", y="Monto_Venta", color="Categoria",
        color_discrete_map=cat_colors, category_orders={"Categoria": cat_orden},
    )
    fig.update_yaxes(title="Ventas Totales ($)")
    st.plotly_chart(style_fig(fig, show_legend=False), use_container_width=True)

    st.subheader("Clasificación ABC de productos (Pareto 80/20)")
    prod_sales = df.groupby("Producto", as_index=False)["Monto_Venta"].sum().sort_values("Monto_Venta", ascending=False)
    total = prod_sales["Monto_Venta"].sum()
    prod_sales["% Acumulado"] = prod_sales["Monto_Venta"].cumsum() / total
    prod_sales["Clase ABC"] = pd.cut(
        prod_sales["% Acumulado"], bins=[0, 0.8, 0.95, 1.0000001], labels=["A", "B", "C"], include_lowest=True
    )
    abc_colors = {"A": GOOD, "B": "#eda100", "C": MUTED}

    def highlight_abc(val):
        return f"background-color: {abc_colors.get(val, '')}; color: white"

    st.dataframe(
        prod_sales.assign(**{
            "Monto_Venta": prod_sales["Monto_Venta"].map(lambda v: f"${v:,.0f}"),
            "% Acumulado": prod_sales["% Acumulado"].map(lambda v: f"{v:.0%}"),
        }).style.map(highlight_abc, subset=["Clase ABC"]),
        hide_index=True,
        use_container_width=True,
    )

# -------------------------------- Vendedores -----------------------------------
with tab_vendedores:
    st.subheader("Ventas por vendedor y región")
    vend_region = df.groupby(["Region", "Vendedor"], as_index=False)["Monto_Venta"].sum()
    fig = px.bar(
        vend_region, x="Vendedor", y="Monto_Venta", color="Region",
        color_discrete_map=REGION_COLORS, category_orders={"Region": REGION_ORDER}, barmode="group",
    )
    fig.update_yaxes(title="Ventas Totales ($)")
    st.plotly_chart(style_fig(fig), use_container_width=True)

    st.subheader("Ranking de vendedores dentro de su región")
    vend_region["Ranking en su Región"] = (
        vend_region.groupby("Region")["Monto_Venta"].rank(ascending=False, method="dense").astype(int)
    )
    vend_region = vend_region.sort_values(["Region", "Ranking en su Región"])
    st.dataframe(
        vend_region.assign(Monto_Venta=vend_region["Monto_Venta"].map(lambda v: f"${v:,.0f}")),
        hide_index=True,
        use_container_width=True,
    )
