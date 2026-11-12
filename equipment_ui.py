"""Views for body state, worn equipment and optional cleanup encounters."""
import streamlit as st
import rogue as game
import physiology
import salvage
import rpg


def loadout(r):
    with st.expander('Angelegte Ausrüstung · sieben Plätze', expanded=True):
        for slot, name in game.SLOTS.items():
            obj = next((o for o in r['inventory'] if o['uid'] == r['equipped'].get(slot)), None)
            label = game.ITEMS[obj['key']]['name'] if obj else 'frei'
            left, right = st.columns([3,1])
            left.write(f'**{name}:** {label}')
            if obj and right.button('Abnehmen',key='remove_'+slot,disabled=r['phase']!='map'):
                game.unequip(r,slot);st.rerun()


def body(r):
    st.markdown('### Was dein Körper gerade mitmacht')
    cols=st.columns(3)
    cols[0].progress(r['hygiene']/100,text=f"Handhygiene {r['hygiene']}/100")
    cols[1].progress(r['gas']/100,text=f"Bauchgas {r['gas']}/100")
    cols[2].progress(r['urgency']/100,text=f"Toilettendrang {r['urgency']}/100")
    queued=sum(meal['energy'] for meal in r['digestion'])
    st.write(f"Noch {queued} Energie in Verdauung · Salzlast {r['salt_load']}/50")
    st.caption('Nahrung liefert ein Drittel Energie sofort und den Rest rundenweise. Fettige Mahlzeiten geben Energie langsamer frei. Ballaststoffreiche Speisen erhöhen Spiel-Bauchgas, Salz erhöht den Wasserverbrauch. Essen mit schmutzigen Händen steigert den Magenreiz. Bei sehr hoher Übelkeit kann der Spielmagen rebellieren.')
    if r['digestion']:
        st.caption('In Verdauung: '+', '.join(meal['name'] for meal in r['digestion']))
    cols=st.columns(2)
    if cols[0].button('Hände am Waschplatz waschen', disabled=r['phase']!='map' or r['water']<8 or r['hygiene']==100):
        physiology.wash(r);st.rerun()
    if cols[1].button('Toilettenpause einlegen', disabled=r['phase']!='map' or not(r['urgency'] or r['gas'] or r['nausea'])):
        physiology.restroom(r);st.rerun()
    st.caption('Waschen: −5 Wasser plus eine Runde. Toilettenpause: Drang auf 0, −25 Bauchgas, −10 Übelkeit plus eine Runde. Das Modell und alle Schutzeffekte sind fiktiv, keine medizinische oder arbeitsschutzbezogene Anleitung.')
    with st.expander('Aktive Effekte'):
        if not r['effects']:st.caption('Keine zeitweiligen Effekte.')
        for key,effect in r['effects'].items():
            labels={'strength':'Muskelkraft','dexterity':'Geschick','insight':'Übersicht','presence':'Auftreten','cooling':'Kühlung','handling':'Hygieneschutz','odor_guard':'Geruchsschutz','digestion':'Verdauung'}
            st.write(f"{labels.get(key,key)}: {effect['power']:+} · noch {max(0,effect['until']-r['turn'])} Runden")
        st.caption('Gleiche Effekte werden erneuert, nicht unbegrenzt gestapelt. Haltbare Handschuhe und Masken verschleißen pro Runde; kaputte Teile geben bis zur Reparatur keine Boni.')


def encounter(r,scene,check_hint,description,prefix='route_'):
    data=salvage.BINS[r['bin_key']]
    scene(data['icon'],data['name'])
    st.subheader('Tonnenrunde · '+data['name'])
    st.write(data['text'])
    st.caption('Abgesprochene, fiktive Sortieraktion. Material kommt aus freigegebenen Beständen. Keine Lebensmittelbeute; nichts wird durch Maske oder Handschuhe zum Verzehr geeignet.')
    if r['phase']=='bins':
        st.write(f"Grundbelastung: {data['dirt']} Hygiene, {data['odor']} Geruch, {data['dust']} Staub. Bei Misserfolg zusätzlich bis zu 12 Kraftverlust.")
        st.caption('Deine Spielboni: '+', '.join(f'{label} {physiology.bonus(r,key)}' for key,label in [('handling','Hygieneschutz'),('dust_guard','Staubschutz'),('odor_guard','Geruchsschutz'),('grip','Griff')]))
        hint=check_hint(salvage.preview(r),'Erfolg: zwei Materialangebote. Misserfolg: kein Material und zusätzliche Belastung. Eine Runde vergeht; Ausrüstung kann verschleißen.')
        if st.button('Sortieren & Material prüfen',key=prefix+'sort',type='primary',help=hint):salvage.resolve(r);st.rerun()
        if st.button('Diese Station ohne Materialsuche beenden',key=prefix+'skip'):salvage.leave(r);st.rerun()
    else:
        st.info(r['bin_result'])
        for i,key in enumerate(r['bin_loot']):
            data=game.ITEMS[key]
            st.write('**'+data['name']+'** · '+description(data))
            if st.button('Material mitnehmen',key=f'{prefix}bin_take_{i}',disabled=game.weight(r)+data['weight']>game.stats(r)['capacity']):salvage.take(r,i);st.rerun()
        if st.button('Tonnenrunde abschließen',key=prefix+'finish',type='primary'):salvage.leave(r);st.rerun()


def collection_points(r):
    st.subheader('Acht Sammelplätze für die Tonnenrunde')
    st.write('Eine optionale Station statt der nächsten Abholung. Vorher Handschuhe, Maske und Schuhe passend wählen. Material aus Freigaben und Spenden ergänzen deinen Rucksack; die Runde zählt nicht als Lebensmittelrettung.')
    for key,data in salvage.BINS.items():
        with st.container(border=True):
            st.markdown('### '+data['icon']+' '+data['name'])
            st.write(data['text'])
            st.caption(f"SG {data['dc']} · {rpg.ATTRIBUTES[data['stat']]} · Hygiene {data['dirt']} / Staub {data['dust']} / Geruch {data['odor']}")
            if st.button('Diesen Sammelplatz aufsuchen',key='bin_choose_'+key,disabled=r['phase']!='map' or (r['day']==5 and r['step']==3)):
                salvage.choose(r,key);st.rerun()
