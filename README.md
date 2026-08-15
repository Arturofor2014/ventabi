# Dashboard de Ventas — Panel Solar (Panamá)

App de Streamlit conectada en vivo a un Google Sheet público. Replica las métricas clave definidas en
la hoja "DAX - Medidas" del archivo original `Modelo Ventas DAX - PowerBI.xlsx` (ventas totales, ticket
promedio, crecimiento YoY, ranking de clientes/vendedores, clasificación ABC de productos y
cumplimiento de presupuesto).

## Cómo lee los datos

El Sheet está compartido como **"Cualquiera con el enlace puede ver"**, así que `app.py` lo lee
directo por su export CSV público — no requiere cuenta de servicio de Google ni JSON. El **ID del
Sheet no está escrito en el código**: vive en `st.secrets` (`.streamlit/secrets.toml`) para que no
quede visible en el repositorio de GitHub.

## Estructura

```
ventas-streamlit-dashboard/
├── app.py                            # App de Streamlit
├── data/ventas.xlsx                   # Copia histórica del Excel original (no se usa como fuente)
├── requirements.txt
└── .streamlit/
    ├── config.toml                    # Tema visual
    ├── secrets.toml                    # ID real del Sheet (NO se sube a git, está en .gitignore)
    └── secrets.toml.example            # Plantilla — sí se sube al repo
```

## Probar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Si ves "Falta configurar `gsheet_id`", copia `.streamlit/secrets.toml.example` a
`.streamlit/secrets.toml` y pon el ID real del sheet (la parte de la URL entre `/d/` y `/edit`).

## Desplegar en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio de GitHub. **No** subas `.streamlit/secrets.toml` (el real,
   con el ID) — solo `secrets.toml.example` debe quedar en el repo.
2. Entra a https://share.streamlit.io y conecta tu cuenta de GitHub.
3. Crea una nueva app apuntando al repo, rama `main` y archivo principal `app.py`.
4. En la app creada: "Settings" → "Secrets" → pega:
   ```toml
   gsheet_id = "1eDOQNSc9HuUq4j84aLTlp8fqUCKZcJNmE0mHbSn1mEk"
   ```
5. Guarda: Streamlit Cloud reinicia la app con el ID configurado.

## Actualizar datos

Cualquier cambio en el Google Sheet se refleja solo (caché de 10 min), o al instante con el botón
"🔄 Recargar datos de Google Sheets" en la barra lateral.

## Si el Sheet pasa a ser privado

Ya no se podrá leer por CSV público: habría que migrar a `gspread` + cuenta de servicio de Google
Cloud (JSON de credenciales), guardando esas credenciales también en `st.secrets`.
