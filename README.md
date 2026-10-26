# XXE add-on for the GiellaLT dictionaries

An add-on for [XMLmind XML Editor](https://www.xmlmind.com/xmleditor/) (XXE)
for editing the dictionaries in `giellalt/dict-sme` and `giellalt/dict-sma`
(more dicts can be added later):
a style sheet with buttons, a Dictionary menu with keyboard shortcuts,
links between entries, and batches with PDFs for proofreading.

One add-on serves all the dictionaries. XXE picks the configuration of a
file by its root element: `<r id="dict-sme">` gets
`dicts/dict-sme/dict-sme.xxe`.

## Contents

```
core/        shared by all the dictionaries
  dict.incl          commands, templates, the Dictionary menu
  dict-batches.incl  batches: added to the menu by dictionaries that use them
  common.incl        save options, running the scripts, PDF of a batch
  dict.css           the style sheet of the dictionary files
  dict-batches.css   the batch line of each entry
  common.css         colours and buttons, shared with batches.css
  batches.xxe/.css   batches.xml of any dictionary
dicts/       a folder for each dictionary, dict-xxx/ with
  dict-xxx.toml      what differs: pos and type values, lemma attributes, batches
  dict-xxx.xxe/.css  made from the .toml file by make_config.py
scripts/     Python scripts, run by the menu in xxe
make_config.py   generates .xxe and .css files from the tomls in dicts/dict-xxx/
```


## The scripts

The scripts work on the dictionary repository they are run in (the
current folder or one above it with `src/*.xml`), so run them from there:

```sh
cd ~/PATH/TO/dict-sme
python3 ~/PATH/TO/giella-dict-xxe/scripts/batch.py -h
python3 ~/PATH/TO/giella-dict-xxe/scripts/check_links.py
```

The menu runs them the same way, in the repository of the open file.
Their lists for XXE are written in `.xxe/` in the dictionary repository,
which should be in its `.gitignore`. Sorting follows the alphabet of the
language of the dictionary (`xml:lang` of its files), in
`scripts/alphabet.py`.

## A new dictionary

1. Make a folder `dicts/dict-xxx/`, copy `dicts/dict-sme/dict-sme.toml`
   to `dicts/dict-xxx/dict-xxx.toml` and change it:

   - `id`: the id of the root element of its files, `<r id="dict-xxx">`
   - `batches`: whether entries are put in batches (`batches/batches.xml`)
   - `pos`: the pos values offered, as in its schema
   - `[types]`: the types that go with each pos
   - `[lemma_attributes]`: other attributes of `<l>`, with their values
     and the pos they go with (as `class` in `dict-sma.toml`)

2. Run `python3 make_config.py` (Python 3.11 or later). It writes
   `dict-xxx.xxe` and `dict-xxx.css` next to it; commit them too, since
   XXE reads them and the people editing do not run make_config.py.

3. If the language is not in `scripts/alphabet.py`, add its alphabet, and
   if the PDFs should be in that language, its texts in
   `scripts/batch2pdf.py`.

The dictionary repository needs `src/*.xml` (the files are named by pos:
`N_xxx.xml`, `Pron_Dem_xxx.xml`, ..., which "New entry" uses for the pos)
and, with batches, `batches/batches.xml`.

## Changing the add-on

Change `core/` for all the dictionaries, the `.toml` file (then run
`make_config.py`) for one of them. Do not edit the `.xxe` and `.css` files in
`dicts/` that `make_config.py` makes. Restart XXE to see the changes.
