# Paylaşımlı Bisiklet Talebi Tahmini

Uçtan Uca Yapay Zeka Projesi: Veriden Tahmine. Washington D.C. bisiklet paylaşım sisteminde **belirli bir saatteki kiralama sayısını** tahmin eden regresyon çalışması: gerçek veri (UCI Bike Sharing, 17.379 saatlik kayıt), zamana göre bölme, zaman serisi çapraz doğrulaması, 5 model, hiperparametre ayarı, iki senaryo, hata analizi, tahmin aralığı ve komut satırı aracı.

| Dosya | Açıklama |
|---|---|
| `bisiklet_talebi_tahmini.ipynb` | Çalıştırılmış not defteri (problem → veri → EDA → model → değerlendirme → hata analizi → mini uygulama) |
| `tahmin_araci.py` | Komut satırı aracı (argparse, girdi doğrulama, etkileşimli mod) |
| `tests/` | pytest, 12 test |
| `Proje_Raporu.docx`, `Sunum.pptx` | 1 sayfalık rapor, 5 slayt |
| `data/hour.csv` | Fanaee-T & Gama (2013), UCI, CC BY 4.0 |
| `metrics.json`, `figures/`, `models/` | Sayısal sonuçlar, grafikler, kaydedilmiş model |

## Kullanım
```bash
pip install -r requirements.txt
python tahmin_araci.py --tarih 2012-10-16 --saat 8 --sicaklik 17 --hava 1
python tahmin_araci.py --interactive
pytest
```
Colab: `!git clone https://github.com/b4tukk/bisiklet-talebi-tahmini` ardından `%cd bisiklet-talebi-tahmini`.

## Ana bulgular
- **Zamana göre bölme** (eğitim 2011–2012/06, test 2012/07–12): rastgele bölme komşu saatleri sızdırıp skoru şişirirdi.
- Test MAE ≈ 40 bisiklet/saat (HistGB), saat profili taban çizgisi MAE ≈ 107 → ≈ %62 iyileşme; R² ≈ 0,92.
- Önceki saat ve gün talebi eklenince (canlı bilgi gerekir) MAE ≈ 30, R² ≈ 0,96.
- Model ortalama ≈ 15 bisiklet/saat eksik tahmin ediyor (2012'deki büyüme trendi).
- En büyük hatalar özel günlerde: Şükran sonrası, Noel arifesi, resmî tatil ama yoğun bir pazartesi, aşırı hava.
- %80 tahmin aralığı testte ≈ %90 kapsıyor: aralık fazla geniş.
