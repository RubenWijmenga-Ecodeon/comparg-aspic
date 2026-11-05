# comparg-aspic

A fork of [PyArg](https://github.com/DaphneOdekerken/PyArg) (by Daphne Odekerken, AnneMarie Borg and Matti Berthold) for modelling ASPIC+ argumentation theories on your own machine and looking at the resulting argument graph. It is a working offline replacement for the [TOAST](http://toast.arg-tech.org) web tool, which is regularly unreachable.

Everything runs locally: you type the axioms, premises, rules and preferences into a web page served from your own computer, and PyArg builds the arguments, draws the defeat graph and computes extensions under grounded, preferred, stable and other semantics.

## What this fork changes

On the ASPIC+ visualisation page (`Visualise > ASPIC+`):

- **Rule names as node labels.** A node shows the rules an argument applies (bottom-up) and its conclusion, for example `r23, r24, r25: allowAI`, instead of the full nested argument. Premise-only arguments keep the premise as label; strict rules show as `s0`, `s1`, ... because PyArg numbers them.
- **The graph fits the canvas.** After every change the graph is laid out once, frozen and zoomed to fit, so no node falls outside the canvas.
- **Compact layout.** Nodes are narrow boxes with wrapping labels and are packed closer together, so large theories stay readable when zoomed out.
- **Readable evaluation results.** The Evaluation panel numbers each extension and lists its conclusions; clicking one colours its arguments without re-laying out the graph. Results follow edits to the theory, the default semantics is grounded, and at most 100 extension buttons are shown.

In the Python library (`py_arg.algorithms.semantics`):

- **Extensions that finish.** Upstream PyArg computes complete, preferred, stable, semi-stable, ideal, eager and admissible extensions by trying every labelling, which does not finish for a theory of about 30 arguments (and on a server shows up as "server doesn't respond"). This fork prunes that search, and derives stable and semi-stable extensions from the preferred and complete ones and ideal and eager extensions from their intersections. For a 31-argument theory every semantics now takes milliseconds, except admissible: that theory has over 1.6 million admissible sets, which still takes about 40 seconds to list.

The rest of PyArg (the other pages, the documentation) is unchanged. General PyArg documentation: https://daphneodekerken.github.io/PyArg/.

## Requirements

- **Python 3.11.** Not newer: `requirements.txt` pins `pandas~=1.5.3`, which has no builds for Python 3.12 or later. If you have [uv](https://docs.astral.sh/uv/), it can fetch Python 3.11 for you (see below).
- git.

## Installation

```bash
git clone https://github.com/RubenWijmenga-Ecodeon/comparg-aspic.git
cd comparg-aspic
```

Create a Python 3.11 virtual environment and install the dependencies, with either plain Python:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt "numpy<2" "dash<3"
```

or uv:

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt "numpy<2" "dash<3"
```

On Windows, use `.venv\Scripts\python` instead of `.venv/bin/python`.

The two extra pins matter, because `requirements.txt` leaves both packages unpinned:

- `"numpy<2"`: with NumPy 2 the pinned pandas 1.5.3 crashes on import with `numpy.dtype size changed`.
- `"dash<3"`: the pinned dash-bootstrap-components 1.4.2 is built for Dash 2. Under Dash 3 or 4 the panels on the page lose their titles and the Evaluation and Explanation panels never show results.

## Running

macOS / Linux, with gunicorn (installed by `requirements.txt`):

```bash
.venv/bin/gunicorn --pythonpath src --bind 127.0.0.1:8000 wsgi:app
```

Then open http://127.0.0.1:8000/22-visualise-aspic.

Any platform, including Windows (gunicorn does not run on Windows), with Flask's built-in server:

```bash
# macOS / Linux
PYTHONPATH=src FLASK_APP=wsgi:app .venv/bin/python -m flask run --port 8000
```

```bat
:: Windows (cmd)
set PYTHONPATH=src
set FLASK_APP=wsgi:app
.venv\Scripts\python -m flask run --port 8000
```

Then open http://127.0.0.1:8000/22-visualise-aspic. Keep the `--port`: Flask's default port 5000 is taken by AirPlay Receiver on macOS.

Stop the server with Ctrl+C. The server does not pick up code changes by itself; restart it after editing files.

Use the commands above rather than the repository's `Procfile` (which points at an `app:server` attribute that does not exist) or `Dockerfile` (which serves uWSGI's own protocol, not plain HTTP).

## Using the ASPIC+ page

Open the **ASPIC+ Argumentation Theory** panel on the left and fill in the boxes. The graph on the right updates as you type.

| Box | One per line | Example |
|---|---|---|
| Axioms (cannot be attacked) | literal | `bird` |
| Ordinary premises (can be undermined) | literal | `-q` |
| Ordinary premise preferences | `a < b` or `b > a` | `p < -q` |
| Strict rules | `antecedents -> consequent` | `p, q -> r` |
| Defeasible rules | `name: antecedents => consequent` | `d1: p => q` |
| Defeasible rule preferences | `name < name` | `d1 < d2` |

Under the boxes, choose the **ordering** (democratic or elitist, last link or weakest link). Then open the **Evaluation** panel to pick a semantics (grounded, preferred, stable, ...) and a strategy (credulous, sceptical, ...) and to list the extensions, and the **Explanation** panel for explanations of why a conclusion is or is not accepted. Clicking an extension colours its arguments in the graph.

### Syntax rules that are easy to get wrong

- **`-` is (strong) negation; `~` is negation as failure.** `-p` contradicts `p` symmetrically. `~p` means "p is not derivable" and is only a contrary of `p`, so an argument for `p` attacks `~p` but not the other way round.
- **Antecedents are separated by commas.**
- **Every defeasible rule needs a unique name** before the colon.
- **Undercutters:** a rule name is also a literal, so an argument concluding `-d1` undercuts every argument that uses rule `d1`.
- **No rules without antecedents.** For a rule that should always apply, add an axiom `true` and write `d7: true => -d4`.
- **No variables.** Literals are plain names; `useAI(X)` style predicates are not supported, so model a single individual.
- **No blank lines** in the rule boxes; a blank line is read as a rule without a name and makes the theory invalid.
- **Nothing is saved.** Reloading the page clears every box, so keep your theory in a text file and paste it in.

### Example

| Box | Content |
|---|---|
| Ordinary premises | `bird`<br>`penguin` |
| Defeasible rules | `d1: bird => flies`<br>`d2: penguin => -flies`<br>`d3: penguin => -d1` |

`d1` and `d2` rebut each other, and `d3` undercuts `d1` ("penguins are an exception to birds flying"). Under grounded semantics, `-flies` is justified and the argument for `flies` is overruled.

### Stored theories (shortlinks)

`/22-visualise-aspic/stored/<id>` opens the ASPIC+ page with a stored theory already filled in. Theories are JSON files `stored_theories/<id>.json` at the repository root; the id may only contain letters, digits, `-` and `_`. Every key is optional:

```json
{
  "axioms": "true",
  "ordinary_premises": "bird\npenguin",
  "ordinary_premise_preferences": "",
  "strict_rules": "",
  "defeasible_rules": "d1: bird => flies\nd2: penguin => -flies\nd3: penguin => -d1",
  "defeasible_rule_preferences": "",
  "ordering_choice": "democratic",
  "ordering_link": "last_link"
}
```

`stored_theories/` is in `.gitignore`, so stored models are not pushed to a public repository; copy the files to the server yourself. A file is read on every page load, so adding or editing one needs no restart.

### Translating a TOAST model

| TOAST | Here |
|---|---|
| `[r1] p(X), q(X) => r(X);` | `r1: p, q => r` |
| `~p` (negation) | `-p` |
| `True => ~[r4];` | axiom `true`, and `r7: true => -r4` |
| premise `p;` | a line `p` under ordinary premises (or axioms, if it should not be attackable) |
| two rules with the same name | give each a unique name |

## Keeping up with upstream PyArg

```bash
git remote add upstream https://github.com/DaphneOdekerken/PyArg.git   # once
git fetch upstream
git merge upstream/main
```

## Credits and licence

PyArg is written by Daphne Odekerken, AnneMarie Borg and Matti Berthold and released under the MIT licence; see [LICENSE](LICENSE). The changes in this fork are released under the same licence.
