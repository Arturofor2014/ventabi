# Dashboard de Ventas — Panel Solar (Panamá)

App de Streamlit generada a partir de `Modelo Ventas DAX - PowerBI.xlsx`. Replica en Python/Streamlit
las métricas clave definidas en la hoja "DAX - Medidas" del archivo original (ventas totales, ticket
promedio, crecimiento YoY, ranking de clientes/vendedores, clasificación ABC de productos y
cumplimiento de presupuesto).

## Estructura

```
ventas-streamlit-dashboard/
├── app.py                 # App de Streamlit
├── data/ventas.xlsx        # Copia de los datos (Ventas, Productos, Clientes, Presupuesto)
├── requirements.txt
└── .streamlit/config.toml  # Tema visual
```

## Probar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio de GitHub (puede ser privado).
2. Entra a https://share.streamlit.io y conecta tu cuenta de GitHub.
3. Crea una nueva app apuntando al repo, rama `main` y archivo principal `app.py`.
4. Streamlit Cloud instalará `requirements.txt` automáticamente y publicará la app.

> Nota: `data/ventas.xlsx` se sube junto al repo, así que la app no depende de ninguna ruta local.
> Si luego el archivo Excel cambia, solo reemplaza `data/ventas.xlsx` y vuelve a hacer push.
