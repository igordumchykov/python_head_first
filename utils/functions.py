def find_vowels(word: str, vowels: str = 'aioeu') -> set:
    """prints intersection"""

    print(type(word))

    if type(word) is str:
        print("It is str")
        vowel_set = set(vowels)
        found = vowel_set.intersection(set(word))
        for ch in found:
            print(ch, end=' ')
    else:
        print("Not str")

    return found


def foo(i: str):
    print(i)


def foo(i: str, j: str = 'abc'):
    print(i + j)
    print("aaa")
