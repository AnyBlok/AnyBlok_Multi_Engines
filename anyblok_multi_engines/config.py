# This file is a part of the AnyBlok Multi Engines project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration, ConfigurationException
from sqlalchemy.engine.url import URL, make_url
import os


def get_url(db_name=None, url=None):
    """ Return an sqlalchemy URL for database

    :param db_name: Name of the database
    :param url: base of the url
    :rtype: SqlAlchemy URL
    :exception: ConfigurationException
    """
    drivername = Configuration.get('db_driver_name', None)
    username = Configuration.get('db_user_name', None)
    password = Configuration.get('db_password', None)
    host = Configuration.get('db_host', None)
    port = Configuration.get('db_port', None)
    database = Configuration.get('db_name', None)

    if db_name is not None:
        database = db_name

    if url:
        url = make_url(url)
        if username:
            url.username = username
        if password:
            url.password = password
        if database:
            url.database = database

        return url

    if drivername is None:
        raise ConfigurationException('No Drivername defined')

    return URL(drivername, username=username, password=password, host=host,
               port=port, database=database)


@Configuration.add('database')
def update_database(group):
    group.add_argument('--db-ro-urls',
                       default=os.environ.get('ANYBLOK_DATABASE_URL_RO'),
                       type=list,
                       help="Complete URL(s) for read only connection with "
                            "the database")
    group.add_argument('--db-wo-url',
                       default=os.environ.get('ANYBLOK_DATABASE_URL_WO'),
                       help="Complete URL for write only connection with "
                            "the database, you can't use bothg --db-wo-url "
                            "and --db-url")


@Configuration.add('plugins', must_be_loaded_by_unittest=True)
def update_plugins(group):
    group.set_defaults(
        Registry='anyblok_multi_engines.registry:RegistryMultiEngines',
        get_url='anyblok_multi_engines.config:get_url')
