import copy
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
import rogue as game
from tests.flows import prepared_visit, complete_briefing

class RogueRulesTest(unittest.TestCase):
    def run_state(self):
        r = game.make_run(22)
        game.confirm_character(r)
        return r

    def fight(self, r):
        prepared_visit(r, 0)
        self.assertEqual(r['phase'], 'combat')

    def test_seed_replays_and_diverges(self):
        a, b = game.make_run(22), game.make_run(22)
        game.confirm_character(a); game.confirm_character(b)
        prepared_visit(a, 0); prepared_visit(b, 0)
        game.combat_action(a, 'attack'); game.combat_action(b, 'attack')
        for key in ('enemy', 'hp', 'energy', 'options', 'combat'):
            self.assertEqual(a[key], b[key])
        self.assertNotEqual(game.make_run(2)['options'], game.make_run(3)['options'])

    def test_equipment_changes_stats_and_does_not_duplicate(self):
        r = self.run_state()
        uid = game.add_item(r, 'rolling')
        before = game.stats(r)['attack']
        game.equip(r, uid)
        self.assertEqual(game.stats(r)['attack'] - before, 9)
        game.equip(r, uid)
        self.assertEqual(game.stats(r)['attack'] - before, 9)
        game.drop(r, uid)
        self.assertIn(uid, [o['uid'] for o in r['inventory']])

    def test_consumables_are_single_use_and_combat_costs_a_turn(self):
        r = self.run_state(); self.fight(r)
        uid = next(o['uid'] for o in r['inventory'] if o['key'] == 'bandage')
        r['hp'] = 40; r['enemy']['intent'] = 'recover'
        turn = r['turn']
        self.assertTrue(game.consume(r, uid))
        self.assertEqual(r['turn'], turn + 1)
        self.assertEqual(r['hp'], 68)
        self.assertFalse(game.consume(r, uid))
        self.assertEqual(r['turn'], turn + 1)
        self.assertEqual(r['enemy']['intent'], 'attack')

    def test_cooling_only_protects_future_ticks(self):
        r = self.run_state()
        uid = game.add_item(r, 'yogurt'); obj = r['inventory'][-1]
        for _ in range(3): game.tick(r)
        self.assertEqual(game.freshness(r, obj), 2)
        cooler = game.add_item(r, 'cooler'); game.equip(r, cooler)
        self.assertEqual(game.freshness(r, obj), 2)
        for _ in range(3): game.tick(r)
        self.assertAlmostEqual(game.freshness(r, obj), 1)
        game.equip(r, next(o['uid'] for o in r['inventory'] if o['key'] == 'tote'))
        game.tick(r)
        self.assertAlmostEqual(game.freshness(r, obj), 0)

    def test_spoiled_food_overeating_and_cramps(self):
        r = self.run_state(); r['fullness'] = 90
        uid = game.add_item(r, 'yogurt'); r['inventory'][-1]['age'] = 10
        game.consume(r, uid)
        self.assertGreaterEqual(r['nausea'], 70)
        self.assertLess(r['hp'], 100)
        self.assertEqual(r['fullness'], 95)

    def test_permadeath_blocks_followup_actions(self):
        r = self.run_state(); self.fight(r)
        r['hp'] = 1; r['water'] = 0
        game.combat_action(r, 'attack')
        self.assertEqual(r['phase'], 'dead')
        snapshot = copy.deepcopy(r['inventory'])
        turn = r['turn']
        game.consume(r, next(o['uid'] for o in r['inventory'] if o['key'] == 'bandage'))
        game.combat_action(r, 'attack'); prepared_visit(r, 0)
        self.assertEqual(r['inventory'], snapshot)
        self.assertEqual(r['turn'], turn)

    def test_loot_limit_and_reward_only_once(self):
        r = self.run_state(); self.fight(r)
        r['enemy']['hp'] = 1
        game.combat_action(r, 'attack')
        self.assertEqual(r['phase'], 'loot')
        game.combat_action(r, 'attack')
        self.assertEqual(r['wins'], 1)
        r['loot'] = ['pot']
        while game.weight(r) < game.stats(r)['capacity']:
            game.add_item(r, 'water')
        self.assertFalse(game.take_loot(r, 0))
        self.assertEqual(r['loot'], ['pot'])
        game.finish_loot(r)
        self.assertEqual(r['step'], 1)
        game.finish_loot(r)
        self.assertEqual(r['step'], 1)

    def test_camp_never_shares_spoiled_or_cold_food(self):
        r = self.run_state()
        r['inventory'] = []; r['equipped'] = {}
        for key in ('bread', 'yogurt', 'apple'): game.add_item(r, key)
        r['inventory'][-1]['age'] = 100
        r['phase'] = 'camp'
        game.camp(r, 'share')
        self.assertEqual(r['shared'], 1)
        self.assertEqual([o['key'] for o in r['inventory']], ['yogurt', 'apple'])
        game.camp(r, 'share')
        self.assertEqual(r['shared'], 1)

    def test_final_boss_is_mandatory_and_completes_run(self):
        r = self.run_state(); r.update(day=5, step=3)
        game.make_options(r)
        self.assertEqual(len(r['options']), 1)
        self.fight(r)
        self.assertTrue(r['enemy']['boss'])
        turn = r['turn']; game.combat_action(r, 'flee')
        self.assertEqual(r['turn'], turn)
        r['enemy']['hp'] = 1
        game.combat_action(r, 'attack')
        self.assertEqual(r['phase'], 'loot')
        game.finish_loot(r)
        self.assertEqual(r['phase'], 'victory')

    def test_business_has_its_own_problem_and_counts_only_packed_food(self):
        from narrative import ENCOUNTERS, FLAVOUR
        self.assertEqual(set(FLAVOUR), set(game.ITEMS))
        self.assertEqual(len({e['name'] for e in ENCOUNTERS}), len(game.BUSINESSES))
        r = self.run_state(); self.fight(r)
        self.assertEqual(r['enemy']['narrative'], ENCOUNTERS[r['encounter']['venue']])
        r['enemy']['hp'] = 1
        game.combat_action(r, 'attack')
        self.assertEqual(r['rescued'], 0)
        self.assertTrue(game.take_loot(r, 0))
        self.assertEqual(r['rescued'], 1)
        game.finish_loot(r)
        self.assertEqual(r['rescued'], 1)

    def test_heavy_attack_cannot_make_energy_negative(self):
        r = self.run_state(); self.fight(r); r['energy'] = 13
        turn = r['turn']; game.combat_action(r, 'heavy')
        self.assertEqual(r['turn'], turn)
        r['energy'] = 15; game.combat_action(r, 'heavy')
        self.assertEqual(r['energy'], 0)

class LocalPvpTest(unittest.TestCase):
    def test_two_humans_alternate_and_block_works(self):
        d = game.make_duel('A', 'B')
        game.duel_action(d, 'defend')
        self.assertEqual(d['turn'], 1)
        game.duel_action(d, 'attack')
        self.assertEqual(d['players'][0]['hp'], 99)
        self.assertEqual(d['turn'], 0)

    def test_victory_and_unavailable_actions_do_not_change_state(self):
        d = game.make_duel('A', 'B')
        d['players'][0]['stamina'] = 0
        game.duel_action(d, 'heavy')
        self.assertEqual(d['turn'], 0)
        d['players'][1]['hp'] = 1
        game.duel_action(d, 'attack')
        self.assertEqual(d['winner'], 0)
        history = list(d['log'])
        game.duel_action(d, 'heal')
        self.assertEqual(d['log'], history)

class RogueUiTest(unittest.TestCase):
    def test_live_combat_inventory_and_hotseat(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == 'Charakter übernehmen & Tour beginnen').click().run()
        next(b for b in app.button if b.key == 'visit_0').click().run()
        complete_briefing(app)
        self.assertFalse(app.exception)
        next(b for b in app.button if b.key == 'fight_attack').click().run()
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == 'Hotseat-Duell starten').click().run()
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == 'PvP: Tempo machen').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['local_duel']['turn'], 1)
        self.assertEqual(app.session_state['rogue_run']['phase'], 'combat')

if __name__ == '__main__': unittest.main()
