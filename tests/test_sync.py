import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from sync_upstream import select, version_key


def release(tag, pre=False, draft=False):
    return dict(tag_name=tag, prerelease=pre, draft=draft)

class SelectionTests(unittest.TestCase):
    def test_numeric_order(self):
        self.assertGreater(version_key('0.1.0-rc.10'),version_key('0.1.0-rc.2'))
    def test_stable_wins(self):
        r = [release('v0.1.0-rc.3',True),release('v0.1.0')]
        self.assertEqual(select(r,'v','0.1.0-rc.2',True)[1],'v0.1.0')
    def test_stable_channel(self):
        self.assertIsNone(select([release('v0.2.0-rc.1',True)],'v','0.1.0',True))
    def test_no_draft_downgrade_or_same(self):
        r = [release('v0.1.0-rc.3',True,True),release('v0.1.0-rc.1',True),release('v0.1.0-rc.2',True)]
        self.assertIsNone(select(r,'v','0.1.0-rc.2',True))
    def test_ir_prefix_and_channel(self):
        r = [release('v9.0.0'),release('pironman-ir-v0.3.0-rc.1',True),release('pironman-ir-v0.2.1')]
        self.assertEqual(select(r,'pironman-ir-v','0.2.0',False)[1],'pironman-ir-v0.2.1')
    def test_inconsistent_flag(self):
        self.assertIsNone(select([release('v0.1.0-rc.3')],'v','0.1.0-rc.2',True))
