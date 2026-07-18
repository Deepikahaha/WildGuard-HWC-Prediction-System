# backend/risk.py
# Canada: real RF probability grid + DBSCAN hotspots.
# Chitwan: DBSCAN hotspots only (no probability grid exists yet) — risk level
#          is approximated from each cluster's Priority_Level instead.
# Region is auto-picked by whichever hotspot set is geographically nearer —
# Canada and Chitwan don't overlap, so this is unambiguous.

import pandas as pd
import numpy as np

_canada_grid = pd.read_csv("data/parks_canada_risk_grid.csv")
_canada_hot = pd.read_csv("data/parks_canada_dbscan_hotspot_summary.csv")
_chitwan_hot = pd.read_csv("data/chitwan_hotspot_summary.csv")
_chitwan_peak = pd.read_csv("data/chitwan_species_peak_month.csv").set_index("PROBLEM_ANIMAL")["Peak_Month"]

_PRIORITY_TO_RISK = {"CRITICAL": "HIGH", "ACTIVE": "MEDIUM"}  # Chitwan has no LOW cluster today

def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

def predict_risk(lat: float, lon: float, species: str = None):
    d_canada = _haversine_km(lat, lon, _canada_hot.Center_Lat, _canada_hot.Center_Lon).min()
    d_chitwan = _haversine_km(lat, lon, _chitwan_hot.Center_Lat, _chitwan_hot.Center_Lon).min()

    if d_canada <= d_chitwan:
        return _canada_risk(lat, lon)
    return _chitwan_risk(lat, lon, species)

def _canada_risk(lat, lon):
    d_grid = _haversine_km(lat, lon, _canada_grid.Latitude, _canada_grid.Longitude)
    cell = _canada_grid.iloc[d_grid.idxmin()]

    d_hot = _haversine_km(lat, lon, _canada_hot.Center_Lat, _canada_hot.Center_Lon)
    hot = _canada_hot.iloc[d_hot.idxmin()]

    return {
        "region": "canada",
        "risk_level": cell.Risk_Level,
        "high_risk_prob": round(float(cell.High_Risk_Prob), 3),
        "nearest_hotspot": hot.Primary_Park,
        "hotspot_species": hot.Primary_Species,
        "hotspot_distance_km": round(float(d_hot.min()), 1),
        "hotspot_priority": hot.Priority,
        "hotspot_peak_month": int(hot.Peak_Month),
    }

def _chitwan_risk(lat, lon, species=None):
    d_hot = _haversine_km(lat, lon, _chitwan_hot.Center_Lat, _chitwan_hot.Center_Lon)
    hot = _chitwan_hot.iloc[d_hot.idxmin()]

    # Prefer the detected species' real peak month; fall back to the cluster's
    # dominant species if we don't have data for whatever YOLO detected.
    lookup_species = (species or hot.Primary_Animal).strip().title()
    peak_month = _chitwan_peak.get(lookup_species, _chitwan_peak.get(hot.Primary_Animal))

    return {
        "region": "chitwan",
        "risk_level": _PRIORITY_TO_RISK.get(hot.Priority_Level, "MEDIUM"),
        "high_risk_prob": None,  # no probability grid for Chitwan yet
        "nearest_hotspot": f"Cluster {hot.DBSCAN_Cluster} ({hot.CONFLICT_TYPE})",
        "hotspot_species": hot.Primary_Animal,
        "hotspot_distance_km": round(float(d_hot.min()), 1),
        "hotspot_priority": hot.Priority_Level,
        "hotspot_peak_month": int(peak_month) if pd.notna(peak_month) else None,
    }
