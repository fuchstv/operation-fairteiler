"""Build the standalone offline HTML from the shared Python data and vanilla JS.
Run: python3 scripts/build_web.py. No third-party packages are required.
"""
import ast
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import catalog, narrative, rogue, rpg, community, foodsharing, salvage


def build():
    # Read literal learning content without executing the Streamlit application.
    learning = {}
    for node in ast.parse((ROOT / 'app.py').read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('QUIZ', 'PICKUPS'):
                    learning[target.id] = ast.literal_eval(node.value)
    data = dict(items=catalog.ITEMS, slots=catalog.SLOTS, foods=catalog.FOOD_POOLS,
                districts=narrative.DISTRICTS, encounters=narrative.ENCOUNTERS, final=narrative.FINAL,
                events=narrative.EVENTS, flavour=narrative.FLAVOUR, notes=narrative.BUSINESS_NOTES,
                businesses=rogue.BUSINESSES, attributes=rpg.ATTRIBUTES, backgrounds=rpg.BACKGROUNDS,
                venueStats=rpg.VENUE_STATS, toolBonuses=rpg.TOOL_BONUSES,
                incidents=community.INCIDENTS, requests=community.REQUESTS,
                briefings=foodsharing.BRIEFINGS, channels=foodsharing.CHANNELS, bins=salvage.BINS,
                learning=learning)
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    (ROOT / 'web/data.json').write_text(payload + '\n')
    template = (ROOT / 'web/template.html').read_text()
    for placeholder, contents in {
        '__STYLE__': (ROOT / 'web/style.css').read_text(), '__DATA__': payload,
        '__ENGINE__': (ROOT / 'web/engine.js').read_text(), '__UI__': (ROOT / 'web/ui.js').read_text()
    }.items():
        template = template.replace(placeholder, contents)
    (ROOT / 'index.html').write_text(template)
    print(f'index.html: {len(template.encode()):,} bytes, {len(data["items"])} items, no external assets')

if __name__ == '__main__':
    build()
