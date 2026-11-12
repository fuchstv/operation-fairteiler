import copy
import unittest
from unittest.mock import patch
from pathlib import Path
from streamlit.testing.v1 import AppTest
import rogue as game
import physiology as body
import salvage
import rpg
import foodsharing
from catalog import FOOD_POOLS
from tests.flows import prepared_visit

class ItemSystemsTest(unittest.TestCase):
    def run_state(self):
        r=game.make_run(72);game.confirm_character(r);return r

    def test_large_catalog_has_usable_slots_descriptions_and_loot_sources(self):
        from narrative import FLAVOUR
        self.assertGreaterEqual(len(game.ITEMS),150)
        self.assertEqual(set(game.ITEMS),set(FLAVOUR))
        self.assertEqual(len(game.SLOTS),7)
        foods={k for pool in FOOD_POOLS for k in pool}|{'snack'}
        self.assertTrue(all(k in foods for k,v in game.ITEMS.items() if v['kind']=='food'))
        for data in game.ITEMS.values():
            self.assertIn(data['kind'], set(game.SLOTS)|{'food','consumable'})
            self.assertGreater(data['weight'],0)

    def test_gloves_mask_and_shoes_have_independent_slots(self):
        r=self.run_state()
        for key in ['rubber_gloves','ffp2_mask','trainers']:
            game.equip(r,game.add_item(r,key))
        self.assertEqual(set(r['equipped']), {'weapon','armor','gear','hands','face','feet'})
        self.assertGreater(body.bonus(r,'handling'),0)
        self.assertGreater(body.bonus(r,'dust_guard'),0)
        before=r['energy'];game.tick(r)
        self.assertEqual(r['energy'],before-2)
        game.unequip(r,'face')
        self.assertEqual(body.bonus(r,'dust_guard'),0)

    def test_legacy_gloves_migrate_without_duplicate_bonuses(self):
        r=self.run_state();uid=game.add_item(r,'gloves');r['equipped']['armor']=uid
        body.ensure(r)
        self.assertEqual(r['equipped']['hands'],uid)
        self.assertNotIn('armor',r['equipped'])
        self.assertEqual(game.stats(r)['defense'],6)

    def test_wear_disables_bonuses_until_repaired_and_does_not_reset_on_equip(self):
        r=self.run_state();uid=game.add_item(r,'ffp2_mask');game.equip(r,uid)
        obj=next(o for o in r['inventory'] if o['uid']==uid);obj['durability']=1
        game.tick(r)
        self.assertEqual(body.bonus(r,'dust_guard'),0)
        game.unequip(r,'face');game.equip(r,uid)
        self.assertEqual(obj['durability'],0)
        game.consume(r,game.add_item(r,'spare_filters'))
        self.assertEqual(obj['durability'],23) # repaired to max 24, then one round of use
        self.assertGreater(body.bonus(r,'dust_guard'),0)

    def test_effects_refresh_expire_and_modify_the_actual_check(self):
        r=self.run_state();base=rpg.preview(r,'insight',14)['bonus']
        game.consume(r,game.add_item(r,'route_note'))
        self.assertEqual(rpg.preview(r,'insight',14)['bonus'],base+2)
        game.consume(r,game.add_item(r,'route_note'))
        self.assertEqual(rpg.preview(r,'insight',14)['bonus'],base+2)
        for _ in range(5):game.tick(r)
        self.assertNotIn('insight',r['effects'])
        self.assertEqual(rpg.preview(r,'insight',14)['bonus'],base)

    def test_temporary_cooling_protects_full_advertised_duration(self):
        r=self.run_state();uid=game.add_item(r,'yogurt');obj=r['inventory'][-1]
        game.consume(r,game.add_item(r,'ice_pack'))
        for _ in range(4):game.tick(r)
        self.assertTrue(obj['cold_chain_ok'])
        self.assertEqual(game.stats(r)['cooling'],0)
        game.tick(r)
        self.assertFalse(obj['cold_chain_ok'])
        self.assertFalse(foodsharing.eligibility(r,obj,'personal')[0])

    def test_food_is_digested_over_time_and_fat_slows_release(self):
        r=self.run_state();r['energy']=20
        game.consume(r,game.add_item(r,'nuts'))
        self.assertGreater(len(r['digestion']),0)
        remaining=r['digestion'][0]['energy']
        energy=r['energy'];game.tick(r)
        self.assertEqual(r['digestion'][0]['energy'],remaining-3)
        self.assertEqual(r['energy'],energy) # -3 action cost +3 absorbed

    def test_dirty_hands_increase_food_risk_and_masks_do_not_make_food_safe(self):
        clean=self.run_state();dirty=copy.deepcopy(clean);dirty['hygiene']=10
        game.equip(dirty,game.add_item(dirty,'ffp3_mask'))
        game.consume(clean,next(o['uid'] for o in clean['inventory'] if o['key']=='banana'))
        game.consume(dirty,next(o['uid'] for o in dirty['inventory'] if o['key']=='banana'))
        self.assertGreater(dirty['nausea'],clean['nausea'])
        self.assertTrue(body.wash(dirty))
        self.assertEqual(dirty['hygiene'],100)

    def test_salt_gas_urgency_and_restroom_have_distinct_effects(self):
        r=self.run_state();water=r['water']
        game.consume(r,game.add_item(r,'chips'))
        self.assertEqual(r['water'],water-4)
        self.assertGreater(r['salt_load'],0)
        r.update(gas=70,urgency=90,nausea=30)
        self.assertTrue(body.restroom(r))
        self.assertLessEqual(r['urgency'],3)
        self.assertLess(r['gas'],50)
        self.assertLess(r['nausea'],30)

    def test_failed_heavy_action_remains_zero_progress_with_nausea(self):
        r=self.run_state();prepared_visit(r,0)
        r['nausea']=60;r['enemy']['intent']='recover'
        hp=r['enemy']['hp']
        with patch.object(r['rng'],'randint',return_value=1):
            game.combat_action(r,'heavy')
        self.assertFalse(r['last_check']['success'])
        self.assertEqual(r['enemy']['hp'],hp)

    def test_new_prepared_food_still_obeys_fairteiler_restrictions(self):
        r=self.run_state();uid=game.add_item(r,'pasta');obj=r['inventory'][-1]
        game.equip(r,game.add_item(r,'cooler'));foodsharing.maintain(r)
        self.assertFalse(foodsharing.eligibility(r,obj,'fairteiler')[0])
        self.assertTrue(foodsharing.eligibility(r,obj,'personal')[0])

class BinSystemsTest(unittest.TestCase):
    def run_state(self):
        r=game.make_run(4);game.confirm_character(r);return r

    def test_protection_changes_real_bin_outcomes_without_food_loot(self):
        plain=self.run_state();protected=self.run_state()
        game.equip(protected,game.add_item(protected,'rubber_gloves'))
        game.equip(protected,game.add_item(protected,'carbon_mask'))
        for r in (plain,protected):
            self.assertTrue(salvage.choose(r,'organic'))
            with patch.object(r['rng'],'randint',return_value=20):salvage.resolve(r)
            self.assertEqual(r['phase'],'bin_loot')
            self.assertFalse(salvage.resolve(r))
            self.assertTrue(all(game.ITEMS[k]['kind']!='food' for k in r['bin_loot']))
        self.assertGreater(protected['hygiene'],plain['hygiene'])
        self.assertLess(protected['nausea'],plain['nausea'])
        self.assertEqual(protected['rescued'],0)
        before=len(protected['inventory'])
        self.assertTrue(salvage.take(protected,0))
        self.assertEqual(len(protected['inventory']),before+1)
        salvage.leave(protected)
        self.assertEqual(protected['step'],1)
        self.assertFalse(salvage.leave(protected))

    def test_finale_and_dead_runs_cannot_be_skipped_for_bin_loot(self):
        r=self.run_state();r.update(day=5,step=3)
        self.assertFalse(salvage.choose(r,'paper'))
        r['phase']='dead'
        self.assertFalse(salvage.choose(r,'paper'))
        self.assertFalse(salvage.take(r,0))
        self.assertFalse(body.wash(r))

class EquipmentUiTest(unittest.TestCase):
    def test_equip_gloves_then_resolve_bin_scene_without_widget_collisions(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run()
        next(b for b in app.button if b.label=='Charakter übernehmen & Tour beginnen').click().run()
        uid=next(o['uid'] for o in app.session_state['rogue_run']['inventory'] if o['key']=='cotton_gloves')
        next(b for b in app.button if b.key==f'bag_equip_{uid}').click().run()
        next(b for b in app.button if b.key=='bin_choose_paper').click().run()
        self.assertFalse(app.exception)
        next(b for b in app.button if b.key=='tab_sort').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['rogue_run']['phase'],'bin_loot')
        next(b for b in app.button if b.key=='tab_finish').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['rogue_run']['phase'],'map')

if __name__=='__main__':unittest.main()
