#!/usr/bin/env python3
"""
process_data.py - 원본 2종 데이터를 Jekyll 페이지 생성용 JSON으로 가공

입력: _rawdata/foodtruck_raw.json, _rawdata/locker_raw.json
출력: _rawdata/foodtruck.json + foodtruck_search_index.json
      _rawdata/locker.json + locker_search_index.json

사용법:
  python scripts/process_data.py
"""
import json, re, hashlib, sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "_rawdata"

DO_MAP = {
    "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구",
    "인천광역시": "인천", "광주광역시": "광주", "대전광역시": "대전",
    "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기",
    "강원특별자치도": "강원", "강원도": "강원",
    "충청북도": "충북", "충청남도": "충남",
    "전북특별자치도": "전북", "전라북도": "전북", "전라남도": "전남",
    "경상북도": "경북", "경상남도": "경남", "제주특별자치도": "제주",
    "전남광주통합특별시": "광주",
}


def make_slug(name: str, addr: str) -> str:
    slug = re.sub(r"[^\w가-힣\s-]", "", name).strip()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    h = hashlib.md5(f"{name}|{addr}".encode("utf-8")).hexdigest()[:6]
    return f"{slug}-{h}" if slug else h


def process_foodtruck():
    raw = json.loads((RAW_DIR / "foodtruck_raw.json").read_text(encoding="utf-8"))
    items, seen, skipped = [], Counter(), 0
    for d in raw:
        # 필드명 주의: Jekyll 내장 Page.name과 충돌하므로 "zoneName" 사용
        zone_name = (d.get("PRMISN_ZONE_NM") or "").strip()
        addr = (d.get("RDNMADR") or "").strip() or (d.get("LNMADR") or "").strip()
        do_full = (d.get("CTPRVN_NM") or "").strip()
        sggu = (d.get("SIGNGU_NM") or "").strip()
        do_short = DO_MAP.get(do_full, do_full if do_full in DO_MAP.values() else None)
        if not zone_name or not do_short:
            skipped += 1
            continue
        slug = make_slug(zone_name, addr or sggu)
        seen[slug] += 1
        if seen[slug] > 1:
            slug = f"{slug}-{seen[slug]}"
        items.append({
            "zoneName": zone_name,
            "locType": (d.get("LC_TYPE") or "").strip(),
            "doShort": do_short,
            "sigungu": sggu,
            "addr": addr,
            "lat": (d.get("LATITUDE") or "").strip(),
            "lng": (d.get("LONGITUDE") or "").strip(),
            "vehicleCount": (d.get("VHCLE_CO") or "").strip(),
            "rentFee": (d.get("PRMISN_ZONE_RNTFEE") or "").strip(),
            "weekdayOpen": (d.get("WEEKDAY_OPER_OPEN_HHMM") or "").strip(),
            "weekdayClose": (d.get("WEEKDAY_OPER_COLSE_HHMM") or "").strip(),
            "weekendOpen": (d.get("WKEND_OPER_OPEN_HHMM") or "").strip(),
            "weekendClose": (d.get("WKEND_OPER_CLOSE_HHMM") or "").strip(),
            "restDay": (d.get("RSTDE") or "").strip(),
            "limitProduct": (d.get("LMTT_PRDLST") or "").strip(),
            "institution": (d.get("INSTITUTION_NM") or "").strip(),
            "tel": (d.get("PHONE_NUMBER") or "").strip(),
            "refDate": (d.get("REFERENCE_DATE") or "").strip(),
            "slug": slug,
        })
    (RAW_DIR / "foodtruck.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    print(f"푸드트럭허가구역 {len(items)}개 저장 (제외 {skipped})")

    index = [{"n": i["zoneName"], "slug": i["slug"], "doShort": i["doShort"], "sigungu": i["sigungu"]} for i in items]
    (ROOT / "foodtruck_search_index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    return items


def process_locker():
    raw = json.loads((RAW_DIR / "locker_raw.json").read_text(encoding="utf-8"))
    items, seen, skipped = [], Counter(), 0
    for d in raw:
        # 필드명 주의: Jekyll 내장 Page.name과 충돌하므로 "fcltyName" 사용
        fclty_name = (d.get("FCLTY_NM") or "").strip()
        addr = (d.get("RDNMADR") or "").strip() or (d.get("LNMADR") or "").strip()
        do_full = (d.get("CTPRVN_NM") or "").strip()
        sggu = (d.get("SIGNGU_NM") or "").strip()
        do_short = DO_MAP.get(do_full, do_full if do_full in DO_MAP.values() else None)
        if not fclty_name or not do_short:
            skipped += 1
            continue
        slug = make_slug(fclty_name, addr or sggu)
        seen[slug] += 1
        if seen[slug] > 1:
            slug = f"{slug}-{seen[slug]}"
        items.append({
            "fcltyName": fclty_name,
            "doShort": do_short,
            "sigungu": sggu,
            "addr": addr,
            "lat": (d.get("LATITUDE") or "").strip(),
            "lng": (d.get("LONGITUDE") or "").strip(),
            "weekdayOpen": (d.get("WEEKDAY_OPER_OPEN_HHMM") or "").strip(),
            "weekdayClose": (d.get("WEEKDAY_OPER_COLSE_HHMM") or "").strip(),
            "freeUseTime": (d.get("FREE_USE_TIME") or "").strip(),
            "arrsUnitTime": (d.get("ARRS_UNIT_TIME") or "").strip(),
            "arrs": (d.get("ARRS") or "").strip(),
            "boxKind": (d.get("HDRYBOX_KND") or "").strip(),
            "boxCount": (d.get("BOX_CO") or "").strip(),
            "customerTel": (d.get("CSTMR_CNTER_PHONE_NUMBER") or "").strip(),
            "institution": (d.get("INSTITUTION_NM") or "").strip(),
            "institutionTel": (d.get("INSTITUTION_PHONE_NUMBER") or "").strip(),
            "refDate": (d.get("REFERENCE_DATE") or "").strip(),
            "slug": slug,
        })
    (RAW_DIR / "locker.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    print(f"안심택배함 {len(items)}개 저장 (제외 {skipped})")

    index = [{"n": i["fcltyName"], "slug": i["slug"], "doShort": i["doShort"], "sigungu": i["sigungu"]} for i in items]
    (ROOT / "locker_search_index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    return items


def main():
    ft = process_foodtruck()
    lk = process_locker()
    for label, items in [("푸드트럭허가구역", ft), ("안심택배함", lk)]:
        c = Counter(i["doShort"] for i in items)
        print(f"\n{label} 지역별 수:")
        for do, cnt in c.most_common(6):
            print(f"  {do}: {cnt}개")


if __name__ == "__main__":
    main()
