# Main-experiment artifacts

This directory contains the published artifacts and execution logs for the 16
applications evaluated in the DRHL main experiment. Each application directory
may include crawl artifacts, graph construction outputs, generated attack
vectors, access-control source-analysis results, repair prompts and attempts,
validation evidence, reports, and aggregate metrics.

The artifacts record local benchmark executions. Credentials appearing in the
crawl artifacts are synthetic or local benchmark-account values already defined
by the public experiment configurations; no LLM API key, external authorization
credential, browser cookie, or private key is included.

Running DRHL again with the corresponding file under `configs/` may update files
inside the matching application directory.
