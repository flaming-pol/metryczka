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

import os
import sys
from enum import IntEnum

import pymupdf
from PyQt6.QtWidgets import (
    QDialog,
    QApplication,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QMessageBox,
)

from gui.metryczka_ui import Ui_MainWindow
from metryczka_cli import (
    stamp_dop,
    stamp_wlasna,
    stamp_klubowa,
    card_hide,
    t_zawody,
)


class CardSize(IntEnum):
    SMALL = 0
    MEDIUM = 28


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
                            if not s[-1].isdecimal():
                                # usuniecie literek z końca
                                for i, c in enumerate(reversed(s)):
                                    if c.isdecimal():
                                        s = s[:-i]
                                        break
                            for i, c in enumerate(reversed(s)):
                                # usuniecie "z" w przypadku 10z13, 20z30 itp.
                                if not c.isdecimal():
                                    s = s[i+1:]
                                    break
                            shoots = int(s)
                        print(f"{card.name} : {shoots}")
                        if (shoots >= 15) and (shoots < 30) and (
                                self.card_size < CardSize.MEDIUM):
                            self.card_size = CardSize.MEDIUM
                        if shoots > 20 or shoots == 0:
                            QMessageBox.critical(
                                None, "Oh!",
                                f"W tej wersji program obsługuje max. konkurencje 20-strzałowe ({card.name} : {shoots})!"
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
                QMessageBox.critical(
                    self, "Oh!",
                    "Pieczątka z dopuszczeneim może być tylko na jednej metryczce!"
                )
                cb_main_dop = getattr(self.ui, f"k{dop_id}_dop")
                cb_main_dop.setChecked(False)

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
        os.startfile(filename[0])   # Otwarcie nowego PDF po zapisie
        QMessageBox.information(
            self, "Zrobione!",
            f"Ostemplowane metryczki zapisano do: {filename[0]}"
        )
        self.score_sheet.reset()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainUI()
    window.show()
    sys.exit(app.exec())
