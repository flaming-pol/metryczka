#  Metryczka -- generowanie metryczek do zawodów KS Amator
#  Copyright (C) 2023-2026  mc (kontakt@zakaznoszeniabroni.pl)
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
import re
import sys
from enum import IntEnum

import pymupdf
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
)

from gui.metryczka_ui import Ui_MainWindow
from zawody import t_zawody


def open_pdf(filename):
    """
    Otwiera PDF w domyślnej aplikacji systemu Windows, Linux lub macOS.
    """
    pdf_url = QUrl.fromLocalFile(os.path.abspath(filename))
    if not QDesktopServices.openUrl(pdf_url):
        raise OSError("System nie znalazł aplikacji do otwierania plików PDF.")


def resource_path(relative_path):
    """Zmienia ścieżkę do pliku na potrzeby uruchomienia przez pyinstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def stamp(page, x, y, color, text, size=20, opacity=1):
    """
    Funkcja umieszcza pieczątkę w ramce ma metryczce.

    Uwaga: pozycja obliczana na podstawie lokalizacji napisu "pieczątka" na metryczce.
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

    Uwaga: pozycja obliczana na podstawie lokalizacji napisu "pieczątka" na metryczce.
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


def stamp_wlasna(page, x, y, opacity=1):
    stamp(page, x, y, "mediumseagreen", "WŁASNA", 25, opacity)


def stamp_klubowa(page, x, y, opacity=1):
    stamp(page, x, y, "firebrick1", "KLUBOWA", 21, opacity)


class CardSize(IntEnum):
    SMALL = 0
    MEDIUM = 28
    BIG = 56


class ScoreCard:
    def __init__(self, page, page_number, X=0, Y=0):
        self.X = X
        self.Y = Y
        self.page = page
        self.page_number = page_number
        self.rect = None
        self.name = ""
        self.locked = False

    def __repr__(self):
        return self.name


class ScoreSheet:
    def __init__(self, filename):
        self.filename = filename
        self.cards = []
        self.card_size = CardSize.SMALL
        self._doc = None
        self._load()

    def _load(self):
        if self._doc:
            self._doc.close()
        self._doc = pymupdf.open(self.filename)
        for page_number, page in enumerate(self._doc):
            w = page.get_text("words")
            card = None
            for r in w:
                if not card and (r[4] == "pieczątka"):
                    card = ScoreCard(page, page_number, r[0], r[1])
                if card and (r[4][:-1] in t_zawody):
                    shoots = 0
                    card.name = r[4][:-1]
                    mpos = card.name.rfind('m')
                    if mpos > 0:
                        s = card.name[mpos+1:]
                        if s.isdecimal() == True and len(s) in [1, 2]:
                            shoots = int(s)
                        elif not s.isdecimal():
                            # np. Pcz25m10z13
                            # np. Pcz25m30ISSF
                            # np. Kcz50m20L
                            for i, c in enumerate(s):
                                if not c.isdecimal():
                                    shoots = int(s[:i])
                                    break
                        # print(f"{card.name} : {shoots}")
                        if (shoots > 10) and (shoots <= 20) and (
                                self.card_size < CardSize.MEDIUM):
                            self.card_size = CardSize.MEDIUM
                        elif (shoots > 20) and (shoots <= 30) and (
                                self.card_size < CardSize.BIG):
                            self.card_size = CardSize.BIG
                        if shoots > 30 or shoots == 0:
                            QMessageBox.critical(
                                None, "Oh!",
                                f"W tej wersji program obsługuje max. konkurencje 30-strzałowe ({card.name} : {shoots})!"
                            )
                            card = None
                            continue
                    self.cards.append(card)
                    card = None

        for card in self.cards:
            card.rect = self._find_card_rect(card)

    def _find_card_rect(self, card):
        """
        Zwraca zewnętrzny prostokąt metryczki.

        Obrys jest odczytywany z samego PDF-a, dzięki czemu składanie działa
        zarówno dla zwykłych, jak i wyższych metryczek.
        """
        point = pymupdf.Point(card.X, card.Y)
        candidates = []
        for drawing in card.page.get_drawings():
            rect = pymupdf.Rect(drawing["rect"])
            if (
                rect.contains(point)
                and rect.width >= card.page.rect.width * 0.7
                and 80 <= rect.height <= 200
            ):
                candidates.append(rect)
        if candidates:
            return max(candidates, key=lambda rect: rect.get_area())

        # Zapas dla zgodnego układu, w którym obrys nie jest osobną ścieżką.
        return pymupdf.Rect(
            card.X - 365.5,
            card.Y - 22,
            card.X + 123,
            card.Y + 92 + self.card_size.value,
        )

    def _copy_page_background(self, output_page, page_number):
        """
        Kopiuje marginesy strony bez środkowego obszaru z metryczkami.
        """
        source_page = self._doc[page_number]
        page_cards = [
            card for card in self.cards if card.page_number == page_number
        ]
        content_rect = pymupdf.Rect(
            min(card.rect.x0 for card in page_cards),
            min(card.rect.y0 for card in page_cards),
            max(card.rect.x1 for card in page_cards),
            max(card.rect.y1 for card in page_cards),
        )
        page_rect = source_page.rect
        gap = 1
        background_parts = (
            pymupdf.Rect(0, 0, page_rect.width, content_rect.y0 - gap),
            pymupdf.Rect(0, content_rect.y1 + gap, page_rect.width, page_rect.height),
            pymupdf.Rect(
                0,
                content_rect.y0 - gap,
                content_rect.x0 - gap,
                content_rect.y1 + gap,
            ),
            pymupdf.Rect(
                content_rect.x1 + gap,
                content_rect.y0 - gap,
                page_rect.width,
                content_rect.y1 + gap,
            ),
        )
        for clip in background_parts:
            if not clip.is_empty:
                output_page.show_pdf_page(
                    clip,
                    self._doc,
                    page_number,
                    clip=clip,
                    keep_proportion=False,
                )

    def save(self, fp, selected_cards=None):
        if selected_cards is None:
            self._doc.save(fp)
            return

        target_slots = self.cards[:len(selected_cards)]
        last_page_number = target_slots[-1].page_number
        output_doc = pymupdf.open()
        try:
            for page_number in range(last_page_number + 1):
                source_page = self._doc[page_number]
                output_page = output_doc.new_page(
                    width=source_page.rect.width,
                    height=source_page.rect.height,
                )
                self._copy_page_background(output_page, page_number)

            for source_card, target_slot in zip(selected_cards, target_slots):
                # Metoda "show_pdf_page" z biblioteki pymupdf:
                # Display a page of another PDF. This is similar to Page.insert_image()
                #  but the source page will appear like a copy of itself and
                #  will not be rasterized.
                output_doc[target_slot.page_number].show_pdf_page(
                    target_slot.rect,
                    self._doc,
                    source_card.page_number,
                    clip=source_card.rect,
                    keep_proportion=False,
                )

            output_doc.set_metadata(self._doc.metadata)
            output_doc.save(fp, garbage=4, deflate=True)
        finally:
            output_doc.close()

    def reset(self):
        self.cards = []
        self._load()


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.score_sheet = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.ui.lbl_filename.setHidden(True)
        self.ui.pbWczytaj.clicked.connect(self.load_data)
        self.ui.pbZapisz.clicked.connect(self.save_data)
        self.ui.pbReset.clicked.connect(self.reset_scene)
        for i in range(1, 13):
            btn_klubowa = getattr(self.ui, f"k{i}_klubowa")
            btn_wlasna = getattr(self.ui, f"k{i}_wlasna")
            cb_dop = getattr(self.ui, f"k{i}_dop")
            btn_klubowa.clicked.connect(lambda c, x=i: self.uncheck(f"k{x}_wlasna"))
            btn_wlasna.clicked.connect(lambda c, y=i: self.uncheck(f"k{y}_klubowa"))
            cb_dop.clicked.connect(lambda c, y=i: self.dop_check(y))

    def reset_scene(self):
        self.score_sheet = None
        self.ui.cb_przezroczyste.setChecked(True)
        self.ui.lbl_filename.setHidden(True)
        for i in range(1, 13):
            text = getattr(self.ui, f"k{i}_edit")
            btn_klubowa = getattr(self.ui, f"k{i}_klubowa")
            btn_wlasna = getattr(self.ui, f"k{i}_wlasna")
            cb_dop = getattr(self.ui, f"k{i}_dop")
            cb_enable = getattr(self.ui, f"k{i}_en")
            text.setText("")
            btn_klubowa.setEnabled(False)
            btn_klubowa.setChecked(False)
            btn_wlasna.setEnabled(False)
            btn_wlasna.setChecked(False)
            cb_dop.setEnabled(False)
            cb_dop.setChecked(False)
            cb_enable.setEnabled(False)
            cb_enable.setChecked(False)

    def uncheck(self, obj_name):
        w = getattr(self.ui, obj_name)
        w.setChecked(False)

    def dop_check(self, dop_id):
        for i in range(1, 13):
            if i == dop_id:
                continue
            cb_dop = getattr(self.ui, f"k{i}_dop")
            if cb_dop.isChecked():
                cb_dop.setChecked(False)

    def load_data(self):
        self.reset_scene()
        filename = QFileDialog.getOpenFileName(
            parent=self, caption="Otwórz...", filter="Pliki metryczek PDF (*.pdf)",
        )
        if not filename or not filename[0]:
            return
        self.score_sheet = ScoreSheet(filename[0])
        for i, c in enumerate(self.score_sheet.cards):
            if i >= 12:
                QMessageBox.warning(
                    self, "Oh!",
                    "W obecnej wersji program obsługuje max 12 metryczek!"
                )
                break
            text = getattr(self.ui, f"k{i+1}_edit")
            btn_klubowa = getattr(self.ui, f"k{i+1}_klubowa")
            btn_wlasna = getattr(self.ui, f"k{i+1}_wlasna")
            cb_dop = getattr(self.ui, f"k{i+1}_dop")
            cb_enable = getattr(self.ui, f"k{i+1}_en")
            text.setText(c.name)
            btn_klubowa.setEnabled(True)
            btn_wlasna.setEnabled(True)
            cb_dop.setEnabled(True)
            cb_enable.setEnabled(True)
            cb_enable.setChecked(True)
        if self.ui.k1_edit.text() == "":
            QMessageBox.critical(
                self, "Oh!",
                "Nie udało się wczytać żadnej metryczki!"
            )
            self.score_sheet = None
        else:
            self.ui.lbl_filename.setText(os.path.basename(filename[0]))
            self.ui.lbl_filename.setHidden(False)

    def save_data(self):
        if not self.score_sheet:
            return
        proposed_filename = (f"{self.score_sheet.filename[:-4]}-STAMP"
                             f"{self.score_sheet.filename[-4:]}")
        filename = QFileDialog.getSaveFileName(
            parent=self, caption="Zapisz...", filter="Pliki metryczek PDF (*.pdf)",
            directory=proposed_filename
        )
        if not filename or not filename[0]:
            return
        opacity = bool(self.ui.cb_przezroczyste.isChecked())
        card_size = self.score_sheet.card_size
        selected_cards = []
        for i, c in enumerate(self.score_sheet.cards):
            if i >= 12:
                QMessageBox.warning(
                    self, "Oh!",
                    "W obecnej wersji program obsługuje max 12 metryczek!"
                )
                break
            klubowa = getattr(self.ui, f"k{i+1}_klubowa")
            wlasna = getattr(self.ui, f"k{i+1}_wlasna")
            dop = getattr(self.ui, f"k{i+1}_dop")
            cb_enable = getattr(self.ui, f"k{i+1}_en")
            if not cb_enable.isChecked():
                continue
            selected_cards.append(c)
            if klubowa.isChecked():
                stamp_klubowa(c.page, c.X, c.Y, 0.60 if opacity else 1)
            if wlasna.isChecked():
                stamp_wlasna(c.page, c.X, c.Y, 0.60 if opacity else 1)
            if dop.isChecked():
                stamp_dop(c.page, c.X, c.Y, card_size.value)
        if not selected_cards:
            QMessageBox.warning(
                self, "Oh!", "Nie wybrano żadnej metryczki do zapisania!"
            )
            return
        self.score_sheet.save(filename[0], selected_cards)
        try:
            open_pdf(filename[0])
        except Exception as error:
            QMessageBox.warning(
                self,
                "Nie udało się otworzyć PDF",
                f"Plik został zapisany poprawnie, ale nie udało się go "
                f"automatycznie otworzyć:\n{error}",
            )
        else:
            QMessageBox.information(
                self, "Zrobione!",
                f"Ostemplowane metryczki zapisano do: {filename[0]}"
            )
        self.score_sheet.reset()


def run_gui():
    """
    Uruchomienie aplikacji w trybie graficznym.
    """
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainUI()
    window.show()
    sys.exit(app.exec())


def run_cli(source_file, dest_file, competitions, dop=False):
    """
    Uruchomienie aplikacji w trybie konsolowym.
    """
    if not os.path.isfile(source_file):
        print(f"Wskazany plik z metryczkami ({source_file}) nie istnieje...")
        sys.exit(1)
    if not dest_file.endswith(".pdf"):
        dest_file += ".pdf"
    if os.path.isfile(dest_file):
        print(f"Uwaga! Plik wynikowy ({dest_file}) istnieje i będze nadpisany!\n")

    pattern = r"^[A-Za-z][A-Za-z0-9]*:[wkb](?:,[A-Za-z][A-Za-z0-9]*:[wkb])*$"
    if not re.match(pattern, competitions):
        print("Błąd składni w definicji konkurencji! Konkurencje definiujemy zgodnie "
              "ze wzorcem: NAZWA:OPCJE, gdzie opcje to k,w,b.\n"
              "Przykład: metryczka.py --no-gui --competitions=Kcz10m5:w,Pcz25m10z13:k")
        sys.exit(1)

    comp_split = competitions.split(",")
    comp_split = [tuple(x.split(":")) for x in comp_split]

    score_sheet = ScoreSheet(source_file)
    selected_cards = []
    for comp, o in comp_split:
        found = False
        for c in score_sheet.cards:
            if comp.upper() == c.name.upper():
                selected_cards.append(c)
                if o == "k":
                    stamp_klubowa(c.page, c.X, c.Y, 0.60)
                if o == "w":
                    stamp_wlasna(c.page, c.X, c.Y, 0.60)
                if dop:
                    stamp_dop(c.page, c.X, c.Y, score_sheet.card_size.value)
                    o += "D"
                    dop = False
                print(f"{comp}\t\t -> {o.upper()}")
                found = True
                break
        if not found:
            print(f"Uwaga: konkurencja {comp} nie znaleziona na metryczkach!")
    if not selected_cards:
        print("Nie wybrano żadnej metryczki do zapisania!")
        sys.exit(1)
    score_sheet.save(dest_file, selected_cards)
    print(f"\nZapisano do {dest_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='metryczka.py',
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
    parser.add_argument('--no-gui', '-n', action='store_true', required=False,
                        help='uruchamia program w trybie konsolowym')
    parser.add_argument('--in', dest="input_file", action='store', required=False,
                        help='ścieżka do pliku pdf z metryczkami (plik źródłowy)')
    parser.add_argument('--out', dest="output_file", action='store', required=False,
                        help='nazwa pliku z wstawionymi pieczątkami. Jeśli nie podasz '
                        'nazwy pliku, ostęplowane metryczki zostaną zapisane pod nazwą '
                        'taką jak plik źródłowy tylko z dopiskiem "-stamp"')
    parser.add_argument('-d', action='store_true', required=False,
                        help='dopuszczenie - pierwsza metryczka będzie oznaczona "DOP"')
    parser.add_argument('--competitions', '-c', action='store', required=False,
                        help='Nazwy konkurencji, które chcesz umieścić na metryczkach, '
                        'wg. formatu: NAZWA_KONKURECNJI:OPCJE. Program przewiduje następujące '
                        'opcje do konkurencji: "w" - pieczątka "własna", "k" - pieczątka '
                        '"klubowa", "b" - brak pieczątki. Gdy strzelasz więcej konkurencji '
                        'rozdziel je przecinkiem. Przykład: Kcz10m5:w,Pcz25m10z13:k program '
                        'wygeneruje metryczki dla konkurencji "Kcz10m5" z pieczątką "własna" '
                        'oraz dla konkurencji Pcz25m10z13 z pieczątką "klubowa". '
                        'Wskazane konkurencje muszą znajdować się na metryczkach źródłowych.')
    args = parser.parse_args()

    if not args.no_gui:
        run_gui()
    else:
        missing = []
        if args.input_file is None:
            missing.append("--in")
        if args.output_file is None and args.input_file is not None:
            dest_file = args.input_file[:-4] + "-STAMP.pdf"
        elif args.output_file is not None:
            dest_file = args.output_file
        if args.competitions is None:
            missing.append("--competitions")
        if missing:
            parser.error(
                "w trybie konsolowym wymagane są parametry: " + ", ".join(missing)
            )
        run_cli(source_file=args.input_file,
                dest_file=dest_file,
                competitions=args.competitions,
                dop=args.d)
