import os
import zipfile
import pandas as pd
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Serve index.html
@app.route("/")
def home():
    return render_template("index.html")

# File upload + dataset parsing
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    filename = file.filename.lower()

    try:
        # Case 1: CSV
        if filename.endswith(".csv"):
            df = pd.read_csv(file, sep=None, engine="python")

        # Case 2: TXT (treat like CSV, often semicolon-separated in UCI dataset)
        elif filename.endswith(".txt"):
            df = pd.read_csv(file, sep=";", engine="python")

        # Case 3: ZIP containing CSV/TXT
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(file) as z:
                # Extract first CSV or TXT inside ZIP
                inner_name = [n for n in z.namelist() if n.endswith((".csv", ".txt"))][0]
                with z.open(inner_name) as f:
                    if inner_name.endswith(".csv"):
                        df = pd.read_csv(f, sep=None, engine="python")
                    else:
                        df = pd.read_csv(f, sep=";", engine="python")
        else:
            return jsonify({"error": "Unsupported file type. Please upload CSV, TXT, or ZIP."}), 400

        # Basic info to send back
        return jsonify({
            "columns": list(df.columns),
            "rows": len(df),
            "preview": df.head(5).to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)





