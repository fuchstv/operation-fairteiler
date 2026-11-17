"""Exercise the real Streamlit script, session transitions and learning gates."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / 'app.py'

class AdventureTest(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(APP)).run()
        self.app.selectbox(key='game_mode').select('Lernabenteuer').run()
        self.assertFalse(self.app.exception)

    def click(self, label):
        next(b for b in self.app.button if b.label == label).click().run()
        self.assertFalse(self.app.exception)

    def state(self):
        return self.app.session_state['adventure']

    def learn(self):
        self.click('Mein Abenteuer beginnen')
        for answer in [
            'Rechtzeitig austragen und gegebenenfalls Ersatz suchen.',
            'Nein, Hackfleisch ist für diese Weitergabe ausgeschlossen.',
            'Nein, nach dem Verbrauchsdatum nicht weitergeben.',
        ]:
            self.click(answer)
            self.click('Weiter')

    def test_complete_adventure_and_reset(self):
        self.app.text_input[0].input('Mira').run()
        self.app.radio[0].set_value('Zu Fuß').run()
        self.learn()
        self.assertEqual(self.state()['name'], 'Mira')
        self.assertEqual(self.state()['route'], 'Zu Fuß')
        gate = next(b for b in self.app.button if b.label == 'Zur ersten Einführungsabholung')
        self.assertTrue(gate.disabled)
        self.app.checkbox[0].check().run()
        self.click('Zur ersten Einführungsabholung')
        for index, answer in enumerate([
            'Absprachen lesen, pünktlich sein und saubere Lebensmittelbehälter mitnehmen.',
            'Jedes Stück prüfen und schimmelige Lebensmittel aussortieren.',
            'Erst einen geeigneten gekühlten Transport organisieren.',
        ]):
            self.click(answer)
            self.assertTrue(self.state()['inventory'])
            self.assertEqual(self.state()['pickup'], index)
            self.click('Lebensmittel teilen & Tour abschließen')
            self.assertFalse(self.state()['inventory'])
        self.assertEqual(self.state()['stage'], 'verification')
        self.assertEqual(self.state()['pickup'], 3)
        self.click('Kapitel abschließen')
        self.assertEqual(self.state()['stage'], 'finish')
        self.assertEqual(self.state()['shared'], 4)
        self.click('Spiel zurücksetzen')
        self.assertEqual(self.state()['stage'], 'intro')
        self.assertEqual(self.state()['shared'], 0)

    def test_wrong_answer_does_not_advance_or_end_game(self):
        self.click('Mein Abenteuer beginnen')
        for _ in range(4):
            self.click('Einfach nicht erscheinen.')
        self.assertEqual(self.state()['quiz'], 0)
        self.assertFalse(self.state()['answered'])
        self.assertEqual(self.state()['mistakes'], 4)
        self.assertFalse(any(b.label == 'Weiter' for b in self.app.button))
        self.click('Rechtzeitig austragen und gegebenenfalls Ersatz suchen.')
        self.assertTrue(self.state()['answered'])
        self.click('Weiter')
        self.assertEqual(self.state()['quiz'], 1)

    def test_preferences_and_blank_name(self):
        self.app.text_input[0].input('   ').run()
        self.app.toggle[0].set_value(True).run()
        self.app.toggle[1].set_value(False).run()
        self.click('Mein Abenteuer beginnen')
        self.assertEqual(self.state()['name'], 'Alex')
        self.assertTrue(self.state()['sound'])
        self.assertFalse(self.state()['motion'])
        self.click('Rechtzeitig austragen und gegebenenfalls Ersatz suchen.')
        self.assertTrue(self.app.get('audio'))
        self.click('Spiel zurücksetzen')
        self.assertFalse(self.state()['sound'])

if __name__ == '__main__':
    unittest.main()
