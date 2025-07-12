import os
import csv
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# 1) Jinja 환경 설정
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=True
)

# 2) 생성할 지역(대륙) 리스트
CONTINENTS = ['Asia', 'Europe', 'Latin America', 'North America']

# 3) 출력 디렉터리 생성
BUILD_DIR = 'build'
os.makedirs(BUILD_DIR, exist_ok=True)

# 4) CSV에서 이벤트 데이터 로드 및 그룹핑
events_by_region = {c: [] for c in CONTINENTS}
with open('events.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        region = row.get('Region', '').strip()
        if region not in events_by_region:
            continue
        # 날짜 처리
        start = row.get('Start Date', '').strip()
        end = row.get('End Date', '').strip()
        if start and end:
            display_date = start if start == end else f"{start}–{end}"
        else:
            display_date = start or end
        iso_date = start
        # datetime for sorting
        try:
            dt = datetime.fromisoformat(start)
        except Exception:
            dt = None
        events_by_region[region].append({
            'name':          row.get('Festival Name', '').strip(),
            'date_display':  display_date,
            'iso_date':      iso_date,
            'city':          row.get('City', '').strip(),
            'country':       row.get('Country', '').strip(),
            'venue':         row.get('Venue', '').strip(),
            'attendance':    row.get('Attendance', '').strip(),
            'revenue':       row.get('Revenue', '').strip(),
            'dt':            dt,
        })

# 5) 날짜 기준 정렬
events_by_region = {
    region: sorted(evs, key=lambda e: e['dt'] or datetime.min)
    for region, evs in events_by_region.items()
}

# 6) 지역별 페이지 생성
template = env.get_template('by-region.html')
for region, evs in events_by_region.items():
    slug = region.lower().replace(' ', '-')
    html = template.render(
        continents=CONTINENTS,
        selected_region=region,
        events_by_region=events_by_region,
        timer_script='timer.js'
    )
    out_file = os.path.join(BUILD_DIR, f'by-region-{slug}.html')
    with open(out_file, 'w', encoding='utf-8') as out:
        out.write(html)

print("✅ by-region 페이지 생성 완료!")
