import unittest,sys,struct,tempfile,subprocess
from pathlib import Path
from types import SimpleNamespace as Port
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import usb_update as u

class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.data=bytearray((u.ROOT/'firmware/dist/nora-app.signed.bin').read_bytes())
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'test.bin'
    def tearDown(self):self.temp.cleanup()
    def check(self):self.path.write_bytes(self.data);return u.check_image(self.path)
    def test_real_image(self):self.assertEqual(self.check(),bytes(self.data))
    def test_factory_hex_is_not_update(self):
        with self.assertRaises(ValueError):u.check_image(u.ROOT/'firmware/dist/nora-factory.hex')
    def test_bad_headers_and_vectors(self):
        for offset,value,fmt in [(0,0,'<I'),(8,0x400,'<H'),(12,0x60000,'<I'),(16,0x10,'<I'),(0x200,0,'<I'),(0x204,0x10001,'<I'),(0x204,0x30200,'<I')]:
            with self.subTest(offset=offset,value=value):
                old=self.data[:];struct.pack_into(fmt,self.data,offset,value)
                with self.assertRaises(ValueError):self.check()
                self.data=old
    def test_truncated_tlv(self):
        del self.data[-1:]
        with self.assertRaises(ValueError):self.check()
    def test_port_selection_respects_physical_board(self):
        a=Port(device='/dev/ttyACM0',vid=u.BOOT_VID,pid=u.BOOT_PID,location='1-2')
        b=Port(device='/dev/ttyACM1',vid=u.BOOT_VID,pid=u.BOOT_PID,location='1-3')
        self.assertEqual(u.recovery_port([a,b],location='1-3'),b.device)
        self.assertEqual(u.recovery_port([a,b],device=a.device),a.device)
        with self.assertRaises(ValueError):u.recovery_port([a,b])
        app=Port(device=a.device,vid=u.BOOT_VID,pid=u.APP_PID,location=a.location)
        with self.assertRaises(ValueError):u.recovery_port([app],device=app.device)
    def test_failed_upload_does_not_reset(self):
        with patch.object(u.subprocess,'run',side_effect=subprocess.CalledProcessError(1,'mcumgr')) as run:
            with self.assertRaises(subprocess.CalledProcessError):u.transfer('mcumgr','/dev/ttyACM0',self.path)
            self.assertEqual(run.call_count,1)
    def test_successful_upload_then_reset(self):
        with patch.object(u.subprocess,'run') as run:
            u.transfer('mcumgr','/dev/ttyACM0',self.path)
            self.assertEqual(run.call_count,2)
            self.assertEqual(run.call_args_list[0].args[0][-3:],['image','upload',str(self.path)])
            self.assertEqual(run.call_args_list[1].args[0][-1],'reset')
    def test_no_reset_option(self):
        with patch.object(u.subprocess,'run') as run:
            u.transfer('mcumgr','/dev/ttyACM0',self.path,reset=False)
            self.assertEqual(run.call_count,1)

if __name__=='__main__':unittest.main()
