#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# NOTE:
# Designer-based refactor (in-place update):
# - Loads RiskCalcMainWindow.ui
# - Uses QTabWidget (Frågeformulär / Manuell)
# - Shows distribution plots (histograms) for LEF, Loss Magnitude and ALE on the Manual tab
#
# Requirements:
#   pip install matplotlib

from __future__ import annotations

import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from currencies import Currency
from PySide6.QtGui import QDoubleValidator
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Matplotlib embedding (no seaborn)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from otyg_risk_base.hybrid import HybridRisk
from otyg_risk_base.montecarlo import MonteCarloRange
from common import D

from filesystem.repo import DiscreteThresholdsRepository
from filesystem.questionaires_repo import JsonQuestionairesRepository
from filesystem.paths import ensure_user_data_initialized, packaged_root
from riskcalculator.questionaire import Questionaires


BASE_DIR = Path(__file__).parent

# Keep original initialization behavior
p = ensure_user_data_initialized()
os.environ["TEMPLATES_DIR"] = str(packaged_root() / "templates")
os.environ["DATA_DIR"] = str(p["data"])

DATA_DIR = Path(os.environ.get("DATA_DIR", str(BASE_DIR / "data")))
AVAILABLE_CURRENCIES = Currency.get_currency_formats()

questionaires_repo = JsonQuestionairesRepository(DATA_DIR / "questionaires")
discrete_thresholds_repo = DiscreteThresholdsRepository(
    DATA_DIR / "discrete_thresholds.json"
)


def load_questionaire_sets() -> Dict[str, Any]:
    sets: Dict[str, Any] = {}
    names = questionaires_repo.list_sets()
    for name in names:
        try:
            sets[name] = questionaires_repo.load_objects(name)
        except Exception:
            continue
    return sets


def load_threshold_names() -> List[str]:
    try:
        return list(discrete_thresholds_repo.get_set_names())
    except Exception:
        return []


def load_threshold_set(name: str) -> dict:
    return discrete_thresholds_repo.load(name).to_dict()


def _extract_samples(dist_obj: Any) -> Optional[Sequence[float]]:
    """
    Tries to retrieve the internal Monte Carlo samples array.

    The user mentioned:
      risk.quantitative.<...>.__samples

    In Python, double-underscore attributes are name-mangled, so we try:
      - "__samples"
      - any attribute that ends with "__samples" or "samples" and looks iterable
    """
    if dist_obj is None:
        return None

    # 1) direct
    if hasattr(dist_obj, "__samples"):
        try:
            s = getattr(dist_obj, "__samples")
            if s is not None:
                return s
        except Exception:
            pass

    # 2) name-mangled search
    for attr in dir(dist_obj):
        if attr.endswith("__samples") or attr.endswith("samples"):
            try:
                s = getattr(dist_obj, attr)
            except Exception:
                continue
            if s is None or isinstance(s, (str, bytes)):
                continue
            try:
                iter(s)
                return s
            except Exception:
                continue

    return None


class RiskCalcQt(QMainWindow):
    """Tabs + Qt Designer (.ui) version (in-place)."""

    TAB_QUESTIONNAIRE = 0
    TAB_MANUAL = 1

    def __init__(self):
        super().__init__()

        # Data / repos
        self.sets = load_questionaire_sets()
        self.set_ids = list(self.sets.keys()) or []
        self.thresholds = load_threshold_names() or ["default"]

        # State
        self.answer_combos: Dict[str, List[QComboBox]] = {
            "tef": [],
            "vuln": [],
            "lm": [],
        }
        self.manual_edits: Dict[str, tuple[QLineEdit, QLineEdit, QLineEdit]] = {}

        # Plot canvases
        self.canvas_lef: Optional[FigureCanvas] = None
        self.canvas_lm: Optional[FigureCanvas] = None
        self.canvas_ale: Optional[FigureCanvas] = None

        # UI (Designer)
        self._load_ui()
        self._wire_signals()
        self._init_static_values()
        self._init_manual_plots()

        # Initial render
        self.on_form_changed(self.form_combo.currentText())

    def _load_ui(self):
        ui_path = (BASE_DIR / "templates" / "RiskCalcMainWindow.ui").resolve()
        if not ui_path.exists():
            alt = Path.cwd() / "templates" / "RiskCalcMainWindow.ui"
            if alt.exists():
                ui_path = alt

        if not ui_path.exists():
            raise FileNotFoundError(
                f"Cannot find UI file: {ui_path}. Place RiskCalcMainWindow.ui next to this file."
            )

        loader = QUiLoader()
        ui_root = loader.load(str(ui_path), None)
        if ui_root is None:
            raise RuntimeError(f"Failed to load UI: {ui_path}")

        if isinstance(ui_root, QMainWindow):
            cw = ui_root.centralWidget()
            if cw is None:
                raise RuntimeError("UI root is QMainWindow but has no centralWidget()")
            self.setCentralWidget(cw)
            if ui_root.menuBar():
                self.setMenuBar(ui_root.menuBar())
            if ui_root.statusBar():
                self.setStatusBar(ui_root.statusBar())
        else:
            self.setCentralWidget(ui_root)

        root = self.centralWidget()

        # Top bar widgets
        self.threshold_combo: QComboBox = root.findChild(QComboBox, "threshold_combo")
        self.budget_edit: QLineEdit = root.findChild(QLineEdit, "budget_edit")
        self.budget_currency: QComboBox = root.findChild(QComboBox, "budget_currency")

        # Tabs
        self.tabs: QTabWidget = root.findChild(QTabWidget, "tabs")
        self.tab_questionnaire: QWidget = root.findChild(QWidget, "tab_questionnaire")
        self.tab_manual: QWidget = root.findChild(QWidget, "tab_manual")

        # Form chooser (inside questionnaire tab)
        self.form_combo: QComboBox = root.findChild(QComboBox, "form_combo")

        # Dynamic questionnaire container
        self.questions_host: QWidget = root.findChild(QWidget, "questions_host")
        self.questions_layout = self.questions_host.layout()

        # Action button
        self.calc_btn: QPushButton = root.findChild(QPushButton, "calc_btn")

        # Result labels
        self.result_labels: Dict[str, QLabel] = {
            "sannolikhet": root.findChild(QLabel, "lbl_sannolikhet"),
            "konsekvens": root.findChild(QLabel, "lbl_konsekvens"),
            "risk": root.findChild(QLabel, "lbl_risk"),
            "lef": root.findChild(QLabel, "lbl_lef_val"),
            "loss_magnitude": root.findChild(QLabel, "lbl_loss_magnitude"),
            "ale": root.findChild(QLabel, "lbl_ale"),
        }

        # Manual edits
        self.manual_edits = {
            "lef": (
                root.findChild(QLineEdit, "lef_min"),
                root.findChild(QLineEdit, "lef_prob"),
                root.findChild(QLineEdit, "lef_max"),
            ),
            "vuln": (
                root.findChild(QLineEdit, "vuln_min"),
                root.findChild(QLineEdit, "vuln_prob"),
                root.findChild(QLineEdit, "vuln_max"),
            ),
            "lm": (
                root.findChild(QLineEdit, "lm_min"),
                root.findChild(QLineEdit, "lm_prob"),
                root.findChild(QLineEdit, "lm_max"),
            ),
        }

        self.setWindowTitle("Risk Calculator (Qt)")
        self.resize(1100, 780)

    def _wire_signals(self):
        self.form_combo.currentTextChanged.connect(self.on_form_changed)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.calc_btn.clicked.connect(self.on_calculate)

    def _init_static_values(self):
        self.form_combo.clear()
        self.form_combo.addItems(self.set_ids)

        self.threshold_combo.clear()
        self.threshold_combo.addItems(self.thresholds)

        self.budget_currency.clear()
        self.budget_currency.addItems(AVAILABLE_CURRENCIES)

        self.budget_edit.setValidator(QDoubleValidator(0.0, 1e18, 4))

        v = QDoubleValidator(0.0, 1e18, 8)
        for _, (e_min, e_prob, e_max) in self.manual_edits.items():
            for e in (e_min, e_prob, e_max):
                e.setValidator(v)

        self._clear_results()

    def _clear_results(self):
        for k in ["sannolikhet", "konsekvens", "risk", "lef", "loss_magnitude", "ale"]:
            lbl = self.result_labels.get(k)
            if lbl is not None:
                lbl.setText("—")

    def _set_result(self, key: str, text: str):
        lbl = self.result_labels.get(key)
        if lbl is not None:
            lbl.setText(text if text else "—")

    def on_tab_changed(self, _idx: int):
        self._clear_results()

    # -------------------------
    # Manual plots
    # -------------------------
    def _make_canvas(self, title: str) -> FigureCanvas:
        fig = Figure(figsize=(5.5, 2.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title(title)
        ax.set_xlabel("Värde")
        ax.set_ylabel("Frekvens")
        fig.tight_layout()
        return FigureCanvas(fig)

    def _init_manual_plots(self):
        layout = self.tab_manual.layout()
        if layout is None:
            layout = QVBoxLayout(self.tab_manual)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

        plots_box = QGroupBox("Fördelningar (Monte Carlo-sampling)")
        plots_layout = QVBoxLayout(plots_box)
        plots_layout.setContentsMargins(10, 10, 10, 10)
        plots_layout.setSpacing(10)

        self.canvas_lef = self._make_canvas("LEF – fördelning")
        self.canvas_lm = self._make_canvas("Loss Magnitude – fördelning")
        self.canvas_ale = self._make_canvas("ALE – fördelning")

        plots_layout.addWidget(self.canvas_lef)
        plots_layout.addWidget(self.canvas_lm)
        plots_layout.addWidget(self.canvas_ale)

        # Insert before the expanding spacer (if present)
        if layout.count() > 0:
            layout.insertWidget(max(0, layout.count() - 1), plots_box)
        else:
            layout.addWidget(plots_box)

    def _plot_hist(
        self, canvas: FigureCanvas, samples: Optional[Sequence[float]], title: str
    ):
        fig: Figure = canvas.figure
        ax = fig.axes[0] if fig.axes else fig.add_subplot(111)
        ax.cla()

        ax.set_title(title)

        if samples is None or (hasattr(samples, "__len__") and len(samples) == 0):
            ax.text(0.5, 0.5, "Inga samples att plotta", ha="center", va="center")
            ax.set_axis_off()
            canvas.draw_idle()
            return

        vals: List[float] = []
        for x in samples:
            try:
                vals.append(float(x))
            except Exception:
                continue

        if not vals:
            ax.text(0.5, 0.5, "Inga numeriska samples", ha="center", va="center")
            ax.set_axis_off()
            canvas.draw_idle()
            return

        ax.hist(vals, bins=40)
        ax.set_xlabel("Värde")
        ax.set_ylabel("Frekvens")
        fig.tight_layout()
        canvas.draw_idle()

    def _update_manual_plots(self, risk: HybridRisk):
        lef_s = _extract_samples(risk.quantitative.loss_event_frequency)
        lm_s = _extract_samples(risk.quantitative.loss_magnitude)
        ale_s = _extract_samples(risk.quantitative.annual_loss_expectancy)

        if self.canvas_lef:
            self._plot_hist(self.canvas_lef, lef_s, "LEF – fördelning")
        if self.canvas_lm:
            self._plot_hist(self.canvas_lm, lm_s, "Loss Magnitude – fördelning")
        if self.canvas_ale:
            self._plot_hist(self.canvas_ale, ale_s, "ALE – fördelning")

    # -------------------------
    # Questionnaire (dynamic UI)
    # -------------------------
    def on_form_changed(self, form_id: str):
        self._clear_results()
        self.answer_combos = {"tef": [], "vuln": [], "lm": []}

        if self.questions_layout is None:
            return

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
            vlay = box.layout()
            if vlay is None:
                vlay = QVBoxLayout(box)
            vlay.setContentsMargins(10, 10, 10, 10)
            vlay.setSpacing(8)

            qobj = qset.get(dim_key)
            questions = list(getattr(qobj, "questions", []))
            for q in questions:
                vlay.addWidget(QLabel(getattr(q, "text", str(q))))

                combo = QComboBox()
                combo.addItem("N/A")
                for alt in getattr(q, "alternatives", []):
                    alt_text = getattr(alt, "text", None) or (
                        alt.get("text") if isinstance(alt, dict) else str(alt)
                    )
                    combo.addItem(alt_text)
                vlay.addWidget(combo)
                self.answer_combos[dim_key].append(combo)

            self.questions_layout.addWidget(box)

        from PySide6.QtWidgets import QSpacerItem, QSizePolicy

        self.questions_layout.addItem(
            QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    # -------------------------
    # Calculation
    # -------------------------
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

        is_manual = self.tabs.currentIndex() == self.TAB_MANUAL
        if is_manual:
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
            self._update_manual_plots(risk)
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
                {"budget": budget, "mappings": threshold_set, "currency": currency_str}
            )

            risk = HybridRisk(values=values)
            self._render_risk(risk)
            self._update_manual_plots(risk)
        except Exception as e:
            QMessageBox.critical(
                self, "Fel", f"Beräkning misslyckades (form/domain): {e}"
            )
            raise

    def _render_risk(self, risk: HybridRisk):
        currency_formatted = Currency(self.budget_currency.currentText().strip())

        self._set_result("sannolikhet", f"{risk.qualitative.overall_likelihood}")
        self._set_result("konsekvens", f"{risk.qualitative.impact}")
        self._set_result("risk", f"{risk.qualitative.overall_risk}")

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
