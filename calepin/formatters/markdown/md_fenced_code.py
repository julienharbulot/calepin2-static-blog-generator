"""
Original code Copyright 2007-2008 Waylan Limberg
All changes Copyright 2008-2014 The Python Markdown Project | License: BSD
Modified 2019 by Julien Harbulot to add filename and terminal.
"""

from __future__ import absolute_import, unicode_literals

import re

from markdown.extensions import Extension
from markdown.extensions.codehilite import (
    CodeHilite,
    CodeHiliteExtension,
    parse_hl_lines,
)
from markdown.preprocessors import Preprocessor


class FencedCodeExtension(Extension):
    def __init__(self, codehilite_config={}):
        self.codehilite_config = codehilite_config

    def extendMarkdown(self, md):
        """Add FencedBlockPreprocessor to the Markdown instance."""
        md.registerExtension(self)
        md.preprocessors.register(
            FencedBlockPreprocessor(md, codehilite_config=self.codehilite_config),
            "my_fenced_code_block",
            25,
        )


class FencedBlockPreprocessor(Preprocessor):
    FENCED_BLOCK_RE = re.compile(
        r"""
(?P<fence>^(?:~{3,}|`{3,}))[ ]*         # Opening ``` or ~~~
(\{?\.?(?P<lang>[\w#.+-]*))?[ ]*        # Optional {, and lang
# Optional highlight lines, single- or double-quote-delimited
(hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]*
}?[ ]*\n                                # Optional closing }
((?:/{2,}|\#|(?:<!--))[ ]*file[ ]*:[ ]*(?P<file>[^\n]+?)[ ]*(?:-->)?[ ]*\n)?    # Optional //file: filename
((?:/{2,}|\#|(?:<!--))[ ]*terminal[ ]*:[ ]*(?P<terminal>[^\n]+?)[ ]*(?:-->)?[ ]*\n)?    # Optional //terminal: terminal name
(?P<in>((?:/{2,}|\#|(?:<!--))[ ]*input_cell[ ]*(?:-->)?[ ]*\n)?)    # Optional //input_cell: 2
(?P<out>((?:/{2,}|\#|(?:<!--))[ ]*output_cell[ ]*(?:-->)?[ ]*\n)?)    # Optional //output_cell: 2
(?P<code>.*?)(?<=\n)
(?P=fence)[ ]*$""",
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )
    CODE_WRAP = "<pre><code%s>%s</code></pre>"
    LANG_TAG = ' class="%s"'

    def __init__(self, md, codehilite_config={}):
        super(FencedBlockPreprocessor, self).__init__(md)
        cf = codehilite_config
        self.codehilite_conf = {
            "linenums": [cf.get("linenums", None)],
            "guess_lang": [cf.get("guess_lang", True)],
            "css_class": [cf.get("css_class", "codehilite")],
            "pygments_style": [cf.get("pygments_style", "default")],
            "use_pygments": [cf.get("use_pygments", True)],
            "noclasses": [cf.get("noclasses", False)],
        }
        self.checked_for_codehilite = bool(codehilite_config)

    def run(self, lines):
        """Match and store Fenced Code Blocks in the HtmlStash."""

        # Check for code hilite extension
        if not self.checked_for_codehilite:
            for ext in self.md.registeredExtensions:
                if isinstance(ext, CodeHiliteExtension):
                    self.codehilite_conf = ext.config
                    break
            self.checked_for_codehilite = True

        text = "\n".join(lines)
        while True:
            m = self.FENCED_BLOCK_RE.search(text)
            if not m:
                break
            else:
                lang = self.LANG_TAG % m.group("lang") if m.group("lang") else ""
                if self.codehilite_conf:
                    # If config is not empty, then the codehighlite extension
                    # is enabled, so we call it to highlight the code
                    highliter = CodeHilite(
                        m.group("code"),
                        linenums=self.codehilite_conf["linenums"][0],
                        guess_lang=self.codehilite_conf["guess_lang"][0],
                        css_class=self.codehilite_conf["css_class"][0],
                        style=self.codehilite_conf["pygments_style"][0],
                        use_pygments=self.codehilite_conf["use_pygments"][0],
                        lang=(m.group("lang") or None),
                        noclasses=self.codehilite_conf["noclasses"][0],
                        hl_lines=parse_hl_lines(m.group("hl_lines")),
                    )
                    inner_code = highliter.hilite()
                else:
                    inner_code = self.CODE_WRAP % (lang, self._escape(m.group("code")))

                if m.group("file"):
                    code = f'<div class="hll-title"><span class="filename">{m.group("file")} </span> {inner_code} </div>'
                elif m.group("terminal"):
                    code = f'<div class="hll-title"><span class="terminal">{m.group("terminal")} </span> {inner_code} </div>'
                elif m.group("in"):
                    code = f'<div class="input_cell"> {inner_code} </div>'
                elif m.group("out"):
                    code = f'<div class="output_cell"> {inner_code} </div>'

                else:
                    code = inner_code

                placeholder = self.md.htmlStash.store(code)
                text = "%s\n%s\n%s" % (text[: m.start()], placeholder, text[m.end() :])
        return text.split("\n")

    def _escape(self, txt):
        """basic html escaping"""
        txt = txt.replace("&", "&amp;")
        txt = txt.replace("<", "&lt;")
        txt = txt.replace(">", "&gt;")
        txt = txt.replace('"', "&quot;")
        return txt


def makeExtension(**kwargs):  # pragma: no cover
    return FencedCodeExtension(**kwargs)
