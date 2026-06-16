# Radyoloji Pulse

Son günlerin radyoloji literatüründen öne çıkan makaleleri PubMed'den çekip,
dergi ağırlığı ve makale tipine göre skorlayıp bir web sayfasında listeleyen araç.

## Dosyalar

- `index.html` — site (veriyi `data.json`'dan okur)
- `fetch_articles.py` — PubMed'den makaleleri çekip `data.json` üretir
- `config.py` — skorlama ayarları (dergiler, tier'lar, ağırlıklar) — asıl özelleştirme burada
- `data.json` — betiğin ürettiği veri
- `.github/workflows/update.yml` — her gün otomatik güncelleme (GitHub Actions)
- `radyoloji-pulse-tek-dosya.html` — veriyi içine gömülü, internetsiz açılabilen tek dosyalık sürüm

## Önemli: çift tıklayınca neden boş açılıyordu?

`index.html` veriyi `fetch("data.json")` ile yükler. Tarayıcılar, dosya bilgisayardan
doğrudan (`file://`) açıldığında güvenlik nedeniyle bu okumayı engeller — bu yüzden
sayfa açılır ama içerik gelmez. `fetch` yalnızca bir web sunucusunda çalışır
(GitHub Pages gibi). Lokal test için sayfadaki "data.json seç…" düğmesini
kullanabilir ya da tek-dosya sürümünü açabilirsin.

## GitHub Pages'te yayınlama

1. Bu klasörü bir GitHub deposuna yükle (örn. `radyoloji-pulse`):
   ```bash
   git init
   git add .
   git commit -m "İlk sürüm"
   git branch -M main
   git remote add origin https://github.com/KULLANICI_ADIN/radyoloji-pulse.git
   git push -u origin main
   ```
2. Depoda **Settings → Pages** bölümüne git.
3. **Source** olarak "Deploy from a branch", **Branch** olarak `main` / `/ (root)` seç, kaydet.
4. Birkaç dakika sonra siten `https://KULLANICI_ADIN.github.io/radyoloji-pulse/` adresinde yayında olur.

## Otomatik günlük güncelleme

`.github/workflows/update.yml` her gün 06:00 UTC'de (~09:00 TR) çalışır, PubMed'den
çeker ve `data.json`'u güncelleyip commit'ler. Pages bu commit'le otomatik yeniden yayınlanır.

İsteğe bağlı (daha hızlı ve nazik istekler için): depoda **Settings → Secrets and variables
→ Actions** altına `NCBI_API_KEY` ve `NCBI_EMAIL` ekle. ([Ücretsiz NCBI API key](https://www.ncbi.nlm.nih.gov/account/))

Manuel tetikleme: **Actions** sekmesi → "Radyoloji Pulse güncelle" → **Run workflow**.

## Lokal çalıştırma

```bash
pip install -r requirements.txt
python fetch_articles.py            # PubMed'den canlı çekip data.json üretir
```

Sonra `index.html`'i bir lokal sunucuyla aç:
```bash
python -m http.server 8000
# tarayıcıda: http://localhost:8000
```

## Skorlamayı özelleştirme

`config.py` içinde dergi tier'larını, makale tipi ağırlıklarını, güncellik bonusunu
ve tarih penceresini (`RELDATE_DAYS`) değiştirebilirsin.
