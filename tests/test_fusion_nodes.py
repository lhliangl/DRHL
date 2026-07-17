import unittest

from drhl.graphs.fusion import fuse_graphs


class FusionNodeTests(unittest.TestCase):
    def test_static_public_nodes_are_in_final_node_set(self):
        dynamic = {"nodes": ["index.php"], "edges": [], "access": {}}
        static = {
            "nodes": ["index.php", "install.php", "functions.php"],
            "edges": [{"from": "index.php", "to": "functions.php"}],
            "url_to_source": {
                "index.php": "index.php",
                "install.php": "install.php",
                "functions.php": "functions.php",
            },
            "classifications": {},
        }
        fused = fuse_graphs(dynamic, static)
        self.assertIn("install.php", fused["nodes"])
        self.assertIn("install.php", fused["static_only"])
        self.assertEqual(fused["static_edges"], static["edges"])
        self.assertEqual(fused["node_origins"]["index.php"], ["dynamic", "static"])


if __name__ == "__main__":
    unittest.main()
