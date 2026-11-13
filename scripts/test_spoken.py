import contextlib, io, json, os, subprocess, sys, tempfile, unittest, aimeter


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

    def test_bold_wrapped_direction(self):
        self.assertEqual(aimeter.spoken("**[VISUAL: map]** This river is old."), "This river is old.")

    def test_bold_timestamp_then_label(self):
        self.assertEqual(aimeter.spoken("**[00:15]** HOST: Hi there."), "Hi there.")

    def test_direction_then_label(self):
        self.assertEqual(aimeter.spoken("**[VISUAL: x]** HOST: Hi there."), "Hi there.")

    def test_speech_that_opens_with_a_time_or_an_acronym_is_kept(self):
        for t in ("10:30 is when we left.", "AI: it is everywhere.", "IMPORTANT: wash hands.",
                  "NOTE: this is spoken."):
            self.assertEqual(aimeter.spoken(t), t)

    def test_bare_timestamp_with_dash_and_numbered_speaker(self):
        self.assertEqual(aimeter.spoken("0:15 - SPEAKER 1: Hi there."), "Hi there.")

    def test_short_direction_words(self):
        self.assertEqual(aimeter.spoken("(pause) Hello."), "Hello.")
        self.assertEqual(aimeter.spoken("*(beat)* Well then."), "Well then.")

    def test_two_column_table_keeps_audio(self):
        src = "| VISUAL | AUDIO |\n|---|---|\n| Map zooms in | This river is two thousand years old. |"
        self.assertEqual(aimeter.spoken(src).strip(), "This river is two thousand years old.")

    def test_table_audio_column_first(self):
        src = "| Audio | Visual |\n|---|---|\n| Hello there. | Map zooms in |"
        self.assertEqual(aimeter.spoken(src).strip(), "Hello there.")

    def test_caption_file_unchanged(self):
        t = "You were on your way home, when you died. It was a car accident."
        self.assertEqual(aimeter.spoken(t), t)

    def test_word_count_lines_are_not_speech(self):
        for line in ("*Word count: ~845*", "*~712 words*", "(Word count: 845)", "*(Extensión aproximada: 779 palabras)*",
                     "Palabras: 780", "*Approximately 460 words.*", "- Longitud aproximada: unas 1.130 palabras.",
                     "*Approximate word count: 2,400, including visual directions.*"):
            self.assertEqual(aimeter.spoken("Hello there.\n\n" + line).strip(), "Hello there.", line)
            self.assertGreater(aimeter.markup_counts("Hello there. " * 100 + "\n\n" + line)["stage"], 0, line)

    def test_runtime_header_and_descriptor_lines(self):
        for line in ("**Runtime: ~8 minutes | Script: ~1,177 words**", "**Target length:** about 1,989 words (roughly 13 minutes)",
                     "*YouTube script, approx. 2,600 words*", "**Recuento aproximado:** ~2.640 palabras.",
                     "**Duración estimada:** 7 minutos (~1100 palabras)", "*Note: this is an original script.*",
                     "**Target runtime:** ~19 minutes at a relaxed pace", "**Guion para YouTube · Duración estimada: 10–12 minutos**",
                     "**Duración estimada:** 8-9 minutos\n**Nota:** donde pone [X], entra el invitado."):
            self.assertEqual(aimeter.spoken("Hello there.\n\n" + line).strip(), "Hello there.", line)
        for t in ("The runtime: it is long.", "This script is about 3 words long."):
            self.assertEqual(aimeter.spoken(t), t)

    def test_spoken_words_mentioning_words_are_kept(self):
        for t in ("That is about 845 words of text.", "Son unas 800 palabras de texto, no más."):
            self.assertEqual(aimeter.spoken(t), t)

    def test_production_note_paragraph(self):
        for note in ("**Production notes:**\n\n- Verify the dates.\n- Trim section two.",
                     "*Production note: verify the figures.*", "**Note for production:** check the numbers.",
                     "**Nota para la producción:** revisa las cifras.", "**Notas de producción:**\n\n- Revisar fechas."):
            self.assertEqual(aimeter.spoken("The end.\n\n" + note).strip(), "The end.", note)
        self.assertGreater(aimeter.markup_counts("The end. " * 100 + "\n\n**Nota para la producción:** x.")["stage"], 0)

    def test_speech_that_opens_with_note_is_kept(self):
        t = "Note: this is spoken.\n\nAnd more."
        self.assertEqual(aimeter.spoken(t), t)

    def test_rules_are_not_speech(self):
        self.assertEqual(aimeter.spoken("One.\n\n---\n\nTwo.\n\n***\n\nThree.").split(), ["One.", "Two.", "Three."])
        self.assertEqual(aimeter.prose(aimeter.spoken("---\nHello there.\n---\nBye.")).split(), ["Hello", "there.", "Bye."])

    def test_markup_counts(self):
        c = aimeter.markup_counts("[B-ROLL]\nNARRATOR: " + "word " * 500)
        self.assertEqual((c["stage"], c["speaker"]), (2.0, 2.0))

    def test_leading_production_parenthesis(self):
        self.assertEqual(aimeter.spoken("(B-roll: here's the twist) The river is old."), "The river is old.")
        self.assertEqual(aimeter.spoken("HOST: (On screen: a map) The river is old."), "The river is old.")
        self.assertEqual(aimeter.spoken("(Plano: la ciudad) (En pantalla: un mapa) El río es viejo."), "El río es viejo.")
        self.assertEqual(aimeter.spoken("(Música: suave) El río es viejo."), "El río es viejo.")
        self.assertEqual(aimeter.markup_counts("(SFX: thunder) " + "word " * 500)["stage"], 2.0)

    def test_spoken_parenthesis_at_line_start_is_kept(self):
        for t in ("(About 40%) of it is water.", "(Yes, really.) It works.", "(And this matters: a lot.) Fine."):
            self.assertEqual(aimeter.spoken(t), t)

    def test_closing_sources_block(self):
        src = "The river is old.\n\nSources:\n- [USGS](https://usgs.gov)\n- https://example.org/a\n"
        self.assertEqual(aimeter.spoken(src).strip(), "The river is old.")
        es = "El río es viejo.\n\n**Fuentes de consulta:** [Universidad](https://x.org)\n"
        self.assertEqual(aimeter.spoken(es).strip(), "El río es viejo.")
        self.assertEqual(aimeter.markup_counts("word " * 500 + "\n\nSources: [A](https://a.org)")["stage"], 2.0)

    def test_sources_block_followed_by_speech_is_kept(self):
        src = "Sources: my grandmother, mostly.\n\nAnd she was right about the river."
        self.assertEqual(aimeter.spoken(src), src)

    def test_inline_source_links(self):
        self.assertEqual(aimeter.spoken("It fell by half. [Source: IMF](https://imf.org), [WB](https://wb.org)").strip(),
                         "It fell by half.")
        self.assertEqual(aimeter.spoken("Es así. [Referencia técnica: David Tong](https://x.org).").strip(), "Es así.")
        self.assertEqual(aimeter.spoken("It stood. [Sources: *[Zoo](https://a.org)*; *[Flak](https://b.org)*.]").strip(),
                         "It stood.")
        self.assertEqual(aimeter.spoken("See [the source code](https://x.org) here."),
                         "See [the source code](https://x.org) here.")

    def test_spanish_labels(self):
        self.assertEqual(aimeter.spoken("[PLANO: la ciudad de noche]\nNARRADOR: Ibas camino a casa.").strip(),
                         "Ibas camino a casa.")

    def test_stacked_directions_keep_both_paragraphs(self):
        # spoken() used to leave a run of blank lines where it removed the directions, and
        # prose() read that run plus the next line as indented code and dropped the line
        first = ("Every town on the river has a story about the water. Most of them are about the "
                 "spring floods. The old people in town still talk about the year the bridge went "
                 "under. They say the water came up to the church steps in one night. Nobody had "
                 "a boat, so the baker rowed people across in a bathtub.")
        second = ("The river floods every spring and the town knows it. Nobody moved, and the levee "
                  "went up in 1927. It took two summers and most of the men in the county to build "
                  "it. The levee held for sixty years before it gave way at the north end. After "
                  "that the town built it again, higher this time, and it has held ever since.")
        text = (first + "\n\n**[SECTION 1 - 0:45]**\n\n*(Wide shot of a river.)*\n\n[MUSIC SWELLS]\n\n"
                + second + "\n")
        kept = aimeter.prose(aimeter.spoken(text))
        for para in (first, second):
            for phrase in (" ".join(para.split()[:6]), " ".join(para.split()[-6:])):
                self.assertIn(phrase, kept)
        words = len(aimeter.PROFILES["en"]["word"].findall(first + " " + second))
        self.assertEqual(aimeter.measure(aimeter.spoken(text))["_words"], words)

    def test_spoken_leaves_no_blank_runs_or_indents(self):
        out = aimeter.spoken("Hello there.\n\n[CUT]\n\n(Pause.)\n\n     Indented speech.\n  \n\n\nEnd.")
        self.assertNotIn("\n\n\n", out)
        self.assertFalse(any(l != l.lstrip() for l in out.split("\n")))
        self.assertEqual(out.split(), "Hello there. Indented speech. End.".split())

    def test_mostly_markup_is_too_short(self):
        self.assertIsNone(aimeter.measure(aimeter.spoken("[SCENE]\n" * 200 + "Hello there.")))

    def test_measure_dir_spoken_only(self):
        body = "".join(f"Sentence number {i} is plain speech about rivers.\n" for i in range(4))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "a.txt"), "w", encoding="utf-8") as f:
                f.write("[B-ROLL: a river at dawn. The camera pans left slowly.]\n" * 40 + body)
            self.assertEqual(len(aimeter.measure_dir(d)), 1)
            self.assertEqual(aimeter.measure_dir(d, spoken_only=True), [])

    def test_recalibration_keeps_spoken(self):
        t = "".join(f"Sentence number {i} is plain speech about rivers and the people near them.\n"
                    for i in range(15))
        with tempfile.TemporaryDirectory() as d:
            for i in range(8):
                with open(os.path.join(d, f"{i}.txt"), "w", encoding="utf-8") as f:
                    f.write("[B-ROLL: a river]\n" + t)
            out = os.path.join(d, "bands.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"_spoken": True}, f)
            with contextlib.redirect_stdout(io.StringIO()):
                aimeter.calibrate(d, out=out)
            with open(out, encoding="utf-8") as f:
                self.assertTrue(json.load(f)["_spoken"])

    def test_spoken_measure_does_not_count_scene_headings(self):
        body = "".join(f"Sentence number {i} is plain speech about rivers and the people near them.\n"
                       for i in range(16))
        text = "## INT. CITY - NIGHT\n" * 6 + body
        old = aimeter.SPOKEN
        try:
            aimeter.SPOKEN = False
            self.assertGreater(aimeter.measure(text)["headings_1k"], 0)
            aimeter.SPOKEN = True
            self.assertEqual(aimeter.measure(text)["headings_1k"], 0)
        finally:
            aimeter.SPOKEN = old

    def test_judge_tokens_skip_stage_directions_in_a_spoken_register(self):
        import evaluate
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("[B-ROLL: tractors]\nNARRATOR: The river runs south.\n")
            old = aimeter.SPOKEN
            try:
                aimeter.SPOKEN = False
                self.assertIn("tractors", evaluate.tokens(p))
                aimeter.SPOKEN = True
                self.assertEqual(evaluate.tokens(p), ["the", "river", "runs", "south"])
            finally:
                aimeter.SPOKEN = old

    def test_recalibration_keeps_register(self):
        t = "".join(f"Sentence number {i} is plain speech about rivers and the people near them.\n"
                    for i in range(15))
        with tempfile.TemporaryDirectory() as d:
            for i in range(8):
                with open(os.path.join(d, f"{i}.txt"), "w", encoding="utf-8") as f:
                    f.write(t)
            out = os.path.join(d, "bands.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"_register": "script"}, f)
            with contextlib.redirect_stdout(io.StringIO()):
                aimeter.calibrate(d, out=out)
            with open(out, encoding="utf-8") as f:
                self.assertEqual(json.load(f)["_register"], "script")


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
