from .detector import ActiveDetector as _ActiveDetector
from .vectors import generate_vectors
from ..progress import progress
from ..reporting import write_vulnerability_report


class ActiveDetector(_ActiveDetector):
    """Public detector that also writes a human-readable vulnerability report."""

    def run(self, vectors):
        findings = super().run(vectors)
        output = self.config.run_dir / "analysis" / "vulnerability_report.md"
        write_vulnerability_report(findings, output)
        progress(f"漏洞页面报告已生成：{output}")
        return findings


__all__ = ["ActiveDetector", "generate_vectors"]
