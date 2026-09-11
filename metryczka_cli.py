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
    "DynKcz5Pcz5", "DynPcz10m2x5UoBiA", "KarabinD Tor1", "KarabinD Tor2", "KarabinD Tor3",
    "KarabinD Tor4", "Kbz50m10", "Kbz50m10K", "Kbz50m10L", "Kbz50m10z13L", "Kbz50m20L",
    "Kbz50m30", "Kbz50m30K", "Kbz50m30L", "Kcp50m5", "Kcz25m10", "Kcz25m10z13",
    "Kcz25m20", "Kcz50m10", "Kcz50m10K", "Kcz50m10L", "Kcz50m10S", "Kcz50m10z13L",
    "Kcz50m20L", "Kcz50m30", "Kcz50m30K", "Kcz50m30L", "Kcz100m10L", "Kcz100m10z13L",
    "Kcz100m20L", "Kcz100mUkazujacy", "Kcz300m10L", "Kcz300m60s10L", "KczKoli25m10",
    "Kczkp25m10", "Kczkp25m20", "Kczkp50m10", "Kczkp50m10L", "Kczkp50m20L", "KczkpD Tor1",
    "KczkpD Tor2", "KczkpD Tor3", "KczkpD Tor4", "KczkpOpen25m10", "KczkpOpen50m10",
    "KczMS100m10", "KczMS100m20", "KczOpen25m10", "KczOpen50m10", "KczOpen100m10L",
    "KczOpen200m10L", "KczOptyka100m10L", "KczOptyka300m10L",
    "KczPrakt25m10", "Kpn10m10", "Kpn10m20", "Kpn10m30", "Kpn10m40", "Ksp25m10",
    "Ksp25m10z13", "Ksp25m20", "Ksp50m10", "Ksp50m10L", "Ksp100m10L", "Ksp100m20L",
    "KspD Tor1", "KspD Tor2", "KspD Tor3", "KspD Tor4", "KspKoli25m10", "KspMS100m10",
    "KspMS100m20", "KspOpen25m10", "KspOpen50m10", "KspOpen100m10L", "KspOptyka100m10L",
    "KspOptyka200m10L", "KspSemi50m20S", "MadKcz50m30s", "MadPcz25m30s", "MadPm25m30s",
    "MadStrzelba25m30s", "Pcp25m5", "Pcz25m10", "Pcz25m10-45ACP", "Pcz25m10z13",
    "Pcz25m20", "Pcz25m30", "Pcz25m30ISSF", "PczDM25m10z13", "PczDM25m20",
    "PczDMOpen25m10", "PczD Tor1", "PczD Tor2", "PczD Tor3", "PczD Tor4", "PczOpen25m10",
    "PczPrakt25m10", "Pdowolny50m5z8", "Pdowolny50m10", "Pkiesz10m10", "Pm25m10",
    "Pm25m20", "Pm50m10", "Pm50m20", "PmD Tor1", "PmD Tor2", "PmD Tor3", "PmD Tor4",
    "PmOpen25m10", "PmOpen50m10", "PmPrakt25m10", "Ppn10m10", "Ppn10m20", "Ppn10m30",
    "Ppn10m40", "Ppn10m60", "Psp25m10", "Psp25m10z13", "Psp25m20", "Psp25m30",
    "Psp25m30ISSF", "PspD Tor1", "PspD Tor2", "PspD Tor3", "PspD Tor4", "PspOpen25m10",
    "Pst25m20s", "Rcz25m6", "RczDAO25m6", "Rsp25m6", "Strzelba25m5", "Strzelba25m10",
    "Strzelba25m15", "Strzelba50m5", "Strzelba50m10", "StrzelbaD Tor1", "StrzelbaD Tor2",
    "StrzelbaD Tor3", "StrzelbaD Tor4", "StrzelbaOpen25m5", "StrzelbaOpen25m10",
    "StrzelbaOpen50m5", "StrzelbaPrakt25m5", "Trap10", "Trap25"
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
    Funkcja umieszcza pieczątkę w ramce na metryczce.

    Uwaga: pozycja obliczana na podstawie lokalizacji napisu "pieczątka" na metryczce.
    """
    clr = pymupdf.utils.getColor(color)

    # filler
    if opacity == 1:
        page.draw_rect(
            [x - 12, y, x + 40, y + 10],
            color=(1, 1, 1),
            fill=(1, 1, 1),
            width=1
        )

    # ramka
    page.draw_rect(
        [x - 46, y - 14, x - 46 + 127, y - 14 + 38],
        color=clr,
        width=2.5,
        stroke_opacity=opacity
    )

    font = resource_path("fonts/lmroman12-bold.otf")

    page.insert_text(
        pymupdf.Point(x - 45, y + 13),
        text,
        fontfile=font,
        fontname="f0",
        fontsize=size,
        rotate=0,
        color=clr,
        fill_opacity=opacity
    )


def stamp_dop(page, x, y):
    """
    Pieczątka "dopuszczenie".

    Uwaga: pozycja obliczana na podstawie lokalizacji napisu "pieczątka" na metryczce.
    """
    clr = pymupdf.utils.getColor("blue")

    page.draw_rect(
        [x - 95, y + 47, x - 48, y + 67],
        color=clr,
        width=2.5
    )

    font = resource_path("fonts/lmroman12-bold.otf")

    page.insert_text(
        pymupdf.Point(x - 92, y + 62),
        "DOP.",
        fontfile=font,
        fontname="f0",
        fontsize=15,
        rotate=0,
        color=clr
    )


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

    parser.add_argument(
        '-h',
        '--help',
        action='help',
        default=argparse.SUPPRESS,
        help='wyświetla ten ekran informacyjny'
    )

    parser.add_argument(
        '--pdf',
        '-p',
        type=str,
        action='store',
        required=True,
        help='ścieżka do pliku pdf z metryczkami'
    )

    args = parser.parse_args()
    file = args.pdf

    if not os.path.isfile(file):
        print(f"Wskazany plik {file} nie istnieje...")
        exit(1)

    dop = input("Czy dopuszczenie? [t]ak/[N]ie  ")

    dop_cnt = 0
    if dop in ["t", "T"]:
        dop_input = input("   na ilu metryczkach? [1] ")

        if not dop_input:
            dop_cnt = 1
        elif not dop_input.isdigit() or int(dop_input) < 1:
            print("\nProszę podać liczbę większą od 0")
            exit(1)
        else:
            dop_cnt = int(dop_input)

    print("\n")

    doc = pymupdf.open(file)
    stamp_pos = (0, 0)

    for page in doc:
        # Jawne przygotowanie strumienia zawartości strony
        # przed dodawaniem nowych elementów graficznych.
        page.wrap_contents()

        w = page.get_text("words")

        for r in w:
            if r[4] == "pieczątka":
                stamp_pos = (r[0], r[1])
                continue

            if r[4][:-1] in t_zawody:
                choice = input(
                    f"{r[4][:-1]}   -  [w]łasna/[k]lubowa/[P]omiń:  "
                )

                if choice in ["W", "w"]:
                    stamp_wlasna(
                        page,
                        stamp_pos[0],
                        stamp_pos[1]
                    )
                    print("WŁASNA")

                elif choice in ["K", "k"]:
                    stamp_klubowa(
                        page,
                        stamp_pos[0],
                        stamp_pos[1]
                    )
                    print("KLUBOWA")

                else:
                    print("POMINIĘTE\n\n")
                    continue

                # symbol dopuszczenia tylko na ostemplowanych metryczkach
                if dop_cnt > 0:
                    stamp_dop(
                        page,
                        stamp_pos[0],
                        stamp_pos[1]
                    )
                    print("DOP!")
                    dop_cnt -= 1

                print("\n")

    if doc:
        new_name = file[:-4] + "-STAMP" + file[-4:]

        doc.save(
            new_name,
            garbage=4,
            deflate=True
        )

        print(
            f"Ostemplowane metryczki zapisano do pliku: {new_name}"
        )


if __name__ == "__main__":
    main()
