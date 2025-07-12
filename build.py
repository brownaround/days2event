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

# 3) CSV에서 이벤트 데이터 로드 및 그룹핑
events_by_region = {c: [] for c in CONTINENTS}
with open('events.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # CSV 헤더에 맞춰 키 사용
        region = row.get('Region', '').strip()
        if region not in events_by_region:
            continue
        name = row.get('Festival Name', '').strip()
        start_date = row.get('Start Date', '').strip()
        end_date = row.get('End Date', '').strip()

        # 표시용 날짜 포맷
        if start_date and end_date:
            display_date = start_date if start_date == end_date else f"{start_date}–{end_date}"
        else:
            display_date = start_date or end_date

        # ISO 날짜 (타이머용)
        iso_date = start_date

        # 정렬용 datetime 객체
        try:
            dt = datetime.fromisoformat(start_date)
        except Exception:
            dt = None

        events_by_region[region].append({
            'name':         name,
            'date_display': display_date,
            'iso_date':     iso_date,
            'city':         row.get('City', '').strip(),
            'country':      row.get('Country', '').strip(),
            'venue':        row.get('Venue', '').strip(),
            'attendance':   row.get('Attendance', '').strip(),
            'revenue':      row.get('Revenue', '').strip(),
            'dt':           dt,
        })

# 4) 날짜 기준 정렬 (존재하지 않을 경우 최소값 사용)
for region, evs in events_by_region.items():
    events_by_region[region] = sorted(evs, key=lambda e: e['dt'] or datetime.min)

# 5) 지역별 페이지 생성
template = env.get_template('by-region.html')
for region in CONTINENTS:
    slug = region.lower().replace(' ', '-')
    html = template.render(
        continents=CONTINENTS,
        selected_region=region,
        events=events_by_region.get(region, []),
        timer_script='timer.js'
    )
    out_path = f'build/by-region-{slug}.html'
    with open(out_path, 'w', encoding='utf-8') as out:
        out.write(html)

print("✅ by-region 페이지 생성 완료!")
