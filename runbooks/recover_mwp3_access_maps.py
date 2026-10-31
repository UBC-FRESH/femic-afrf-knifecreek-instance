#!/usr/bin/env python3
"""Recover the MWP #3 Appendix 11 access maps with figrecover and test georeferencing.

The two Appendix 11 maps are scanned plan figures. This runbook uses
``figrecover`` to render and crop them, then tests whether the Knife Creek
magenta boundary can be registered to the legal SUP boundary. It does not
claim a road GIS layer: the map lines are scanned, schematic, and mixed with
contours, streams, and labels.

Usage::

    PYTHONPATH=/path/to/figrecover/src python runbooks/recover_mwp3_access_maps.py \
      --pdf reference/AFRF-management-working-plan-3-2007.pdf \
      --out-dir data/roads/plan_map
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pymupdf
from PIL import Image, ImageDraw
from scipy.ndimage import (
    binary_closing,
    binary_dilation,
    distance_transform_edt,
    label,
)
from scipy.optimize import minimize
from shapely.geometry import MultiPolygon
from shapely.geometry.base import BaseGeometry

EXPECTED_SHA256 = "9bfd8b8f0449f45fb97fcf529236640ace09b73ba74f77001f677eee7307ff6a"
MAP_PAGES = {165: "gavin", 166: "knife_creek"}
MAP_DPI = 300


def _sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _boundary_points(geom: BaseGeometry, step: float = 30.0) -> np.ndarray:
    """Densify and return the exterior coordinates of a polygon or multipolygon."""
    polygons = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    points: list[tuple[float, float]] = []
    for polygon in polygons:
        points.extend(polygon.segmentize(step).exterior.coords)
    return np.asarray(points, dtype=float)


def _magenta_mask(image: np.ndarray) -> np.ndarray:
    """Return the large magenta components, which are the plan boundary."""
    mask = (image[:, :, 0] > 130) & (image[:, :, 1] < 140) & (image[:, :, 2] > 130)
    connected = binary_closing(binary_dilation(mask, iterations=2), iterations=2)
    labels, _ = label(connected, structure=np.ones((3, 3)))
    sizes = np.bincount(labels.ravel())
    keep = np.where(sizes > 1000)[0]
    keep = keep[keep != 0]
    return np.isin(labels, keep)


def _fit_boundary(
    mask: np.ndarray,
    gis_path: Path,
) -> dict[str, object]:
    """Fit a similarity transform from GIS coordinates to image pixels."""
    height, width = mask.shape
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return {"status": "unresolved", "reason": "no magenta boundary detected"}
    distance = distance_transform_edt(~mask)
    gis = gpd.read_file(gis_path).to_crs(3005)
    geom = gis.geometry.union_all()
    points = _boundary_points(geom)
    gx0, gy0, gx1, gy1 = geom.bounds
    gcx, gcy = (gx0 + gx1) / 2.0, (gy0 + gy1) / 2.0
    scale_x = (xs.max() - xs.min()) / (gx1 - gx0)
    scale_y = (ys.max() - ys.min()) / (gy1 - gy0)
    scale = (scale_x + scale_y) / 2.0
    pixel_cx = (xs.min() + xs.max()) / 2.0
    pixel_cy = (ys.min() + ys.max()) / 2.0

    def transform(params: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        scale_value, theta, tx, ty = params
        cos = np.cos(theta)
        sin = np.sin(theta)
        x = (points[:, 0] - gcx) * scale_value
        y = (points[:, 1] - gcy) * scale_value
        return (
            cos * x - sin * y + tx,
            -(sin * x + cos * y) + ty,
        )

    def objective(params: np.ndarray) -> float:
        px, py = transform(params)
        xi = np.clip(np.round(px).astype(int), 0, width - 1)
        yi = np.clip(np.round(py).astype(int), 0, height - 1)
        outside = ((px < 0) | (px >= width) | (py < 0) | (py >= height)).sum()
        return float(distance[yi, xi].mean() + outside * 2.0)

    initial = np.array([scale, 0.0, pixel_cx, pixel_cy], dtype=float)
    result = minimize(
        objective,
        initial,
        method="Nelder-Mead",
        options={"maxiter": 3000, "xatol": 1e-4, "fatol": 1e-4},
    )
    scale_value, theta, tx, ty = result.x
    return {
        "status": "ok" if result.fun < 10.0 else "unresolved",
        "scale_px_per_m": float(scale_value),
        "theta_rad": float(theta),
        "tx_px": float(tx),
        "ty_px": float(ty),
        "gis_centroid_epsg3005": [float(gcx), float(gcy)],
        "mean_boundary_distance_px": float(result.fun),
        "meters_per_pixel": float(1.0 / scale_value),
        "initial_scale_px_per_m": float(scale),
    }


def _overlay(
    image_path: Path,
    georef: dict[str, object],
    gis_path: Path,
    roads_path: Path | None,
    output_path: Path,
) -> None:
    """Draw the GIS boundary and public roads on the scanned map."""
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    gis = gpd.read_file(gis_path).to_crs(3005)
    geom = gis.geometry.union_all()
    scale = float(georef["scale_px_per_m"])
    theta = float(georef["theta_rad"])
    tx = float(georef["tx_px"])
    ty = float(georef["ty_px"])
    gcx, gcy = (float(value) for value in georef["gis_centroid_epsg3005"])
    cos = np.cos(theta)
    sin = np.sin(theta)

    def to_pixel(x: float, y: float) -> tuple[float, float]:
        x0 = (x - gcx) * scale
        y0 = (y - gcy) * scale
        return cos * x0 - sin * y0 + tx, -(sin * x0 + cos * y0) + ty

    for polygon in list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]:
        draw.line(
            [to_pixel(x, y) for x, y in polygon.exterior.coords],
            fill=(0, 200, 0),
            width=2,
        )
    if roads_path is not None and roads_path.exists():
        roads = gpd.read_file(roads_path).to_crs(3005)
        for geom_line in roads.geometry:
            lines = (
                list(geom_line.geoms) if geom_line.geom_type == "MultiLineString" else [geom_line]
            )
            for line in lines:
                draw.line(
                    [to_pixel(x, y) for x, y in line.coords],
                    fill=(0, 0, 255),
                    width=2,
                )
    image.save(output_path)


def main() -> None:
    """Render, crop, register, and record the two access maps."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pdf",
        type=Path,
        default=Path("reference/AFRF-management-working-plan-3-2007.pdf"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("data/roads/plan_map"))
    parser.add_argument("--tmp-dir", type=Path, default=Path("tmp/figrecover/mwp3-access-maps"))
    parser.add_argument(
        "--kc-sup",
        type=Path,
        default=Path("data/boundaries/knife_creek_sup_S15382.gpkg"),
    )
    parser.add_argument(
        "--kc-roads",
        type=Path,
        default=Path("data/patchworks_knifecreek/spatial/roads.gpkg"),
    )
    parser.add_argument(
        "--gavin-fragments",
        type=Path,
        default=Path(
            "../femic-afrf-gavinlake-instance/data/legacy_gavinlake/spatial/fragments.shp"
        ),
    )
    args = parser.parse_args()

    actual_sha256 = _sha256(args.pdf)
    if actual_sha256 != EXPECTED_SHA256:
        raise SystemExit(f"unexpected MWP #3 SHA-256: {actual_sha256}")

    try:
        import figrecover

        figrecover_version = str(getattr(figrecover, "__version__", "0.1.0a1"))
        from figrecover.documents import render_pdf_pages
        from figrecover.manifest import FigureManifest
        from figrecover.records import BoundingBox, FigureCandidate
    except ImportError as exc:
        raise SystemExit(
            "figrecover is required. Set PYTHONPATH to the figrecover source or install it."
        ) from exc

    args.out_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = args.tmp_dir / "pages"
    crops_dir = args.tmp_dir / "crops"
    native_dir = args.tmp_dir / "native"
    rendered = render_pdf_pages(
        args.pdf,
        pages_dir,
        pages=[165, 166],
        dpi=MAP_DPI,
        overwrite=True,
    )
    document = pymupdf.open(args.pdf)
    candidates: list[FigureCandidate] = []
    native_paths: dict[str, Path] = {}
    for page_number, name in MAP_PAGES.items():
        page = document.load_page(page_number - 1)
        images = page.get_images(full=True)
        if not images:
            raise SystemExit(f"page {page_number} has no embedded image")
        xref = images[0][0]
        image_info = document.extract_image(xref)
        native_dir.mkdir(parents=True, exist_ok=True)
        native_path = native_dir / f"{name}.{image_info['ext']}"
        native_path.write_bytes(image_info["image"])
        native_paths[name] = native_path
        rect = page.get_image_rects(xref)[0]
        zoom = MAP_DPI / 72.0
        bbox = BoundingBox(
            left=rect.x0 * zoom,
            top=rect.y0 * zoom,
            right=rect.x1 * zoom,
            bottom=rect.y1 * zoom,
        )
        rendered_page = next(item for item in rendered if item.page_number == page_number)
        candidates.append(
            FigureCandidate(
                figure_id=f"mwp3-appendix11-{name}",
                document_id="afrf-mwp3",
                page_number=page_number,
                image_path=rendered_page.image_path,
                source_image_path=rendered_page.image_path,
                bbox=bbox,
                label=f"Appendix 11 {name} access plan",
                source="manual map crop",
                metadata={"map_scale": "1:40,000", "schematic": True},
            )
        )
    document.close()
    cropped = []
    from figrecover.documents import crop_figure_candidates

    cropped = crop_figure_candidates(candidates, crops_dir, overwrite=True, image_format="png")
    manifest = FigureManifest.from_candidates(
        cropped,
        metadata={
            "source": "AFRF Management and Working Plan #3",
            "sha256": actual_sha256,
            "pages": [165, 166],
            "dpi": MAP_DPI,
            "figrecover_version": figrecover_version,
        },
    )
    manifest.write_jsonl(args.out_dir / "figure_manifest.jsonl")

    georefs: dict[str, dict[str, object]] = {}
    for name, native_path in native_paths.items():
        image = np.asarray(Image.open(native_path).convert("RGB"))
        mask = _magenta_mask(image)
        gis_path = args.kc_sup if name == "knife_creek" else args.gavin_fragments
        georef = _fit_boundary(mask, gis_path)
        georef["source_image"] = str(native_path)
        georef["gis_path"] = str(gis_path)
        georefs[name] = georef

    kc = georefs["knife_creek"]
    (args.out_dir / "knife_creek_access_georef.json").write_text(json.dumps(kc, indent=2) + "\n")
    (args.out_dir / "gavin_access_georef.json").write_text(
        json.dumps(georefs["gavin"], indent=2) + "\n"
    )
    if kc.get("status") == "ok":
        _overlay(
            native_paths["knife_creek"],
            kc,
            args.kc_sup,
            args.kc_roads,
            args.out_dir / "knife_creek_access_overlay.png",
        )

    summary = {
        "source": "AFRF Management and Working Plan #3, Appendix 11",
        "sha256": actual_sha256,
        "figrecover_version": figrecover_version,
        "pages": MAP_PAGES,
        "crops": [str(path.image_path) for path in cropped],
        "georeference": georefs,
        "caveats": [
            "The maps are schematic and carry no coordinate grid.",
            "The Knife Creek boundary fit is a similarity transform, not a survey control.",
            "The Gavin Lake boundary does not register cleanly to the managed "
            "fragments; its georeference is unresolved.",
            "The map lines mix roads, contours, streams, and labels; no road GIS layer is claimed.",
        ],
    }
    (args.out_dir / "recovery_manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["georeference"], indent=2))


if __name__ == "__main__":
    main()
