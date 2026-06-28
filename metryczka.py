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
    def __init__(self, page, X=0, Y=0):
        self.X = X
        self.Y = Y
        self.page = page
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
        self._doc = pymupdf.open(self.filename)
        for page in self._doc:
            w = page.get_text("words")
            card = None
            for r in w:
                if not card and (r[4] == "pieczątka"):
                    card = ScoreCard(page, r[0], r[1])
                if card and (r[4][:-1] in t_zawody):
                    shoots = 0
                    card.name = r[4][:-1]
                    mpos = card.name.rfind('m')
                    if mpos > 0:
                        s = card.name[mpos+1:]
                        if (len(s) == 1) or (len(s) == 2 and s.isdecimal() == True):
                            shoots = int(s)
                        elif not s.isdecimal():
                            c_tmp = ""
                            for c in reversed(s):
                                if c.isdecimal():
                                    c_tmp += c
                                else:
                                    break
                            if c_tmp:
                                shoots = int(c_tmp[::-1])
                        # print(shoots)
                        if (shoots >= 15) and (shoots < 30) and (
                                self.card_size < CardSize.MEDIUM):
                            self.card_size = CardSize.MEDIUM
                        if shoots > 20 or shoots == 0:
                            QMessageBox.critical(
                                None, "Oh!",
                                f"W tej wersji program obsługuje max. konkurencje 20-strzałowe ({card.name})!"
                            )
                            card = None
                            continue
                    self.cards.append(card)
                    card = None

    def save(self, fp):
        self._doc.save(fp)

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
                card_hide(c.page, c.X, c.Y, card_size.value)
                continue
            if klubowa.isChecked():
                stamp_klubowa(c.page, c.X, c.Y, 0.60 if opacity else 1)
            if wlasna.isChecked():
                stamp_wlasna(c.page, c.X, c.Y, 0.60 if opacity else 1)
            if dop.isChecked():
                stamp_dop(c.page, c.X, c.Y, card_size.value)
        self.score_sheet.save(filename[0])
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
