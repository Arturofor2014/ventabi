# Dashboard de Ventas — Panel Solar (Panamá)

App de Streamlit conectada en vivo a un Google Sheet. Replica las métricas clave definidas en la hoja
"DAX - Medidas" del archivo original `Modelo Ventas DAX - PowerBI.xlsx` (ventas totales, ticket
promedio, crecimiento YoY, ranking de clientes/vendedores, clasificación ABC de productos y
cumplimiento de presupuesto).

Sheet fuente: https://docs.google.com/spreadsheets/d/1eDOQNSc9HuUq4j84aLTlp8fqUCKZcJNmE0mHbSn1mEk/edit

## Estructura

```
ventas-streamlit-dashboard/
├── app.py                            # App de Streamlit
├── data/ventas.xlsx                   # Copia histórica del Excel original (ya no se usa como fuente)
├── requirements.txt
├── .streamlit/
│   ├── config.toml                    # Tema visual
│   └── secrets.toml.example           # Plantilla de credenciales (copiar a secrets.toml, NUNCA subir el real)
```

## Configurar el acceso a Google Sheets (una sola vez)

La app lee los datos con una **cuenta de servicio de Google** guardada en `secrets`, el patrón
recomendado por Streamlit para conectar a Google Sheets de forma segura y reproducible.

1. **Crear proyecto y cuenta de servicio en Google Cloud**
   - Ve a https://console.cloud.google.com/ → crea (o selecciona) un proyecto.
   - En "APIs y servicios" → "Biblioteca", habilita **Google Sheets API** y **Google Drive API**.
   - En "APIs y servicios" → "Credenciales" → "Crear credenciales" → **Cuenta de servicio**.
   - Dentro de la cuenta de servicio creada, ve a la pestaña **Claves** → "Agregar clave" → **Crear clave nueva** → tipo **JSON**. Se descarga un archivo `.json`.

2. **Compartir el Google Sheet con la cuenta de servicio**
   - Abre el JSON descargado y copia el valor de `client_email` (algo como `xxx@tu-proyecto.iam.gserviceaccount.com`).
   - En el Google Sheet, botón "Compartir" → agrega ese correo con permiso de **Lector**.

3. **Completar `secrets.toml` local**
   - Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml`.
   - Rellena cada campo con los valores del JSON descargado (`project_id`, `private_key_id`, `private_key`,
     `client_email`, `client_id`, `client_x509_cert_url`). El campo `spreadsheet` ya viene con la URL correcta.
   - `.streamlit/secrets.toml` está en `.gitignore`: nunca se sube al repo.

## Probar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Si ves un error "No se pudo conectar a Google Sheets", revisa que `secrets.toml` exista y tenga las
credenciales correctas (paso 3 arriba).

## Desplegar en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio de GitHub (puede ser privado). **No** subas `secrets.toml` (real).
2. Entra a https://share.streamlit.io y conecta tu cuenta de GitHub.
3. Crea una nueva app apuntando al repo, rama `main` y archivo principal `app.py`.
4. En la app ya creada: "Settings" → "Secrets" → pega el contenido completo de tu `secrets.toml` local
   (con los valores reales, no la plantilla).
5. Guarda: Streamlit Cloud reinicia la app con acceso a Google Sheets.

## Actualizar datos

Cualquier cambio en el Google Sheet se refleja solo (caché de 10 min), o al instante con el botón
"🔄 Recargar datos de Google Sheets" en la barra lateral.
