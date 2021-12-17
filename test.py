import timeit
import random
import itertools
import numpy as np

characters = "abcdefghijklmnopqrstuvwxyz" + " "

database = {
    "khanh": "this is my real password"
}


def check_password(user: str, pred: str) -> bool:
    actual = database.get(user, None)
    if actual is None:
        return False
    if len(pred) != len(actual):
        return False
    for i in range(len(pred)):
        if pred[i] != actual[i]:
            return False
    return True


def random_str(n: int) -> str:
    return "".join(random.choice(characters) for i in range(n))


def crack_length(user: str, max_length: int = 32, verbose: bool = False) -> int:
    trials = 1000
    times = np.empty(max_length)
    for i in range(max_length):
        i_time = timeit.repeat(
            stmt="check_password(user, x)",
            setup=f"user={user!r};x=random_str({i!r})",
            globals=globals(),
            number=trials,
            repeat=100,
        )
        times[i] = min(i_time)
    if verbose:
        most_likely_n = np.argsort(times)[::-1][:5]
        print(most_likely_n, times[most_likely_n] / times[most_likely_n[0]])

    most_likely = int(np.argmax(times))
    return most_likely


def crack_password(user: str, length: int, verbose: bool = False):
    guess = random_str(length)
    counter = itertools.count()
    trials = 1000
    while True:
        i = next(counter) % length
        for c in characters:
            alt = guess[:i] + c + guess[i + 1:]

            alt_time = timeit.repeat(
                stmt="check_password(user, x)",
                setup=f"user={user!r};x={alt!r}",
                globals=globals(),
                number=trials,
            )
            guess_time = timeit.repeat(
                stmt="check_password(user, x)",
                setup=f"user={user!r};x={guess!r}",
                globals=globals(),
                number=trials,
            )
            if check_password(user, alt):
                if verbose:
                    print(alt)
                return alt

            if min(alt_time) > min(guess_time):
                guess = alt
                if verbose:
                    print(guess)


if __name__ == "__main__":
    length = crack_length("khanh", verbose=True)
    guess = crack_password("khanh", length, verbose=True)
