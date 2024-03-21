#! /usr/bin/env python
from pylatex import Document, Section, Subsection, Tabular
from pylatex import Math, TikZ, Axis, Plot, Figure, Matrix, Alignat
from pylatex.utils import italic

import os
import subprocess
import random
import math
from string import Template


class SolveFragment:
    """docstring for SolveFragment."""

    def __init__(
        self,
        name,
        latexFormula,
        qalcFormula,
        dependancies=[],
        parents=[],
        isSubStep=False,
        latexName=None,
    ):
        self.name = name
        self.latexName = latexName
        self.latexFormula = latexFormula
        self.qalcFormula = qalcFormula
        self.dependancies = dependancies
        self.parents = parents
        self.isSubStep = isSubStep
        self.answer = None
        self.latex = None
        self.preview = None

    def __str__(self):
        return "{} => {}".format(self.latexFormula, self.qalcFormula)

    def PreviewLatex(self, recurse=False):
        if self.preview == None:
            t = Template(self.latexFormula)
            vars = dict(
                map(
                    lambda dep: (dep.name, dep.latexName or dep.name), self.dependancies
                )
            )
            print("preview", self.latexFormula, vars)
            self.preview = t.substitute(vars)
        return self.preview

    def ShowLatex(self, recurse=False):
        if self.latex == None:
            t = Template(self.latexFormula)
            vars = dict(
                map(lambda dep: (dep.name, dep.ShowAnswer(False)), self.dependancies)
            )
            print("latex", self.latexFormula, vars)
            self.latex = t.substitute(vars)
        return self.latex

    def ShowAnswer(self, recurse=False):
        if self.answer == None or recurse:
            t = Template(self.qalcFormula)
            vars = dict(
                map(lambda dep: (dep.name, dep.ShowAnswer(True)), self.dependancies)
            )
            print("answer", self.qalcFormula, vars)
            r = t.substitute(vars)
            if recurse:
                return r
            self.answer = qalculate(r)
        return self.answer

    def RecurseAnswer(self, adoc):
        if len(self.parents) < 1 and not self.isSubStep:
            return
        for ans in self.parents:
            ans.RecurseAnswer(adoc)
        name = self.latexName or self.name
        adoc.append(
            Math(
                data=[name, "=", self.PreviewLatex(), "\\\\"],
                escape=False,
            )
        )
        if not self.isSubStep:
            adoc.append(
                Math(
                    data=[name, "=", self.ShowLatex(), "\\\\"],
                    escape=False,
                )
            )
            adoc.append(
                Math(
                    data=[name, "=", self.ShowAnswer()],
                    escape=False,
                )
            )
            adoc.append("\n")


def qalculate(input):
    return (
        subprocess.run(
            ["qalc", "-t", input],
            capture_output=True,
        )
        .stdout.decode()
        .strip()
        .replace("−", "-")
    )


def qGiven(vars):
    given = dict(filter(lambda v: not callable(v[1]), vars.items())).items()
    qv = []
    for k, v in given:
        qv.append(v.latexName or v.name)
        qv.append(v.latexFormula)
    q = "Given " + ("{}={}, " * (given.__len__() - 1)) + "and {}={};\n"
    return q.format(*qv)


def qSect(title):
    return Section(title), Section(title)


def qSubSect(qparts):
    q, a = Subsection(""), Subsection("")
    for item in qparts:
        q.append(item)
        a.append(item)
    return q, a


def RandomVar(vars, name, source):
    if not name in vars.keys():
        b = source()
        if callable(b):
            b = b(vars)
        else:
            vars[name] = b
    else:
        b = vars[name]
    return b


def ShannonQueryC():
    vars = {}
    ans = ShannonSolveC(vars)
    qdoc, adoc = qSubSect(
        [
            qGiven(vars),
            "Using the ",
            italic("Shannon Capacity Formula "),
            "what is the theoretical maximum capacity?\n",
        ]
    )
    ans.RecurseAnswer(adoc)
    return qdoc, adoc


# $$C = B\log_2(1+SNR)$$
def ShannonSolveC(vars):
    b = RandomVar(vars, "B", RandomB)
    snr = RandomVar(vars, "SNR", RandomSNR)

    trueFormula = SolveFragment(
        "C", "$B\log_2(1+$SNR)", "$B log2(1+$SNR)", [b, snr], [b, snr], isSubStep=True
    )

    return SolveFragment(
        "C",
        "$B\\frac{\log_{10}(1+$SNR)}{\log_{10}2}",
        "($B log2(1+$SNR))",
        [b, snr],
        [trueFormula],
    )


def ShannonQueryB():
    vars = {}
    ans = ShannonSolveB(vars)
    qdoc, adoc = qSubSect(
        [
            qGiven(vars),
            "Using the ",
            italic("Shannon Capacity Formula "),
            "what is the bandwidth B?\n",
        ]
    )
    ans.RecurseAnswer(adoc)
    return qdoc, adoc


def ShannonSolveB(vars):
    snr = RandomVar(vars, "SNR", RandomSNR)
    c = RandomVar(vars, "C", RandomC)
    b = SolveFragment("B", "B", "1")

    base = SolveFragment(
        "", "$B\log_2(1+$SNR)", "", [b, snr], isSubStep=True, latexName="C"
    )
    # base = SolveFragment(
    #    "",
    #    "\log_2(1+SNR)",
    #    "",
    #    [],
    #    [base],
    #    isSubStep=True,
    #    latexName="\\frac{C}{B}",
    # )
    # base = SolveFragment(
    #    "",
    #    "\\frac{1}{\log_2(1+SNR)}",
    #    "",
    #    [],
    #    [base],
    #    isSubStep=True,
    #    latexName="\\frac{B}{C}",
    # )
    base = SolveFragment(
        "B",
        "$C\\frac{1}{\log_2(1+$SNR)}",
        "($C*(1/log2(1+$SNR)))",
        [c, snr],
        isSubStep=True,
    )
    base = SolveFragment(
        "B",
        "$C\\frac{1}{\\frac{\log_{10}(1+$SNR)}{\log_{10}2}}",
        "($C*(1/log2(1+$SNR)))",
        [c, snr],
        [c, snr, base],
    )
    return base


def NyquistQueryC():
    vars = {}
    ans = NyquistSolveC(vars)
    qdoc, adoc = qSubSect(
        [
            qGiven(vars),
            "Using the ",
            italic("Nyquist Bandwidth Formula "),
            "what is the capacity C?\n",
        ]
    )
    ans.RecurseAnswer(adoc)
    return qdoc, adoc


def NyquistSolveC(vars):
    l = RandomVar(vars, "L", RandomL)
    b = RandomVar(vars, "B", RandomB)
    return SolveFragment("C", "2 \cdot $B \cdot $L", "2 * $B * $L", [l, b], [l, b])


def NyquistQueryL():
    vars = {}
    ans = NyquistSolveL(vars)
    qdoc, adoc = qSubSect(
        [
            qGiven(vars),
            "Using the ",
            italic("Nyquist Bandwidth Formula "),
            "what is __ L?\n",
            "NOTE: not done\n"
        ]
    )
    ans.RecurseAnswer(adoc)
    return qdoc, adoc


def NyquistSolveL(vars):
    c = RandomVar(vars, "C", RandomC)
    b = RandomVar(vars, "B", RandomB)
    l = SolveFragment("L", "L", "1")
    base = SolveFragment("C", "2 \cdot $B \cdot $L", "2 * $B * $L", [l, b], [l, b])
    # todo
    return base


# $$B = f_H-f_L$$
def SolveB(vars):
    fH, fL = RandomFrqSet()
    vars["f_H"] = fH
    vars["f_L"] = fL
    return SolveFragment("B", "($f_H - $f_L)", "($f_H - $f_L)", [fH, fL], [fH, fL])


# $$SNR = 10^{(\frac{SNR_{dB}}{10})}$$
def SolveSNR(vars):
    snr_db = RandomVar(vars, "SNR_dB", RandomSNR_dB)
    return SolveFragment(
        "SNR", "10^{(\\frac{$SNR_dB}{10})}", "(10^($SNR_dB/10))", [snr_db], [snr_db]
    )


# $$SNR_{dB} = 10\cdot\log_{10}\frac{signal\ power}{signal\ noise}$$
def SolveSNR_dB(vars):
    pwr = RandomdB("pwr")
    noise = RandomdB("noise")
    vars["pwr"] = pwr
    vars["noise"] = noise
    return SolveFragment(
        "SNR_dB",
        "10\cdot\log_{10}\\frac{$pwr}{$noise}",
        "(10 log10($pwr/$noise))",
        [pwr, noise],
        [pwr, noise],
        latexName="SNR_{dB}",
    )


def RandomB():
    rng = random.randint(0, 3)
    i = random.randint(1, 6)
    if rng == 0:
        return SolveFragment("B", "{}KHz".format(i), "{}E3".format(i))
    elif rng == 1:
        return SolveFragment("B", "{}MHz".format(i), "{}E6".format(i))
    elif rng == 2:
        return SolveFragment("B", "{}GHz".format(i), "{}E9".format(i))
    elif rng == 3:
        return SolveB


def RandomC():
    rng = random.randint(0, 2)
    i = random.randint(1, 6)
    if rng == 0:
        return SolveFragment("C", "{}Kbps".format(i), "{}E3".format(i))
    elif rng == 1:
        return SolveFragment("C", "{}Mbps".format(i), "{}E6".format(i))
    elif rng == 2:
        return SolveFragment("C", "{}Gbps".format(i), "{}E9".format(i))


def RandomSNR_dB():
    rng = random.randint(0, 1)
    if rng == 0:
        return SolveSNR_dB
    elif rng == 1:
        u = random.randint(1, 5)
        l = random.randint(11, 99)
        return SolveFragment(
            "SNR_dB",
            "{}.{}".format(u, l) + "dB",
            "{}.{}".format(u, l),
            latexName="SNR_{dB}",
        )


def RandomSNR():
    rng = random.randint(0, 1)
    if rng == 0:
        return SolveSNR
    elif rng == 1:
        u = random.randint(0, 3)
        l = random.randint(11, 99)
        return SolveFragment("SNR", "{}.{}".format(u, l), "{}.{}".format(u, l))


def RandomFrqSet():
    rng = random.randint(0, 1)
    if rng == 0:
        lower = random.randint(1, 99) * 100
        upper = lower + (random.randint(1, 99) * 100)
        return (
            SolveFragment("f_H", "{}KHz".format(upper), "{}E3".format(upper)),
            SolveFragment("f_L", "{}KHz".format(lower), "{}E3".format(lower)),
        )
    if rng == 1:
        lower = random.randint(1, 99) * 10
        upper = lower + (random.randint(1, 99) * 10)
        return (
            SolveFragment("f_H", "{}MHz".format(upper), "{}E6".format(upper)),
            SolveFragment("f_L", "{}MHz".format(lower), "{}E6".format(lower)),
        )


def SolveL(vars):
    m = RandomVar(vars, "M", RandomM)
    base = SolveFragment("L", "\log_2M", "", isSubStep=True)
    return SolveFragment(
        "L", "\\frac{\log_{10}$M}{\log_{10}2}", "log2($M)", [m], [m, base]
    )


def RandomdB(name):
    u = random.randint(1, 5)
    l = random.randint(11, 99)
    return SolveFragment(name, "{}.{}".format(u, l) + "dB", "{}.{}".format(u, l))


def RandomM():
    i = math.pow(random.randint(2, 4), 2)
    return SolveFragment("M", "{}".format(i), "{}".format(i))


def RandomL():
    rng = random.randint(0, 1)
    if rng == 0:
        return SolveL
    elif rng == 1:
        i = random.randint(2, 4)
        return SolveFragment("L", "{}".format(i), "{}".format(i))


if __name__ == "__main__":
    random.seed()
    geometry_options = {"margin": "1cm"}
    qdoc = Document(geometry_options=geometry_options)
    adoc = Document(geometry_options=geometry_options)

    sq, sa = qSect("Snannon Capacity")
    queries = [ShannonQueryC, ShannonQueryB]
    qdoc.append(sq)
    adoc.append(sa)

    for query in queries:
        c = random.randint(1, 5)
        for i in range(c):
            q, a = query()
            sq.append(q)
            sa.append(a)

    sq, sa = qSect("Nyquist Bandwidth")
    queries = [NyquistQueryC, NyquistQueryL]
    qdoc.append(sq)
    adoc.append(sa)

    for query in queries:
        c = random.randint(1, 5)
        for i in range(c):
            q, a = query()
            sq.append(q)
            sa.append(a)

    # making a pdf using .generate_pdf
    if not os.path.isdir("./build"):
        os.mkdir("./build")
    qdoc.generate_pdf("./build/questions", clean_tex=False)
    adoc.generate_pdf("./build/answers", clean_tex=False)
