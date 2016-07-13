# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase, LogCapture
from anyblok.config import Configuration
from anyblok_multi_engines.registry import RegistryMultiEngines as Registry
from anyblok.registry import RegistryException
from logging import DEBUG


class TestRegistry(DBTestCase):

    def setUp(self):
        super(TestRegistry, self).setUp()
        self._registry = None

    def tearDown(self):
        super(TestRegistry, self).tearDown()
        if self._registry:
            self._registry.close()

    def get_registry(self, unittest=True, **kwargs):
        db_name = Configuration.get('db_name')
        self._registry = Registry(db_name, unittest=unittest, **kwargs)
        return self._registry

    def test_init(self):
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='', db_wo_url=''
        ):
            registry = self.get_registry()
            self.assertTrue(registry.System.Model.query().count())

    def test_get_engine_ro(self):
        with DBTestCase.Configuration(
            db_ro_urls=['postgresql:///'], db_url='', db_wo_url=''
        ):
            registry = self.get_registry()
            self.assertTrue(registry.engines['ro'])
            self.assertIsNone(registry.engines['wo'])
            engine = registry.get_engine_for()
            self.assertIn(engine, registry.engines['ro'])

    def test_get_engine_ro_without_r(self):
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='', db_wo_url='postgresql:///'
        ):
            registry = self.get_registry()
            with self.assertRaises(RegistryException):
                registry.get_engine_for()

    def test_get_engine_rw(self):
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='postgresql:///', db_wo_url=''
        ):
            registry = self.get_registry()
            self.assertTrue(registry.engines['ro'])
            self.assertIsNotNone(registry.engines['wo'])
            engine = registry.get_engine_for()
            self.assertIn(engine, registry.engines['ro'])
            self.assertIs(engine, registry.engines['wo'])

    def test_get_engine_wo(self):
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='', db_wo_url='postgresql:///'
        ):
            registry = self.get_registry()
            self.assertIsNotNone(registry.engines['wo'])
            self.assertFalse(registry.engines['ro'])
            engine = registry.get_engine_for(ro=False)
            self.assertIs(engine, registry.engines['wo'])

    def test_get_engine_wo_without_w(self):
        with DBTestCase.Configuration(
            db_ro_urls=['postgresql:///'], db_url='', db_wo_url=''
        ):
            registry = self.get_registry()
            with self.assertRaises(RegistryException):
                registry.get_engine_for(ro=False)

    def test_bind(self):
        registry = self.get_registry()
        bind = registry.bind
        self.assertIs(bind, registry.unittest_bind)

    def test_bind_without_unittest(self):
        # WARNING don't commit here
        registry = self.get_registry(unittest=False)
        bind1 = registry.bind
        bind2 = registry.bind
        self.assertIs(bind1, bind2)

    def test_engine(self):
        with DBTestCase.Configuration(
            db_ro_urls=['postgresql:///'], db_url='', db_wo_url='postgresql:///'
        ):
            registry = self.get_registry()
            self.assertIs(registry.engine, registry._engine)
            self.assertIs(registry.engine, registry.engines['wo'])
            self.assertNotIn(registry.engine, registry.engines['ro'])

    def test_engine_with_loadwithoutmigration(self):
        with DBTestCase.Configuration(
            db_ro_urls=['postgresql:///'], db_url='', db_wo_url='postgresql:///'
        ):
            registry = self.get_registry(loadwithoutmigration=True)
            self.assertIs(registry.engine, registry._engine)
            self.assertIn(registry.engine, registry.engines['ro'])
            self.assertIsNot(registry.engine, registry.engines['wo'])

    def test_db_url_and_db_wo_url(self):
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='postgresql:///', db_wo_url='postgresql:///'
        ):
            with self.assertRaises(RegistryException):
                self.get_registry()

    def test_commit(self):
        registry = self.get_registry()
        registry.session_connection = 'False value'
        registry.commit()
        self.assertIsNone(registry.session_connection)

    def test_ro_force_no_automigration(self):
        with DBTestCase.Configuration(
            db_ro_urls=['postgresql:///'], db_url='', db_wo_url=''
        ):
            with LogCapture('anyblok_multi_engines.registry',
                            level=DEBUG) as logs:
                self.get_registry()
                messages = logs.get_debug_messages()
                self.assertIn('No WRITE engine defined use READ ONLY mode',
                              messages)

    def test_db_exists_without_url(self):
        db_name = Configuration.get('db_name')
        Registry = Configuration.get('Registry')
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='', db_wo_url=''
        ):
            self.assertTrue(Registry.db_exists(db_name=db_name))

    def test_db_exists_with_url(self):
        db_name = Configuration.get('db_name')
        Registry = Configuration.get('Registry')
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='postgresql:///', db_wo_url=''
        ):
            self.assertTrue(Registry.db_exists(db_name=db_name))

    def test_db_exists_with_wo_url(self):
        db_name = Configuration.get('db_name')
        Registry = Configuration.get('Registry')
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='', db_wo_url='postgresql:///'
        ):
            self.assertTrue(Registry.db_exists(db_name=db_name))

    def test_db_exists_with_ro_url(self):
        db_name = Configuration.get('db_name')
        Registry = Configuration.get('Registry')
        with DBTestCase.Configuration(
            db_ro_urls=['postgresql:///'], db_url='', db_wo_url=''
        ):
            self.assertTrue(Registry.db_exists(db_name=db_name))

    def test_db_exists_without_db_name(self):
        Registry = Configuration.get('Registry')
        with self.assertRaises(RegistryException):
            Registry.db_exists()

    def test_db_exists_with_wrong_db_name(self):
        db_name = 'wrong_db_name'
        Registry = Configuration.get('Registry')
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='', db_wo_url=''
        ):
            self.assertFalse(Registry.db_exists(db_name=db_name))

    def test_db_exists_with_url_with_wrong_db_name(self):
        db_name = 'wrong_db_name'
        Registry = Configuration.get('Registry')
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='postgresql:///', db_wo_url=''
        ):
            self.assertFalse(Registry.db_exists(db_name=db_name))

    def test_db_exists_with_wo_url_with_wrong_db_name(self):
        db_name = 'wrong_db_name'
        Registry = Configuration.get('Registry')
        with DBTestCase.Configuration(
            db_ro_urls=[], db_url='', db_wo_url='postgresql:///'
        ):
            self.assertFalse(Registry.db_exists(db_name=db_name))

    def test_db_exists_with_ro_url_with_wrong_db_name(self):
        db_name = 'wrong_db_name'
        Registry = Configuration.get('Registry')
        with DBTestCase.Configuration(
            db_ro_urls=['postgresql:///'], db_url='', db_wo_url=''
        ):
            self.assertFalse(Registry.db_exists(db_name=db_name))
