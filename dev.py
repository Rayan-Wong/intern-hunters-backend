import uvicorn

# note: my port 8000 is blocked by something
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=False)