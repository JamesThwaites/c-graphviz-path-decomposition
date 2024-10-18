import unittest
from read_dotgraph_tokenise import main as tokenise

class CustomTest(unittest.TestCase):
    def test_simple_break(self):
        tokens = tokenise("tests/custom_test_graphs/break.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 o4 b1 f0 i1 o6 e1 o7 f1 o8 d1 i2 o11 f2 o12 r0 m")

    def test_break_or_if_then_return(self):
        tokens = tokenise("tests/custom_test_graphs/break_or_if_then_return.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 i1 o5 b1 f1 i2 o7 e2 o8 f2 o9 r0 f0 i3 o11 e3 o12 f3 o13 d1 o15 r1 m")

    def test_break_in_if_and_else(self):
        tokens = tokenise("tests/custom_test_graphs/break_in_if_and_else.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 i1 o5 b1 f1 o6 b1 f0 i2 o8 e2 o9 f2 o10 d1 o12 r0 m")

    def test_break_after_if_and_else(self):
        tokens = tokenise("tests/custom_test_graphs/break_after_if_and_else.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 i1 o5 e1 o6 f1 o7 b1 f0 i2 o9 e2 o10 f2 o11 d1 o13 r0 m")

    def test_breaks_in_else(self):
        tokens = tokenise("tests/custom_test_graphs/breaks_in_else.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 i1 o5 e1 o6 f1 o7 e0 i2 o9 b1 f2 o10 b1 f0 d1 o12 r0 m")

    def test_lots_of_else_breaks(self):
        tokens = tokenise("tests/custom_test_graphs/break_both_branches.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 i1 i2 o6 e2 o7 f2 i3 o17 f3 e1 i4 o9 e4 o10 f4 o11 b1 f1 e0 i5 o13 e5 o14 f5 o15 b1 f0 d1 o19 r0 m")

    def test_continues(self):
        tokens = tokenise("tests/custom_test_graphs/continues.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 i1 o5 e1 o6 f1 i2 o12 c1 f2 o13 c1 f0 i3 o8 e3 o9 f3 o10 d1 o15 r0 m")

    def test_continue_in_else(self):
        tokens = tokenise("tests/custom_test_graphs/continue_in_else.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 i1 o5 e1 o6 f1 i2 o9 c1 f2 o10 c1 f0 o7 d1 o12 r0 m")

    def test_immediate_continue_in_if(self):
        tokens = tokenise("tests/custom_test_graphs/continue_immediate_in_if.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 i1 o5 e1 o6 f1 e0 i2 o8 c1 f2 o9 f0 i3 o11 c1 f3 o12 d1 o14 r0 m")

    def test_while_in_break(self):
        tokens = tokenise("tests/custom_test_graphs/while_in_break.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 o4 w2 o5 d2 o7 b1 f0 i1 o9 e1 o10 f1 o11 d1 i2 o14 f2 o15 r0 m")

    def test_nested_while_in_break(self):
        tokens = tokenise("tests/custom_test_graphs/3while_in_break.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 o4 w2 i1 o6 b2 f1 o7 w3 i2 o9 b3 f2 d3 d2 o12 w4 o13 d4 o15 b1 f0 i3 o17 e3 o18 f3 o19 d1 i4 o22 f4 o23 r0 m")

    def test_custom_multiconditional_with_break(self):
        tokens = tokenise("tests/custom_test_graphs/more_multiconditionals.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 i0 o6 e0 i1 o10 b1 f1 f0 d1 o14 r0 m")

    def test_custom_multiconditional_without_else(self):
        tokens = tokenise("tests/custom_test_graphs/multiconditional_no_else.cfg.dot")
        self.assertEqual(tokens, "p i0 o6 f0 i1 o11 f1 o12 r0 m")
