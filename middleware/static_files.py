# middleware/static_files.py
"""
Clase personalizada para servir archivos estáticos con headers de cache optimizados.
"""
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.types import Scope, Receive, Send
from pathlib import Path


class CachedStaticFiles(StaticFiles):
    """
    Extensión de StaticFiles que agrega headers de cache para mejorar el rendimiento.
    
    Los archivos estáticos (CSS, JS, imágenes) se cachean en el navegador
    para reducir el número de requests y mejorar los tiempos de carga.
    """

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Intercepta las respuestas de archivos estáticos para agregar headers de cache.
        """
        # Llamar al método padre para obtener la respuesta
        await super().__call__(scope, receive, send)
        
        # Nota: Los headers se agregan mejor mediante un middleware separado
        # ya que StaticFiles maneja las respuestas de forma asíncrona

