#  Metryczka -- generowanie metryczek do zawodów KS Amator
#  Copyright (C) 2023-2025  mc (kontakt@zakaznoszeniabroni.pl)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import os
import pymupdf
import sys


t_zawody = [
    # < 10 strzalow
    "Pcp25m5", "Rcz25m6", "RczDAO25m6", "Rsp25m6", "Strzelba25m5", "Strzelba50m5",
    "Kcp50m5", "StrzelbaOpen50m5", "StrzelbaOpen25m5",
    # 10 strzalow
    "Kbz50m10", "Kbz50m10K", "Kbz50m10L", "Kcz25m10", "Kcz50m10", "Kczkp25m10",
    "Kcz50m10K", "Kcz50m10L", "Kcz50m10S", "Kcz100m10L", "Kcz300m10L", "Kczkp50m10",
    "KczKoli25m10", "Kczkp50m10L", "KczkpOpen25m10", "KczkpOpen50m10",
    "KczMS100m10", "KczOpen25m10", "KczOpen50m10", "KczOpen100m10L",
    "KczOpen200m10L", "KczOptyka100m10L", "KczOptyka300m10L", "KczPrakt25m10", "Kpn10m10",
    "Ksp25m10", "Ksp50m10", "Ksp50m10L", "Ksp100m10L", "KspKoli25m10", "KspMS100m10",
    "KspOpen25m10", "KspOpen50m10", "KspOpen100m10L", "KspOptyka100m10L", "Psp25m10",
    "KspOptyka200m10L", "Pcz25m10", "PczDMOpen25m10", "PczOpen25m10", "Pkiesz10m10",
    "Pm25m10", "Pm50m10", "PmOpen25m10", "PmOpen50m10", "PmPrakt25m10", "Ppn10m10",
    "PspOpen25m10", "Strzelba25m10", "Strzelba50m10", "StrzelbaOpen25m10",
    "KczOpen300m10L", "Pdowolny50m10",
    # >10 & < 20 strzalow
    "Kbz50m10z13L", "Kcz25m10z13", "Kcz50m10z13L", "Kcz100m10z13L", "Ksp25m10z13",
    "Pcz25m10z13", "PczDM25m10z13", "Psp25m10z13", "Strzelba25m15",
    # 20 strzalow
    "Kbz50m20L", "Kcz25m20", "Kcz50m20L", "Kcz100m20L", "Kczkp25m20", "Kczkp50m20L",
    "KczMS100m20", "Kpn10m20", "Ksp25m20", "Ksp100m20L", "KspMS100m20", "KspSemi50m20S",
    "Pcz25m20", "PczDM25m20", "Pm25m20",  "Pm50m20", "Ppn10m20", "Psp25m20", "Pst25m20s",
    # 30 strzalow
    "Kbz50m30", "Kbz50m30K", "Kbz50m30L", "Kcz50m30", "Kcz50m30K", "Kcz50m30L",
    "Kpn10m30", "Pcz25m30", "Pcz25m30ISSF", "Ppn10m30", "Psp25m30", "Psp25m30ISSF",
]


def resource_path(relative_path):
    """Zmienia ścieżkę do pliku na potrzeby uruchomienia przez pyinstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def stamp(page, x, y, color, text, size=20, opacity=1):
    """
    Funkcja umieszcza pieczątkę w ramce ma matryczce.

    Uwaga: pozycja obliczna na podstawie lokalizacji napisu "pieczątka" na metryczce.
    """
    clr = pymupdf.utils.getColor(color)
    # filler
    if opacity == 1:
        page.draw_rect([x-12, y, x+40, y+10], color=(1, 1, 1), fill=(1, 1, 1), width=1)
    # ramka
    page.draw_rect([x-46, y-14, x-46+127, y-14+38], color=clr,
                   width=2.5, stroke_opacity=opacity)
    font = resource_path("fonts/lmroman12-bold.otf")
    page.insert_text(pymupdf.Point(x-45, y+13),
                     text,
                     fontfile=font,
                     fontname="f0",
                     fontsize=size,
                     rotate=0,
                     color=clr,
                     fill_opacity=opacity)


def stamp_dop(page, x, y, y_offset=0):
    """
    Pieczątka "dopuszczenie".

    Uwaga: pozycja obliczna na podstawie lokalizacji napisu "pieczątka" na metryczce.
    """
    clr = pymupdf.utils.getColor("blue")
    page.draw_rect([x-95, y+47+y_offset, x-48, y+67+y_offset], color=clr, width=2.5)
    font = resource_path("fonts/lmroman12-bold.otf")
    page.insert_text(pymupdf.Point(x-92, y+62+y_offset),
                     "DOP.",
                     fontfile=font,
                     fontname="f0",
                     fontsize=15,
                     rotate=0,
                     color=clr)


def card_hide(page, x, y, y_offset=0):
    page.draw_rect([x-361, y-18, x+119, y+88+y_offset], color=(1, 1, 1), fill=(1, 1, 1), width=1)


def stamp_wlasna(page, x, y, opacity=1):
    stamp(page, x, y, "mediumseagreen", "WŁASNA", 25, opacity)


def stamp_klubowa(page, x, y, opacity=1):
    stamp(page, x, y, "firebrick1", "KLUBOWA", 21, opacity)


def main():
    parser = argparse.ArgumentParser(
        prog='metryczki.py',
        description='Program do stemplowania metryczek na zawody KS Amator. '
                    'Po wskazaniu pliku z metryczkami program umożliwi dodanie pieczątki '
                    '"KLUBOWA" lub "WŁASNA" oraz opcjonalnie "DOP." Edytowany przez '
                    'program plik z metryczkami zostanie zapisany w tym samym katalogu '
                    'co plik źródłowy, ale z dopisanym tekstem -stamp w nazwie pliku. '
                    'UWAGA: program jest zgodny ze wzorem metryczek KS Amator '
                    ' obowiązującym od dnia 25.04.2025.',
        epilog='Autor: m_c',
        add_help=False
    )
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='wyświetla ten ekran informacyjny')
    parser.add_argument('--pdf', '-p', type=str, action='store', required=True,
                        help='ścieżka do pliku pdf z metryczkami')
    args = parser.parse_args()
    file = args.pdf
    if not os.path.isfile(file):
        print(f"Wskazany plik {file} nie istnieje...")
        exit(1)

    offset = input("Czy są konkurencje 20-strzałowe (większa metryczka)? [t]ak/[N]ie  ")
    offset_val = 0
    if offset in ["t", "T"]:
        offset_val = 28

    dop = input("Czy dopuszczenie? [t]ak/[N]ie  ")
    dop_cnt = 0
    if dop in ["t", "T"]:
        dop_cnt = 1
    print("\n")

    doc = pymupdf.open(file)
    stamp_pos = (0, 0)
    for page in doc:
        w = page.get_text("words")
        for r in w:
            if r[4] == "pieczątka":
                stamp_pos = (r[0], r[1])
                continue
            if r[4][:-1] in t_zawody:
                choice = input(f"{r[4][:-1]}   -  [w]łasna/[k]lubowa/[z]akryj/[P]omiń:  ")
                if choice in ["W", "w"]:
                    stamp_wlasna(page, stamp_pos[0], stamp_pos[1], 0.6)
                    print("WŁASNA")
                elif choice in ["K", "k"]:
                    stamp_klubowa(page, stamp_pos[0], stamp_pos[1], 0.6)
                    print("KLUBOWA")
                elif choice in ["Z", "z"]:
                    card_hide(page, stamp_pos[0], stamp_pos[1], offset_val)
                    print("ZAKRYTE\n\n")
                    continue  # symbol dopuszczenia tylko na ostemplowanych metryczkach
                else:
                    print("POMINIĘTE\n\n")
                    continue  # symbol dopuszczenia tylko na ostemplowanych metryczkach
                if dop_cnt > 0:
                    stamp_dop(page, stamp_pos[0], stamp_pos[1], offset_val)
                    print("DOP!")
                    dop_cnt -= 1
                print("\n")

    if doc:
        new_name = file[:-4] + "-STAMP" + file[-4:]
        doc.save(new_name)
        print(f"Ostemplowane metryczki zapisano do pliku: {new_name}")


if __name__ == "__main__":
    main()
