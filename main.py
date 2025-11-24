from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx
import matplotlib.pyplot as plt
import io
import base64
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable"

@app.get("/", response_class=HTMLResponse)
def index():
    return open("app/templates/index.html").read()

async def fetch_price_change(symbol: str):
    url = f"{BASE_URL}/stock-price-change?symbol={symbol}&apikey={API_KEY}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            return None
        try:
            data = r.json()
            if not data or "symbol" not in data[0]:
                return None
            return data[0]
        except:
            return None

@app.get("/api/stock")
async def stock(symbol: str = Query(..., min_length=1)):
    """
    Fetch current percent changes of a stock symbol, return a symlog plot image with color-coded bars and value labels.
    """
    data = await fetch_price_change(symbol.upper())
    if not data:
        return {"error": "No data found for symbol", "symbol": symbol.upper()}

    # Extract percent changes and round
    timeframes = ["1D","5D","1M","3M","6M","ytd","1Y","3Y","5Y","10Y","max"]
    values = [round(data.get(tf, 0), 3) for tf in timeframes]

    # Determine bar colors: green for positive, red for negative
    colors = ["green" if v >= 0 else "red" for v in values]

    # Create symlog bar plot
    plt.figure(figsize=(10,6))
    bars = plt.bar(timeframes, values, color=colors)
    plt.yscale("symlog", linthresh=1)  # linear within ±1, log outside
    plt.ylabel("Percent Change")
    plt.title(f"{symbol.upper()} Percent Changes")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Annotate bars with values
    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2, 
            value + (0.5 if value >= 0 else -0.5),  # offset slightly
            f"{value}%", 
            ha='center', 
            va='bottom' if value >= 0 else 'top',
            fontsize=9
        )

    # Convert plot to base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")

    return {
        "symbol": symbol.upper(),
        "raw_data": dict(zip(timeframes, values)),
        "plot_base64": img_b64
    }
