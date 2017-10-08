# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import TestCase
from anyblok.registry import RegistryManager
from anyblok.blok import BlokManager
from anyblok.config import Configuration
from sqlalchemy.orm import clear_mappers


class TestBlok(TestCase):

    def setUp(self):
        super(TestBlok, self).setUp()
        self.__class__.init_configuration_manager()
        self.__class__.createdb(keep_existing=False)
        BlokManager.load(entry_points=('bloks', 'test_bloks'))
        registry = RegistryManager.get(Configuration.get('db_name'))
        registry.commit()
        registry.close()

    def tearDown(self):
        """ Clear the registry, unload the blok manager and  drop the database
        """
        registry = RegistryManager.get(Configuration.get('db_name'))
        registry.close()
        RegistryManager.clear()
        BlokManager.unload()
        clear_mappers()
        self.__class__.dropdb()
        super(TestBlok, self).tearDown()

    def test_update_session(self):
        registry = RegistryManager.get(Configuration.get('db_name'))
        registry.upgrade(install=('test-me-blok1',))
        registry.commit()
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = RegistryManager.get(Configuration.get('db_name'))
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all())

    def test_update_query(self):
        registry = RegistryManager.get(Configuration.get('db_name'))
        registry.upgrade(install=('test-me-blok2',))
        registry.commit()
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = RegistryManager.get(Configuration.get('db_name'))
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())

    def test_update_query_and_session_1(self):
        registry = RegistryManager.get(Configuration.get('db_name'))
        registry.upgrade(install=('test-me-blok3',))
        registry.commit()
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = RegistryManager.get(Configuration.get('db_name'))
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())

    def test_update_query_and_session_2(self):
        registry = RegistryManager.get(Configuration.get('db_name'))
        registry.upgrade(install=('test-me-blok1',))
        registry.upgrade(install=('test-me-blok2',))
        registry.commit()
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = RegistryManager.get(Configuration.get('db_name'))
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())

    def test_update_query_and_session_3(self):
        registry = RegistryManager.get(Configuration.get('db_name'))
        registry.upgrade(install=('test-me-blok1', 'test-me-blok2'))
        registry.commit()
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = RegistryManager.get(Configuration.get('db_name'))
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
