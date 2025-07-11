import httpx
from .config import API_KEY, BACKEND_URL

async def obtener_respuesta(query: str) -> str:
    try:
        payload = {"query": query}
        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json"  # ← Asegúrate que esté con C mayúscula
        }

        # print("📨 Enviando:", payload)  # Log para depuración

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                BACKEND_URL,
                headers=headers,
                json=payload
            )

        # print("📦 Respuesta cruda:", response.text)  # Log para analizar el contenido devuelto

        # response.raise_for_status()  # Esto lanza excepciones si el status code ≥ 400

        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("⚠️ La respuesta no es un dict válido.")
        return data.get("response", "⚠️ Respuesta vacía del servidor.")

    except httpx.ReadTimeout:
        return "⏱️ El servidor tardó demasiado en responder."
    except httpx.HTTPStatusError as e:
        return f"❌ Error del servidor: {e.response.status_code}\n📭 Detalles: {e.response.text}"
    except httpx.RequestError:
        return "❌ No se pudo contactar con el servidor."
    except Exception as e:
        return f"❌ Error inesperado: {str(e)}"