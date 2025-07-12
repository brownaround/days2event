import os
import csv
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# 1) 템플릿 환경 설정
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=True
)

# 2) 출력 디렉터리 설정 (Cloudflare Pages 기본값)
BUILD_DIR = 'site'
os.makedirs(BUILD_DIR, exist_ok=True)

# 3) 생성할 지역 리스트
CONTINENTS = ['Asia', 'Europe', 'Latin America', 'North America']

# 4) CSV 로드 및 지역별 그룹핑
events_by_region = {c: [] for c in CONTINENTS}
with open('events.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        region = row.get('Region', '').strip()
        if region not in events_by_region:
            continue

        start = row.get('Start Date', '').strip()
        end = row.get('End Date', '').strip()
        display_date = start if start == end else f"{start}–{end}" if start and end else start or end
        iso_date = start
        try:
            dt = datetime.fromisoformat(start)
        except Exception:
            dt = None

        events_by_region[region].append({
            'name':         row.get('Festival Name', '').strip(),
            'date_display': display_date,
            'iso_date':     iso_date,
            'city':         row.get('City', '').strip(),
            'country':      row.get('Country', '').strip(),
            'venue':        row.get('Venue', '').strip(),
            'attendance':   row.get('Attendance', '').strip(),
            'revenue':      row.get('Revenue', '').strip(),
            'dt':           dt
        })

# 5) 날짜 기준 정렬
for region in CONTINENTS:
    events_by_region[region] = sorted(events_by_region[region], key=lambda e: e['dt'] or datetime.min)

# 6) 페이지 렌더링
template = env.get_template('by-region.html')
for region in CONTINENTS:
    slug = region.lower().replace(' ', '-')
    html = template.render(
        continents=CONTINENTS,
        selected_region=region,
        events=events_by_region[region],
        timer_script='timer.js'
    )
    output_path = os.path.join(BUILD_DIR, f'by-region-{slug}.html')
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(html)

print("✅ by-region 페이지 생성 완료!")
