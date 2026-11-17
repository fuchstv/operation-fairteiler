"""Optional browser regression checks; requires Playwright and Chromium only for development."""
from pathlib import Path
import json
import argparse
import tempfile
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description='Test the standalone game in Chromium. Defaults to file://; use --url for a managed browser that blocks local files.')
parser.add_argument('--url')
parser.add_argument('--chromium', default=None, help='Optional Chromium executable path')
parser.add_argument('--artifacts', type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
artifacts=args.artifacts or Path(tempfile.mkdtemp(prefix='fairteiler-browser-'))
artifacts.mkdir(parents=True,exist_ok=True)
data=json.loads((root/'web/data.json').read_text())
url=args.url or (root/'index.html').as_uri()
parsed=urlsplit(url)
origin=f'{parsed.scheme}://{parsed.netloc}/'
def network_policy(ctx):
 if parsed.scheme=='file':ctx.set_offline(True)
 else:ctx.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin) else route.abort())
key='operation-fairteiler-offline-v1'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':1440,'height':1100},accept_downloads=True)
 network_policy(ctx)
 page=ctx.new_page();page.set_default_timeout(8000)
 errors=[];network=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) and not r.url.startswith(origin) else None)
 page.add_init_script("""window.__tones=0; const old=AudioContext.prototype.createOscillator; AudioContext.prototype.createOscillator=function(){window.__tones++;return old.apply(this,arguments);};""")
 page.goto(url)
 page.get_by_role('heading',name='Wer übernimmt die Runde?',exact=True).wait_for()
 page.get_by_role('textbox',name='Name auf dem Abholzettel',exact=True).fill('Mira')
 page.get_by_role('combobox',name='Dein Hintergrund',exact=True).select_option('Lagercrew')
 page.get_by_role('button',name='Attribute neu würfeln',exact=True).click()
 assert page.get_by_role('textbox',name='Name auf dem Abholzettel',exact=True).input_value()=='Mira'
 page.screenshot(path=str(artifacts/'index-charakter.png'),full_page=True)
 page.get_by_role('button',name='Charakter übernehmen & Tour beginnen',exact=True).click()
 page.get_by_role('button',name='Route 1:',exact=False).click()
 page.get_by_role('heading',name='Abholbriefing: vorbereitet in den Betrieb',exact=True).wait_for()
 for label in ['Foodsaver-Ausweis dabei','Aktuelle Betriebs-Besonderheiten','Saubere, lebensmittelechte Behälter','Saubere Hände;']:
  page.get_by_role('checkbox',name=label,exact=False).check()
 brief=next(b for b in data['briefings'] if page.get_by_role('heading',name=b['title'],exact=True).count())
 page.get_by_role('radio',name=brief['options'][brief['correct']],exact=True).check()
 page.get_by_role('button',name='Vorbereitung bestätigen & Abholung beginnen',exact=True).click()
 page.get_by_role('button',name='🛠️ Weiterarbeiten',exact=True).click()
 page.get_by_role('status').filter(has_text='gegen SG').first.wait_for()
 saved=page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',key)
 assert saved['run']['character_name']=='Mira' and saved['run']['phase']=='combat'
 page.reload()
 assert page.evaluate('(k)=>JSON.parse(localStorage.getItem(k)).run.turn',key)==saved['run']['turn']
 page.get_by_role('button',name='🛠️ Weiterarbeiten',exact=True).wait_for()
 page.screenshot(path=str(artifacts/'index-abholung.png'),full_page=True)
 page.get_by_role('button',name='🥊 PvP · Hotseat',exact=True).click()
 page.get_by_role('textbox',name='Spieler 1',exact=True).fill('A')
 page.get_by_role('textbox',name='Spieler 2',exact=True).fill('B')
 page.get_by_role('button',name='Hotseat-Duell starten',exact=True).click()
 page.get_by_role('button',name='PvP: Tempo machen',exact=True).click()
 page.get_by_role('status').filter(has_text='B ist am Zug').wait_for()
 page.get_by_role('button',name='📚 Item-Lexikon',exact=True).click()
 page.get_by_role('combobox',name='Kategorie',exact=True).select_option('face')
 page.get_by_role('searchbox',name='Im Item-Lexikon suchen',exact=True).fill('FFP')
 page.get_by_text('2 Treffer',exact=True).wait_for()
 assert page.locator('main article.item').count()==2
 page.get_by_role('checkbox',name='Sounds einschalten',exact=True).check()
 page.wait_for_function('window.__tones >= 3')
 with page.expect_download() as dl:
  page.get_by_role('button',name='Spielstand exportieren',exact=True).click()
 download=dl.value
 content=Path(download.path()).read_bytes()
 export=json.loads(content)
 assert export['version']==1 and export['duel']['turn']==1
 current=page.evaluate('(k)=>localStorage.getItem(k)',key)
 page.locator('#import-file').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"version":99}'})
 page.get_by_role('status').filter(has_text='Import abgelehnt:').wait_for()
 assert page.evaluate('(k)=>localStorage.getItem(k)',key)==current
 page.locator('#import-file').set_input_files({'name':'save.json','mimeType':'application/json','buffer':content})
 page.get_by_role('status').filter(has_text='Spielstand importiert.').wait_for()
 assert page.evaluate('(k)=>JSON.parse(localStorage.getItem(k)).run.turn',key)==saved['run']['turn']
 assert not errors,errors
 assert not network,network
 print('PASS: standalone HTML (file or selected local origin), no external requests; character, briefing, real check, persistence/reload, hotseat, codex, WebAudio, export/import, corrupt import preservation')
 # Separate offline profile for a genuine end-to-end basket journey.
 ctx2=browser.new_context(viewport={'width':1440,'height':1100});network_policy(ctx2)
 page2=ctx2.new_page();page2.goto(url)
 page2.get_by_role('button',name='Charakter übernehmen & Tour beginnen',exact=True).click()
 page2.get_by_role('button',name='🧺 Fairteilen',exact=True).click()
 page2.get_by_role('combobox',name='Weg der Fairteilung',exact=True).select_option('basket')
 page2.get_by_role('checkbox',name='Vollkornbrot',exact=False).check()
 page2.get_by_role('checkbox',name='Jedes ausgewählte Stück auf Genießbarkeit geprüft.',exact=True).check()
 page2.get_by_role('button',name='Fiktiven Essenskorb anlegen',exact=True).click()
 page2.get_by_role('heading',name='Dein reservierter Essenskorb',exact=True).wait_for()
 page2.get_by_role('button',name='Eine Runde auf die Abholabsprache warten',exact=True).click()
 page2.get_by_role('checkbox',name='Vor dieser Übergabe jedes Stück erneut auf Genießbarkeit geprüft.',exact=True).check()
 page2.get_by_role('checkbox',name='Persönliches Gespräch möglich;',exact=False).check()
 page2.get_by_role('button',name='Essenskorb persönlich übergeben',exact=True).click()
 assert page2.evaluate('(k)=>JSON.parse(localStorage.getItem(k)).run.shared',key)==1
 page2.get_by_role('button',name='🗑️ Tonnenrunde',exact=True).click()
 page2.get_by_role('button',name='Diesen Sammelplatz aufsuchen',exact=True).first.click()
 page2.get_by_role('button',name='Sortieren & Material prüfen',exact=True).click()
 page2.get_by_role('button',name='Tonnenrunde abschließen',exact=True).click()
 assert page2.evaluate('(k)=>JSON.parse(localStorage.getItem(k)).run.phase',key)=='map'
 print('PASS: local basket reservation -> waiting -> personal handover; cleanup round -> route')
 mobileCtx=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');network_policy(mobileCtx)
 mobile=mobileCtx.new_page();mobile.goto(url)
 mobile.get_by_role('button',name='Charakter übernehmen & Tour beginnen',exact=True).click()
 mobile.get_by_text('🥕 Menü & Spielstand',exact=True).click()
 mobile.get_by_role('button',name='🎒 Inventar & Magen',exact=True).click()
 mobile.get_by_role('heading',name='Was dein Körper gerade mitmacht',exact=True).wait_for()
 assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
 mobile.screenshot(path=str(artifacts/'index-mobil.png'),full_page=True)
 print('PASS: local mobile layout, menu, inventory and no horizontal overflow')
 # Direct content loading verifies that all code/assets work with networking disabled.
 offlineCtx=browser.new_context();offlineCtx.set_offline(True)
 offline=offlineCtx.new_page();offline_errors=[]
 offline.on('pageerror',lambda e:offline_errors.append(str(e)))
 offline.set_content((root/'index.html').read_text(),wait_until='load')
 offline.get_by_role('button',name='Charakter übernehmen & Tour beginnen',exact=True).click()
 offline.get_by_role('heading',name='Wähle deine nächste Abholung',exact=True).wait_for()
 offline.get_by_role('button',name='📚 Item-Lexikon',exact=True).click()
 offline.get_by_role('heading',name='152 Fundstücke für deinen Run',exact=True).wait_for()
 assert not offline_errors,offline_errors
 print('PASS: embedded HTML content with networking disabled and blocked storage fallback')
 print('Screenshots:',artifacts)
 browser.close()
