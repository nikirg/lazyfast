# LazyFast Examples

Initialize virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Run any example via uvicorn:
```bash
uvicorn user_form:app --host 0.0.0.0 --reload --timeout-graceful-shutdown 1
``` 
Go to `http://127.0.0.1:8000/`
