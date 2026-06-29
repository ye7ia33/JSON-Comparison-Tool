# 🔍 JSON Comparison Tool

A tool to compare two JSON objects and highlight the differences — supporting key/structure changes, value changes, or both.

## Live Demos

| Platform | URL |
|---|---|
| Cloudflare Workers | https://json-comparison.wrker.workers.dev |
| Vercel (Static) | https://json-comparison.vercel.app/ |
| Streamlit Cloud | https://json-comparison.streamlit.app/ |

## Features

- **Three comparison modes**
  - **Full** — reports added/removed keys and changed values
  - **Keys & Structure Only** — reports only structural changes, ignores value differences
  - **Values Only** — reports only value changes for keys that exist in both JSONs
- **Two input methods** — paste JSON directly or upload `.json` files
- **Path-based diff** — shows exact dot-notation paths (e.g. `user.address.city`, `items[0].price`)
- **Syntax-highlighted JSON viewer** for both inputs
- **Download report** — export the diff result as a `.json` file

## Project Structure

```
├── index.html           # Static app (Vercel / Cloudflare Workers)
├── app.py               # Streamlit app (Streamlit Cloud)
├── compare_json_app.py  # Streamlit entrypoint → imports from app.py
├── vercel.json          # Vercel static deployment config
└── requirements.txt     # Python dependencies
```

## Running Locally

**Streamlit:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Static (no install needed):**  
Open `index.html` directly in a browser.

---

Made by [Yahia Eldow](https://www.yahia-eldow.com)
