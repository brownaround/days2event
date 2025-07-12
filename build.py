import csv
import json
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# — 1) 환경 설정
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=True
)

# — 2) 상수 정의
CONTINENTS = ['Asia', 'Europe', 'Latin America', 'North America']
GENRES     = ['Multi-genre', 'EDM', 'POP', 'K-POP', 'PRIDE']  # 필요에 따라 확장
TIMER_SCRIPT = 'timer.js'

# — 3) CSV에서 이벤트 데이터 로드
events = []
with open('events.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # ISO 날짜로 정렬하기 위해 datetime 변환
        dt = datetime.fromisoformat(row['date_iso'])
        events.append({
            'name':        row.get('name', ''),
            'city':        row.get('city', ''),
            'country':     row.get('country', ''),
            'flag':        row.get('emoji', ''),             # CSV에 🇰🇷 같은 이모지 컬럼이 있다고 가정
            'venue':       row.get('venue', ''),
            'attendance':  row.get('attendance', ''),
            'revenue':     row.get('revenue', ''),
            'region':      row.get('region', ''),
            'genre':       row.get('genre', ''),             # CSV에 장르 컬럼이 있다면
            'date_display':row.get('date_display', ''),
            'date_iso':    row['date_iso'],
            'dt':          dt
        })

# — 4) 지역별·장르별 그룹핑
events_by_region = defaultdict(list)
events_by_genre  = defaultdict(list)
for ev in sorted(events, key=lambda e: e['dt']):
    events_by_region[ev['region']].append(ev)
    events_by_genre[ev['genre']].append(ev)

# — 5) 지역별 페이지 생성
tmpl_region = env.get_template('by-region.html')
for region in CONTINENTS:
    slug = region.lower().replace(' ', '-')
    html = tmpl_region.render(
        continents=CONTINENTS,
        selected_region=region,
        events=events_by_region.get(region, []),
        timer_script=TIMER_SCRIPT
    )
    with open(f'build/by-region-{slug}.html', 'w', encoding='utf-8') as out:
        out.write(html)

# — 6) 장르별 페이지 생성
tmpl_genre = env.get_template('by-genre.html')
for genre in GENRES:
    slug = genre.lower().replace(' ', '-')
    html = tmpl_genre.render(
        genres=GENRES,
        selected_genre=genre,
        events=events_by_genre.get(genre, []),
        timer_script=TIMER_SCRIPT
    )
    with open(f'build/by-genre-{slug}.html', 'w', encoding='utf-8') as out:
        out.write(html)

print("✅ 지역별 및 장르별 페이지 생성 완료!")
