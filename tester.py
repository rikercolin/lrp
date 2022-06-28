import re
import datetime
import pyap
from enum import Enum


class Result_Class(Enum):
    UNCLASSIFIED = 0
    TRUE_POSITIVE = 1
    FALSE_POSITIVE = 2
    FALSE_NEGATIVE = 3


class Answer:
    def __init__(self, doc_id, word, surroundings):
        self.doc_id = doc_id
        self.word = word
        self.surroundings = surroundings

    def __str__(self):
        if True:
            return "{word} - {surroundings}".format(word=self.word, surroundings=self.surroundings)
        return "{word}".format(word=self.word)


class Guess:
    def __init__(self, doc_id, word, surroundings):
        self.doc_id = doc_id
        self.word = word
        self.surroundings = surroundings

    def __str__(self):
        if True:
            return "{word} - {surroundings}".format(word=self.word, surroundings=self.surroundings)
        return "{word}".format(word=self.word)


class Result:
    def __init__(self, doc_id, answer=None, guess=None):
        self.answer = answer
        self.guess = guess
        self.doc_id = doc_id
        self.answered = False
        self.classification = Result_Class.UNCLASSIFIED

    def __str__(self):
        s = 'Classification: {classification}, Doc ID: {doc_id},\n'.format(
            classification=self.classification.name, doc_id=self.doc_id
        )

        if self.classification is Result_Class.UNCLASSIFIED:
            self.classify()

        if self.classification is Result_Class.TRUE_POSITIVE:
            s += "Answer: {answer}, Guess: {guess}\n".format(
                answer=self.answer, guess=self.guess
            )
        elif self.classification is Result_Class.FALSE_POSITIVE:
            s += "Guess: {guess}\n".format(guess=self.guess)

        elif self.classification is Result_Class.FALSE_NEGATIVE:
            s += "Answer: {answer}\n".format(answer=self.answer)

        else:
            s += "Error: Result Unclassified\n"

        return s

    ''' Compare() strictly matches the guess to the answer. Positively returning only if
    they are identical.'''

    def compare(self, guess):
        if not guess.doc_id == self.doc_id:
            self.time_out()
            return False

        if not self.answer == None:
            if normalize_characters(guess.word) == normalize_characters(self.answer.word):
                self.guess = guess
                self.answered = True
                self.classify()
                return True

            else:
                self.classify()
                return False

        else:
            self.classify()
            return False

    ''' Partial_Compare() match looks to see if the guess or the answer are subsets of eachother
    and returns positively if it does.'''

    def partial_compare(self, guess):
        if not guess.doc_id == self.doc_id:
            self.time_out()
            return False

        if not self.answer == None:
            if re.match(guess.word, self.answer.word) or re.match(self.answer.word, guess.word):
                self.guess = guess
                self.answered = True
                self.classify()
                return True
            else:
                self.classify()
                return False

        else:
            self.classify()
            return False

    ''' Classify() attempts to analyise it's internal parameters and decided on
    it's results class, True Positive, False Negative or False Positive.
    '''

    def classify(self):
        if self.answered == True:
            self.classification = Result_Class.TRUE_POSITIVE

        elif (not self.answer == None) and (self.guess == None):
            self.classification = Result_Class.FALSE_NEGATIVE

        elif (self.answer == None) and (not self.guess == None):
            self.classification = Result_Class.FALSE_POSITIVE

        else:
            self.classification = Result_Class.UNCLASSIFIED

    ''' Time_Out() Flags the result when the document id has changed signifying that
    the guesser has moved onto a different document.
    '''

    def time_out(self):
        self.classify()


class Outcome:
    def __init__(self, total_hits, total_possible_hits, true_positives, time_elapsed):
        self.total_hits = total_hits
        self.total_possible_hits = total_possible_hits
        self.true_positives = true_positives
        self.time_elapsed = time_elapsed

        self.false_positives = total_hits - true_positives
        self.false_negatives = total_possible_hits - true_positives

        self.recall = true_positives / total_possible_hits
        self.precision = true_positives / total_hits

        self.f_messure = 2 * \
            ((self.precision * self.recall)/(self.precision + self.recall))

    def __str__(
        self): return ("Total Hits: {total_hits}, Total Possible Hits: {total_possible_hits},\n" +
                       "False Positives: {false_positives}, False Negatives: {false_negatives},\n" +
                       "True Positives: {true_positives}, Time Elapsed: {time_elapsed}\n\n" +
                       "Recall: {recall}, Precision: {precision}, F-Messure: {f_messure}").format(
        total_hits=self.total_hits,
        total_possible_hits=self.total_possible_hits,
        false_positives=self.false_positives,
        false_negatives=self.false_negatives,
        true_positives=self.true_positives,
        time_elapsed=self.time_elapsed,
        recall=self.recall,
        precision=self.precision,
        f_messure=self.f_messure
    )

    def write(self):
        pass


def test(documents):
    print("[Starting Testing]")

    total_hits = 0
    total_possible_hits = 0
    true_positives = 0
    time_elapsed = 0

    results = []

    start_time = datetime.datetime.now()
    for document in documents:
        results.extend(pyap_guesser(document))

    for result in results:
        if result.classification == Result_Class.TRUE_POSITIVE:
            true_positives += 1
            total_possible_hits += 1
            total_hits += 1
        elif result.classification == Result_Class.FALSE_POSITIVE:
            total_hits += 1
        elif result.classification == Result_Class.FALSE_NEGATIVE:
            total_possible_hits += 1
    time_elapsed = 4
    return Outcome(total_hits, total_possible_hits, true_positives, time_elapsed)


def pyap_guesser(document):
    text = document.read()
    results = []

    for answer in document.answers:
        start = answer['location']['start']
        end = answer['location']['end']
        word = text[start: end + 1]
        surroundings = text[start - 10: end + 11]

        a = Answer(document.doc_id, word, surroundings)
        r = Result(a.doc_id, a)
        results.append(r)

    addresses = pyap.parse(text, country='us')

    if not addresses == None:
        for r in addresses:
            g = Guess(document.doc_id, str(r), 'none')
            found = False
            for result in results:
                if result.compare(g):
                    found = True
                    break
            if not found:
                a = Result(g.doc_id, None, g)
                a.classify()
                results.append(a)

        return results

def guesser(document):
    text = document.read()
    results = []

    for answer in document.answers:
        start = answer['location']['start']
        end = answer['location']['end']
        word = text[start: end + 1]
        surroundings = text[start - 10: end + 11]

        a = Answer(document.doc_id, word, surroundings)
        r = Result(a.doc_id, a)
        results.append(r)

    pattern = '((?:(?<=[\s:\(\[\/\-\~c\\u200c])(?<!(\.org\/)|(doi:\s))1?[0-9]\.\d{1,4}\s?(?:\/\s?1?\d\.?\d{0,4})?)|(?:(?<=GPA[\s:])\d))'
    rs = re.finditer(pattern, text, re.IGNORECASE)
    if not rs == None:
        for r in rs:
            g = Guess(document.doc_id, r.group(), text[r.span()[0] - 10:r.span()[1] + 10])
            found = False
            for result in results:
                if result.compare(g):
                    found = True
                    break
            if not found:
                a = Result(g.doc_id, None, g)
                a.classify()
                results.append(a)

        return results

def normalize_characters(word):
    return re.sub(r'[^a-zA-Z0-9]', '', word)
