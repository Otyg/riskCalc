#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (c) 2025 Martin Vesterlund
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import annotations

import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List
from currencies import Currency

from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from otyg_risk_base.hybrid import HybridRisk
from filesystem.repo import DiscreteThresholdsRepository
from filesystem.questionaires_repo import JsonQuestionairesRepository
from riskcalculator.questionaire import Questionaires
from filesystem.paths import ensure_user_data_initialized, packaged_root
from otyg_risk_base.montecarlo import MonteCarloRange
from common import D

BASE_DIR = Path(__file__).parent


p = ensure_user_data_initialized()
os.environ["TEMPLATES_DIR"] = str(packaged_root() / "templates")
os.environ["DATA_DIR"] = str(p["data"])

TEMPLATES_DIR = Path(os.environ.get("TEMPLATES_DIR", str(BASE_DIR / "templates")))
DATA_DIR = Path(os.environ.get("DATA_DIR", str(BASE_DIR / "data")))

DEFAULT_QUESTIONAIRES_SET = "default"
QUESTIONAIRES_DIR = Path(str(BASE_DIR / "questionaires"))
AVAILABLE_CURRENCIES = Currency.get_currency_formats()

questionaires_repo = None
discrete_thresholds_repo = None
questionaires_repo = JsonQuestionairesRepository(DATA_DIR / "questionaires")
discrete_thresholds_repo = DiscreteThresholdsRepository(
    DATA_DIR / "discrete_thresholds.json"
)


def load_questionaire_sets() -> Dict[str, Any]:
    sets: Dict[str, Any] = {}
    try:
        names = questionaires_repo.list_sets()
        for name in names:
            try:
                sets[name] = questionaires_repo.load_objects(name)
            except Exception:
                continue
    except Exception as e:
        QMessageBox(
            icon=QMessageBox.Icon.Critical,
            title="Cannot load questionaires",
            detailedText=e,
        )
        raise e
    return sets


def load_threshold_names() -> List[str]:
    try:
        return list(discrete_thresholds_repo.get_set_names())
    except Exception:
        return []
    return []


def load_threshold_set(name: str) -> dict:
    return discrete_thresholds_repo.load(name).to_dict()


class RiskCalcQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Risk Calculator (Qt)")
        self.resize(1100, 780)

        self.sets = load_questionaire_sets()
        self.set_ids = list(self.sets.keys()) or []
        self.thresholds = load_threshold_names() or ["default"]

        self.answer_combos: Dict[str, List[QComboBox]] = {
            "tef": [],
            "vuln": [],
            "lm": [],
        }

        self.manual_edits: Dict[str, tuple[QLineEdit, QLineEdit, QLineEdit]] = {}

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(10)

        top = QFrame()
        top.setFrameShape(QFrame.StyledPanel)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(10)

        top_layout.addWidget(QLabel("Formulär:"))
        self.form_combo = QComboBox()
        self.form_combo.addItems(self.set_ids)
        self.form_combo.currentTextChanged.connect(self.on_form_changed)
        self.form_combo.setMinimumWidth(260)
        top_layout.addWidget(self.form_combo)

        top_layout.addSpacing(10)

        self.rb_questionnaire = QRadioButton("Frågeformulär")
        self.rb_manual = QRadioButton("Manuell")
        self.rb_questionnaire.setChecked(True)
        self.rb_questionnaire.toggled.connect(self.on_mode_toggled)
        top_layout.addWidget(self.rb_questionnaire)
        top_layout.addWidget(self.rb_manual)

        top_layout.addSpacing(10)

        top_layout.addWidget(QLabel("Tröskelset:"))
        self.threshold_combo = QComboBox()
        self.threshold_combo.addItems(self.thresholds)
        self.threshold_combo.setMinimumWidth(180)
        top_layout.addWidget(self.threshold_combo)

        top_layout.addSpacing(10)

        top_layout.addWidget(QLabel("Budget:"))
        self.budget_edit = QLineEdit("1000000")
        self.budget_edit.setValidator(QDoubleValidator(0.0, 1e18, 4))
        self.budget_edit.setMaximumWidth(140)
        top_layout.addWidget(self.budget_edit)

        top_layout.addWidget(QLabel("Valuta:"))
        self.budget_currency = QComboBox()
        self.budget_currency.addItems(AVAILABLE_CURRENCIES)
        self.budget_currency.setMinimumWidth(50)
        top_layout.addWidget(self.budget_currency)

        top_layout.addItem(
            QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        root_layout.addWidget(top)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, 1)

        self.page_questionnaire = QWidget()
        self.page_manual = QWidget()
        self.stack.addWidget(self.page_questionnaire)
        self.stack.addWidget(self.page_manual)

        self._build_questionnaire_page()
        self._build_manual_page()

        self.result_panel = QGroupBox("Resultat")
        rp = QVBoxLayout(self.result_panel)
        rp.setContentsMargins(10, 10, 10, 10)
        rp.setSpacing(8)

        actions = QHBoxLayout()
        self.calc_btn = QPushButton("🧮 Beräkna risk")
        self.calc_btn.clicked.connect(self.on_calculate)
        actions.addWidget(self.calc_btn)
        actions.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        rp.addLayout(actions)

        cols = QHBoxLayout()
        cols.setSpacing(18)

        left_box = QGroupBox("Skala")
        left_layout = QGridLayout(left_box)
        left_layout.setHorizontalSpacing(12)
        left_layout.setVerticalSpacing(6)

        right_box = QGroupBox("Kvantitativt")
        right_layout = QGridLayout(right_box)
        right_layout.setHorizontalSpacing(12)
        right_layout.setVerticalSpacing(6)

        self.result_labels: Dict[str, QLabel] = {}

        left_rows = [
            ("Sannolikhet:", "sannolikhet"),
            ("Konsekvens:", "konsekvens"),
            ("Risk:", "risk"),
        ]
        for r, (title, key) in enumerate(left_rows):
            lbl_title = QLabel(title)
            lbl_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            lbl_val = QLabel("—")
            lbl_val.setWordWrap(True)
            left_layout.addWidget(lbl_title, r, 0, Qt.AlignLeft)
            left_layout.addWidget(lbl_val, r, 1)
            self.result_labels[key] = lbl_val

        right_rows = [
            ("LEF:", "lef"),
            ("Loss Magnitude:", "loss_magnitude"),
            ("ALE:", "ale"),
        ]
        for r, (title, key) in enumerate(right_rows):
            lbl_title = QLabel(title)
            lbl_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            lbl_val = QLabel("—")
            lbl_val.setWordWrap(True)
            right_layout.addWidget(lbl_title, r, 0, Qt.AlignLeft)
            right_layout.addWidget(lbl_val, r, 1)
            self.result_labels[key] = lbl_val

        left_layout.setColumnStretch(1, 1)
        right_layout.setColumnStretch(1, 1)

        cols.addWidget(left_box, 1)
        cols.addWidget(right_box, 1)
        rp.addLayout(cols)

        root_layout.addWidget(self.result_panel, 0)
        self.on_form_changed(self.form_combo.currentText())

    def _build_questionnaire_page(self):
        layout = QVBoxLayout(self.page_questionnaire)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.questions_host = QWidget()
        self.questions_layout = QVBoxLayout(self.questions_host)
        self.questions_layout.setContentsMargins(0, 0, 0, 0)
        self.questions_layout.setSpacing(10)

        self.scroll.setWidget(self.questions_host)
        layout.addWidget(self.scroll, 1)

    def _build_manual_page(self):
        layout = QVBoxLayout(self.page_manual)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        box = QGroupBox("Manuell inmatning (MonteCarloRange: min / probable / max)")
        b = QGridLayout(box)
        b.setHorizontalSpacing(10)
        b.setVerticalSpacing(6)

        def add_range_row(
            row: int,
            label: str,
            key: str,
            defaults: tuple[str, str, str] = ("", "", ""),
        ):
            b.addWidget(QLabel(label), row, 0)

            v = QDoubleValidator(0.0, 1e18, 8)

            e_min = QLineEdit(defaults[0])
            e_min.setValidator(v)
            e_prob = QLineEdit(defaults[1])
            e_prob.setValidator(v)
            e_max = QLineEdit(defaults[2])
            e_max.setValidator(v)

            e_min.setPlaceholderText("min")
            e_prob.setPlaceholderText("probable")
            e_max.setPlaceholderText("max")

            b.addWidget(e_min, row, 1)
            b.addWidget(e_prob, row, 2)
            b.addWidget(e_max, row, 3)

            self.manual_edits[key] = (e_min, e_prob, e_max)

        add_range_row(0, "LEF (loss_event_frequency)", "lef")
        add_range_row(1, "VULN (vulnerability)", "vuln")
        add_range_row(2, "LM (loss_magnitude)", "lm")

        b.addWidget(QLabel("min"), 3, 1)
        b.addWidget(QLabel("probable"), 3, 2)
        b.addWidget(QLabel("max"), 3, 3)

        b.setColumnStretch(0, 0)
        b.setColumnStretch(1, 1)
        b.setColumnStretch(2, 1)
        b.setColumnStretch(3, 1)

        layout.addWidget(box)
        layout.addStretch(1)

    def _clear_results(self):
        for k in ["sannolikhet", "konsekvens", "risk", "lef", "loss_magnitude", "ale"]:
            self.result_labels[k].setText("—")

    def _set_result(self, key: str, text: str):
        self.result_labels[key].setText(text if text else "—")

    def on_form_changed(self, form_id: str):
        self._clear_results()
        self.answer_combos = {"tef": [], "vuln": [], "lm": []}

        while self.questions_layout.count():
            item = self.questions_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        qset = self.sets.get(form_id, {})

        for dim_key, title in [
            ("tef", "TEF"),
            ("vuln", "Vulnerability"),
            ("lm", "Loss magnitude"),
        ]:
            box = QGroupBox(title)
            v = QVBoxLayout(box)
            v.setContentsMargins(10, 10, 10, 10)
            v.setSpacing(8)

            qobj = qset.get(dim_key)
            questions = list(getattr(qobj, "questions", []))
            for q in questions:
                v.addWidget(QLabel(getattr(q, "text", str(q))))

                combo = QComboBox()
                combo.addItem("N/A")
                for alt in getattr(q, "alternatives", []):
                    alt_text = getattr(alt, "text", None) or (
                        alt.get("text") if isinstance(alt, dict) else str(alt)
                    )
                    combo.addItem(alt_text)
                v.addWidget(combo)
                self.answer_combos[dim_key].append(combo)
            self.questions_layout.addWidget(box)
        self.questions_layout.addStretch(1)

    def on_mode_toggled(self):
        if self.rb_manual.isChecked():
            self.stack.setCurrentWidget(self.page_manual)
        else:
            self.stack.setCurrentWidget(self.page_questionnaire)
        self._clear_results()

    def _build_range(self, min_s: str, prob_s: str, max_s: str):
        return MonteCarloRange(min=D(min_s), probable=D(prob_s), max=D(max_s))

    def on_calculate(self):
        self._clear_results()

        try:
            threshold_name = self.threshold_combo.currentText().strip()
            threshold_set = (
                load_threshold_set(threshold_name) if threshold_name else None
            )
        except Exception as e:
            QMessageBox.critical(self, "Fel", f"Kunde inte ladda threshold-set: {e}")
            return

        try:
            budget = D(self.budget_edit.text() or "1000000")
        except Exception:
            QMessageBox.critical(self, "Fel", "Budget måste vara ett tal.")
            return

        if self.rb_manual.isChecked():
            self._calculate_manual(budget, threshold_set)
        else:
            self._calculate_questionnaire(budget, threshold_set)

    def _calculate_manual(self, budget: Decimal, threshold_set: Any):
        lef_min, lef_prob, lef_max = (e.text() for e in self.manual_edits["lef"])
        vuln_min, vuln_prob, vuln_max = (e.text() for e in self.manual_edits["vuln"])
        lm_min, lm_prob, lm_max = (e.text() for e in self.manual_edits["lm"])

        lef_range = self._build_range(lef_min, lef_prob, lef_max)
        vuln_range = self._build_range(vuln_min, vuln_prob, vuln_max)
        lm_range = self._build_range(lm_min, lm_prob, lm_max)
        currency_str = self.budget_currency.currentText().strip()
        try:
            values = {
                "loss_event_frequency": lef_range,
                "threat_event_frequency": lef_range,
                "vulnerability": vuln_range,
                "loss_magnitude": lm_range,
                "budget": budget,
                "currency": currency_str,
                "mappings": threshold_set,
            }
            risk = HybridRisk(values=values)
            self._render_risk(risk)
        except Exception as e:
            QMessageBox.critical(
                self, "Fel", f"Beräkning misslyckades (manual/domain): {e}"
            )

    def _calculate_questionnaire(self, budget: Decimal, threshold_set: Any):
        form_id = self.form_combo.currentText()
        qset = self.sets.get(form_id, {})
        currency_str = self.budget_currency.currentText().strip()
        try:
            for dim in ("tef", "vuln", "lm"):
                qobj = qset.get(dim)
                if qobj is None:
                    raise ValueError(f"Saknar {dim} i valt formulär.")

                for qi, combo in enumerate(self.answer_combos[dim]):
                    chosen = combo.currentText()
                    found_idx = None
                    for ai, alt in enumerate(qobj.questions[qi].alternatives):
                        alt_text = getattr(alt, "text", None) or (
                            alt.get("text") if isinstance(alt, dict) else str(alt)
                        )
                        if alt_text == chosen:
                            found_idx = ai
                            break
                    if found_idx is not None:
                        qobj.questions[qi].set_answer(found_idx)
            questionaires = Questionaires(
                tef=qset["tef"], vuln=qset["vuln"], lm=qset["lm"]
            )
            values = questionaires.calculate_questionairy_values()
            values.update(
                {
                    "budget": budget,
                    "mappings": threshold_set,
                    "currency": currency_str,
                }
            )

            risk = HybridRisk(values=values)
            self._render_risk(risk)
        except Exception as e:
            QMessageBox.critical(
                self, "Fel", f"Beräkning misslyckades (form/domain): {e}"
            )
            raise e

    def _render_risk(self, risk: HybridRisk):
        risk.qualitative.overall_likelihood
        risk_dict = getattr(risk, "risk", None) or {}
        currency_formatted = Currency(self.budget_currency.currentText().strip())
        if isinstance(risk_dict, dict):
            self._set_result("sannolikhet", f"{risk.qualitative.overall_likelihood}")
            self._set_result("konsekvens", f"{risk.qualitative.impact}")
            self._set_result("risk", f"{risk.qualitative.overall_risk}")
        else:
            self._set_result("sannolikhet", "")
            self._set_result("konsekvens", "")
            self._set_result("risk", "")

        lef = risk.quantitative.loss_event_frequency
        lm = risk.quantitative.loss_magnitude
        ale = risk.quantitative.annual_loss_expectancy

        self._set_result("lef", f"{round(lef.probable, 3)} (P90: {round(lef.p90, 3)})")
        self._set_result(
            "loss_magnitude", f"{round(lm.probable, 3)} (P90: {round(lm.p90, 3)})"
        )
        self._set_result(
            "ale",
            f"{currency_formatted.get_money_format(round(ale.probable, 2))} (P90: {currency_formatted.get_money_format(round(ale.p90, 2))})",
        )


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    w = RiskCalcQt()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
