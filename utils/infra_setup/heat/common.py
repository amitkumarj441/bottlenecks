##############################################################################
# Copyright (c) 2016 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os
import logging

from keystoneauth1 import loading
from keystoneauth1 import session

log = logging.getLogger(__name__)

DEFAULT_HEAT_API_VERSION = '1'
DEFAULT_NOVA_API_VERSION = '2'
DEFAULT_GLANCE_API_VERSION = '2'


def get_credentials():
    """Returns a creds dictionary filled with parsed from env"""
    creds = {}

    keystone_api_version = os.getenv('OS_IDENTITY_API_VERSION')

    if keystone_api_version is None or keystone_api_version == '2':
        keystone_v3 = False
        tenant_env = 'OS_TENANT_NAME'
        tenant = 'tenant_name'
    else:
        keystone_v3 = True
        tenant_env = 'OS_PROJECT_NAME'
        tenant = 'project_name'

    # The most common way to pass these info to the script is to do it
    # through environment variables.
    creds.update({
        "username": os.environ.get("OS_USERNAME"),
        "password": os.environ.get("OS_PASSWORD"),
        "auth_url": os.environ.get("OS_AUTH_URL"),
        tenant: os.environ.get(tenant_env)
    })

    if keystone_v3:
        if os.getenv('OS_USER_DOMAIN_NAME') is not None:
            creds.update({
                "user_domain_name": os.getenv('OS_USER_DOMAIN_NAME')
            })
        if os.getenv('OS_PROJECT_DOMAIN_NAME') is not None:
            creds.update({
                "project_domain_name": os.getenv('OS_PROJECT_DOMAIN_NAME')
            })

    return creds


def get_session_auth():
    loader = loading.get_plugin_loader('password')
    creds = get_credentials()
    auth = loader.load_from_options(**creds)
    return auth


def get_session():
    auth = get_session_auth()
    try:
        cacert = os.environ['OS_CACERT']
    except KeyError:
        return session.Session(auth=auth)
    else:
        insecure = os.getenv('OS_INSECURE', '').lower() == 'true'
        cacert = False if insecure else cacert
        return session.Session(auth=auth, verify=cacert)


def get_endpoint(service_type, endpoint_type='publicURL'):
    auth = get_session_auth()
    return get_session().get_endpoint(auth=auth,
                                      service_type=service_type,
                                      endpoint_type=endpoint_type)


def get_heat_api_version():
    api_version = os.getenv('HEAT_API_VERSION')
    if api_version is not None:
        log.info("HEAT_API_VERSION is set in env as '%s'", api_version)
        return api_version
    return DEFAULT_HEAT_API_VERSION


def get_nova_api_version():
    api_version = os.getenv('OS_COMPUTE_API_VERSION')
    if api_version is not None:
        log.info("NOVA_API_VERSION is set in env as '%s'", api_version)
        return api_version
    return DEFAULT_NOVA_API_VERSION


def get_glance_api_version():
    api_version = os.getenv('OS_IMAGE_API_VERSION')
    if api_version is not None:
        log.info("GLANCE_API_VERSION is set in env as '%s'", api_version)
        return api_version
    return DEFAULT_GLANCE_API_VERSION
