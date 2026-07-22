import re

import requests

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


class DOILookupError(Exception):
    pass


def normalize_doi(raw_doi):
    doi = raw_doi.strip()
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = doi.strip().strip("/")
    return doi


def resolve_doi(raw_doi):
    """Resolve a DOI to {doi, title, abstract}. Raises DOILookupError on failure."""
    doi = normalize_doi(raw_doi)
    if not DOI_RE.match(doi):
        raise DOILookupError(f"'{raw_doi}' doesn't look like a valid DOI (expected format: 10.xxxx/xxxxx).")

    try:
        resp = requests.get(
            SEMANTIC_SCHOLAR_URL.format(doi=doi),
            params={"fields": "title,abstract"},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise DOILookupError(f"Could not reach Semantic Scholar: {exc}") from exc

    if resp.status_code == 404:
        raise DOILookupError(f"No paper found for DOI '{doi}' on Semantic Scholar.")
    if resp.status_code == 429:
        raise DOILookupError("Semantic Scholar rate limit hit — please try again in a moment.")
    if resp.status_code != 200:
        raise DOILookupError(f"Semantic Scholar returned status {resp.status_code}.")

    payload = resp.json()
    title = payload.get("title")
    abstract = payload.get("abstract")

    if not abstract:
        raise DOILookupError(
            "Found the paper but it has no abstract available via Semantic Scholar. "
            "Paste the abstract text manually instead."
        )

    return {"doi": doi, "title": title, "abstract": abstract}
