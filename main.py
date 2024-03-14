#! /usr/bin/env python
import numpy as np

from pylatex import Document, Section, Subsection, Tabular
from pylatex import Math, TikZ, Axis, Plot, Figure, Matrix, Alignat
from pylatex.utils import italic

import os
import random


# $$C = B\log_2(1+SNR)$$
def ShannonSolveC(qdoc, adoc, vars, depth):
    if depth == 0:
        vars["B"] = RandomB(vars)
        vars["SNR"] = RandomSNR(vars)
        qdoc.append(
            "Given B={} and SNR={};\n Using the ".format(vars["B"], vars["SNR"])
        )
        qdoc.append(italic("Shannon Capacity Formula "))
        qdoc.append(
            "what is the theoretical maximum capacity?\n".format(
                vars["B"], vars["SNR"], italic("Shannon Capacity Formula")
            )
        )
    if callable(vars["B"]):
        vars["B"] = vars["B"](qdoc, adoc, vars, depth + 1)
    if callable(vars["SNR"]):
        vars["SNR"] = vars["SNR"](qdoc, adoc, vars, depth + 1)


# $$B = f_H-f_L$$
def SolveB(qdoc, adoc, vars, depth):
    pass


# $$SNR = 10^{(\frac{SNR_{dB}}{10})}$$
def SolveSNR(qdoc, adoc, vars, depth):
    pass


def RandomB(vars):
    return 1_000_001

def RandomSNR(vars):
    return 1.5


if __name__ == "__main__":
    random.seed()
    geometry_options = {"margin": "1cm"}
    qdoc = Document(geometry_options=geometry_options)
    adoc = Document(geometry_options=geometry_options)

    qsect = Section("Shannon Capacity Formula")
    asect = Section("Shannon Capacity Formula")
    qdoc.append(qsect)
    adoc.append(asect)
    ShannonSolveC(qsect, asect, {}, 0)

    # making a pdf using .generate_pdf
    if not os.path.isdir("./build"):
        os.mkdir("./build")
    qdoc.generate_pdf("./build/questions", clean_tex=True)
    adoc.generate_pdf("./build/answers", clean_tex=True)
