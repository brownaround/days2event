import csv
import json
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# — 1) Jinja 환경 설정
env = Environment(loader=FileSystemLoader('templates'), autoescape=True)

# — 2) 상수: 페이지로 만들 대상 리스트
CONTINENTS = ['Asia', 'Europe', 'Latin America', 'North America']
GENRES     = ['Multi-genre', 'EDM', 'POP', 'K-POP', 'PRIDE']  # 필요에 따라 수정

# — 3) 이벤트 정의 로드: CSV
events_csv = []
with open('events.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        events_csv.append({
            'festival_name': row['Festival Name'],
            'start_date':    row['Start Date'],
            'end_date':      row['End Date'],
            'city':          row['City'],
            'country':       row['Country'],
            'genre':         row['Genre'],
            'artist':        row.get('Artist',''),
            'region':        row['Region'],
            'link':          row['Link'],
            'slug':          row['Slug']
        })

# — 4) 보조 데이터 로드: JSON (이모지·표시형 날짜·타이머용 ISO 날짜)
with open('festivals.json', encoding='utf-8') as f:
    festivals_json = json.load(f)
fest_map = { fest['slug']: fest for fest in festivals_json }

# — 5) 데이터 머지 & 정렬
all_events = []
for ev in events_csv:
    fest = fest_map.get(ev['slug'], {})
    # display용 날짜: JSON의 dates 리스트가 있으면 첫 항목, 아니면 CSV 날짜 합치기
    if fest.get('dates'):
        display_date = fest['dates'][0]
        iso_date     = fest['timer_date']
        location     = fest['location']
    else:
        # fallback
        display_date = (ev['start_date'] if ev['start_date']==ev['end_date']
                        else f"{ev['start_date']}–{ev['end_date']}")
        iso_date = ev['start_date']
        location = f"{ev['city']}, {ev['country']}"
    all_events.append({
        'title':         fest.get('title', ev['festival_name']),
        'slug':          ev['slug'],
        'location':      location,
        'date_display':  display_date,
        'iso_date':      iso_date,
        'link':          fest.get('official_site', ev['link']),
        'genre':         ev['genre'],
        'region':        ev['region'],
        'lineup':        fest.get('lineup', []),
        'ticket_link':   fest.get('ticket_link',''),
        'meta_description': fest.get('meta_description','')
    })

# — 6) 그룹핑
by_region = defaultdict(list)
by_genre  = defaultdict(list)
for e in sorted(all_events, key=lambda x: datetime.fromisoformat(x['iso_date'])):
    by_region[e['region']].append(e)
    by_genre[e['genre']].append(e)

# — 7) 페이지 생성 함수
def render_pages(template_name, grouping, key_list, out_prefix, context_name):
    tmpl = env.get_template(template_name)
    for key in key_list:
        events = grouping.get(key, [])
        slug   = key.lower().replace(' ', '-')
        html = tmpl.render({ 
            context_name: events, 
            'tabs': key_list, 
            'selected': key 
        })
        with open(f'build/{out_prefix}-{slug}.html', 'w', encoding='utf-8') as f:
            f.write(html)

# — 8) 렌더링 호출
render_pages('by-region.html', by_region, CONTINENTS, 'by-region', 'events')
render_pages('by-genre.html',  by_genre,  GENRES,     'by-genre',  'events')

print("✅ 지역별·장르별 페이지 생성 완료!")
