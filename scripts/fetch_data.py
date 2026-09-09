#!/usr/bin/env python3
"""
fetch_data.py - wooalife 데이터 수집
전국 푸드트럭허가구역 + 안심택배함 2개 표준데이터셋을 data.go.kr 표준데이터
다운로드(활용신청 불필요)로 수집.

사용법:
  python scripts/fetch_data.py
"""
import sys
import time
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "_rawdata"
RAW_DIR.mkdir(exist_ok=True)

DATASETS = {
    "foodtruck": {
        "label": "푸드트럭허가구역",
        "pk": "15028208",
        "table": "tn_pubr_public_food_truck_permit_area_api",
        "columns": [
            "PRMISN_ZONE_NM", "LC_TYPE", "CTPRVN_NM", "SIGNGU_NM", "RDNMADR", "LNMADR",
            "LATITUDE", "LONGITUDE", "VHCLE_CO", "PRMISN_ZONE_RNTFEE",
            "WEEKDAY_OPER_OPEN_HHMM", "WEEKDAY_OPER_COLSE_HHMM",
            "WKEND_OPER_OPEN_HHMM", "WKEND_OPER_CLOSE_HHMM", "RSTDE",
            "LMTT_PRDLST", "INSTITUTION_NM", "PHONE_NUMBER", "REFERENCE_DATE",
        ],
        "out": RAW_DIR / "foodtruck_raw.json",
    },
    "locker": {
        "label": "안심택배함",
        "pk": "15034534",
        "table": "tn_pubr_public_female_safety_hdrycstdyplace_api",
        "columns": [
            "FCLTY_NM", "CTPRVN_NM", "SIGNGU_NM", "RDNMADR", "LNMADR",
            "LATITUDE", "LONGITUDE", "WEEKDAY_OPER_OPEN_HHMM", "WEEKDAY_OPER_COLSE_HHMM",
            "FREE_USE_TIME", "ARRS_UNIT_TIME", "ARRS", "HDRYBOX_KND", "BOX_CO",
            "CSTMR_CNTER_PHONE_NUMBER", "INSTITUTION_NM", "INSTITUTION_PHONE_NUMBER",
            "REFERENCE_DATE",
        ],
        "out": RAW_DIR / "locker_raw.json",
    },
}


def fetch_page(pk: str, table: str, columns: list, page: int, per_page: int) -> list:
    params = [("publicDataPk", pk)]
    params += [("colNmList", c) for c in columns]
    params += [
        ("totalCount", "99999"),
        ("svcTableNm", table),
        ("perPage", str(per_page)),
        ("page", str(page)),
    ]
    resp = requests.get(
        "https://www.data.go.kr/download/standard.json",
        params=params, timeout=60,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        return []
    return data


def fetch_one(key: str):
    cfg = DATASETS[key]
    print(f"=== {cfg['label']} 수집 시작 ===")
    all_items = []
    page = 1
    per_page = 10000
    while True:
        items = fetch_page(cfg["pk"], cfg["table"], cfg["columns"], page, per_page)
        if not items:
            break
        all_items.extend(items)
        print(f"  페이지 {page}: {len(items)}개 (누적 {len(all_items)})")
        if len(items) < per_page:
            break
        page += 1
        time.sleep(0.3)

    if not all_items:
        print(f"  ⚠ {cfg['label']} 수집된 데이터 없음")
        return

    import json
    cfg["out"].write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  완료: {cfg['out']} ({len(all_items)}개)\n")


def main():
    for k in DATASETS:
        fetch_one(k)


if __name__ == "__main__":
    main()
