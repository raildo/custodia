# Copyright (C) 2017  Custodia Project Contributors - see LICENSE file
import os
import unittest

from custodia.httpd.server import HTTPServer
from custodia.server.args import parse_args
from custodia.server.config import parse_config

HERE = os.path.dirname(os.path.abspath(__file__))
CONF_DIR = os.path.join(HERE, 'test_custodia.conf')


class BaseTest(unittest.TestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        self.config_file = CONF_DIR
        self.args = parse_args([CONF_DIR])

    def test_args(self):
        self.assertEqual(self.args.configfile.name, CONF_DIR)

    def test_create_server(self):
        _, config = parse_config(self.args)
        self.httpd = HTTPServer(config['server_url'], config)
        self.assertEqual(type(self.httpd), HTTPServer)
