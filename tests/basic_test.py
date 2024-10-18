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