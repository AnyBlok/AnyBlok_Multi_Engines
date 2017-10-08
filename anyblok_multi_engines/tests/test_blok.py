# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase


class TestBlok(DBTestCase):
    blok_entry_points = ('bloks', 'test_bloks')

    def test_without_update_session_or_query(self):
        registry = self.init_registry(None)
        self.assertTrue(registry.System.Blok.query().all())

    def test_update_session(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test-me-blok1',))
        registry.commit()
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = self.init_registry(None)
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all())

    def test_update_query(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test-me-blok2',))
        registry.commit()
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = self.init_registry(None)
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())

    def test_update_query_and_session_1(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test-me-blok3',))
        registry.commit()
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = self.init_registry(None)
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())

    def test_update_query_and_session_2(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test-me-blok1',))
        registry.upgrade(install=('test-me-blok2',))
        registry.commit()
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = self.init_registry(None)
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())

    def test_update_query_and_session_3(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test-me-blok1', 'test-me-blok2'))
        registry.commit()
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
        registry.close()
        registry = self.init_registry(None)
        self.assertTrue(registry.test_the_session_is_updated())
        self.assertTrue(registry.System.Blok.query().all_name())
        self.assertTrue(registry.System.Blok.query().all())
