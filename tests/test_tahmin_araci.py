import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tahmin_araci as t  # noqa: E402


@pytest.fixture(scope="module")
def paket():
    return t.yukle()


def test_aralik_siralamasi(paket):
    r = t.tahmin("2012-10-16", 8, 17, paket=paket)
    assert 0 <= r["alt"] <= r["nokta"] <= r["ust"]


def test_is_gunu_zirve_geceden_yuksek(paket):
    zirve = t.tahmin("2012-10-16", 8, 17, paket=paket)["nokta"]
    gece = t.tahmin("2012-10-16", 3, 17, paket=paket)["nokta"]
    assert zirve > 3 * gece


def test_kotu_hava_talebi_dusurur(paket):
    acik = t.tahmin("2012-10-16", 17, 18, hava=1, paket=paket)["nokta"]
    yagis = t.tahmin("2012-10-16", 17, 18, nem=95, ruzgar=25, hava=3, paket=paket)["nokta"]
    assert yagis < acik


def test_hafta_sonu_oglen_pik_sabahtan_yuksek(paket):
    assert t.tahmin("2012-10-20", 14, 22, paket=paket)["nokta"] > t.tahmin("2012-10-20", 7, 22, paket=paket)["nokta"]


@pytest.mark.parametrize("kotu", [dict(tarih="16.10.2012", saat=8, sicaklik=17), dict(tarih="2012-10-16", saat=24, sicaklik=17),
                                  dict(tarih="2012-10-16", saat=8, sicaklik=99), dict(tarih="2012-10-16", saat=8, sicaklik=17, hava=7),
                                  dict(tarih="2012-10-16", saat=8, sicaklik=17, nem=130)])
def test_gecersiz_girdi_reddedilir(kotu, paket):
    with pytest.raises(ValueError):
        t.tahmin(paket=paket, **kotu)


def test_haftanin_gunu_ve_is_gunu(paket):
    g = t.dogrula("2012-10-21", 8, 17)  # Pazar
    assert t.satir_olustur(g, paket).iloc[0].workingday == 0
    g = t.dogrula("2012-10-22", 8, 17)  # Pazartesi
    assert t.satir_olustur(g, paket).iloc[0].workingday == 1
    g = t.dogrula("2012-10-22", 8, 17, tatil=1)
    assert t.satir_olustur(g, paket).iloc[0].workingday == 0


def test_yorum_seviyeleri():
    assert "çok yoğun" in t.yorumla("2012-10-16", 8, dict(nokta=700, alt=300, ust=1200))
    assert "sakin" in t.yorumla("2012-10-16", 3, dict(nokta=20, alt=10, ust=40))


def test_cli_cikis_kodlari():
    assert t.main(["--tarih", "2012-10-16", "--saat", "8", "--sicaklik", "17"]) == 0
    assert t.main(["--tarih", "yanlis", "--saat", "8", "--sicaklik", "17"]) == 2
