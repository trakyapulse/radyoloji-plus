# -*- coding: utf-8 -*-
"""
Radyoloji Pulse — ayarlar.

EN ÇOK BURAYI DÜZENLEYECEKSİN. Skorlamanın "gizli sosu" bu dosyadır:
hangi dergi kaç puan, hangi makale tipi öne çıkar. Veriyi herkes çekebilir;
asıl değer bu ağırlıklarda.

Dergi anahtarları PubMed'in NLM kısaltmalarıdır (ISOAbbreviation ile eşleşir).
Yeni dergi eklerken https://pubmed.ncbi.nlm.nih.gov adresinde derginin
"NLM Title Abbreviation" değerine bak.
"""

# --------------------------------------------------------------------------
# DERGİLER ve TIER'LARI
# Tier 1 = bayrak/üst düzey, Tier 2 = güçlü uzmanlık, Tier 3 = geniş/bölgesel
# --------------------------------------------------------------------------
JOURNAL_TIERS = {
    # --- Tier 1: genel/bayrak ---
    "Radiology": 1,
    "Radiol Artif Intell": 1,        # Radiology: Artificial Intelligence
    "Radiographics": 1,
    "Eur Radiol": 1,
    "Invest Radiol": 1,
    "AJR Am J Roentgenol": 1,
    "J Am Coll Radiol": 1,

    # --- Tier 2: güçlü uzmanlık ---
    "Eur J Radiol": 2,
    "Korean J Radiol": 2,
    "Insights Imaging": 2,
    "J Magn Reson Imaging": 2,
    "Neuroradiology": 2,
    "AJNR Am J Neuroradiol": 2,
    "Abdom Radiol (NY)": 2,
    "Pediatr Radiol": 2,
    "Acad Radiol": 2,

    # --- Senin alanların: girişimsel + US/elastografi ---
    "J Vasc Interv Radiol": 2,            # JVIR
    "Cardiovasc Intervent Radiol": 2,     # CVIR
    "Ultraschall Med": 2,                 # Ultraschall in der Medizin
    "J Ultrasound Med": 3,
    "Ultrasonography": 3,
    "Eur Radiol Exp": 3,
    "Diagn Interv Radiol": 3,
    "Clin Radiol": 3,

    # --- Görüntüleme bilimi / yöntem / yapay zeka (SCI) ---
    "Med Image Anal": 1,                  # Medical Image Analysis
    "IEEE Trans Med Imaging": 1,          # IEEE TMI
    "Radiol Med": 1,                      # La Radiologia Medica
    "J Nucl Med": 1,                      # JNM
    "Eur J Nucl Med Mol Imaging": 1,      # EJNMMI
    "Magn Reson Med": 2,
    "Neuroimage": 2,
    "Med Phys": 2,
    "Phys Med Biol": 2,
    "Radiother Oncol": 2,                 # Green Journal
    "Br J Radiol": 2,
    "Skeletal Radiol": 2,
    "Cancer Imaging": 2,
    "Jpn J Radiol": 2,
    "Int J Comput Assist Radiol Surg": 2,
    "NMR Biomed": 2,
    "Radiol Imaging Cancer": 2,
    "J Imaging Inform Med": 2,            # eski adı J Digit Imaging
    "Comput Med Imaging Graph": 3,
    "Quant Imaging Med Surg": 3,
    "Emerg Radiol": 3,
    "Clin Imaging": 3,
    "Magn Reson Imaging": 3,
    "Jpn J Radiol Technol": 3,
    "Tomography": 3,
    "Diagnostics (Basel)": 3,
}

# Tier başına temel puan
JOURNAL_TIER_WEIGHT = {1: 100, 2: 60, 3: 35}

# Listede olmayan/eşleşmeyen dergi için varsayılan tier
DEFAULT_TIER = 3

# --------------------------------------------------------------------------
# DERGİ ETKİ FAKTÖRLERİ (yaklaşık JCR değerleri — "Best of 2026" sıralaması için)
# Bu değerler her yıl güncellenir; dilediğin gibi düzenleyebilirsin.
# --------------------------------------------------------------------------
JOURNAL_IF = {
    "Radiology": 12.1,
    "Radiol Artif Intell": 8.1,
    "Radiographics": 5.2,
    "Invest Radiol": 7.0,
    "Eur Radiol": 4.7,
    "AJR Am J Roentgenol": 4.7,
    "Korean J Radiol": 4.4,
    "Insights Imaging": 4.1,
    "Ultraschall Med": 4.0,
    "J Am Coll Radiol": 4.0,
    "Acad Radiol": 3.8,
    "Eur Radiol Exp": 3.7,
    "J Magn Reson Imaging": 3.3,
    "AJNR Am J Neuroradiol": 3.3,
    "Eur J Radiol": 3.2,
    "J Vasc Interv Radiol": 3.2,
    "Ultrasonography": 3.2,
    "Cardiovasc Intervent Radiol": 2.6,
    "Neuroradiology": 2.4,
    "Abdom Radiol (NY)": 2.3,
    "Pediatr Radiol": 2.1,
    "Clin Radiol": 2.1,
    "J Ultrasound Med": 1.8,
    "Diagn Interv Radiol": 1.7,
    # Görüntüleme bilimi / yöntem / yapay zeka
    "Med Image Anal": 10.7,
    "IEEE Trans Med Imaging": 10.6,
    "Radiol Med": 9.4,
    "J Nucl Med": 9.1,
    "Eur J Nucl Med Mol Imaging": 8.6,
    "Neuroimage": 4.7,
    "Radiother Oncol": 4.9,
    "Cancer Imaging": 4.9,
    "Radiol Imaging Cancer": 5.0,
    "Magn Reson Med": 3.0,
    "Med Phys": 3.8,
    "Phys Med Biol": 3.3,
    "Br J Radiol": 2.8,
    "Skeletal Radiol": 2.0,
    "Jpn J Radiol": 3.0,
    "Int J Comput Assist Radiol Surg": 2.9,
    "NMR Biomed": 2.7,
    "J Imaging Inform Med": 2.9,
    "Comput Med Imaging Graph": 5.4,
    "Quant Imaging Med Surg": 2.9,
    "Emerg Radiol": 2.1,
    "Clin Imaging": 1.9,
    "Magn Reson Imaging": 2.1,
    "Tomography": 2.2,
    "Diagnostics (Basel)": 3.0,
}

# Listede olmayan dergi için varsayılan etki faktörü
DEFAULT_IF = 1.5

# "Best of 2026" listesinde en fazla kaç makale tutulsun
BEST_KEEP = 60

# --------------------------------------------------------------------------
# MAKALE TİPİ AĞIRLIKLARI
# PubMed PublicationType etiketleriyle birebir eşleşir.
# Pozitif tip varsa en yükseği alınır; ceza tipi varsa düşülür.
# --------------------------------------------------------------------------
PUBTYPE_WEIGHTS = {
    "Meta-Analysis": 45,
    "Systematic Review": 40,
    "Practice Guideline": 38,
    "Guideline": 35,
    "Randomized Controlled Trial": 35,
    "Clinical Trial, Phase III": 30,
    "Multicenter Study": 18,
    "Clinical Trial": 15,
    "Validation Study": 12,
    "Review": 10,
    # cezalar
    "Case Reports": -15,
    "Editorial": -25,
    "Letter": -30,
    "Comment": -30,
    "Published Erratum": -100,
    "Retraction of Publication": -200,
}

# --------------------------------------------------------------------------
# GÜNCELLİK
# Her gün için küçük bir bonus (yeni olan biraz daha öne çıksın).
# --------------------------------------------------------------------------
RECENCY_PER_DAY = 2.0

# --------------------------------------------------------------------------
# ARAMA AYARLARI
# --------------------------------------------------------------------------
RELDATE_DAYS = 1         # son kaç gün (1 = sadece bugün eklenenler; canlı/taze akış)
DATETYPE = "edat"         # "edat" = PubMed'e eklenme tarihi (taze radar için ideal)
                          # "pdat" = yayın tarihi  (sitedeki "yayınlanan" mantığı)
RETMAX = 300              # en fazla kaç makale çekilsin

# İstersen konuyla daralt (boş bırak = sadece dergi filtresi).
# Örn: 'hasta OR "Diagnostic Imaging"[Mesh]' gibi. Genelde boş bırakmak en temizi.
EXTRA_TERMS = ""

# Makale "tier" rozetleri için toplam skor eşikleri (görsel sınıflandırma)
TIER1_THRESHOLD = 110
TIER2_THRESHOLD = 80

# Dergi listesini sorgu için düz liste olarak çıkar
JOURNALS = list(JOURNAL_TIERS.keys())
