"""Shared journey steps used by tests of later encounter mechanics."""
import rogue as game
import foodsharing as fs


def prepared_visit(r, index):
    game.visit(r, index)
    if r['phase'] == 'briefing':
        fs.finish_briefing(r, fs.briefing(r)['correct'], True, True, True, True)


def complete_briefing(app):
    r = app.session_state['rogue_run']
    if r['phase'] != 'briefing':
        return
    for prefix in ('papers_', 'notes_', 'containers_', 'hands_'):
        next(c for c in app.checkbox if c.key and c.key.startswith(prefix)).check().run()
    next(c for c in app.radio if c.key and c.key.startswith('brief_response_')).set_value(fs.briefing(r)['correct']).run()
    next(b for b in app.button if b.label == 'Vorbereitung bestätigen & Abholung beginnen').click().run()
