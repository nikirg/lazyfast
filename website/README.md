# LazyFast Docs Site

Documentation website for the LazyFast framework, built with LazyFast itself.

## Run

From the **project root** (`/home/user/lazyfast`):

```bash
uv run --with uvicorn -m website.main
```

Then open http://localhost:8000

## Structure

```
website/
├── main.py       # FastAPI app entry point
├── shared.py     # head(), site_nav(), CDN constants
├── home.py       # Home page (hero + feature cards)
├── docs.py       # Docs page (sidebar + 4 interactive demos)
└── static/
    └── styles.css
```
