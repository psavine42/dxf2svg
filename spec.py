import unittest
import dxf2svg

class TestMethods(unittest.TestCase):

    def test_overrides_parse(self):
        file = 'resources/overrides.json'
        trgt = 'resources/cl.dxf'

        z = dxf2svg.parse_override_file(file, trgt)

        self.assertEqual(z,  {'A-WALL': {'color': '#ff0000'}})

    def test_svg(self):
        file = 'resources/overrides.json'
        trgt = 'resources/clsmall.dxf'

        z = dxf2svg.parse_override_file(file, trgt)

        self.assertEqual(z,  {'A-Wall': {'color': '#ff0000'}})

if __name__ == '__main__':
    unittest.main()

