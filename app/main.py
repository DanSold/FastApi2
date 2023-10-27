import uvicorn
from fastapi import FastAPI
from app.web_pages import router_web_pages
from app.auth import router_auth

app = FastAPI(
    title='Web-recipes',
    version='0.0.1',
    debug=True
)

app.include_router(router_web_pages.router)
app.include_router(router_auth.router)
if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
