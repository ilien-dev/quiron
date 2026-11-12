import os, tempfile, unittest, aimeter


class Spoken(unittest.TestCase):
    def test_strips_markup(self):
        src = "## COLD OPEN\n[B-ROLL: city at night]\nNARRATOR: You were on your way home.\n(0:15) It was late.\n[Music]\n♪ ♪"
        self.assertEqual(aimeter.spoken(src).split(), "You were on your way home. It was late.".split())

    def test_keeps_spoken_parenthesis(self):
        self.assertIn("(about 40%)", aimeter.spoken("Most of it (about 40%) is water."))

    def test_bold_speaker_label(self):
        self.assertEqual(aimeter.spoken("**HOST (V.O.):** Here is the thing.").strip(), "Here is the thing.")

    def test_sentence_with_colon_is_not_a_label(self):
        t = "Here is the thing: it works."
        self.assertEqual(aimeter.spoken(t), t)

    def test_two_column_table_keeps_audio(self):
        src = "| VISUAL | AUDIO |\n|---|---|\n| Map zooms in | This river is two thousand years old. |"
        self.assertEqual(aimeter.spoken(src).strip(), "This river is two thousand years old.")

    def test_table_audio_column_first(self):
        src = "| Audio | Visual |\n|---|---|\n| Hello there. | Map zooms in |"
        self.assertEqual(aimeter.spoken(src).strip(), "Hello there.")

    def test_caption_file_unchanged(self):
        t = "You were on your way home, when you died. It was a car accident."
        self.assertEqual(aimeter.spoken(t), t)

    def test_markup_counts(self):
        c = aimeter.markup_counts("[B-ROLL]\nNARRATOR: " + "word " * 500)
        self.assertEqual((c["stage"], c["speaker"]), (2.0, 2.0))

    def test_spanish_labels(self):
        self.assertEqual(aimeter.spoken("[PLANO: la ciudad de noche]\nNARRADOR: Ibas camino a casa.").strip(),
                         "Ibas camino a casa.")

    def test_mostly_markup_is_too_short(self):
        self.assertIsNone(aimeter.measure(aimeter.spoken("[SCENE]\n" * 200 + "Hello there.")))

    def test_measure_dir_spoken_only(self):
        body = "".join(f"Sentence number {i} is plain speech about rivers.\n" for i in range(4))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "a.txt"), "w", encoding="utf-8") as f:
                f.write("[B-ROLL: a river at dawn. The camera pans left slowly.]\n" * 40 + body)
            self.assertEqual(len(aimeter.measure_dir(d)), 1)
            self.assertEqual(aimeter.measure_dir(d, spoken_only=True), [])


if __name__ == "__main__":
    unittest.main()
