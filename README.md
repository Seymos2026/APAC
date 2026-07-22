# Academic Paper Abstract Classifier — Web App

Enter a paper's DOI, the app fetches its abstract (via the [Semantic Scholar API](https://api.semanticscholar.org/)) and classifies it into one of 7 research areas using a TF-IDF + Logistic Regression model trained on ~1,900 arXiv abstracts.

Labels: Machine learning, Data mining, Natural language processing, Computer vision, Security, Software engineering, Human-computer interaction.

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# (model/ already contains trained artifacts — only needed if you change the training data)
python train_model.py

python app.py
```

Open http://localhost:5000.

## Deploy to Render

1. Push this folder to a GitHub repo.
2. In Render: **New > Web Service**, connect the repo.
3. Render will detect `render.yaml` automatically (or set manually: build command `pip install -r requirements.txt`, start command `gunicorn app:app`).
4. Deploy. No environment variables are required.

## Project layout

```
app.py                     Flask app (serves the page + /api/classify)
classifier/doi_lookup.py   DOI -> {title, abstract} via Semantic Scholar
classifier/predict.py      Loads trained model, classifies abstract text
train_model.py             Retrains the TF-IDF + Logistic Regression model
model/                     Pre-trained model artifacts (checked in)
data/abstracts_clean.csv   Training data (arXiv abstracts, 7 categories)
templates/, static/        Frontend (single page, vanilla JS)
```

## Notes

- If a DOI has no abstract on Semantic Scholar, use the "paste abstract manually" option in the form.
- "Data mining" has no dedicated arXiv category, so it's trained on `cs.IR` (Information Retrieval) abstracts as the closest proxy.
- Test-set accuracy: ~68% across 7 classes (see `train_model.py` output).
