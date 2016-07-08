# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import config
from anyblok.config import Configuration, ConfigurationException
from anyblok_multi_engines.config import update_database, update_plugins
from anyblok.tests.testcase import TestCase
from anyblok.tests.test_config import MockArgumentParser
from sqlalchemy.engine.url import make_url
from anyblok_multi_engines.config import get_url


old_getParser = config.getParser


class TestConfiguration(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestConfiguration, cls).setUpClass()

        def getParser(*args, **kwargs):
            return MockArgumentParser()

        config.getParser = getParser
        cls.old_configuration = Configuration.configuration.copy()
        cls.old_groups = Configuration.groups.copy()
        cls.old_labels = Configuration.labels.copy()

    @classmethod
    def tearDownClass(cls):
        super(TestConfiguration, cls).tearDownClass()
        config.getParser = old_getParser
        Configuration.configuration = cls.old_configuration
        Configuration.groups = cls.old_groups
        Configuration.labels = cls.old_labels

    def setUp(self):
        super(TestConfiguration, self).setUp()
        Configuration.groups = {}
        Configuration.labels = {}
        Configuration.configuration = {}

    def check_url(self, url, wanted_url):
        wanted_url = make_url(wanted_url)
        for x in ('drivername', 'host', 'port', 'username', 'password',
                  'database'):
            self.assertEqual(
                getattr(url, x), getattr(wanted_url, x),
                "check url(%s) == url(%s) on attribute %r" % (url, wanted_url,
                                                              x))

    def test_get_url(self):
        Configuration.update(
            db_name='anyblok',
            db_driver_name='postgres',
            db_host='localhost',
            db_user_name=None,
            db_password=None,
            db_port=None)
        url = get_url()
        self.check_url(url, 'postgres://localhost/anyblok')

    def test_get_url2(self):
        Configuration.update(
            db_name='anyblok',
            db_driver_name='postgres',
            db_host='localhost',
            db_user_name=None,
            db_password=None,
            db_port=None,)
        url = get_url(db_name='anyblok2')
        self.check_url(url, 'postgres://localhost/anyblok2')

    def test_get_url3(self):
        db_url = 'postgres:///anyblok'
        Configuration.update(
            db_name=None,
            db_driver_name=None,
            db_host=None,
            db_user_name=None,
            db_password=None,
            db_port=None)
        url = get_url(url=db_url)
        self.check_url(url, 'postgres:///anyblok')

    def test_get_url4(self):
        db_url = 'postgres:///anyblok'
        Configuration.update(
            db_name='anyblok2',
            db_driver_name=None,
            db_host=None,
            db_user_name='jssuzanne',
            db_password='secret',
            db_port=None)
        url = get_url(url=db_url)
        self.check_url(url, 'postgres://jssuzanne:secret@/anyblok2')

    def test_get_url5(self):
        db_url = 'postgres:///anyblok'
        Configuration.update(
            db_driver_name=None,
            db_host=None,
            db_user_name='jssuzanne',
            db_password='secret',
            db_port=None)
        url = get_url(db_name='anyblok3', url=db_url)
        self.check_url(url, 'postgres://jssuzanne:secret@/anyblok3')

    def test_get_url_without_drivername(self):
        Configuration.update(
            db_name=None,
            db_driver_name=None,
            db_host=None,
            db_user_name=None,
            db_password=None,
            db_port=None)
        with self.assertRaises(ConfigurationException):
            get_url()


class TestConfigurationOption(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestConfigurationOption, cls).setUpClass()
        cls.parser = MockArgumentParser()
        cls.group = cls.parser.add_argument_group('label')
        cls.function = {
            'update_plugins': update_plugins,
            'update_database': update_database,
        }

    def test_update_plugins(self):
        self.function['update_plugins'](self.group)

    def test_update_database(self):
        self.function['update_database'](self.group)
