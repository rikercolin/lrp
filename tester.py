import re
import datetime
import pyap
import time
import util
from enum import Enum

debug = False


class Result_Class(Enum):
    UNCLASSIFIED = 0
    TRUE_POSITIVE = 1
    FALSE_POSITIVE = 2
    FALSE_NEGATIVE = 3


class Answer:
    def __init__(self, doc_id, word, surroundings, cordinates):
        self.doc_id = doc_id
        self.word = word
        self.surroundings = surroundings
        self.start_cordinate = cordinates[0]
        self.end_cordinate = cordinates[1]

    def __str__(self):
        if debug:
            return "{word} - {surroundings} | {start}-{end}".format(
                word=self.word,
                surroundings=util.file_formating(self.surroundings), start=self.start_cordinate, end=self.end_cordinate)
        return "{word}".format(word=self.word)


class Guess:
    def __init__(self, doc_id, word, surroundings, cordinates):
        self.doc_id = doc_id
        self.word = word
        self.surroundings = surroundings
        self.start_cordinate = cordinates[0]
        self.end_cordinate = cordinates[1]

    def __str__(self):
        if debug:
            return "{word} - {surroundings} | {start}-{end}".format(
                word=self.word,
                surroundings=util.file_formating(self.surroundings), start=self.start_cordinate, end=self.end_cordinate)
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
            if util.normalize_characters(guess.word) == util.normalize_characters(self.answer.word):
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

        if not isinstance(self.answer, type(None)):
            if util.is_substring(util.normalize_characters(self.answer.word), util.normalize_characters(guess.word)) | util.is_substring(util.normalize_characters(guess.word), util.normalize_characters(self.answer.word)):
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

    ''' Cordinate_Compare() takes the regex match cordinates and the answer
    cordinates and compares to see if they have a union of the two intervals.
    '''

    def cordinate_compare(self, guess):
        if isinstance(self.answer, type(None)):
            self.classify()
            return False

        if not guess.doc_id == self.doc_id:
            self.time_out()
            return False

        a_start = self.answer.start_cordinate
        a_end = self.answer.end_cordinate
        g_start = guess.start_cordinate
        g_end = guess.end_cordinate

        # Answer contains guess cordinates
        if a_start <= g_start and a_end >= g_end:
            self.guess = guess
            self.answered = True
            self.classify()
            return True

        # Guess contains Answer cordinates
        elif g_start <= a_start and g_end >= a_end:
            self.guess = guess
            self.answered = True
            self.classify()
            return True

        else:
            self.classify()
            return False

    ''' Classify() attemts to analyise it's internal parameters and decided on
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


def test(documents, tebug):
    print("[Starting Testing]")
    debug = tebug

    total_hits = 0
    total_possible_hits = 0
    true_positives = 0

    results = []

    start_time = time.perf_counter()
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

    if debug:
        with open('results.txt', 'w', encoding='utf-8') as f:
            for result in results:
                t = ''
                if result.classification == Result_Class.TRUE_POSITIVE:
                    t = '{}, {} : {}\n'.format(result.classification.name, util.file_formating(
                        str(result.answer)), util.file_formating(str(result.guess)))
                    pass
                if result.classification == Result_Class.FALSE_POSITIVE:
                    t = '{}, {}\n'.format(
                        result.classification.name, util.file_formating(str(result.guess)))
                    pass
                elif result.classification == Result_Class.FALSE_NEGATIVE:
                    t = '{}, {}\n'.format(
                        result.classification.name, util.file_formating(str(result.answer)))
                    pass
                if t == '':
                    continue
                f.write(t)
            f.close()

    return Outcome(total_hits, total_possible_hits, true_positives, time.perf_counter() - start_time)


def pyap_guesser(document):
    text = document.read()
    results = []

    for answer in document.answers:
        start = answer['location']['start']
        end = answer['location']['end']
        word = text[start: end + 1]
        surroundings = text[start - 10: end + 11]

        a = Answer(document.doc_id, word, surroundings, (start, end))
        r = Result(a.doc_id, a)
        results.append(r)

    addresses = pyap.parse(text, country='us')

    if not addresses == None:
        for re_guess in addresses:
            guess = Guess(document.doc_id, str(re_guess), 'none', (re_guess.as_dict()[
                          'match_start'], re_guess.as_dict()['match_end']))
            found = False
            for result in results:
                if result.answered == True:
                    continue
                if result.cordinate_compare(guess):
                    found = True
                    break

            if not found:
                for result in results:
                    if result.answered == True:
                        continue
                    if result.compare(guess):
                        found = True
                        break

            if not found:
                for result in results:
                    if result.answered == True:
                        continue
                    if result.partial_compare(guess):
                        found = True
                        break

            if not found:
                result = Result(guess.doc_id, None, guess)
                result .classify()
                results.append(result)
        return results


def regex_guesser(document):
    text = document.read()
    results = []

    for answer in document.answers:
        start = answer['location']['start']
        end = answer['location']['end']
        word = text[start: end + 1]
        surroundings = text[start - 10: end + 11]

        a = Answer(document.doc_id, word, surroundings, (start, end))
        r = Result(a.doc_id, a)
        results.append(r)

    pattern = ''
    rs = re.finditer(pattern, text, re.IGNORECASE)
    if not rs == None:
        for r in rs:
            g = Guess(document.doc_id, r.group(),
                      text[r.span()[0] - 10:r.span()[1] + 10], r.span())
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
