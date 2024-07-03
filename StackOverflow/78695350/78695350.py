import pyparsing as pp
import textwrap as tw

text = """
    A) Red
    B) Green
    C) Blue
    """

a = pp.AtLineStart("A)") + pp.Word(pp.alphas) + pp.line_end.suppress()
b = pp.AtLineStart("B)") + pp.Word(pp.alphas) + pp.line_end.suppress()
c = pp.AtLineStart("C)") + pp.Word(pp.alphas)

grammar = a + b + c
grammar.run_tests([tw.dedent(text).strip()])


# outputs...
"""
A) Red
B) Green
C) Blue
['A)', 'Red', 'B)', 'Green', 'C)', 'Blue']
"""
