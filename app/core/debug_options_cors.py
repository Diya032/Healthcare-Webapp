# Debug middleware to log OPTIONS requests for CORS troubleshooting
# Use only for development, not in production

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class OptionsDebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            print(f"[OPTIONS DEBUG] Incoming OPTIONS request to: {request.url}")
            print(f"[OPTIONS DEBUG] Origin: {request.headers.get('origin')}")
            print(f"[OPTIONS DEBUG] Requested Method: {request.headers.get('access-control-request-method')}")
            print(f"[OPTIONS DEBUG] Requested Headers: {request.headers.get('access-control-request-headers')}")
        return await call_next(request)