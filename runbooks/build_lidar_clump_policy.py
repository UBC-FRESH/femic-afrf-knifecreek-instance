#!/usr/bin/env python3
"""Build a block-level LiDAR spatial-clump FVS policy screen.

Each block's LiDAR trees are grouped into 4-10-tree clumps at 10 m. Each clump
is a separate FVS plot, assigned a 3-digit plot key so the after-treatment rows
can be traced back to the clump. The three largest trees in each clump are
reserved; the remaining clump trees are harvested. Singletons are reserved.

This is a structural pilot: LiDAR DBH is height-allometry, species is FD, and
the population is scaled to VRI TPH. It is not a KC CFI or a legal compliance
product.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from fresh_fvsbc.outputs import read_table
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "v3", str(ROOT / "runbooks/build_state_library_v3.py")
)
v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)
BLOCK_FEATURES = ROOT / "ws4/dataset_kc_spatial_v5/block_features.csv"
VRI = ROOT / "data/inventory/vri_2025_kc.gpkg"
TREES = ROOT / "data/lidar/kc_2024/trees.parquet"
OUT = ROOT / "ws4/lidar_clump_policy"
RUNTIME = Path("/tmp/kc_lidar_clump_policy")


def _clumps(xy: np.ndarray, eps: float = 10.0) -> list[list[int]]:
    parent = list(range(len(xy)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for a, b in cKDTree(xy).query_pairs(eps):
        union(a, b)
    groups: dict[int, list[int]] = {}
    for i in range(len(xy)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def _block_population(block: dict[str, Any], trees: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    vri_tph = float(block["vri_tph"])
    area = float(block["area_ha"])
    inside = trees.copy().reset_index(drop=True)
    # Use a one-hectare spatial sample for large blocks; keep small blocks whole.
    if area > 2.0 and len(inside) > 120:
        center = inside.iloc[len(inside) // 2]
        for radius in (50.0, 75.0, 100.0, 150.0):
            distance = np.hypot(inside.x - float(center.x), inside.y - float(center.y))
            sample = inside[distance <= radius].copy()
            if len(sample) >= 60:
                inside = sample.reset_index(drop=True)
                break
    lidar_ba = float((0.00007854 * inside.dbh_cm_est**2).sum())
    if lidar_ba > 0 and float(block.get("vri_ba", 0.0)) > 0:
        scale = min(2.0, max(0.5, (float(block["vri_ba"]) / lidar_ba) ** 0.5))
        inside["dbh_cm_est"] = inside["dbh_cm_est"] * scale
    large = inside[inside.height_m >= 20.0].copy().reset_index(drop=True)
    if large.empty:
        return pd.DataFrame(), str(block["regime"])
    rep = max(1, min(30, round(vri_tph / max(1, len(large)))))
    rows = []
    clump_idx = 0
    rng = np.random.default_rng(int(block["block_id"]))
    mix = block.get("species_mix", [("FD", 100.0)])
    codes = [c for c, _ in mix]
    weights = np.array([w for _, w in mix], dtype=float)
    weights = weights / weights.sum()

    def pick_species() -> str:
        return str(rng.choice(codes, p=weights))

    groups = _clumps(np.column_stack([large.x, large.y]))
    for group in groups:
        for start in range(0, len(group), 10):
            chunk = group[start : start + 10]
            if not chunk:
                continue
            clump_idx += 1
            stand = f"CLUMP{clump_idx:03d}"
            for i in chunk:
                r = large.iloc[int(i)]
                species = pick_species()
                for _ in range(rep):
                    rows.append(
                        {
                            "stand_id": stand,
                            "dbh_cm": float(r.dbh_cm_est),
                            "height_m": float(r.height_m),
                            "crown_ratio": 0.5,
                            "species": species,
                            "orig": f"{stand}:{i}",
                            "clump": stand,
                        }
                    )
    # small trees are reserved in their own group
    small = inside[inside.height_m < 20.0].copy()
    if len(small):
        for i in range(min(len(small), 900)):
            r = small.iloc[i]
            rows.append(
                {
                    "stand_id": "SMALL",
                    "dbh_cm": float(r.dbh_cm_est),
                    "height_m": float(r.height_m),
                    "crown_ratio": 0.5,
                    "species": pick_species(),
                    "orig": f"SMALL:{i}",
                    "clump": "SMALL",
                }
            )
    return pd.DataFrame(rows), str(block["regime"])


def _run_block(block: dict[str, Any], trees: pd.DataFrame) -> dict[str, Any]:
    frame, regime = _block_population(block, trees)
    if frame.empty:
        return {
            "block_id": block["block_id"],
            "area_ha": block["area_ha"],
            "cuts": [],
            "regime": regime,
            "status": "no_large",
        }
    cur = frame.copy()
    cuts = []
    for entry in range(1, 11):
        pop = cur[["stand_id", "dbh_cm", "height_m", "crown_ratio", "species"]].to_dict("records")
        res = v3._run_case(
            pop,
            stand=f"LIDAR_B{block['block_id']}",
            age=120.0 + 30 * (entry - 1),
            regime=regime,
            runtime_dir=RUNTIME / f"B{block['block_id']}" / f"E{entry}",
            plot_id_offset=100,
            species=None,
        )
        summary = read_table(res.database, "FVS_Summary_Metric")
        srow = summary[summary.Year == 30].iloc[0]
        try:
            a = read_table(res.database, "FVS_ATRTList_Metric")
            a = a[a.Year == 30].copy()
        except Exception:
            try:
                a = read_table(res.database, "FVS_TreeList_Metric")
                a = a[a.Year == 30].copy()
            except Exception:
                a = pd.DataFrame()
        if a.empty:
            cuts.append(
                {
                    "entry": entry,
                    "cut_m3_ha": 0.0,
                    "fvs_cut": 0.0,
                    "clump_cut": 0.0,
                    "kept": len(cur),
                }
            )
            break
        a = (
            a[a.TreeIndex <= len(cur)]
            .drop_duplicates("TreeIndex")
            .copy()
            .sort_values("TreeIndex")
            .reset_index(drop=True)
        )
        if len(a) != len(cur):
            raise RuntimeError(
                f"block {block['block_id']} entry {entry}: FVS rows {len(a)} != input {len(cur)}"
            )
        a["orig"] = cur["orig"].to_numpy()
        a["clump"] = cur["clump"].to_numpy()
        # choose the three largest original trees per 4-10 clump; reserve all singletons/small
        reserve = set()
        for _clump, g in a.groupby("clump"):
            unique = g.drop_duplicates("orig").sort_values(["Ht", "DBH"], ascending=False)
            # columns are Ht/DBH after FVS
            if len(unique) >= 4:
                reserve.update(unique.head(3)["orig"].tolist())
            else:
                reserve.update(unique["orig"].tolist())
        harvest = a[~a.orig.isin(reserve)]
        kept = a[a.orig.isin(reserve)]
        clump_cut = float((harvest.TCuM * harvest.TPH).sum()) if len(harvest) else 0.0
        cuts.append(
            {
                "entry": entry,
                "cut_m3_ha": float(srow.RTCuM) + clump_cut,
                "fvs_cut": float(srow.RTCuM),
                "clump_cut": clump_cut,
                "kept": len(kept),
                "harvest": len(harvest),
            }
        )
        if kept.empty:
            break
        cur = pd.DataFrame(
            {
                "stand_id": kept.clump.to_numpy(),
                "dbh_cm": kept.DBH.to_numpy(),
                "height_m": kept.Ht.to_numpy(),
                "crown_ratio": np.clip(kept.PctCr.to_numpy() / 100.0, 0.0, 0.89),
                "species": kept.SpeciesFVS.to_numpy(),
                "orig": kept.orig.to_numpy(),
                "clump": kept.clump.to_numpy(),
            }
        )
    return {
        "block_id": int(block["block_id"]),
        "area_ha": float(block["area_ha"]),
        "regime": regime,
        "cuts": cuts,
    }


def _load_blocks() -> tuple[list[dict[str, Any]], dict[int, pd.DataFrame]]:
    bf = pd.read_csv(BLOCK_FEATURES)
    blocks_df = pd.read_parquet(ROOT / "ws4/dataset_kc_spatial_v5/blocks.parquet")
    vri = gpd.read_file(VRI).to_crs(3005)
    vri = vri.set_index("POLYGON_ID")
    trees = pd.read_parquet(TREES)
    tg = gpd.GeoDataFrame(trees, geometry=gpd.points_from_xy(trees.x, trees.y), crs=6653).to_crs(
        3005
    )
    vri_polys = gpd.read_file(VRI).to_crs(3005)
    joined = gpd.sjoin(tg, vri_polys[["POLYGON_ID", "geometry"]], how="inner", predicate="within")
    by_poly = {
        int(pid): g.drop(columns="geometry").sort_values("tree_id").reset_index(drop=True)
        for pid, g in joined.groupby("POLYGON_ID")
    }
    blocks = []
    for i, r in bf.iterrows():
        pid = int(r.POLYGON_ID)
        v = vri.loc[pid]
        if str(r.hmz_group) == "U" or float(r.harvest_tph) <= 0:
            continue
        regime = "GWM_LOW" if str(r.hmz_group) == "L" else "GWM_MODERATE"
        code_map = {
            "FDI": "FD",
            "PLI": "PL",
            "AT": "AT",
            "CW": "CW",
            "HW": "HW",
            "BG": "BG",
            "SE": "SE",
            "LW": "LW",
            "PY": "PY",
        }
        mix = []
        for k in range(1, 7):
            c = code_map.get(str(getattr(v, f"SPECIES_CD_{k}", "")))
            pct = float(getattr(v, f"SPECIES_PCT_{k}", 0) or 0)
            if c and pct > 0:
                mix.append((c, pct))
        if not mix:
            mix = [("FD", 100.0)]
        blocks.append(
            {
                "block_id": i + 1,
                "area_ha": float(blocks_df.iloc[i].area_ha),
                "vri_tph": float(v.VRI_LIVE_STEMS_PER_HA),
                "vri_ba": float(v.BASAL_AREA),
                "species_mix": mix,
                "regime": regime,
            }
        )
    return blocks, by_poly


def main() -> None:
    """Run the full LiDAR clump policy and write its cut table."""
    blocks, by_poly = _load_blocks()
    print("blocks", len(blocks))
    results = []
    for n, block in enumerate(blocks, 1):
        trees = by_poly.get(
            int(pd.read_csv(BLOCK_FEATURES).iloc[block["block_id"] - 1].POLYGON_ID), pd.DataFrame()
        )
        if trees.empty:
            continue
        try:
            result = _run_block(block, trees)
            results.append(result)
        except Exception as exc:
            print("FAILED", block["block_id"], type(exc).__name__, exc, flush=True)
            results.append(
                {
                    "block_id": int(block["block_id"]),
                    "area_ha": float(block["area_ha"]),
                    "regime": str(block["regime"]),
                    "cuts": [],
                    "status": f"failed:{type(exc).__name__}",
                }
            )
        if n % 10 == 0:
            print("done", n, "/", len(blocks), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "block_results.json").write_text(json.dumps(results, indent=2) + "\n")
    rows = []
    for r in results:
        for c in r["cuts"]:
            rows.append(
                {"block_id": r["block_id"], "area_ha": r["area_ha"], "regime": r["regime"], **c}
            )
    pd.DataFrame(rows).to_csv(OUT / "cuts.csv", index=False)
    print("wrote", len(results), "blocks")


if __name__ == "__main__":
    main()
