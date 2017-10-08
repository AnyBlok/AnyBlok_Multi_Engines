# This file is a part of the AnyBlok Multi Engines project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# flake8: noqa
from anyblok.blok import Blok


class Test1Blok(Blok):
    version = '1.0.0'
    author = "Suzanne Jean-Sébastien"
    required = [
        'anyblok-core',
    ]


    @classmethod
    def import_declaration_module(cls):
        from . import test  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import test
        reload(test)
