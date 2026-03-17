# LazyFast Examples

For convenience, examples use [uv](https://docs.astral.sh/uv/getting-started/installation/) — no virtual environment setup needed.

**Install uv:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Structure

```
example/
├── showcase.py        ← all examples in one app
|── shared.py          ← common nav & helpers
└── apps/
    ├── todo.py
    ├── btc.py
    ├── search.py
    ├── users.py
    ├── files.py
    ├── converter.py
    └── chat.py
```

---

## Showcase (all examples)

```bash
uv run --with uvicorn \
       --with aiohttp \
       --with openai \
       --with markdown \
       --with beautifulsoup4 \
       -m example.showcase
```

Open `http://127.0.0.1:8000/`