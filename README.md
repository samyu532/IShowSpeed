# IShowSpeed


**Automata-Based Time Complexity Simulator**

IShowSpeed is a small web app that races three formal-language models against each other. You type a string, click **Run Analysis**, and the page plots how many steps each machine needs as the input grows. A Python backend does the counting, and the charts update on the same screen with no page reload.

| Machine | Growth | What it does |
|---|---|---|
| DFA | O(n) | Reads one symbol per move |
| PDA | O(n²) | Pushes a half of the input, pops to compare, and tries every midpoint |
| Turing Machine | O(n³) | Zig-zags across a single tape and checks every centre |

## Features

- One input box. The string's length is shown live as you type.
- All three machines always run, whatever the input.
- A large "Race Track" line chart of steps against input length, with a Linear / Log switch.
- One card per machine, each with its own chart. The measured steps are plotted against O(n), O(n²) and O(n³) reference curves, and the fitted growth exponent is shown.
- A table with the exact step count for each machine at five input lengths, and a marker on the fastest machine.
- No reloads. The page calls the Python backend with `fetch` and redraws the charts.

## Project structure

```
IShowSpeed/
├── app.py                 # Flask backend: DFA, PDA and Turing Machine step counters + API
├── requirements.txt
├── README.md
└── templates/
    └── index.html         # The whole front end (HTML, CSS, JS)
```

## Getting started

Requires Python 3.9 or newer.

```bash
git clone <https://github.com/samyu532/IShowSpeed.git>
cd IShowSpeed
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

The page loads the Onest font from Google Fonts and Chart.js from cdnjs, so you need an internet connection to see it as designed.

## How it works

1. You type any string into the single input box (up to 100 characters).
2. The page reads the length `n` of the string.
3. It sends the string to the backend with `POST /api/run`.
4. The backend runs all three machines at every length from 1 to `n`. Each run counts elementary moves as steps.
5. The page redraws the large chart, the three model charts and the table from the response.

### Step counting

Each machine runs on a worst-case input of the given length (every symbol the same), so nothing exits early. This means the step counts depend only on the length, and any two strings of the same length give the same graph.

- **DFA:** one step per input symbol.
- **PDA:** the nondeterministic midpoint guess is simulated by exploring every branch. Each branch counts its pushes, the guess move, an optional middle-symbol read, and the pop-and-compare moves.
- **Turing Machine:** every head move counts as a step. For each of the 2n-1 centres, the head zig-zags between symbol pairs, then rewinds. Each pair costs the travel distance plus two read/write steps.

Example for a string of length 19:

| Machine | Steps |
|---|---|
| DFA | 19 |
| PDA | 609 |
| Turing Machine | 12,391 |

## API

### `POST /api/run`

Request body:

```json
{ "string": "racecarlevelracecar" }
```

Response (shortened):

```json
{
  "n": 19,
  "lengths": [1, 2, 3, "..."],
  "series": { "DFA": [1, 2, 3, "..."], "PDA": ["..."], "TM": ["..."] },
  "final": { "DFA": { "steps": 19 }, "PDA": { "steps": 609 }, "TM": { "steps": 12391 } },
  "task": { "DFA": "scans every symbol", "PDA": "tries every midpoint", "TM": "checks every centre" }
}
```

An empty string returns HTTP 400 with an `error` message.

## Design

- **Palette:** `#000040` and `#E8E8B7`, plus lighter and darker mixes of those two.
- **Font:** Onest, used across the whole page.
- **Charts:** Chart.js 4.4.1. In log view the y-axis shows one tick per power of ten.

## Limitations

- Because every machine runs on a worst-case input, the content of the string does not change the results. Only its length does.
- Input is capped at 100 characters. The Turing Machine's O(n³) cost grows quickly beyond that.
- The three machines do not solve the same problem. A finite automaton cannot recognise palindromes, so each machine is given the kind of work it handles naturally, and the comparison is about how step counts grow with length.

## Tech stack

Python, Flask, vanilla JavaScript, Chart.js.
=======
Automata-based time complexity simulator: race a DFA, PDA and Turing Machine and watch their step counts grow on live charts.
>>>>>>> 5d2200873fa8adcbd4b82823366bbce0a8bdbef8
