import unittest
from read_dotgraph_tokenise import main as tokenise

class BasicTest(unittest.TestCase):
    def test_if(self):
        tokens = tokenise("tests/basic_test_graphs/a-0005-ifstmt.c.015t.cfg.dot")
        self.assertEqual(tokens, "p i0 o3 e0 i1 o5 e1 i2 o7 e2 o8 f2 f1 f0 o9 r0 m")

    def test_while(self):
        tokens = tokenise("tests/basic_test_graphs/a-0006-whilestmt.c.015t.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 o3 d1 o5 r0 m")

    def test_multiconditional_if_merging(self):
        tokens = tokenise("tests/basic_test_graphs/a-11_precedence.c.015t.cfg.dot")
        self.assertEqual(tokens, "p i0 o5 e0 o6 f0 i1 o10 e1 o11 f1 i2 o15 e2 o16 f2 i3 o20 e3 o21 f3 i4 o24 e4 o25 f4 i5 o28 e5 o29 f5 o30 r0 m")

    def test_large_conditional_tree(self):
        tokens = tokenise("tests/basic_test_graphs/a-0034-logandor.c.015t.cfg.dot")
        self.assertEqual(tokens, "p i0 o4 r0 f0 i1 o6 r1 f1 i2 i3 o10 r2 f3 o11 i4 i5 o16 r3 f5 o17 i6 i7 o22 r4 f7 o23 o25 r5 f6 o24 r6 f4 o18 r7 f2 o12 r8 m")

    def test_sequential_whiles(self):
        tokens = tokenise("tests/basic_test_graphs/a-0035-breakcont.c.015t.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 o5 o6 d1 o4 w2 o9 o10 d2 o8 w3 o13 o14 d3 o12 o15 r0 m")

    def test_nested_whiles(self):
        tokens = tokenise("tests/basic_test_graphs/a-0042-prime.c.015t.cfg.dot")
        self.assertEqual(tokens, "p o2 w1 o3 w2 i0 o5 f0 o6 d2 i1 o9 f1 d1 i2 o12 r0 f2 o13 r1 m")

    def test_switch(self):
        tokens = tokenise("tests/basic_test_graphs/a-0052-switch.c.015t.cfg.dot")
        self.assertEqual(tokens, "p i0 i1 o4 i2 o8 r0 f2 i3 o10 r1 f3 o11 i4 o14 r2 f4 i5 o12 r3 f5 o13 r4 f1 o5 r5 f0 o6 r6 m")

    def test_returns_in_switch(self):
        tokens = tokenise("tests/basic_test_graphs/a-47_switch_return.c.015t.cfg.dot")
        self.assertEqual(tokens, "p o2 i0 o3 r0 f0 i1 o4 e1 i2 o5 r1 f2 f1 o6 r2 m")
    