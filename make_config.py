#!/usr/bin/env python3
"""Make the XXE configuration of each dictionary from its .toml file.

Usage: make_config.py [dicts/dict-xxx/dict-xxx.toml ...]

Each dictionary has a folder of its own, dicts/dict-xxx/. For each
dict-xxx.toml there (all of them by default), writes dict-xxx.xxe and
dict-xxx.css next to it. Those files are made by this
script: change the .toml file and run it again, instead of editing them.
See README.md for what goes in the .toml file.

The .xxe file includes the shared configuration in core/. The .css file
imports the shared style sheet core/dict.css and adds what differs
between dictionaries: the pos menu, and the lemma line with its
attributes (type, homograph number, and any others the dictionary has).

On the lemma line, an attribute that is set is shown with a menu to
change or remove it. Those not set yet are offered by one small button,
since they are rarely used. The type menu only offers the types that go
with the pos, and a type that does not go with it is flagged. XXE cannot
put a menu together from parts, so there is a rule for each pos that has
types and each combination of attributes that are set. The rules rely on
CSS specificity: one with more attributes in its selector wins, and of
two equal ones the later wins.

Needs Python 3.11 or later (tomllib).
"""

import itertools
import sys
from pathlib import Path

import tomllib

HERE = Path(__file__).resolve().parent
DICTS = HERE / "dicts"

NOTE = "Made by make_config.py from {toml}: change that file and run make_config.py, do not edit this one."


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def menu(items):
    """CSS menu(): items are (label, command, parameter), or None for a
    separator."""
    parts = []
    for item in items:
        label, command, parameter = item or ("", "", "")
        parts.append(f"{q(label)}, {q(command)}, {q(parameter)}")
    return "menu(" + ",\n    ".join(parts) + ")"


class Dictionary:
    def __init__(self, toml):
        self.toml = toml
        spec = tomllib.loads(toml.read_text(encoding="utf-8"))
        self.id = spec["id"]
        self.batches = spec.get("batches", False)
        self.pos = spec["pos"]
        self.types = spec.get("types", {})
        self.homographs = spec.get("homographs", 4)
        # the other attributes of l: name -> values, and name -> the pos
        # they go with (None: all of them)
        self.extra, self.extra_pos = {}, {}
        for name, spec_ in spec.get("lemma_attributes", {}).items():
            if isinstance(spec_, list):
                spec_ = {"values": spec_}
            self.extra[name] = spec_["values"]
            self.extra_pos[name] = spec_.get("pos")
        for pos in [
            *self.types,
            *(p for ps in self.extra_pos.values() for p in ps or []),
        ]:
            if pos not in self.pos:
                sys.exit(f"{toml.name}: {pos} is not in pos")
        # the pos that need rules of their own: those with types, or with
        # attributes that only go with some pos
        self.special = list(
            dict.fromkeys(
                [*self.types, *(p for ps in self.extra_pos.values() for p in ps or [])]
            )
        )
        # the attributes of l, in the order they are shown
        self.attrs = [*self.extra, "type", "hid"]

    # --- menu items for setting an attribute ---------------------------

    def items(self, attr, pos):
        """Items setting attr, in the menu of attributes not set yet;
        labelled with the attribute, since the menu has several."""
        if attr == "hid":
            return [
                (f"homograph {n}", "putAttribute", f"hid {n}")
                for n in range(1, self.homographs + 1)
            ]
        values = self.types.get(pos, []) if attr == "type" else self.extra[attr]
        return [(f"{attr} {v}", "putAttribute", f"{attr} {v}") for v in values]

    def goes_with(self, attr, pos):
        """Whether attr can be set for a lemma with this pos (None: a pos
        with no rules of its own)."""
        if attr == "type":
            return bool(self.types.get(pos))
        if attr in self.extra:
            return self.extra_pos[attr] is None or pos in self.extra_pos[attr]
        return True

    def offered(self, pos):
        """The attributes that can be set for a lemma with this pos."""
        return [a for a in self.attrs if self.goes_with(a, pos)]

    # --- the CSS ---------------------------------------------------------

    def css(self):
        out = [
            f"/*\n * XMLmind XML Editor (XXE) style sheet for {self.id}.",
            " * " + NOTE.format(toml=self.toml.name),
            " */",
            "",
            '@import "../../core/dict.css";',
        ]
        if self.batches:
            out.append('@import "../../core/dict-batches.css";')
        out += [
            "",
            "/* --- pos ----------------------------------------------------------- */",
            "",
        ]
        pos_menu = menu([(p, "putAttribute", f"pos {p}") for p in self.pos])
        out += ["lg:before {", f"  content: pos-field({pos_menu});", "}", ""]

        out += [
            "/* --- menus to change an attribute that is set ---------------------- */",
            "",
        ]
        for pos, types in self.types.items():
            items = [(t, "putAttribute", f"type {t}") for t in types]
            items += [None, ("no type", "removeAttribute", "type")]
            out.append(f"@property-value types-{pos}() set-menu({menu(items)});")
        for attr, values in self.extra.items():
            items = [(v, "putAttribute", f"{attr} {v}") for v in values]
            items += [None, (f"no {attr}", "removeAttribute", attr)]
            out.append(
                f'@property-value {attr}-field() "   {attr} " value(attr({attr})) set-menu({menu(items)});'
            )
            if self.extra_pos[attr] is not None:
                out.append(
                    f'@property-value wrong-{attr}() text("   {attr} does not go with this pos", '
                    "color, warning-color());"
                )
        out.append("")

        out += [
            "/* --- the lemma line ------------------------------------------------ */",
            "",
            "/* the rules for any pos, then those for each pos with types or",
            "   attributes of its own; see make_config.py for how they work */",
            "",
        ]
        mores = {}
        for pos in [None, *self.special]:
            for n in range(len(self.attrs) + 1):
                for set_ in itertools.combinations(self.attrs, n):
                    out += self.rules(pos, set_, mores)
        # the menus of attributes not set yet, defined before the rules
        # that use them
        defs = [
            "/* --- menus of the attributes not set yet ---------------------------- */",
            "",
        ]
        for name, items in mores.items():
            defs.append(f"@property-value {name}() more({menu(items)});")
        defs.append("")
        i = out.index(
            "/* --- the lemma line ------------------------------------------------ */"
        )
        return "\n".join(out[:i] + defs + out[i:]) + "\n"

    def selector(self, pos, set_, type_=None):
        s = f'lg[pos="{pos}"]>l' if pos else "l"
        for a in set_:
            s += f'[type="{type_}"]' if a == "type" and type_ else f"[{a}]"
        return s + ":after"

    def rules(self, pos, set_, mores):
        """The rules for a lemma with this pos (None: any pos with no
        rules of its own) and these attributes set: one for a type that does not go with the
        pos, then one for the types that do."""
        unset = [a for a in self.offered(pos) if a not in set_]
        items = []
        for a in unset:
            if items:
                items.append(None)
            items += self.items(a, pos)
        more = ""
        if items:
            name = "more-" + (pos or "any") + "-" + "-".join(unset)
            mores[name] = items
            more = f" {name}()"

        def content(valid):
            parts = []
            for a in set_:
                if a == "hid":
                    parts.append("hid-field()")
                elif a == "type" and self.types.get(pos):
                    parts.append(
                        f"type-field(types-{pos}())"
                        + ("" if valid else " wrong-type()")
                    )
                elif a == "type":
                    parts.append(
                        '"   type " value(attr(type)) remove-attribute-button(attribute, type, '
                        "color, header-button-color(), background-color, header-button-background()) wrong-type()"
                    )
                else:
                    parts.append(
                        f"{a}-field()"
                        + ("" if self.goes_with(a, pos) else f" wrong-{a}()")
                    )
            return " ".join(parts) + more + " add-lemma()"

        out = []
        if "type" in set_ and self.types.get(pos):
            out += [
                self.selector(pos, set_) + " {",
                f"  content: {content(False)};",
                "}",
                "",
            ]
            sels = [self.selector(pos, set_, t) for t in self.types[pos]]
            out += [",\n".join(sels) + " {", f"  content: {content(True)};", "}", ""]
        else:
            out += [
                self.selector(pos, set_) + " {",
                f"  content: {content(False)};",
                "}",
                "",
            ]
        return out

    # --- the XXE configuration --------------------------------------------

    def xxe(self):
        includes = ['    <include location="../../core/dict.incl" />']
        if self.batches:
            includes.append('    <include location="../../core/dict-batches.incl" />')
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  XMLmind XML Editor (XXE) configuration for {self.id}.
  {NOTE.format(toml=self.toml.name)}
-->
<configuration name="{self.id}" xmlns="http://www.xmlmind.com/xmleditor/schema/configuration"
    xmlns:cfg="http://www.xmlmind.com/xmleditor/schema/configuration">
    <!-- active for the files with the root element <r id="{self.id}"> -->
    <detect>
        <and>
            <rootElementLocalName>r</rootElementLocalName>
            <rootElementAttribute localName="id" value="{self.id}" />
        </and>
    </detect>

    <css name="Editing view" location="{self.id}.css" />

{chr(10).join(includes)}
</configuration>
"""


def main():
    tomls = [Path(a) for a in sys.argv[1:]] or sorted(DICTS.glob("*/*.toml"))
    for toml in tomls:
        d = Dictionary(toml.resolve())
        for ext, text in (("xxe", d.xxe()), ("css", d.css())):
            out = toml.with_suffix("." + ext)
            out.write_text(text, encoding="utf-8")
            print(f"{toml.name} -> {out.name}")


if __name__ == "__main__":
    main()
