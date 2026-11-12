import json, os, subprocess, sys, tempfile, unittest, aimeter


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


class AuditSpoken(unittest.TestCase):
    """audit.py reads only the spoken words when the band file says "_spoken": true."""
    HERE = os.path.dirname(os.path.abspath(__file__))
    TELL = "It was not just a city, but a home."

    def audit_states(self, text, spoken_bands):
        with tempfile.TemporaryDirectory() as d:
            with open(aimeter.BANDS_FILE, encoding="utf-8") as f:
                bands = json.load(f)
            if spoken_bands:
                bands["_spoken"] = True
            bf, tf = os.path.join(d, "b.json"), os.path.join(d, "t.txt")
            with open(bf, "w", encoding="utf-8") as f:
                json.dump(bands, f)
            with open(tf, "w", encoding="utf-8") as f:
                f.write(text)
            out = subprocess.run([sys.executable, os.path.join(self.HERE, "audit.py"), "--json", tf],
                                 capture_output=True, text=True, encoding="utf-8",
                                 env={**os.environ, "QUIRON_BANDS": bf})
            return {i["id"]: i["state"] for i in json.loads(out.stdout)["items"]}

    FILLER = "".join(f"Sentence number {i} talks about rivers and why they matter nearby.\n" for i in range(20))

    def test_stage_direction_does_not_trip_a_pattern(self):
        text = f"[B-ROLL: {self.TELL}]\n" + self.FILLER
        self.assertEqual(self.audit_states(text, False)["A1b"], "TELL")
        self.assertEqual(self.audit_states(text, True)["A1b"], "PASS")

    def test_spoken_words_still_trip_it(self):
        text = f"NARRATOR: {self.TELL}\n" + self.FILLER
        self.assertEqual(self.audit_states(text, True)["A1b"], "TELL")


if __name__ == "__main__":
    unittest.main()
