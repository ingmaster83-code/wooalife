#!/usr/bin/env python3
"""foodtruck-region/{시도}/index.html, locker-region/{시도}/index.html 생성"""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent

FULLNAME = {
    "서울": "서울특별시", "경기": "경기도", "인천": "인천광역시", "강원": "강원특별자치도",
    "충북": "충청북도", "충남": "충청남도", "대전": "대전광역시", "세종": "세종특별자치시",
    "전북": "전북특별자치도", "전남": "전라남도", "광주": "광주광역시", "경북": "경상북도",
    "경남": "경상남도", "부산": "부산광역시", "대구": "대구광역시", "울산": "울산광역시",
    "제주": "제주특별자치도",
}


def gen(data_file, out_folder, layout, icon, label):
    data = json.loads((ROOT / "_rawdata" / data_file).read_text(encoding="utf-8"))
    counts = Counter(f["doShort"] for f in data)

    for region in sorted(counts):
        full = FULLNAME.get(region, region)
        cnt = counts[region]
        d = ROOT / out_folder / region
        d.mkdir(parents=True, exist_ok=True)

        content = f"""---
layout: {layout}
title: {full} {label}
description: {full} {label} 정보. 위치와 이용시간을 확인하세요.
do_name: {region}
title_h1: {full} {label} {cnt}곳
subtitle: {full} 지역 {label}을 확인하세요.
---
"""
        (d / "index.html").write_text(content, encoding="utf-8")
        print(f"  {region} ({full}): {cnt}곳")

    print(f"완료: {len(counts)}개 {label} 지역 페이지 생성\n")


gen("foodtruck.json", "foodtruck-region", "foodtruck-region", "🚚", "푸드트럭허가구역")
gen("locker.json", "locker-region", "locker-region", "📦", "안심택배함")
