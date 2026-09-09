import csv, importlib.util, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location("ingest",Path(__file__).resolve().parents[1]/"scripts/ingest.py")
ingest=importlib.util.module_from_spec(spec);spec.loader.exec_module(ingest)

class IngestionTests(unittest.TestCase):
    def setUp(self):
        with (ingest.ROOT/"sources/katalon_testops_sample_dataset.csv").open(encoding="utf-8-sig") as stream:
            self.rows=list(csv.DictReader(stream))[:2]
    def import_rows(self,rows):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"test.csv"
            with path.open("w",newline="",encoding="utf-8") as stream:
                writer=csv.DictWriter(stream,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
            return ingest.csv_documents(path)
    def test_duplicate_idempotent(self):
        docs,stats=self.import_rows(self.rows+[self.rows[0]])
        self.assertEqual(stats["rows"],2)
        self.assertEqual(stats["raw_rows"],3)
        self.assertTrue(all(d["source_rows"] for d in docs))
    def test_conflicting_duplicate_rejected(self):
        with self.assertRaises(ValueError): self.import_rows(self.rows+[{**self.rows[0],"status":"FAILED"}])
    def test_invalid_duration_rejected(self):
        with self.assertRaises(ValueError): self.import_rows([{**self.rows[0],"duration_seconds":"NaN"}])
    def test_cleaning_and_overlap(self):
        self.assertEqual(ingest.clean("<script>secret</script><p>A &amp; B</p>"),"A & B")
        chunks=ingest.chunk({"id":"d","content":" ".join(str(i) for i in range(500))})
        self.assertEqual(chunks[1]["word_start"],205)
        self.assertEqual(chunks[-1]["word_end"],500)
    def test_missing_scope_fails_closed(self):
        with self.assertRaises(ValueError): ingest.validate({"source_type":"jira"})

if __name__=="__main__": unittest.main()
