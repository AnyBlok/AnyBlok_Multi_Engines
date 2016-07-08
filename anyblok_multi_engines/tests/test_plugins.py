# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import TestCase
from anyblok.config import Configuration
from anyblok_multi_engines.config import get_url
from anyblok_multi_engines.registry import RegistryMultiEngines


class TestPlugins(TestCase):

    def test_have_plugin_get_url(self):
        self.assertIs(Configuration.get('get_url'), get_url)

    def test_have_plugin_Registry(self):
        self.assertIs(Configuration.get('Registry'), RegistryMultiEngines)
