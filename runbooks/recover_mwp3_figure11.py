#!/usr/bin/env python3
"""Recover the Knife Creek target stand structure from MWP #3 Figure 11.

The Alex Fraser Research Forest Management and Working Plan #3 publishes
Figure 11 as a vector chart of target density and basal area by 5 cm DBH
class for the three mule-deer winter-range habitat classes. This script
renders the page, crops the chart, masks the legend, and uses
``figrecover`` to recover the six plotted series.

The published figure is a target diagram, not observed plot data. The
recovered values are approximate to the plotted line and bar resolution.
Table 29 of the same plan remains the authoritative residual basal-area,
maximum-DBH and q-factor contract.

Usage::

    python runbooks/recover_mwp3_figure11.py --artifacts

The default writes only the reviewed tables and provenance records under
``data/benchmarks/``. ``--artifacts`` also writes the rendered page, crop,
and overlay under ``tmp/figrecover/mwp3-figure11/`` for inspection.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = REPO_ROOT / "reference" / "AFRF-management-working-plan-3-2007.pdf"
OUT_DIR = REPO_ROOT / "data" / "benchmarks"
ARTIFACT_DIR = REPO_ROOT / "tmp" / "figrecover" / "mwp3-figure11"

PAGE_NUMBER = 97
PAGE_INDEX = PAGE_NUMBER - 1
RENDER_DPI = 300
CROP_BBOX = (300, 1550, 2200, 2400)
LEGEND_MASK = (1345, 400, 1615, 610)
PLOT_FRAME = {"left": 224, "right": 1802, "top": 88, "bottom": 716}
X_RANGE = (2.5, 72.5)
DENSITY_Y_RANGE = (0.0, 140.0)
BASAL_AREA_Y_RANGE = (0.0, 4.0)
DBH_CLASSES = list(range(5, 71, 5))
MAX_DBH = {"low": 50, "moderate": 55, "high": 60}
DENSITY_SERIES = {
    "low": "#ffff00",
    "moderate": "#0000ff",
    "high": "#5f0080",
}
BASAL_AREA_SERIES = {
    "low": "#ff00ff",
    "moderate": "#00ffff",
    "high": "#800000",
}


def _require_figrecover() -> tuple[object, object, object, object]:
    """Import the optional figrecover API or explain how to install it."""
    try:
        from figrecover import Calibration, DigitizeSpec, SeriesSpec, digitize_image
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise SystemExit(
            "figrecover is required. Install it with `python -m pip install 'figrecover[pdf,cv]'`."
        ) from exc
    return Calibration, DigitizeSpec, SeriesSpec, digitize_image


def render_and_crop(*, write_artifacts: bool) -> Path:
    """Render the published page and crop the Figure 11 chart area."""
    import pymupdf

    document = pymupdf.open(PDF_PATH)
    page = document[PAGE_INDEX]
    pixmap = page.get_pixmap(dpi=RENDER_DPI, alpha=False)
    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    crop = image.crop(CROP_BBOX)
    draw = ImageDraw.Draw(crop)
    draw.rectangle(LEGEND_MASK, fill=(255, 255, 255))
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    crop_path = ARTIFACT_DIR / "figure11-crop.png"
    crop.save(crop_path)
    if write_artifacts:
        image.save(ARTIFACT_DIR / "page97.png")
    return crop_path


def _calibration(y_range: tuple[float, float]) -> object:
    """Build a plot-frame calibration for one vertical axis."""
    calibration_class = _require_figrecover()[0]
    return calibration_class.from_plot_bounds(
        plot_left=PLOT_FRAME["left"],
        plot_right=PLOT_FRAME["right"],
        plot_top=PLOT_FRAME["top"],
        plot_bottom=PLOT_FRAME["bottom"],
        x_min=X_RANGE[0],
        x_max=X_RANGE[1],
        y_min=y_range[0],
        y_max=y_range[1],
    )


def _digitize(
    image: Path,
    *,
    image_id: str,
    y_range: tuple[float, float],
    series: dict[str, str],
    mode: str,
) -> object:
    """Run one calibrated figrecover extraction."""
    calibration_class, spec_class, series_class, digitize_image = _require_figrecover()
    del calibration_class
    series_specs = [
        series_class(
            name=name,
            color=color,
            mode=mode,
            tolerance=30 if mode == "bar" else 20,
            min_component_pixels=20 if mode == "bar" else 4,
            bar_baseline=0 if mode == "bar" else None,
        )
        for name, color in series.items()
    ]
    spec = spec_class(
        image_id=image_id,
        source_document_id="afrf-mwp3-2007",
        source_figure_id="figure-11",
        figure_label="Figure 11",
        source_pdf=PDF_PATH,
        source_page=PAGE_NUMBER,
        source_crop_bbox=CROP_BBOX,
        calibration=_calibration(y_range),
        series=series_specs,
        extraction_tool_version="0.1.0a1",
    )
    return digitize_image(image, spec)


def _density_by_class(result: object) -> dict[tuple[str, int], float]:
    """Aggregate bar-top points to the nearest 5 cm DBH class."""
    values: dict[tuple[str, int], float] = {}
    for series_result in result.series:
        for point in series_result.points:
            dbh_class = int(round(point.x / 5.0) * 5)
            if 5 <= dbh_class <= 70:
                values[(series_result.spec.name, dbh_class)] = float(point.y)
    return values


def _basal_area_by_class(result: object) -> dict[tuple[str, int], float]:
    """Aggregate line points to the median near each DBH-class centre."""
    values: dict[tuple[str, int], float] = {}
    for series_result in result.series:
        points = pd.DataFrame([point.model_dump() for point in series_result.points])
        for dbh_class in DBH_CLASSES:
            subset = points[(points["x"] >= dbh_class - 1.2) & (points["x"] <= dbh_class + 1.2)]
            if len(subset):
                values[(series_result.spec.name, dbh_class)] = float(subset["y"].median())
    return values


def _series_value(values: dict[tuple[str, int], float], habitat: str, dbh_class: int) -> float:
    """Return a recovered value, using zero beyond the published maximum DBH."""
    if dbh_class > MAX_DBH[habitat]:
        return 0.0
    return values.get((habitat, dbh_class), 0.0)


def _implied_q(table: pd.DataFrame, column: str, max_dbh: int) -> float:
    """Estimate the q-factor implied by a decreasing density distribution."""
    subset = table[table["dbh_class_cm"] <= max_dbh]
    dbh = subset["dbh_class_cm"].to_numpy(dtype=float)
    density = subset[column].to_numpy(dtype=float)
    positive = density > 0
    slope, _ = np.polyfit(dbh[positive], np.log(density[positive]), 1)
    return float(np.exp(-slope * 5.0))


def build_table(image: Path) -> tuple[pd.DataFrame, object, object]:
    """Build the wide target table and return the two digitization results."""
    density_result = _digitize(
        image,
        image_id="mwp3-figure11-density",
        y_range=DENSITY_Y_RANGE,
        series=DENSITY_SERIES,
        mode="bar",
    )
    basal_area_result = _digitize(
        image,
        image_id="mwp3-figure11-basal-area",
        y_range=BASAL_AREA_Y_RANGE,
        series=BASAL_AREA_SERIES,
        mode="line",
    )
    density = _density_by_class(density_result)
    basal_area = _basal_area_by_class(basal_area_result)
    rows = []
    for dbh_class in DBH_CLASSES:
        rows.append(
            {
                "dbh_class_cm": dbh_class,
                "tpha_low": round(_series_value(density, "low", dbh_class), 1),
                "tpha_moderate": round(_series_value(density, "moderate", dbh_class), 1),
                "tpha_high": round(_series_value(density, "high", dbh_class), 1),
                "ba_low_m2_ha": round(_series_value(basal_area, "low", dbh_class), 2),
                "ba_moderate_m2_ha": round(_series_value(basal_area, "moderate", dbh_class), 2),
                "ba_high_m2_ha": round(_series_value(basal_area, "high", dbh_class), 2),
            }
        )
    return pd.DataFrame(rows), density_result, basal_area_result


def write_outputs(
    table: pd.DataFrame,
    density_result: object,
    basal_area_result: object,
    *,
    write_artifacts: bool,
) -> None:
    """Write the reviewed table, long table, metadata, and review manifest."""
    from figrecover.qa import compute_quality_metrics, render_overlay
    from figrecover.review import ReviewCorrection, ReviewEntry, ReviewManifest

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_DIR / "mwp3_figure11_target_stand_structure.csv", index=False)

    long_rows = []
    for _, row in table.iterrows():
        for habitat, column in (("Low", "low"), ("Moderate", "moderate"), ("High", "high")):
            long_rows.append(
                {
                    "habitat_class": habitat,
                    "dbh_class_cm": int(row["dbh_class_cm"]),
                    "variable": "density",
                    "value": float(row[f"tpha_{column}"]),
                    "unit": "trees/ha",
                }
            )
            long_rows.append(
                {
                    "habitat_class": habitat,
                    "dbh_class_cm": int(row["dbh_class_cm"]),
                    "variable": "basal_area",
                    "value": float(row[f"ba_{column}_m2_ha"]),
                    "unit": "m2/ha",
                }
            )
    long_table = pd.DataFrame(long_rows)
    long_table["source_document"] = "AFRF Management and Working Plan #3 (2007)"
    long_table["source_page"] = PAGE_NUMBER
    long_table["source_figure"] = "Figure 11"
    long_table["extraction_tool"] = "figrecover"
    long_table["extraction_tool_version"] = "0.1.0a1"
    long_table["review_status"] = "accepted"
    long_table["review_id"] = "mwp3-figure11"
    long_table["notes"] = (
        "Recovered from the published vector figure; zeros assigned beyond each habitat "
        "class maximum DBH (Low 50, Moderate 55, High 60 cm)."
    )
    long_table.to_csv(
        OUT_DIR / "mwp3_figure11_target_stand_structure_long.csv",
        index=False,
    )

    sums = {
        habitat: {
            "density_trees_ha": round(float(table[f"tpha_{column}"].sum()), 1),
            "basal_area_m2_ha": round(float(table[f"ba_{column}_m2_ha"].sum()), 2),
        }
        for habitat, column in (("Low", "low"), ("Moderate", "moderate"), ("High", "high"))
    }
    q_factors = {
        habitat: round(_implied_q(table, f"tpha_{column}", MAX_DBH[habitat.lower()]), 3)
        for habitat, column in (("Low", "low"), ("Moderate", "moderate"), ("High", "high"))
    }
    source_sha = hashlib.sha256(PDF_PATH.read_bytes()).hexdigest()
    metadata = {
        "dataset": "mwp3_figure11_target_stand_structure",
        "title": (
            "Target stand structures by habitat class for the Knife Creek Mule Deer Winter Range"
        ),
        "source_document": (
            "Alex Fraser Research Forest Management and Working Plan #3 (January 1, 2007)"
        ),
        "source_pdf": "reference/AFRF-management-working-plan-3-2007.pdf",
        "source_pdf_sha256": source_sha,
        "source_page_pdf": PAGE_NUMBER,
        "source_page_printed": 89,
        "figure": "Figure 11",
        "figure_caption": (
            "Target stand structures by habitat class for the Knife Creek Mule Deer "
            "Winter Range, comparing density (stems/ha on left, basal area on right "
            "axis) by diameter class."
        ),
        "extraction": {
            "tool": "figrecover",
            "version": "0.1.0a1",
            "render_dpi": RENDER_DPI,
            "crop_bbox_px": list(CROP_BBOX),
            "plot_frame_px": PLOT_FRAME,
            "x_axis": {"min_cm": X_RANGE[0], "max_cm": X_RANGE[1]},
            "left_y_axis": {
                "min": DENSITY_Y_RANGE[0],
                "max": DENSITY_Y_RANGE[1],
                "unit": "trees/ha",
            },
            "right_y_axis": {
                "min": BASAL_AREA_Y_RANGE[0],
                "max": BASAL_AREA_Y_RANGE[1],
                "unit": "m2/ha",
            },
            "legend_mask_bbox_px": list(LEGEND_MASK),
            "review_status": "accepted",
            "review_note": (
                "Overlay checked; lines and bar tops follow the plotted series. Legend "
                "swatches were masked before extraction. Zero values beyond each "
                "habitat class maximum DBH are recorded explicitly."
            ),
        },
        "policy_targets_table29": {
            "High": {
                "residual_basal_area_m2_ha": 29,
                "max_dbh_cm": 60,
                "q_factor": 1.25,
                "cutting_cycle_years": 30,
            },
            "Moderate": {
                "residual_basal_area_m2_ha": 22,
                "max_dbh_cm": 55,
                "q_factor": 1.25,
                "cutting_cycle_years": 30,
            },
            "Low": {
                "residual_basal_area_m2_ha": 16,
                "max_dbh_cm": 50,
                "q_factor": 1.30,
                "cutting_cycle_years": 30,
            },
        },
        "recovered_sums": sums,
        "recovered_q_factor": q_factors,
        "caveats": [
            "Figure 11 is a target diagram, not observed plot data.",
            (
                "The recovered per-class basal areas sum to about "
                f"{sums['Low']['basal_area_m2_ha']}, "
                f"{sums['Moderate']['basal_area_m2_ha']} and "
                f"{sums['High']['basal_area_m2_ha']} m2/ha for Low, Moderate and High, "
                "versus Table 29 targets of 16, 22 and 29 m2/ha. Do not force the "
                "figure to close; use Table 29 as the policy target and Figure 11 as "
                "the relative diameter-distribution shape."
            ),
            (
                "The recovered density distribution implies q-factors of "
                f"{q_factors['Low']}, {q_factors['Moderate']} and {q_factors['High']} "
                "for Low, Moderate and High, versus Table 29 values of 1.30, 1.25 and "
                "1.25. This is a shape check, not a recalibration."
            ),
            (
                "The figure has no uncertainty bands; recovered values are approximate "
                "to the plotted line and bar resolution."
            ),
            (
                "The map on MWP #3 page 162 is schematic and was not used to "
                "georeference this table."
            ),
        ],
    }
    (OUT_DIR / "mwp3_figure11_target_stand_structure.metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    notes = (
        "Accepted after visual overlay review. Legend swatches masked. Zero density and "
        "basal area assigned beyond the published maximum DBH by habitat class. The "
        f"published figure sums to {sums['Low']['basal_area_m2_ha']}/"
        f"{sums['Moderate']['basal_area_m2_ha']}/"
        f"{sums['High']['basal_area_m2_ha']} m2/ha versus Table 29 targets 16/22/29; "
        "the difference is recorded, not corrected. The recovered density distribution "
        f"implies q {q_factors['Low']}/{q_factors['Moderate']}/{q_factors['High']} "
        "versus Table 29 1.30/1.25/1.25."
    )
    entries = []
    for result, label in ((density_result, "density"), (basal_area_result, "basal area")):
        if write_artifacts:
            overlay = render_overlay(
                result, ARTIFACT_DIR / f"overlay-{label.replace(' ', '-')}.png"
            )
            overlay_path = Path(overlay.path).relative_to(REPO_ROOT)
        else:
            overlay_path = None
        metrics = compute_quality_metrics(result)
        with contextlib.suppress(ValueError):
            metrics.image_path = Path(metrics.image_path).relative_to(REPO_ROOT)
        entries.append(
            ReviewEntry(
                review_id=f"mwp3-figure11-{label.replace(' ', '-')}",
                figure_id="figure-11",
                extraction_run_id=result.spec.image_id,
                image_path=Path("reference/AFRF-management-working-plan-3-2007.pdf"),
                overlay_path=overlay_path,
                table_path=Path("data/benchmarks/mwp3_figure11_target_stand_structure_long.csv"),
                status="accepted",
                reviewer="opencode",
                notes=notes,
                metrics=metrics,
                diagnostics=result.diagnostics,
                correction=ReviewCorrection(
                    corrected_table_path=Path(
                        "data/benchmarks/mwp3_figure11_target_stand_structure.csv"
                    ),
                    notes=notes,
                    provenance={"method": "figrecover calibrated extraction"},
                ),
                metadata={
                    "source_page": PAGE_NUMBER,
                    "figure": "Figure 11",
                    "series": label,
                },
            )
        )
    ReviewManifest.from_entries(
        entries,
        metadata={
            "source": "AFRF MWP #3",
            "review_policy": "accepted after overlay inspection",
        },
    ).write_jsonl(OUT_DIR / "mwp3_figure11_review.jsonl")


def main() -> None:
    """Run the recovery and print the recovered basal-area sums."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifacts",
        action="store_true",
        help="Write page, crop, and overlays under tmp/figrecover/mwp3-figure11/.",
    )
    args = parser.parse_args()
    image = render_and_crop(write_artifacts=args.artifacts)
    table, density_result, basal_area_result = build_table(image)
    write_outputs(
        table,
        density_result,
        basal_area_result,
        write_artifacts=args.artifacts,
    )
    print(table.to_string(index=False))
    print(
        "basal-area sums (Low/Moderate/High): "
        f"{table['ba_low_m2_ha'].sum():.2f} / "
        f"{table['ba_moderate_m2_ha'].sum():.2f} / "
        f"{table['ba_high_m2_ha'].sum():.2f} m2/ha"
    )


if __name__ == "__main__":
    main()
