# Sample SRD corpus

A tiny slice of SRD 5.1 content (one class + a few spells) so you can run the
ingestion pipeline end-to-end without fetching the full corpus:

```bash
python scripts/ingest_srd.py --srd-dir scripts/sample_srd --reset
```

For the real corpus, point `--srd-dir` at a full SRD 5.1 markdown checkout
(e.g. github.com/OldManUmby/DND.SRD.Wiki), which is licensed CC-BY-4.0.

Content here is derived from the System Reference Document 5.1, © Wizards of the
Coast LLC, CC-BY-4.0.
