# This file is a part of the AnyBlok Multi Engines project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.registry import Registry, RegistryException, RegistryManager
from anyblok.config import Configuration
from sqlalchemy.orm import sessionmaker, scoped_session
from anyblok.environment import EnvironmentManager
from anyblok_multi_engines.config import get_url
from sqlalchemy import create_engine
from sqlalchemy_utils.functions import database_exists
from random import choice
from logging import getLogger


logger = getLogger(__name__)


class MixinSession:
    """Mixin for the SQLAlchemy session the goal is to allow the connection
    with more than one engine: masters / slaves engines
    """

    def get_bind(self, mapper=None, clause=None):
        """Overload the ``Session.get_bind`` method of SQLAlchemy

        the rule are:

        * if has session_connection: use the session_connection, because it
          use during the creation of the AnyBlok Registry, which need get the
          same bind
        * if unittest_transaction: durring unittest, they are no
          slaves / masters
        * if flushing: write on the database then we use the master
        * read the database then use a slave
        """
        if self.registry.session_connection:
            return self.registry.session_connection
        elif self.registry.unittest_transaction:
            return self.registry.bind
        elif self._flushing:
            return self.registry.get_engine_for(ro=False)
        else:
            return self.registry.get_engine_for()


class MultiEngines:
    """Mixin class which overload the AnyBlok Registry class

    the goal is to implement in the the Registry the masters / slaves
    behaviour
    """

    def init_engine(self, db_name=None):
        """Overload the initiation of engine to create more than one
        engine

        use the Configuration option to create engines:

        * db_url: read and write engine
        * db_ro_urls: read only engines (list)
        * db_wo_url: write only engines

        .. warning::

            All the engines use the same database name not at the same location

        :param db_name: name of the database for the engines
        """
        kwargs = self.init_engine_options()
        gurl = Configuration.get('get_url', get_url)
        self.engines = {'ro': [], 'wo': None}
        self._engine = None

        for url in Configuration.get('db_ro_urls', []) or []:
            url = gurl(db_name=db_name, url=url)
            engine = create_engine(url, **kwargs)
            self.engines['ro'].append(engine)

        wo_url = Configuration.get('db_wo_url')
        if wo_url:
            url = gurl(db_name=db_name, url=wo_url)
            engine = create_engine(url, **kwargs)
            self.engines['wo'] = engine

        url = Configuration.get('db_url')
        if url and wo_url:
            raise RegistryException(
                "You have not to use the both Configuration option "
                "--get-wo-url [%s] and --get-url [%s], chose only one of them "
                "because only one master can be chose" % (wo_url, url))
        elif url:
            url = gurl(db_name=db_name, url=url)
            engine = create_engine(url, **kwargs)
            self.engines['wo'] = engine
            self.engines['ro'].append(engine)

        if not self.engines['ro'] and not self.engines['wo']:
            url = gurl(db_name=db_name)
            engine = create_engine(url, **kwargs)
            self.engines['wo'] = engine
            self.engines['ro'].append(engine)
        elif not self.engines['wo']:
            logger.debug('No WRITE engine defined use READ ONLY mode')
            self.loadwithoutmigration = True

    def get_engine_for(self, ro=True):
        """ Return one engine among the engines

        :param ro: if True the engine will be read only else write only
        :rtype: engine
        :exception: RegistryException
        """
        engines = self.engines['ro'] if ro else self.engines['wo']
        if not engines:
            raise RegistryException("No engine found for do action %r" % (
                "read" if ro else "write"))

        if ro:
            return choice(engines)

        return engines

    def init_bind(self):
        """ Initialise the bind for unittest"""
        self._bind = None
        self.unittest_transaction = None
        if self.unittest:
            self.unittest_bind = self.engine.connect()
            self.unittest_transaction = self.bind.begin()

    @property
    def bind(self):
        """ Return the bind in function of engine"""
        if not self._bind:
            if self.unittest:
                self._bind = self.unittest_bind
            else:
                self._bind = self.engine

        return self._bind

    @property
    def engine(self):
        """Return the engine"""
        if not self._engine:
            self._engine = self.get_engine_for(ro=self.loadwithoutmigration)

        return self._engine

    def create_session_factory(self):
        """Overwrite the creation of Session factory to Use the multi binding
        """
        if self.Session is None or self.must_recreate_session_factory():
            query_bases = [] + self.loaded_cores['Query']
            query_bases += [self.registry_base]
            Query = type('Query', tuple(query_bases), {})
            session_bases = [self.registry_base, MixinSession]
            session_bases.extend(self.loaded_cores['Session'])
            Session = type('Session', tuple(session_bases), {
                'registry_query': Query})

            self.session_connection = None
            if self.Session:
                self.session_connection = self.connection()

            extension = self.additional_setting.get('sa.session.extension')
            if extension:
                extension = extension()

            self.Session = scoped_session(
                sessionmaker(class_=Session, extension=extension),
                EnvironmentManager.scoped_function_for_session())
            self.nb_query_bases = len(self.loaded_cores['Query'])
            self.nb_session_bases = len(self.loaded_cores['Session'])
        else:
            self.flush()

    def commit(self, *args, **kwargs):
        super(MultiEngines, self).commit(*args, **kwargs)
        self.session_connection = None

    def close(self):
        """Overwrite close to cloe all the engines"""
        self.close_session()
        for engine in self.engines['ro']:
            engine.dispose()

        if self.engines['wo']:
            self.engines['wo'].dispose()

        if self.db_name in RegistryManager.registries:
            del RegistryManager.registries[self.db_name]

    @classmethod
    def db_exists(cls, db_name=None):
        if not db_name:
            raise RegistryException('db_name is required')

        urls = []
        url = Configuration.get('db_url')
        if url:
            urls.append(url)

        wo_url = Configuration.get('db_wo_url')
        if wo_url:
            urls.append(wo_url)

        for ro_url in Configuration.get('db_ro_urls', []) or []:
            urls.append(ro_url)

        gurl = Configuration.get('get_url', get_url)
        for url in urls:
            url = gurl(db_name=db_name, url=url)
            if not database_exists(url):
                return False
        else:
            return database_exists(gurl(db_name=db_name))

        return True


class RegistryMultiEngines(MultiEngines, Registry):
    """Pluging class"""
