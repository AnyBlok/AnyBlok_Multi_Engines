# This file is a part of the AnyBlok Multi Engines project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration
import os


@Configuration.add('database')
def update_database(group):
    group.add_argument('--db-ro-url',
                       default=os.environ.get('ANYBLOK_DATABASE_URL_RO'),
                       type=list,
                       help="Complete URL(s) for read only connection with "
                            "the database")
    group.add_argument('--db-wo-url',
                       default=os.environ.get('ANYBLOK_DATABASE_URL_WO'),
                       type=list,
                       help="Complete URL(s) for write only connection with "
                            "the database")


@Configuration.add('pluggins')
def update_pluggins(group):
    group.set_defaults(
        Registry='anyblok_multi_engines.registry:RegistryMultiEngines')
