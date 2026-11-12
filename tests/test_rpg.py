import unittest
from unittest.mock import patch
import rogue as game
from tests.flows import prepared_visit, complete_briefing
import rpg
from pathlib import Path
from streamlit.testing.v1 import AppTest

class CharacterChecksTest(unittest.TestCase):
    def test_four_dice_drop_lowest_and_limited_rerolls(self):
        r = game.make_run(7)
        self.assertEqual(r['phase'], 'creation')
        for key, dice in r['attribute_dice'].items():
            self.assertEqual(len(dice), 4)
            self.assertTrue(all(1 <= n <= 6 for n in dice))
            self.assertEqual(sum(sorted(dice)[1:]), r['attributes'][key])
        prepared_visit(r, 0)
        self.assertEqual(r['phase'], 'creation')
        game.reroll_character(r); game.reroll_character(r)
        before = dict(r['attributes'])
        game.reroll_character(r)
        self.assertEqual(r['rerolls'], 2)
        self.assertEqual(r['attributes'], before)
        game.confirm_character(r, 'Mira', 'Lagercrew')
        self.assertEqual(r['attributes']['strength'], before['strength'] + 2)
        self.assertEqual(r['character_name'], 'Mira')
        game.confirm_character(r, 'Other', 'Lagercrew')
        self.assertEqual(r['attributes']['strength'], before['strength'] + 2)

    def test_chance_matches_all_twenty_possible_rolls(self):
        r = game.make_run()
        for bonus in (-8, 0, 5, 25):
            spec = dict(bonus=bonus, dc=14, attribute='strength')
            outcomes = []
            for face in range(1, 21):
                with patch.object(r['rng'], 'randint', return_value=face):
                    outcomes.append(rpg.resolve(r, spec))
            self.assertEqual(sum(outcomes) * 5, rpg.chance(bonus, 14))
            self.assertFalse(outcomes[0])
            self.assertTrue(outcomes[-1])

    def test_preview_is_pure_and_accounts_for_gear_and_condition(self):
        r = game.make_run(7); game.confirm_character(r)
        uid = game.add_item(r, 'clipboard'); game.equip(r, uid)
        r.update(energy=20, nausea=55)
        state = r['rng'].getstate()
        spec = rpg.preview(r, 'insight', 13)
        self.assertEqual(spec['tool'], 2)
        self.assertEqual(spec['fatigue'], -2)
        self.assertEqual(spec['stomach'], -2)
        self.assertEqual(spec['bonus'], spec['base'] - 2)
        self.assertEqual(r['rng'].getstate(), state)
        self.assertIsNone(r['last_check'])

    def test_heavy_failure_spends_energy_and_success_makes_progress(self):
        for face, success in [(1, False), (20, True)]:
            r = game.make_run(7); game.confirm_character(r); prepared_visit(r, 0)
            r['enemy']['intent'] = 'recover'
            hp = r['enemy']['hp']; energy = r['energy']
            spec = rpg.action_spec(r, 'heavy')
            with patch.object(r['rng'], 'randint', return_value=face):
                game.combat_action(r, 'heavy')
            self.assertEqual(r['energy'], energy - 15)
            self.assertEqual(r['last_check']['success'], success)
            self.assertEqual(r['last_check']['chance'], spec['chance'])
            self.assertEqual(r['enemy']['hp'] < hp, success)

    def test_event_and_replacement_really_use_checks(self):
        r = game.make_run(); game.confirm_character(r)
        r.update(phase='event', event='rain')
        with patch.object(r['rng'], 'randint', return_value=1):
            game.event(r, False)
        self.assertFalse(r['last_check']['success'])
        self.assertEqual(r['last_check']['attribute'], 'dexterity')
        prepared_visit(r, 0)
        with patch.object(r['rng'], 'randint', return_value=20):
            game.combat_action(r, 'flee')
        self.assertTrue(r['last_check']['success'])
        self.assertEqual(r['last_check']['attribute'], 'presence')
        self.assertEqual(r['phase'], 'map')

class CharacterUiTest(unittest.TestCase):
    def test_creation_tooltips_and_roll_result(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == 'Attribute neu würfeln').click().run()
        self.assertEqual(app.session_state['rogue_run']['rerolls'], 1)
        next(b for b in app.button if b.label == 'Charakter übernehmen & Tour beginnen').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('check-tooltip' in m.value for m in app.markdown))
        next(b for b in app.button if b.key == 'visit_0').click().run()
        complete_briefing(app)
        next(b for b in app.button if b.key == 'fight_attack').click().run()
        self.assertFalse(app.exception)
        self.assertIsNotNone(app.session_state['rogue_run']['last_check'])
        self.assertTrue(app.success or app.warning)

if __name__ == '__main__': unittest.main()
