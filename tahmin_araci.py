"""Bisiklet talebi tahmin aracı (komut satırı).

Kullanım:
    python tahmin_araci.py --tarih 2012-10-16 --saat 8 --sicaklik 17 --hava 1
    python tahmin_araci.py --interactive

Model, `bisiklet_talebi_tahmini.ipynb` çalıştırılınca `models/model.joblib` olarak kaydedilir.
Çıktı bir nokta tahmini ve yaklaşık %80'lik aralıktır (aralık eğitim dönemindeki hatalardan türetilir).
"""
import argparse
import datetime as dt
import os
import sys

import joblib
import numpy as np
import pandas as pd

MODEL_YOLU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "model.joblib")


def dogrula(tarih: str, saat, sicaklik, nem=60.0, ruzgar=10.0, hava=1, tatil=0) -> dict:
    """Girdileri doğrular ve türler; geçersizse ValueError fırlatır."""
    try:
        t = dt.date.fromisoformat(str(tarih))
    except ValueError:
        raise ValueError(f"tarih YYYY-AA-GG biçiminde olmalı (verilen: {tarih})") from None
    saat, hava, tatil = int(saat), int(hava), int(tatil)
    sicaklik, nem, ruzgar = float(sicaklik), float(nem), float(ruzgar)
    if not 0 <= saat <= 23:
        raise ValueError("saat 0–23 arasında olmalı")
    if not -20 <= sicaklik <= 50:
        raise ValueError("sıcaklık -20 ile 50 °C arasında olmalı")
    if not 0 <= nem <= 100:
        raise ValueError("nem 0–100 arasında olmalı")
    if not 0 <= ruzgar <= 80:
        raise ValueError("rüzgâr 0–80 km/sa arasında olmalı")
    if hava not in (1, 2, 3, 4):
        raise ValueError("hava 1 (açık) – 4 (şiddetli yağış) arasında olmalı")
    if tatil not in (0, 1):
        raise ValueError("tatil 0 veya 1 olmalı")
    return dict(t=t, saat=saat, sicaklik=sicaklik, nem=nem, ruzgar=ruzgar, hava=hava, tatil=tatil)


def yukle(yol: str = MODEL_YOLU) -> dict:
    if not os.path.exists(yol):
        raise FileNotFoundError("models/model.joblib yok. Önce not defterini çalıştırın.")
    return joblib.load(yol)


def satir_olustur(g: dict, paket: dict) -> pd.DataFrame:
    t, saat = g["t"], g["saat"]
    wd = (t.weekday() + 1) % 7  # UCI: 0 = Pazar
    satir = dict(
        season=paket["mevsim"][t.month], yr=int(t.year >= 2012), mnth=t.month, hr=saat,
        hr_sin=np.sin(2 * np.pi * saat / 24), hr_cos=np.cos(2 * np.pi * saat / 24),
        holiday=g["tatil"], weekday=wd, workingday=int(wd not in (0, 6) and not g["tatil"]),
        weathersit=g["hava"], temp_c=g["sicaklik"], hum_pct=g["nem"], ruzgar_kmh=g["ruzgar"],
    )
    return pd.DataFrame([satir])[paket["kolonlar"]]


def tahmin(tarih, saat, sicaklik, nem=60.0, ruzgar=10.0, hava=1, tatil=0, paket: dict | None = None) -> dict:
    """{'nokta', 'alt', 'ust'} döndürür (kiralama/saat)."""
    paket = paket or yukle()
    g = dogrula(tarih, saat, sicaklik, nem, ruzgar, hava, tatil)
    nokta = max(float(paket["model"].predict(satir_olustur(g, paket))[0]), 0.0)
    alt = float(np.expm1(np.log1p(nokta) + paket["q10"]))
    ust = float(np.expm1(np.log1p(nokta) + paket["q90"]))
    return {"nokta": nokta, "alt": alt, "ust": ust}


def yorumla(tarih, saat, r: dict) -> str:
    seviye = "çok yoğun" if r["nokta"] >= 500 else "yoğun" if r["nokta"] >= 250 else "orta" if r["nokta"] >= 100 else "sakin"
    return f"{tarih} saat {int(saat):02d}:00: tahmini talep ≈ {r['nokta']:.0f} bisiklet/saat ({seviye}); yaklaşık %80 aralık {r['alt']:.0f}–{r['ust']:.0f}."


def etkilesimli() -> dict:
    def sor(m, v):
        return input(f"{m} [{v}]: ").strip() or v
    return dict(tarih=sor("Tarih (YYYY-AA-GG)", "2012-10-16"), saat=sor("Saat (0-23)", "8"), sicaklik=sor("Sıcaklık °C", "17"),
                nem=sor("Nem %", "60"), ruzgar=sor("Rüzgâr km/sa", "10"), hava=sor("Hava (1 açık … 4 şiddetli)", "1"), tatil=sor("Resmî tatil (0/1)", "0"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Saatlik bisiklet talebi tahmini")
    ap.add_argument("--tarih")
    ap.add_argument("--saat")
    ap.add_argument("--sicaklik")
    ap.add_argument("--nem", default=60)
    ap.add_argument("--ruzgar", default=10)
    ap.add_argument("--hava", default=1)
    ap.add_argument("--tatil", default=0)
    ap.add_argument("--interactive", action="store_true")
    a = ap.parse_args(argv)
    try:
        girdi = etkilesimli() if a.interactive else dict(tarih=a.tarih, saat=a.saat, sicaklik=a.sicaklik, nem=a.nem, ruzgar=a.ruzgar, hava=a.hava, tatil=a.tatil)
        if not a.interactive and None in (a.tarih, a.saat, a.sicaklik):
            ap.error("--tarih, --saat ve --sicaklik zorunlu (ya da --interactive)")
        print(yorumla(girdi["tarih"], girdi["saat"], tahmin(**girdi)))
    except (ValueError, FileNotFoundError) as e:
        print("Hata:", e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
