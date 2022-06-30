import re

def is_substring(s1, s2):
    M = len(s1)
    N = len(s2)

    # A loop to slide pat[] one by one
    for i in range(N - M + 1):

        # For current index i,
        # check for pattern match
        for j in range(M):
            if (s2[i + j] != s1[j]):
                break

        if j + 1 == M:
            return True

    return False


def normalize_characters(word):
    return re.sub(r'[^a-zA-Z0-9]', '', word)


def file_formating(line):
    return re.sub(r'\r*[\n\r]', ' ', line)