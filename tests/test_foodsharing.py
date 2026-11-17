import copy
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
import rogue as game
import foodsharing as fs

class WikiJourneyTest(unittest.TestCase):
    def run_state(self):
        r = game.make_run(9); game.confirm_character(r)
        return r

    def test_briefing_gate_requires_papers_and_correct_decision(self):
        r = self.run_state(); game.visit(r, 0)
        self.assertEqual(r['phase'], 'briefing')
        response = fs.briefing(r)['correct']
        turn = r['turn']; rng = r['rng'].getstate()
        self.assertFalse(fs.finish_briefing(r, response, False, True, True, True))
        self.assertFalse(fs.finish_briefing(r, 1-response, True, True, True, True))
        self.assertEqual(r['phase'], 'briefing')
        self.assertEqual(r['rng'].getstate(), rng)
        self.assertFalse(r['violations'])
        self.assertEqual(r['turn'], turn)
        self.assertTrue(fs.finish_briefing(r, response, True, True, True, True))
        self.assertEqual(r['phase'], 'combat')
        enemy = copy.deepcopy(r['enemy'])
        self.assertFalse(fs.finish_briefing(r, response, True, True, True, True))
        self.assertEqual(r['enemy'], enemy)

    def test_all_eight_wiki_situations_can_be_reached_and_corrected(self):
        covered = set()
        for venue in range(8):
            r = self.run_state(); r['options'] = [dict(kind='business', venue=venue, danger=1)]
            game.visit(r, 0)
            data = fs.briefing(r); covered.add(data['title'])
            self.assertTrue(fs.finish_briefing(r, data['correct'], True, True, True, True))
        self.assertEqual(len(covered), 8)

    def test_personal_handover_requires_checks_and_conversation(self):
        r = self.run_state(); bread = next(o['uid'] for o in r['inventory'] if o['key']=='bread')
        self.assertFalse(fs.transfer(r, [bread], 'personal', True, False))
        self.assertFalse(fs.transfer(r, [bread], 'personal', False, True))
        self.assertTrue(fs.transfer(r, [bread], 'personal', True, True))
        self.assertEqual(r['shared'], 1)
        self.assertFalse(fs.transfer(r, [bread], 'personal', True, True))
        self.assertEqual(r['shared'], 1)
        self.assertEqual(r['distribution_log'][0]['channel'], 'personal')
        self.assertEqual(r['fairteiler_shared'], 0)

    def test_prepared_meal_cannot_go_in_fairteiler_but_can_be_personal(self):
        r = self.run_state(); uid = game.add_item(r, 'soup'); obj=r['inventory'][-1]
        self.assertFalse(fs.eligibility(r, obj, 'fairteiler')[0])
        self.assertTrue(fs.eligibility(r, obj, 'personal')[0])
        self.assertTrue(fs.transfer(r, [uid], 'personal', True, True))

    def test_cold_food_needs_recorded_fridge_and_intact_chain(self):
        r = self.run_state(); game.equip(r, game.add_item(r, 'cooler'))
        uid=game.add_item(r, 'yogurt'); obj=r['inventory'][-1]
        self.assertFalse(fs.transfer(r, [uid], 'fairteiler', True, False))
        self.assertTrue(fs.maintain(r))
        self.assertFalse(fs.maintain(r))
        self.assertEqual(len(r['hygiene_log']), 1)
        self.assertTrue(fs.eligibility(r, obj, 'fairteiler')[0])
        self.assertTrue(fs.transfer(r, [uid], 'fairteiler', True, False))
        r['day']=2; uid=game.add_item(r, 'cheese')
        self.assertFalse(fs.eligibility(r, r['inventory'][-1], 'fairteiler')[0])

    def test_late_cooling_does_not_repair_broken_chain(self):
        r=self.run_state(); uid=game.add_item(r, 'yogurt'); obj=r['inventory'][-1]
        game.tick(r)
        game.equip(r, game.add_item(r, 'cooler'))
        fs.maintain(r)
        self.assertGreater(game.freshness(r,obj),0)
        self.assertFalse(fs.eligibility(r,obj,'personal')[0])
        self.assertFalse(fs.eligibility(r,obj,'fairteiler')[0])

    def test_basket_reservation_blocks_consumption_drop_and_double_transfer(self):
        r=self.run_state(); uid=next(o['uid'] for o in r['inventory'] if o['key']=='bread')
        self.assertTrue(fs.create_basket(r,[uid],True))
        self.assertEqual(r['shared'],0)
        self.assertFalse(game.consume(r,uid)); game.drop(r,uid)
        self.assertTrue(any(o['uid']==uid for o in r['inventory']))
        self.assertFalse(fs.transfer(r,[uid],'personal',True,True))
        self.assertFalse(fs.deliver_basket(r,True,True))
        self.assertTrue(fs.wait_for_basket(r))
        self.assertTrue(fs.deliver_basket(r,True,True))
        self.assertEqual(r['shared'],1)
        self.assertFalse(fs.deliver_basket(r,True,True))

    def test_food_is_rechecked_at_basket_handover(self):
        r=self.run_state(); uid=game.add_item(r,'berries'); obj=r['inventory'][-1];obj['age']=3
        self.assertTrue(fs.create_basket(r,[uid],True))
        self.assertTrue(fs.wait_for_basket(r))
        self.assertEqual(game.freshness(r,obj),0)
        self.assertFalse(fs.deliver_basket(r,True,True))
        self.assertEqual(r['shared'],0)
        self.assertTrue(fs.cancel_basket(r))
        self.assertFalse(fs.reserved(r,uid))

    def test_unknown_duplicate_or_dead_transfers_are_rejected(self):
        r=self.run_state(); uid=next(o['uid'] for o in r['inventory'] if o['key']=='bread')
        self.assertFalse(fs.transfer(r,[uid,uid],'personal',True,True))
        self.assertFalse(fs.transfer(r,[uid,999],'personal',True,True))
        r['phase']='dead'
        self.assertFalse(fs.transfer(r,[uid],'personal',True,True))
        self.assertFalse(fs.create_basket(r,[uid],True))
        self.assertFalse(fs.maintain(r))

    def test_camp_does_not_take_reserved_or_prepared_food(self):
        r=self.run_state(); uid=next(o['uid'] for o in r['inventory'] if o['key']=='bread')
        fs.create_basket(r,[uid],True); game.add_item(r,'soup')
        r['phase']='camp'; game.camp(r,'share')
        self.assertTrue(any(o['uid']==uid for o in r['inventory']))
        self.assertTrue(any(o['key']=='soup' for o in r['inventory']))
        self.assertEqual(r['shared'],1) # only the unreserved starter banana

class FairteilungUiTest(unittest.TestCase):
    def test_real_widgets_reserve_wait_and_deliver_basket(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run()
        next(b for b in app.button if b.label=='Charakter übernehmen & Tour beginnen').click().run()
        app.selectbox(key='sharing_channel').select('basket').run()
        uid=next(o['uid'] for o in app.session_state['rogue_run']['inventory'] if o['key']=='bread')
        app.multiselect(key='share_selection_basket').set_value([uid]).run()
        app.checkbox(key='share_checked_basket').check().run()
        next(b for b in app.button if b.key=='share_execute').click().run()
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label=='Eine Runde auf die Abholabsprache warten').click().run()
        app.checkbox(key='basket_checked').check().run()
        app.checkbox(key='basket_conversation').check().run()
        next(b for b in app.button if b.label=='Essenskorb persönlich übergeben').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['rogue_run']['shared'],1)
        self.assertIsNone(app.session_state['rogue_run']['basket'])

if __name__=='__main__':unittest.main()
