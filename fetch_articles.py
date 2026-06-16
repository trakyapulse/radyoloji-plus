#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radyoloji Pulse — PubMed makale toplayıcı.

Son N günün radyoloji makalelerini PubMed E-utilities ile çeker, skorlar ve
frontend'in okuduğu data.json dosyasını üretir.

Kullanım:
    python fetch_articles.py            # PubMed'den canlı çek ve data.json üret

Ortam değişkenleri (opsiyonel ama önerilir):
    NCBI_API_KEY   NCBI'dan ücretsiz alınır, hız limitini 3->10 istek/sn yapar
    NCBI_EMAIL     iletişim e-postası (NCBI nezaket kuralı)
"""
import os
import json
import time
import datetime
import xml.etree.ElementTree as ET

import requests

from config import (
    JOURNALS, JOURNAL_TIERS, JOURNAL_TIER_WEIGHT, DEFAULT_TIER,
    PUBTYPE_WEIGHTS, RECENCY_PER_DAY,
    RELDATE_DAYS, DATETYPE, RETMAX, EXTRA_TERMS,
    TIER1_THRESHOLD, TIER2_THRESHOLD,
)

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
API_KEY = os.environ.get("NCBI_API_KEY", "").strip()
EMAIL = os.environ.get("NCBI_EMAIL", "").strip()
TOOL = "radyoloji-pulse"

# dergi -> tier hızlı arama (normalize edilmiş anahtarlarla)
_TIER_LOOKUP = {k.lower().rstrip("."): v for k, v in JOURNAL_TIERS.items()}

MONTHS = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}


# ----------------------------------------------------------------------------
# Yardımcılar
# ----------------------------------------------------------------------------
def _params(extra):
    p = {"tool": TOOL}
    if EMAIL:
        p["email"] = EMAIL
    if API_KEY:
        p["api_key"] = API_KEY
    p.update(extra)
    return p


def _sleep():
    # API key varsa 10 req/sn, yoksa 3 req/sn sınırına saygı
    time.sleep(0.11 if API_KEY else 0.34)


def _text(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def _fmt_date(y, m, d):
    if not y:
        return ""
    mm = MONTHS.get(m, m if m.isdigit() else "")
    if mm and len(mm) == 1:
        mm = "0" + mm
    dd = d if (d and d.isdigit()) else ""
    if dd and len(dd) == 1:
        dd = "0" + dd
    out = y
    if mm:
        out += "-" + mm
    if mm and dd:
        out += "-" + dd
    return out


# ----------------------------------------------------------------------------
# PubMed istekleri
# ----------------------------------------------------------------------------
def build_query():
    journ = " OR ".join('"%s"[Journal]' % j for j in JOURNALS)
    q = "(%s)" % journ
    if EXTRA_TERMS.strip():
        q = "%s AND (%s)" % (q, EXTRA_TERMS.strip())
    return q


def esearch():
    params = _params({
        "db": "pubmed",
        "term": build_query(),
        "reldate": RELDATE_DAYS,
        "datetype": DATETYPE,
        "retmax": RETMAX,
        "retmode": "json",
        "sort": "date",
    })
    r = requests.get(EUTILS + "/esearch.fcgi", params=params, timeout=30)
    r.raise_for_status()
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    _sleep()
    return ids


def efetch(pmids):
    arts = []
    for i in range(0, len(pmids), 200):
        chunk = pmids[i:i + 200]
        params = _params({"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"})
        r = requests.post(EUTILS + "/efetch.fcgi", data=params, timeout=60)
        r.raise_for_status()
        arts.extend(parse_articles(r.text))
        _sleep()
    return arts


# ----------------------------------------------------------------------------
# XML ayrıştırma
# ----------------------------------------------------------------------------
def parse_date(article):
    ad = article.find(".//ArticleDate")
    if ad is not None:
        iso = _fmt_date(_text(ad.find("Year")), _text(ad.find("Month")), _text(ad.find("Day")))
        if iso:
            return iso
    pd = article.find(".//Journal/JournalIssue/PubDate")
    if pd is not None:
        iso = _fmt_date(_text(pd.find("Year")), _text(pd.find("Month")), _text(pd.find("Day")))
        if iso:
            return iso
        medline = _text(pd.find("MedlineDate"))
        if medline:
            return medline[:7]
    return ""


def parse_articles(xml_text):
    root = ET.fromstring(xml_text)
    out = []
    for art in root.findall(".//PubmedArticle"):
        medline = art.find(".//MedlineCitation")
        if medline is None:
            continue
        article = medline.find("Article")
        if article is None:
            continue

        pmid = _text(medline.find("PMID"))
        title = _text(article.find("ArticleTitle"))

        abs_parts = []
        for ab in article.findall(".//Abstract/AbstractText"):
            label = ab.get("Label")
            t = _text(ab)
            if not t:
                continue
            abs_parts.append("%s: %s" % (label, t) if label else t)
        abstract = " ".join(abs_parts).strip()

        journal = (_text(article.find(".//Journal/ISOAbbreviation"))
                   or _text(article.find(".//Journal/Title")))

        authors = []
        for a in article.findall(".//AuthorList/Author"):
            last = _text(a.find("LastName"))
            init = _text(a.find("Initials"))
            coll = _text(a.find("CollectiveName"))
            if last:
                authors.append(("%s %s" % (last, init)).strip())
            elif coll:
                authors.append(coll)

        ptypes = [_text(p) for p in article.findall(".//PublicationTypeList/PublicationType")]

        doi = ""
        for aid in art.findall(".//ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi":
                doi = _text(aid)
                break
        if not doi:
            for el in article.findall(".//ELocationID"):
                if el.get("EIdType") == "doi":
                    doi = _text(el)
                    break

        out.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "date": parse_date(article),
            "authors": authors,
            "pubtypes": ptypes,
            "doi": doi,
        })
    return out


# ----------------------------------------------------------------------------
# Skorlama  (özelleştireceğin asıl yer config.py)
# ----------------------------------------------------------------------------
def journal_tier(journal):
    return _TIER_LOOKUP.get(journal.strip().lower().rstrip("."), DEFAULT_TIER)


def pubtype_score(ptypes):
    weights = [PUBTYPE_WEIGHTS.get(pt, 0) for pt in ptypes]
    pos = max([w for w in weights if w > 0], default=0)
    neg = min([w for w in weights if w < 0], default=0)
    return pos + neg


def recency_bonus(date_iso):
    try:
        d = datetime.date.fromisoformat(date_iso[:10])
    except Exception:
        return 0.0
    days = (datetime.date.today() - d).days
    days = max(0, days)
    return max(0, (RELDATE_DAYS - days)) * RECENCY_PER_DAY


def score_article(a):
    jt = journal_tier(a["journal"])
    jw = JOURNAL_TIER_WEIGHT.get(jt, JOURNAL_TIER_WEIGHT[DEFAULT_TIER])
    pw = pubtype_score(a["pubtypes"])
    rw = recency_bonus(a["date"])
    total = jw + pw + rw

    a["journal_tier"] = jt
    a["score"] = round(total, 1)
    a["score_parts"] = {"journal": jw, "pubtype": pw, "recency": round(rw, 1)}
    a["tier"] = 1 if total >= TIER1_THRESHOLD else (2 if total >= TIER2_THRESHOLD else 3)
    return a


# ----------------------------------------------------------------------------
# Çıktı
# ----------------------------------------------------------------------------
def write_json(articles, path="data.json"):
    articles = sorted(articles, key=lambda x: x["score"], reverse=True)
    payload = {
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "window_days": RELDATE_DAYS,
        "datetype": DATETYPE,
        "count": len(articles),
        "tier1_count": sum(1 for a in articles if a["tier"] == 1),
        "source": "PubMed (NCBI E-utilities)",
        "articles": articles,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


def build():
    print("PubMed sorgusu hazırlanıyor...")
    if not API_KEY:
        print("  (NCBI_API_KEY yok — daha yavaş çalışır. Ücretsiz key önerilir.)")
    pmids = esearch()
    print("  %d makale bulundu" % len(pmids))
    arts = efetch(pmids) if pmids else []
    for a in arts:
        score_article(a)
    payload = write_json(arts)
    print("Tamam -> data.json  (%d makale, %d Tier 1)"
          % (payload["count"], payload["tier1_count"]))


if __name__ == "__main__":
    build()
