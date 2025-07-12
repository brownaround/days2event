import csv
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# — 1) Jinja 환경 설정
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=True
)

# — 2) 생성할 “대륙(지역)” 리스트
CONTINENTS = ['Asia', 'Europe', 'Latin America', 'North America']

# — 3) CSV에서 이벤트 데이터 로드 & 그룹핑
events_by_region = {c: [] for c in CONTINENTS}
with open('events.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # 날짜 정렬용 datetime(필요 없으면 제거)
        try:
            dt = datetime.fromisoformat(row['date_iso'])
        except Exception:
            dt = None

        events_by_region[row['region']].append({
            'name':         row.get('name', ''),
            'date_display': row.get('date_display', row.get('date', '')),
            'iso_date':     row.get('date_iso', ''),
            'emoji':        row.get('emoji', ''),
            'city':         row.get('city', ''),
            'country':      row.get('country', ''),
            'venue':        row.get('venue', ''),
            'attendance':   row.get('attendance', ''),
            'revenue':      row.get('revenue', ''),
            'dt':           dt,
        })

# (선택) 날짜 기준 정렬
for region, evs in events_by_region.items():
    events_by_region[region] = sorted(
        evs, key=lambda e: e['dt'] or datetime.min
    )

# — 4) 지역별 페이지 생성
template = env.get_template('by-region.html')
for region in CONTINENTS:
    slug = region.lower().replace(' ', '-')
    html = template.render(
        continents=CONTINENTS,
        selected_region=region,
        events=events_by_region.get(region, []),
        timer_script='timer.js'  # 타이머 스크립트 경로
    )
    out_path = f'build/by-region-{slug}.html'
    with open(out_path, 'w', encoding='utf-8') as out:
        out.write(html)

print("✅ by-region 페이지 생성 완료!")
