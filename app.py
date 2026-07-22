import os

from flask import Flask, jsonify, render_template, request

from classifier.doi_lookup import DOILookupError, resolve_doi
from classifier.predict import classify_abstract

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/classify", methods=["POST"])
def api_classify():
    payload = request.get_json(silent=True) or {}
    doi = (payload.get("doi") or "").strip()
    manual_abstract = (payload.get("abstract") or "").strip()

    title = None
    abstract = manual_abstract

    if not abstract:
        if not doi:
            return jsonify({"error": "Provide a DOI or paste an abstract."}), 400
        try:
            paper = resolve_doi(doi)
        except DOILookupError as exc:
            return jsonify({"error": str(exc)}), 422
        title = paper["title"]
        abstract = paper["abstract"]

    if len(abstract.split()) < 10:
        return jsonify({"error": "Abstract text is too short to classify reliably."}), 400

    result = classify_abstract(abstract)
    result["title"] = title
    result["doi"] = doi or None
    result["abstract"] = abstract
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
