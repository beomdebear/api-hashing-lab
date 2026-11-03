"""Portable arithmetic checks. GCC or MSVC can compile the small C vector tool.
This test uses GCC here; it does not validate Windows API calls or PE parsing.
"""
import importlib.util
import subprocess
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("generator", ROOT / "scripts/tv1-generate-hashes.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

class HashTests(unittest.TestCase):
    def test_standard_vectors(self):
        self.assertEqual(gen.hash_name("", 1, 5381), 5381)
        self.assertEqual(gen.hash_name("hello", 1, 5381), 0x0F923099)
        self.assertEqual(gen.hash_name("hello", 2, 2166136261), 0x4F9F2CAB)
        self.assertEqual(gen.hash_name("123456789", 3, 0xFFFFFFFF), 0xCBF43926)

    def test_c_matches_reference(self):
        names = ("", "123456789", *gen.APIS)
        for alg, seed in ((1, 5381), (2, 2166136261), (3, 0xFFFFFFFF), (1, 1337)):
            with self.subTest(algorithm=alg, seed=seed), tempfile.TemporaryDirectory() as tmp:
                exe = str(Path(tmp) / "hash-vectors")
                subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                                f"-DTV1_ALGORITHM={alg}", f"-DTV1_SEED={seed}u",
                                str(ROOT / "tests/resolver/tv1-hash-vectors.c"), "-o", exe], check=True)
                got = subprocess.check_output([exe], text=True).splitlines()
                expected = [f"{gen.hash_name(name, alg, seed):08X}" for name in names]
                self.assertEqual(got, expected)

    def test_generated_targets(self):
        for _, (folder, alg, seed, _) in gen.VARIANTS.items():
            source = (ROOT / "samples" / folder / "main.c").read_text()
            for slot, name in zip(("CREATE", "WRITE", "CLOSE"), gen.APIS):
                self.assertIn(f"#define TV1_TARGET_{slot} 0x{gen.hash_name(name, alg, seed):08X}u", source)
            for name in gen.APIS:
                self.assertNotIn('"' + name + '"', source)

if __name__ == "__main__":
    unittest.main(verbosity=2)
