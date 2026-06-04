# Hoteles y rutas de running en Barcelona

Este proyecto es un prototipo Django para explorar hoteles de Barcelona segun su cercania a rutas de running. Se basa en datos de GeoJSON para el mapa, Excel para metadatos y reviews de hoteles, y una pagina web con el mapa interactivo de Barcelona.

## Estructura global

- `main/backend/`: aplicacion Django, scripts de datos y datasets.
- `main/backend/mapapp/`: vistas HTTP y servicios GeoJSON usados por el mapa.
- `main/backend/data/`: fuentes que alimentan el mapa.
- `main/backend/scripts/`: utilidades para obtener atributos de hoteles.
- `main/frontend/templates/mapapp/`: plantilla HTML de la pagina principal.
- `main/frontend/static/mapapp/`: CSS y JavaScript del mapa. El JS esta separado en modulos por responsabilidad.
- `docs/`: documentacion funcional sobre la estructura, datos y flujo de trabajo.

## Ejecucion local

Desde la raiz del proyecto:

```powershell
cd main\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
```

Despues abre `http://127.0.0.1:8000/`.

## Documentacion importante

- `docs/estructura-del-proyecto.md`: explica como se organiza el codigo.
- `docs/datos-y-flujo.md`: explica los datasets y el orden recomendado de los scripts.
- `main/backend/README.md`: resume la app Django.
- `main/backend/data/README.md`: describe los archivos de datos.
- `main/backend/scripts/README.md`: explica como ejecutar los scripts.
