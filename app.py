"""IShowSpeed - Automata-Based Time Complexity Simulator (Flask backend).

Three formal models are always run on the same input and every elementary
move is counted as one step:

  DFA - substring-match automaton for the user's pattern. One transition per
        input symbol, so steps grow as O(n).
  PDA - nondeterministic palindrome recogniser. Its "guess the midpoint"
        choice is simulated deterministically by exploring every branch
        (push the first half, pop-and-compare the rest). O(n^2).
  TM  - single-tape palindrome decider. For every candidate centre it
        zig-zags across the tape marking symbol pairs, and every head move
        costs one step. No early exit, so it is O(n^3).
"""
from flask import Flask, jsonify, request, send_file
import os

app = Flask(__name__)
MAX_LEN = 100
HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- DFA
def build_dfa(pattern, alphabet):
    """Substring-match DFA (KMP automaton). State = chars of pattern matched."""
    m = len(pattern)
    delta = [dict() for _ in range(m + 1)]
    for state in range(m + 1):
        for ch in alphabet:
            if state == m:
                delta[state][ch] = m            # accepting, absorbing
                continue
            k = state
            while True:
                if k < m and pattern[k] == ch:
                    delta[state][ch] = k + 1
                    break
                if k == 0:
                    delta[state][ch] = 0
                    break
                # fall back: longest border of pattern[:k]
                k = _border(pattern, k)
    return delta


def _border(p, k):
    for b in range(k - 1, 0, -1):
        if p[:b] == p[k - b:k]:
            return b
    return 0


def run_dfa(s, pattern):
    steps = 0
    if pattern:
        delta = build_dfa(pattern, set(s) | set(pattern))
        state, accept = 0, len(pattern)
        for ch in s:
            state = delta[state][ch]
            steps += 1                           # one transition per symbol
        return state == accept, steps
    # no pattern given: parity DFA (accepts even-length strings)
    state = 0
    for _ in s:
        state ^= 1
        steps += 1
    return state == 0, steps


# ---------------------------------------------------------------- PDA
def run_pda(s):
    """Palindrome PDA; the nondeterministic midpoint guess is simulated by
    exploring every branch (even-length and odd-length centres)."""
    n, steps, accepted = len(s), 0, False
    for k in range(n + 1):
        for skip in (0, 1):                      # 1 = consume a middle symbol
            if k + skip > n:
                continue
            stack = []
            for i in range(k):                   # phase 1: push first half
                stack.append(s[i])
                steps += 1
            steps += 1                           # epsilon move: guess centre
            pos, ok = k + skip, True
            if skip:
                steps += 1                       # read middle symbol
            while pos < n:                       # phase 2: pop and compare
                steps += 1
                if not stack or stack.pop() != s[pos]:
                    ok = False
                    break
                pos += 1
            if ok and not stack and pos == n:
                accepted = True
    return accepted, steps


# ------------------------------------------------------------ Turing machine
def run_tm(s):
    """Single-tape TM palindrome decider counting head moves + writes."""
    n = len(s)
    if n == 0:
        return True, 1
    tape = list(s)
    head, steps, accepted = 0, 0, False
    for centre in range(2 * n - 1):              # every even/odd centre
        steps += 1                               # enter state for this centre
        if centre % 2 == 0:                      # odd palindrome, centre char
            left = right = centre // 2
            left -= 1
            right += 1
        else:                                    # even palindrome
            left, right = centre // 2, centre // 2 + 1
        match = True
        # The machine must verify the WHOLE string is a palindrome around the
        # centre, so the only centre that can accept is the middle one; all
        # others still run to completion (no early exit).
        while left >= 0 or right < n:
            l_cell = max(left, 0)
            r_cell = min(right, n - 1)
            steps += abs(head - l_cell); head = l_cell     # travel to left
            steps += 1                                      # read/mark
            steps += abs(head - r_cell); head = r_cell     # travel to right
            steps += 1                                      # compare/mark
            if left < 0 or right >= n or tape[l_cell] != tape[r_cell]:
                match = False
            left -= 1
            right += 1
        steps += head; head = 0                             # rewind
        if match and (left < 0 and right >= n):
            accepted = True
    return accepted, steps


# ---------------------------------------------------------------- API
@app.route("/")
def index():
    return send_file(os.path.join(HERE, "templates", "index.html"))


@app.route("/api/run", methods=["POST"])
def api_run():
    """One input box: the string's length n is fed to all three engines.
    Each engine runs on a worst-case input of that length (every symbol the
    same, so nothing exits early), which makes step counts depend on n only."""
    data = request.get_json(silent=True) or {}
    s = str(data.get("string", ""))[:MAX_LEN]
    n = len(s)
    if n == 0:
        return jsonify(error="Enter a string to run the race."), 400

    lengths, dfa, pda, tm = [], [], [], []
    for k in range(1, n + 1):
        w = "a" * k
        lengths.append(k)
        dfa.append(run_dfa(w, "")[1])
        pda.append(run_pda(w)[1])
        tm.append(run_tm(w)[1])

    return jsonify(
        n=n,
        lengths=lengths,
        series={"DFA": dfa, "PDA": pda, "TM": tm},
        final={"DFA": {"steps": dfa[-1]}, "PDA": {"steps": pda[-1]}, "TM": {"steps": tm[-1]}},
        task={"DFA": "scans every symbol", "PDA": "tries every midpoint",
              "TM": "checks every centre"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
