"""The checks of the video-script register (S1-S7, SE1-SE8): they run only under a band file
with "_register": "script", read only the spoken words, and leave the other registers alone."""
import json, os, re, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EN = os.path.join(HERE, "bands-script.json")
ES = os.path.join(HERE, "bands-script-es.json")
BLOG = os.path.join(HERE, "bands.json")
BLOG_ES = os.path.join(HERE, "bands-es.json")


def states(text, bands):
    with tempfile.TemporaryDirectory() as d:
        tf = os.path.join(d, "t.md")
        with open(tf, "w", encoding="utf-8") as f:
            f.write(text)
        out = subprocess.run([sys.executable, os.path.join(HERE, "audit.py"), "--json", tf],
                             capture_output=True, text=True, encoding="utf-8",
                             env={**os.environ, "QUIRON_BANDS": bands})
        return {i["id"]: i["state"] for i in json.loads(out.stdout)["items"]}


class English(unittest.TestCase):
    CASES = {  # id: (fires, does not fire)
        "S1": ("Imagine a city with no roads. It would be quiet.", "I can't imagine a city with no roads."),
        "S2": ("But here's the twist: it worked. Then there's the cost.", "Here is a list of what we found."),
        "S3": ("Let me know in the comments what you think.", "The comments on the first video were rude."),
        "S4": ("Next time you cross a bridge, look down.", "The next time we met, it was raining."),
        "S5": ("The catch? It costs twice as much.", "What is the catch with this one?"),
        "S6": ("No roads. No cars. Just fields.", "No roads were built. Cars came much later."),
    }

    def test_each_fires_and_stays_quiet(self):
        for cid, (yes, no) in self.CASES.items():
            with self.subTest(cid):
                self.assertEqual(states(yes, EN)[cid], "TELL")
                self.assertEqual(states(no, EN)[cid], "PASS")

    def test_a_mention_of_the_comments_is_not_a_request(self):
        for t in ("Someone in the comments pointed out that I was wrong.",
                  "As many of you said in the comments, the river is old."):
            self.assertEqual(states(t, EN)["S3"], "PASS")

    def test_a_line_break_inside_a_sentence_is_not_a_sentence_start(self):
        self.assertEqual(states("You can't even\nimagine how big it is.", EN)["S1"], "PASS")
        self.assertEqual(states("It was big.\nImagine how big.", EN)["S1"], "TELL")
        self.assertEqual(states("Big rivers.\n\nImagine how big.", EN)["S1"], "TELL")
        self.assertEqual(states("It costs more than\nthe catch? No.", EN)["S5"], "PASS")

    def test_an_inline_production_parenthesis_is_not_read(self):
        self.assertEqual(states("(B-roll: here's the twist) The river is old.", EN)["S2"], "PASS")
        self.assertEqual(states("It fell. [Source: here's why](https://x.org)", EN)["S2"], "PASS")

    def test_stage_directions_are_not_read(self):
        for cid, (yes, _) in self.CASES.items():
            with self.subTest(cid):
                text = f"[B-ROLL: {yes}]\nNARRATOR: The river is old and it is still here."
                self.assertEqual(states(text, EN)[cid], "PASS")

    def test_spoken_after_a_label_is_read(self):
        self.assertEqual(states("NARRATOR: Imagine a city with no roads.", EN)["S1"], "TELL")

    def test_three_together_fail(self):
        two = "Imagine a city with no roads. But here's the twist: it worked."
        self.assertEqual(states(two, EN)["S7"], "PASS")
        self.assertEqual(states(two + " Let me know in the comments.", EN)["S7"], "FAIL")

    def test_checks_that_do_not_separate_are_off(self):
        text = "It was not just a city, but a home. Rather than walk, they ran."
        self.assertNotIn("A1b", states(text, EN))
        self.assertEqual(states(text, BLOG)["A1b"], "TELL")

    def test_one_lexicon_word_is_not_a_tell_here(self):
        text = "We will additionally look at the river and why it is old."
        self.assertEqual(states(text, EN)["B1"], "PASS")
        self.assertEqual(states(text, BLOG)["B1"], "TELL")

    def test_blog_bands_have_no_script_checks(self):
        got = states("Imagine a city with no roads. Let me know in the comments.", BLOG)
        self.assertFalse([c for c in got if c.startswith("S")])


class Spanish(unittest.TestCase):
    CASES = {
        "SE1": ("Quédate hasta el final, porque merece la pena.", "Me quedé hasta el final de la película."),
        "SE2": ("Hoy te cuento por qué el cielo es azul.", "Hoy llueve en toda la ciudad."),
        "SE3": ("Imagina un país sin mar. Así es Bolivia.", "No me lo imagino sin mar."),
        "SE4": ("Y aquí viene lo bueno: funcionó.", "Aquí vive mi tía desde hace años."),
        "SE5": ("Entonces, ¿quién ganó la guerra?", "Entonces se fue de la ciudad."),
        "SE6": ("Cuéntame en los comentarios qué opinas.", "Los comentarios del primer vídeo eran largos."),
        "SE7": ("La próxima vez que mires el cielo, piensa en esto.", "La próxima semana hablaremos del mar."),
    }

    def test_each_fires_and_stays_quiet(self):
        for cid, (yes, no) in self.CASES.items():
            with self.subTest(cid):
                self.assertEqual(states(yes, ES)[cid], "FAIL" if cid == "SE1" else "TELL")
                self.assertEqual(states(no, ES)[cid], "PASS")

    def test_a_mention_of_the_comments_is_not_a_request(self):
        for t in ("Como dijeron en los comentarios, el río es viejo.",
                  "Déjame decirte una cosa sobre los comentarios del otro día."):
            self.assertEqual(states(t, ES)["SE6"], "PASS")
        self.assertEqual(states("Déjame en los comentarios qué opinas.", ES)["SE6"], "TELL")

    def test_staying_with_someone_is_dialogue(self):
        self.assertEqual(states("Quédate conmigo, le dijo ella.", ES)["SE1"], "PASS")

    def test_a_line_break_inside_a_sentence_is_not_a_sentence_start(self):
        self.assertEqual(states("Nadie se\nimagina lo grande que es.", ES)["SE3"], "PASS")
        self.assertEqual(states("Era grande.\nImagina cuánto.", ES)["SE3"], "TELL")

    def test_stage_directions_are_not_read(self):
        for cid, (yes, _) in self.CASES.items():
            with self.subTest(cid):
                text = f"[EN PANTALLA: {yes}]\nNARRADOR: El río es viejo y sigue aquí."
                self.assertEqual(states(text, ES)[cid], "PASS")

    def test_three_together_fail(self):
        two = "Hoy te cuento por qué. Imagina un país sin mar."
        self.assertEqual(states(two, ES)["SE8"], "PASS")
        self.assertEqual(states(two + " Cuéntame en los comentarios qué opinas.", ES)["SE8"], "FAIL")

    def test_fragment_rows_are_off_here_only(self):
        text = "Un país. Sin mar. Sin playa. Sin puerto. Así es Bolivia, y así lo cuenta su historia."
        self.assertNotIn("A2b", states(text, ES))
        self.assertIn("A2b", states(text, BLOG_ES))

    def test_spanish_blog_bands_have_no_script_checks(self):
        got = states("Hoy te cuento por qué. Quédate hasta el final.", BLOG_ES)
        self.assertFalse([c for c in got if c.startswith("SE")])


class JudgePrompt(unittest.TestCase):
    """Only "es" or a name ending in "-es" gets the Spanish narration prompt."""

    def test_prompt_choice(self):
        sys.path.insert(0, os.path.join(HERE, "..", "eval", "e2e"))
        import harness
        for name in ("es", "scr-es", "scr2-es"):
            self.assertIs(harness.script_prompt(name), harness.JPROMPT_SCR_ES)
        for name in ("1", "yes", "scr", "scr2", "scr-titles", "scripts"):
            self.assertIs(harness.script_prompt(name), harness.JPROMPT_SCR)


class ScriptSets(unittest.TestCase):
    """The e2e script sets: the rewriter's prompt carries the title, in the set's language,
    and the sets of the other registers keep the prompts they had."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(HERE, "..", "eval", "e2e"))
        import harness
        cls.h = harness
        cls.sets = harness.sets()

    def test_sets_have_twenty_scripts_spread_over_models(self):
        for name, per in (("scr", 5), ("scr2", 4), ("scr-es", 5), ("scr2-es", 4)):
            rows = self.sets[name]
            self.assertEqual(len(rows), 20, name)
            models = {}
            for r in rows:
                self.assertEqual(r[2], "-")
                models[os.path.basename(os.path.dirname(r[1]))] = models.get(os.path.basename(os.path.dirname(r[1])), 0) + 1
            self.assertEqual(set(models.values()), {per}, name)
        self.assertTrue(all("/train-" in r[1].replace(os.sep, "/") for r in self.sets["scr"]))
        self.assertTrue(all("/test-" in r[1].replace(os.sep, "/") for r in self.sets["scr2"]))

    def test_script_prompt_has_the_title_in_the_set_language(self):
        en, es = self.sets["scr"][0], self.sets["scr-es"][0]
        self.assertEqual(self.h.rewrite_prompt(en[0], "-"), self.h.PROMPT_SCR % en[3])
        self.assertIn(f'titled "{en[3]}"', self.h.rewrite_prompt(en[0], "-"))
        self.assertEqual(self.h.rewrite_prompt(es[0], "-"), self.h.PROMPT_SCR_ES % es[3])
        self.assertIn("Conserva las acotaciones", self.h.rewrite_prompt(es[0], "-"))
        for r in self.sets["scrh"]:
            self.assertEqual(self.h.rewrite_prompt(r[0], "-"), self.h.PROMPT_SCR % r[3])
        for r in self.sets["scrh-es"]:
            self.assertEqual(self.h.rewrite_prompt(r[0], "-"), self.h.PROMPT_SCR_ES % r[3])

    def test_other_sets_keep_their_prompts(self):
        h = self.h
        self.assertEqual(h.rewrite_prompt(self.sets["dev"][0][0], self.sets["dev"][0][2]), h.PROMPT)
        self.assertEqual(h.rewrite_prompt(self.sets["devnn"][0][0], "-"), h.PROMPT_NONOTES)
        self.assertEqual(h.rewrite_prompt(self.sets["es"][0][0], self.sets["es"][0][2]), h.PROMPT_ES)
        fic = self.sets["fic"][0]
        self.assertEqual(h.rewrite_prompt(fic[0], "-"), h.PROMPT_FIC % fic[3])
        self.assertEqual(h.rewrite_prompt(self.sets["hum"][0][0], "-"), h.PROMPT_NONOTES)
        script_names = {r[0] for s, rows in self.sets.items() if s.startswith("scr") for r in rows}
        other = {r[0] for s, rows in self.sets.items() if not s.startswith("scr") for r in rows}
        self.assertFalse(script_names & other)

    def test_full_narration_keeps_the_paragraph_after_stacked_directions(self):
        text = ("Every town on the river has a story about the water.\n\n---\n\n**[SECTION 1 - 0:45]**\n\n"
                "*(Wide shot of a river.)*\n\nThe river floods every spring and the town knows it.\n\n"
                "Nobody moved, and the levee went up in 1927.\n")
        old = os.environ.pop("QUIRON_FULL_NARRATION", None)
        try:
            os.environ["QUIRON_FULL_NARRATION"] = "1"
            full = self.h.narration(text)
            del os.environ["QUIRON_FULL_NARRATION"]
            default = self.h.narration(text)
        finally:
            if old is not None:
                os.environ["QUIRON_FULL_NARRATION"] = old
        self.assertIn("The river floods", full)
        self.assertIn("levee went up", full)
        self.assertNotIn("SECTION", full)
        self.assertNotIn("The river floods", default)  # the gap the flag works around

    def test_judge_prompt_follows_the_set_name(self):
        self.assertIs(self.h.script_prompt("scrh"), self.h.JPROMPT_SCR)
        self.assertIs(self.h.script_prompt("scrh-es"), self.h.JPROMPT_SCR_ES)

    def snap_from(self, files):
        d = tempfile.mkdtemp()
        for rel, text in files.items():
            os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
            with open(os.path.join(d, rel), "w", encoding="utf-8") as out:
                out.write(text)
        return d

    def check_stripped(self, dst):
        self.assertFalse(os.path.exists(os.path.join(dst, "references", "script.md")))
        skill = open(os.path.join(dst, "SKILL.md"), encoding="utf-8").read()
        self.assertNotIn("script.md", skill)
        self.assertIn("bands-script.json", skill)
        self.assertIn("_new = []", open(os.path.join(dst, "scripts", "audit.py"), encoding="utf-8").read())

    def test_bands_snapshot_of_the_tested_rules(self):
        """At 37a1cff, where the rules were tested, the snapshot drops them and the checks."""
        repo = os.path.abspath(os.path.join(HERE, ".."))
        files = {}
        for rel in ("SKILL.md", "references/script.md", "scripts/audit.py"):
            r = subprocess.run(["git", "show", f"37a1cff:{rel}"], cwd=repo, capture_output=True,
                               text=True, encoding="utf-8")
            if r.returncode:
                self.skipTest("commit 37a1cff is not in this clone")
            files[rel] = r.stdout
        dst = self.snap_from(files)
        self.h.strip_script_rules(dst)
        self.check_stripped(dst)

    def test_bands_snapshot_of_this_tree(self):
        """With no references/script.md, only the script checks go."""
        repo = os.path.abspath(os.path.join(HERE, ".."))
        files = {rel: open(os.path.join(repo, rel), encoding="utf-8").read()
                 for rel in ("SKILL.md", "scripts/audit.py")}
        dst = self.snap_from(files)
        self.h.strip_script_rules(dst)
        self.check_stripped(dst)


class LanguageWarning(unittest.TestCase):
    """A script band file names the other language's script band file, not the blog one."""
    ES_TEXT = "El cielo es azul porque la luz del sol que llega a la tierra se dispersa en el aire de la mañana."
    EN_TEXT = "The sky is blue because the light of the sun is scattered in the air and it is still there."

    def suggested(self, text, bands):
        """the band file the WARNING tells the user to set"""
        code = "import sys, aimeter; print(aimeter.lang_warning(sys.stdin.read()))"
        out = subprocess.run([sys.executable, "-c", code], input=text, capture_output=True, text=True,
                             encoding="utf-8", cwd=HERE, env={**os.environ, "QUIRON_BANDS": bands}).stdout
        m = re.search(r"QUIRON_BANDS=(\S+) and run again", out)
        return os.path.basename(m.group(1)) if m else None

    def test_script_bands_name_script_bands(self):
        self.assertEqual(self.suggested(self.ES_TEXT, EN), "bands-script-es.json")
        self.assertEqual(self.suggested(self.EN_TEXT, ES), "bands-script.json")

    def test_blog_bands_still_name_blog_bands(self):
        self.assertEqual(self.suggested(self.ES_TEXT, BLOG), "bands-es.json")
        self.assertEqual(self.suggested(self.EN_TEXT, BLOG_ES), "bands.json")

if __name__ == "__main__":
    unittest.main()
