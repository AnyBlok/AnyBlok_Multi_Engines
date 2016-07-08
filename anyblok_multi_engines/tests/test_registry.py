# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok.config import Configuration
from anyblok_multi_engines.registry import RegistryMultiEngines as Registry
from anyblok.registry import RegistryException


class TestRegistry(DBTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestRegistry, cls).setUpClass()
        cls.old_configuration = Configuration.configuration.copy()

    @classmethod
    def tearDownClass(cls):
        super(TestRegistry, cls).tearDownClass()
        Configuration.configuration = cls.old_configuration

    def setUp(self):
        super(TestRegistry, self).setUp()
        Configuration.configuration = self.__class__.old_configuration.copy()
        Configuration.update(**dict(db_url=None, db_ro_url=[], db_wo_url=[]))
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
        registry = self.get_registry()
        self.assertTrue(registry.System.Model.query().count())

    def test_get_engine_ro(self):
        Configuration.update(**dict(db_ro_url=['postgres:///']))
        registry = self.get_registry()
        self.assertTrue(registry.engines['ro'])
        self.assertFalse(registry.engines['wo'])
        engine = registry.get_engine_for()
        self.assertIn(engine, registry.engines['ro'])

    def test_get_engine_ro_without_r(self):
        Configuration.update(**dict(db_wo_url=['postgres:///']))
        registry = self.get_registry()
        with self.assertRaises(RegistryException):
            registry.get_engine_for()

    def test_get_engine_rw(self):
        Configuration.update(**dict(db_url='postgres:///'))
        registry = self.get_registry()
        self.assertTrue(registry.engines['ro'])
        self.assertTrue(registry.engines['wo'])
        engine = registry.get_engine_for()
        self.assertIn(engine, registry.engines['ro'])
        self.assertIn(engine, registry.engines['wo'])

    def test_get_engine_wo(self):
        Configuration.update(**dict(db_wo_url=['postgres:///']))
        registry = self.get_registry()
        self.assertTrue(registry.engines['wo'])
        self.assertFalse(registry.engines['ro'])
        engine = registry.get_engine_for(ro=False)
        self.assertIn(engine, registry.engines['wo'])

    def test_get_engine_wo_without_w(self):
        Configuration.update(**dict(db_ro_url=['postgres:///']))
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
        Configuration.update(**dict(db_ro_url=['postgres:///'],
                                    db_wo_url=['postgres:///']))
        registry = self.get_registry()
        self.assertIs(registry.engine, registry._engine)
        self.assertIn(registry.engine, registry.engines['wo'])
        self.assertNotIn(registry.engine, registry.engines['ro'])

    def test_engine_with_loadwithoutmigration(self):
        Configuration.update(**dict(db_ro_url=['postgres:///'],
                                    db_wo_url=['postgres:///']))
        registry = self.get_registry(loadwithoutmigration=True)
        self.assertIs(registry.engine, registry._engine)
        self.assertIn(registry.engine, registry.engines['ro'])
        self.assertNotIn(registry.engine, registry.engines['wo'])

    def test_commit(self):
        registry = self.get_registry()
        registry.session_connection = 'False value'
        registry.commit()
        self.assertIsNone(registry.session_connection)

    def test_ro_force_no_automigration(self):
        Configuration.update(**dict(db_ro_url=['postgres:///']))
        registry = self.get_registry()
        self.assertTrue(registry.loadwithoutmigration)
