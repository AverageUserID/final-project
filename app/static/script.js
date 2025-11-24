document.getElementById("stock-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const symbol = document.getElementById("symbol-input").value.trim().toUpperCase();
    const errorDiv = document.getElementById("error");
    const resultsDiv = document.getElementById("results");

    errorDiv.textContent = "";
    resultsDiv.style.display = "none";

    try {
        const response = await fetch(`/api/stock?symbol=${symbol}`);
        const data = await response.json();

        if (data.error) {
            errorDiv.textContent = data.error;
            return;
        }

        // Display results
        document.getElementById("stock-title").textContent = `Symbol: ${data.symbol}`;
        document.getElementById("plot").src = `data:image/png;base64,${data.plot_base64}`;
        document.getElementById("raw-data").textContent = JSON.stringify(data.raw_data, null, 2);
        resultsDiv.style.display = "block";
    } catch (err) {
        errorDiv.textContent = "Error fetching stock data.";
        console.error(err);
    }
});
