#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radyoloji Pulse — günlük e-posta bülteni.

data.json'u okur, o günün makalelerini bölümlere ayırıp Türkçe özetleriyle
bir HTML bülten oluşturur ve e-posta olarak gönderir.

GitHub Actions'ta çalışır. Gerekli gizli anahtarlar (Settings > Secrets > Actions):
    MAIL_USERNAME   gönderen Gmail adresi (örn. capsman255@gmail.com)
    MAIL_PASSWORD   Gmail "Uygulama Şifresi" (app password, normal şifre DEĞİL)
    MAIL_TO         alıcı adres (opsiyonel; boşsa MAIL_USERNAME'e gönderilir)

MAIL_PASSWORD tanımlı değilse script sessizce çıkar (Action'ı hata vermez).
"""
import os
import json
import html
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from config import SECTION_ORDER, SECTION_LABELS
except Exception:
    SECTION_ORDER, SECTION_LABELS = [], {}

SITE_NAME = os.environ.get("SITE_NAME", "Radyoloji Pulse")
SITE_URL = os.environ.get("SITE_URL", "https://capsman255-ctrl.github.io/radyoloji-pulse/")
DATA_PATH = os.environ.get("DATA_PATH", "data.json")

MONTHS_TR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
             "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def esc(s):
    return html.escape(s or "")


def fmt_date(iso):
    try:
        y, m, d = iso[:10].split("-")[:3]
        return "%s %s %s" % (int(d), MONTHS_TR[int(m) - 1], y)
    except Exception:
        return iso or ""


def article_url(a):
    if a.get("doi"):
        return "https://doi.org/" + a["doi"]
    if a.get("pmid"):
        return "https://pubmed.ncbi.nlm.nih.gov/%s/" % a["pmid"]
    return "#"


def build_html(data):
    arts = data.get("articles", [])
    today = fmt_date(datetime.date.today().isoformat())
    order = SECTION_ORDER or sorted({a.get("section", "genel") for a in arts})

    parts = []
    parts.append(
        '<div style="font-family:Arial,Helvetica,sans-serif;max-width:680px;margin:0 auto;'
        'color:#0f1d2e;background:#eef2f6;padding:20px">'
    )
    parts.append(
        '<div style="background:#fff;border-radius:10px;padding:22px 24px;border:1px solid #d6dee6">'
        '<div style="font-size:12px;letter-spacing:2px;color:#64748b;text-transform:uppercase">Günlük Bülten</div>'
        '<h1 style="margin:4px 0 2px;font-size:24px">%s</h1>'
        '<div style="color:#3b4b5b;font-size:14px">%s · %d makale</div>'
        '<div style="height:5px;border-radius:3px;margin:14px 0 0;'
        'background:linear-gradient(90deg,#0f1d2e,#5b6b7a 40%%,#aab8c4 70%%,#fff)"></div>'
        '</div>' % (esc(SITE_NAME), today, len(arts))
    )

    seen_any = False
    for key in order:
        items = [a for a in arts if a.get("section", "genel") == key]
        if not items:
            continue
        seen_any = True
        label = SECTION_LABELS.get(key, "Diğer")
        parts.append(
            '<h2 style="font-size:16px;margin:24px 0 10px;padding-bottom:6px;'
            'border-bottom:2px solid #bfe9f1">%s <span style="color:#64748b;'
            'font-size:12px;font-weight:normal">(%d)</span></h2>' % (esc(label), len(items))
        )
        for a in items:
            tr = (a.get("abstract_tr") or "").strip()
            en = (a.get("abstract") or "").strip()
            body = tr or en
            meta = " · ".join(filter(None, [
                esc(a.get("journal", "")),
                fmt_date(a.get("date", "")),
                ("IF %s" % a["impact"]) if a.get("impact") else "",
                ("Tier %s" % a["tier"]) if a.get("tier") else "",
            ]))
            parts.append('<div style="background:#fff;border:1px solid #d6dee6;border-left:3px solid #0e8aa0;'
                         'border-radius:8px;padding:14px 16px;margin:0 0 12px">')
            parts.append('<a href="%s" style="color:#0f1d2e;text-decoration:none;font-size:16px;'
                         'font-weight:bold">%s</a>' % (article_url(a), esc(a.get("title", ""))))
            parts.append('<div style="color:#0e8aa0;font-size:12px;margin:6px 0">%s</div>' % meta)
            if body:
                tag = "" if tr else ' <span style="color:#94a6b6">(İngilizce — çeviri yapılamadı)</span>'
                parts.append('<div style="color:#3b4b5b;font-size:13.5px;line-height:1.6">%s%s</div>'
                             % (esc(body), tag))
            parts.append('</div>')

    if not seen_any:
        parts.append('<p style="color:#3b4b5b">Bugün yeni makale bulunamadı.</p>')

    parts.append(
        '<div style="color:#64748b;font-size:12px;margin-top:18px;text-align:center">'
        'Kaynak: PubMed · Çeviri: Google Translate · '
        '<a href="%s" style="color:#0e8aa0">Siteyi aç</a></div>' % esc(SITE_URL)
    )
    parts.append('</div>')
    return "".join(parts)


def main():
    user = os.environ.get("MAIL_USERNAME", "").strip()
    pw = os.environ.get("MAIL_PASSWORD", "").strip()
    to = os.environ.get("MAIL_TO", "").strip() or user

    if not user or not pw:
        print("Bülten atlanıyor — secret'lar adıma ulaşmıyor.")
        print("  MAIL_USERNAME dolu mu: %s (uzunluk %d)" % (bool(user), len(user)))
        print("  MAIL_PASSWORD dolu mu: %s (uzunluk %d)" % (bool(pw), len(pw)))
        print("  MAIL_TO: %r" % to)
        print("  -> Secret'lar repoda 'Repository secrets' altında ve adları birebir "
              "MAIL_USERNAME / MAIL_PASSWORD olmalı.")
        return

    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    today = fmt_date(datetime.date.today().isoformat())
    n = data.get("count", len(data.get("articles", [])))
    subject = "%s — Günlük Bülten (%s, %d makale)" % (SITE_NAME, today, n)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.attach(MIMEText(build_html(data), "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, pw)
        server.sendmail(user, [x.strip() for x in to.split(",") if x.strip()], msg.as_string())
    print("Bülten gönderildi -> %s" % to)


if __name__ == "__main__":
    main()
