# -*- coding: utf-8 -*-
from integration import BaseMongoTest
from tavi import fields
from tavi.documents import Document


class Phrase(Document):
    text = fields.StringField("text")


class PhraseBookUnicodePersistTest(BaseMongoTest):
    """Tests for unicode supports. Phrases taken from
    http://www.cl.cam.ac.uk/~mgk25/ucs/examples/quickbrown.txt

    """

    def assertPhrasePersisted(self, text):
        pb = Phrase()
        pb.text = text

        if not pb.save():
            raise AssertionError("Unable to save phrase")

        phrases = list(self.db.phrases.find())

        if not 1 == len(phrases):
            raise AssertionError("More than one phrase was persisted (%s)")

        if unicode(text, "utf-8") != phrases[0]["text"]:
            raise AssertionError("Persisted string is not unicode")

    def test_danish(self):
        self.assertPhrasePersisted(
            "Quizdeltagerne spiste jordbær med fløde, mens cirkusklovnen "
            "Wolther spillede på xylofon."
        )

    def test_german(self):
        self.assertPhrasePersisted("Heizölrückstoßabdämpfung")

    def test_greek(self):
        self.assertPhrasePersisted(
            "Γαζέες καὶ μυρτιὲς δὲν θὰ βρῶ πιὰ στὸ χρυσαφὶ ξέφωτο"
        )

    def test_spanish(self):
        self.assertPhrasePersisted(
            "El pingüino Wenceslao hizo kilómetros bajo exhaustiva lluvia y "
            "frío, añoraba a su querido cachorro."
        )

    def test_french(self):
        self.assertPhrasePersisted(
            "Le cœur déçu mais l'âme plutôt naïve, Louÿs rêva de crapaüter "
            "en canoë au delà des îles, près du mälström où brûlent les novæ."
        )

    def test_hungarian(self):
        self.assertPhrasePersisted("Árvíztűrő tükörfúrógép")

    def test_japanese(self):
        self.assertPhrasePersisted(
            "いろはにほへとちりぬるを"
            "わかよたれそつねならむ"
            "うゐのおくやまけふこえて"
            "あさきゆめみしゑひもせす"
        )

    def test_polish(self):
        self.assertPhrasePersisted("Pchnąć w tę łódź jeża lub ośm skrzyń fig")

    def test_russian(self):
        self.assertPhrasePersisted(
            "Съешь же ещё этих мягких французских булок да выпей чаю"
        )
