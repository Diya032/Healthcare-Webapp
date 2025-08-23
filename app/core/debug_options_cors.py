# app/core/debug_options.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import traceback

class OptionsDebugMiddleware(BaseHTTPMiddleware):
    """
    Logs all OPTIONS requests and catches exceptions in dependencies/middleware
    to help identify why preflight fails.
    """

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            print(f"[OPTIONS DEBUG] Incoming OPTIONS request to: {request.url}")
            try:
                response = await call_next(request)
            except Exception as e:
                print(f"[OPTIONS DEBUG] Exception caught during preflight:\n{traceback.format_exc()}")
                raise  # re-raise so FastAPI still returns 500
            else:
                print(f"[OPTIONS DEBUG] OPTIONS request processed successfully")
                return response
        else:
            return await call_next(request)
