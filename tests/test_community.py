import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import community
import rogue as game
from tests.flows import prepared_visit, complete_briefing
import rpg

class DistrictRulesTest(unittest.TestCase):
    def run_state(self):
        r = game.make_run(19); game.confirm_character(r)
        return r

    def test_every_second_business_pickup_prompts_a_real_decision(self):
        r = self.run_state()
        for n in range(2):
            prepared_visit(r, 0); r['enemy']['hp'] = 1
            game.combat_action(r, 'attack'); game.finish_loot(r)
            self.assertEqual(r['phase'], 'map' if n == 0 else 'incident')
        self.assertEqual(r['business_pickups'], 2)
        community.incident_choice(r, 'good')
        self.assertEqual(r['phase'], 'map')
        self.assertEqual(r['responsible_choices'], 1)
        self.assertFalse(r['violations'])
        count = r['step']; community.incident_choice(r, 'bad')
        self.assertEqual(r['step'], count)

    def test_deliberate_violation_and_once_only_repair(self):
        r = self.run_state(); r.update(phase='incident', incident='cold')
        community.incident_choice(r, 'bad')
        self.assertEqual(r['trust'], 35)
        self.assertEqual(len(r['violations']), 1)
        self.assertFalse(community.support(r))
        energy = r['energy']; turn = r['turn']
        self.assertTrue(community.repair(r, 0))
        self.assertEqual(r['trust'], 42)
        self.assertEqual(r['energy'], energy - 11)
        self.assertEqual(r['turn'], turn + 1)
        self.assertTrue(r['violations'][0]['resolved'])
        self.assertFalse(community.repair(r, 0))
        self.assertEqual(len(r['violations']), 1)

    def test_bad_roll_is_not_a_rule_violation(self):
        r = self.run_state(); r.update(phase='incident', incident='sorting')
        with patch.object(r['rng'], 'randint', return_value=1):
            community.incident_choice(r, 'ask')
        self.assertFalse(r['last_check']['success'])
        self.assertFalse(r['violations'])
        self.assertEqual(r['responsible_choices'], 1)
        self.assertEqual(r['trust'], 55)

    def test_support_requires_trust_and_is_limited_per_district(self):
        r = self.run_state(); r.update(hp=40, energy=40, water=40)
        self.assertTrue(community.support(r))
        self.assertEqual((r['hp'], r['energy'], r['water']), (52, 57, 67))
        self.assertFalse(community.support(r))
        r['day'] = 2
        self.assertTrue(community.support(r))
        r.update(day=3, trust=39)
        self.assertFalse(community.support(r))

    def test_quests_need_progress_capacity_and_cannot_be_farmed(self):
        r = self.run_state()
        self.assertFalse(community.claim(r, 'supply'))
        r['fairteiler_shared'] = 3
        while game.weight(r) < game.stats(r)['capacity']:
            game.add_item(r, 'water')
        self.assertFalse(community.claim(r, 'supply'))
        for obj in list(r['inventory']):
            if obj['key'] == 'water': game.drop(r, obj['uid'])
        self.assertTrue(community.claim(r, 'supply'))
        self.assertFalse(community.claim(r, 'supply'))
        self.assertEqual(sum(o['key'] == 'cooler' for o in r['inventory']), 1)

    def test_trust_and_familiarity_affect_preview(self):
        r = self.run_state(); option = dict(kind='business', venue=0, danger=2)
        baseline = rpg.action_spec(r, 'attack', option)
        r['standing'][0] = 2
        self.assertEqual(rpg.action_spec(r, 'attack', option)['dc'], baseline['dc']-1)
        r['trust'] = 75
        self.assertEqual(rpg.preview(r, 'presence', 13)['community'], 1)
        r['trust'] = 20
        self.assertEqual(rpg.preview(r, 'presence', 13)['community'], -1)

class DistrictUiTest(unittest.TestCase):
    def test_incident_has_explicit_confirmation_and_dossier(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
        next(b for b in app.button if b.label == 'Charakter übernehmen & Tour beginnen').click().run()
        r = app.session_state['rogue_run']
        r.update(phase='incident', incident='cold', business_pickups=2)
        app.run()
        self.assertFalse(app.exception)
        bad = next(b for b in app.button if b.label == community.INCIDENTS['cold']['bad'])
        self.assertTrue(bad.disabled)
        app.checkbox(key='bad_choice_2').check().run()
        next(b for b in app.button if b.label == community.INCIDENTS['cold']['bad']).click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state['rogue_run']['violations']), 1)
        next(b for b in app.button if b.key == 'repair_0').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state['rogue_run']['violations'][0]['resolved'])

if __name__ == '__main__': unittest.main()
