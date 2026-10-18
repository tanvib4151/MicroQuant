import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .routers.analysis import router
from .services.image_loader import InputError

class UploadLimitMiddleware:
    """Enforce an actual request-body limit before multipart decoding/spooling."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] != "/analyze":
            return await self.app(scope, receive, send)
        limit = int(os.getenv("MAX_UPLOAD_BYTES", "20971520")) + 65536
        chunks = []
        size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > limit:
                return await JSONResponse(status_code=413, content={"detail": "Request exceeds the configured upload limit."})(scope, receive, send)
            chunks.append(chunk)
            if not message.get("more_body", False):
                break
        body = b"".join(chunks)
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        await self.app(scope, replay, send)

app = FastAPI(title="NeuroQuant", version="1.0.0")
app.add_middleware(UploadLimitMiddleware)

@app.exception_handler(InputError)
async def invalid_input(request: Request, exc: InputError):
    return JSONResponse(status_code=exc.status, content={"detail": str(exc)})

@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Image processing failed. Try a smaller supported image."})

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router)
