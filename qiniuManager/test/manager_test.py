# coding=utf8
import os
import string
import random
import unittest
import tempfile

from qiniuManager.manager import *


def generate_random_string(size):
    return "".join([random.choice(string.ascii_letters + string.digits) for _ in range(size)])


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.origin_access = self.config.get_one_access()
        self.origin_default_space = self.config.get_default_space()
        self.test_access = tuple([generate_random_string(30), generate_random_string(30)])
        self.test_space = tuple([generate_random_string(20), generate_random_string(30)])

    def test_all(self):
        # access test
        self.config.add_access(*self.test_access)
        self.assertTupleEqual(self.config.get_one_access(), self.test_access)

        # space test
        self.config.set_space(*self.test_space)
        self.assertTupleEqual(self.config.get_default_space(), self.test_space)
        self.assertTupleEqual(self.config.get_space(self.test_space[0]), self.test_space)
        self.config.remove_space(self.test_space[0])

    def tearDown(self):
        self.config.add_access(*self.origin_access)
        self.config.set_space(*self.origin_default_space)
        self.config.remove_space(self.test_space[0])


class ManagerTest(unittest.TestCase):
    def setUp(self):
        self.manager = Qiniu()
        self.tmp_file_name = 'tmp.data'
        self.tmp_file = os.path.join(tempfile.gettempdir(), self.tmp_file_name)
        with open(self.tmp_file, 'wb') as handle:
            handle.write(os.urandom(102400))

    def test_api(self):
        # 上传
        print("换行")
        self.manager.upload(self.tmp_file)

        # 重命名
        self.manager.rename(self.tmp_file_name, 'data.tmp')
        self.manager.rename("data.tmp", self.tmp_file_name)

        # 导出下载链接
        ex = self.manager.export_download_links()
        self.assertTrue(self.tmp_file_name in ex[1])

        # 文件列表
        l = self.manager.list()
        self.assertTrue(self.tmp_file_name in l[1])

        # 文件通配符
        find = self.manager.list(find_pattern=self.tmp_file_name + '*')
        self.assertTrue(self.tmp_file_name in find[1])

        # 文件状态检查
        self.manager.check(self.tmp_file_name)

        # 下载文件
        print("换行")
        if self.manager.download(self.tmp_file_name):
            os.unlink(self.tmp_file_name)

        # 删除文件
        self.manager.remove('tmp.data', no_prompt=True)

    def test_link(self):
        link = self.manager.regular_download_link(self.tmp_file_name)
        self.assertTrue(link.endswith(self.tmp_file_name))

    def test_p_link(self):
        p_link = self.manager.private_download_link(self.tmp_file_name)
        self.assertTrue(self.tmp_file_name in p_link)

    def tearDown(self):
        os.unlink(self.tmp_file)


if __name__ == '__main__':
    unittest.main()
