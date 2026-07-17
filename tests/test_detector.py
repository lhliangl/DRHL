from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from drhl.analysis.detector import ActiveDetector
from drhl.config import PipelineConfig, RoleConfig, TargetConfig
from drhl.models import AttackVector, RequestSpec


class Response:
    def __init__(self, text="private page", status=200, url="http://example.test/private.php"):
        self.text = text
        self.status_code = status
        self.url = url
        self.headers = {}


class Session:
    def __init__(self, responses):
        self.responses = responses
        self.headers = {}
        self.cookies = {}

    def get(self, *args, **kwargs):
        return self.responses.pop(0)

    def request(self, *args, **kwargs):
        return self.responses.pop(0)

    def close(self):
        pass


class Snapshot:
    def __init__(self):
        self.restores = 0

    def restore(self):
        self.restores += 1


class DetectorTests(unittest.TestCase):
    def test_database_restores_between_baseline_and_attack_and_after_attack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            role = RoleConfig("user1", "user")
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "php", (".php",)),
                database={},
                crawl={},
                roles=(role,),
                analysis={},
                repair={},
            )
            responses = [Response("authorized private page " * 20), Response("different but accessible page " * 20)]
            snapshot = Snapshot()
            detector = ActiveDetector(config, snapshot, session_factory=lambda: Session(responses))
            vector = AttackVector(
                "authenticated_only", "private.php", ["user1"], RequestSpec("GET")
            )
            findings = detector.run([vector])
            self.assertEqual(findings[0].status, "vulnerable")
            self.assertEqual(findings[0].confidence, "high")
            self.assertIn("HTTP 200 without redirect or denial marker", " ".join(findings[0].evidence))
            self.assertEqual(snapshot.restores, 1)

    def test_static_only_accessible_to_visitor_is_vulnerable_without_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "php", (".php",)),
                database={},
                crawl={},
                roles=(),
                analysis={},
                repair={},
            )
            responses = [Response("installer page " * 20, 200, "http://example.test/install.php")]
            snapshot = Snapshot()
            detector = ActiveDetector(config, snapshot, session_factory=lambda: Session(responses))
            vector = AttackVector("static_only", "install.php", [], RequestSpec("GET"))

            findings = detector.run([vector])

            self.assertEqual(findings[0].status, "vulnerable")
            self.assertEqual(findings[0].confidence, "high")
            self.assertIn("HTTP 200 without redirect or denial marker", " ".join(findings[0].evidence))
            self.assertEqual(snapshot.restores, 1)


if __name__ == "__main__":
    unittest.main()

