# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from xml.etree import cElementTree as ET


ROLE = 'tagcreator'
VERSION_SCHEME = 'alphanumeric'
XMLNS = 'http://standards.iso.org/iso/19770/-2/2014/schema.xsd'


def _create_payload_tag(package_info):
    payload = ET.Element('Payload')
    for file_info in package_info.files:
        file_element = ET.SubElement(payload, 'File')
        file_element.set('name', file_info.name)
        file_element.set('location', file_info.location)

    return payload


def _create_unique_id(os_info, package_info, architecture):
    unique_id_format = '{os_info}-{architecture}-{pi.package}-{pi.version}'
    return unique_id_format.format(os_info=os_info,
                                   pi=package_info,
                                   architecture=architecture)


def _create_software_id(os_info, package_info, regid, architecture):
    return '{regid}_{uniqueID}'.format(
        regid=regid, uniqueID=_create_unique_id(os_info, package_info, architecture))


def create_swid_tags(environment, entity_name, regid, full=False, target=None):
    """
    Return SWID tags as xml strings for all available packages.

    Args:
        environment (swid_generator.environment.CommonEnvironment):
            The package management environment.
        entity_name (str):
            The SWID tag entity name.
        regid (str):
            The SWID tag regid.
        full (bool):
            Whether to include file payload. Default is False.
        target (str):
            Return only SWID tags whose software-id fully matches the given target. Default is False.

    Returns:
        A generator object for all available SWID XML strings.

    """
    os_info = environment.get_os_string()
    pkg_info = environment.get_list()

    for pi in pkg_info:
        # Check if the software-id of the current package matches the targeted request
        if target and _create_software_id(os_info, pi, regid, environment.get_architecture()) != target:
            continue

        software_identity = ET.Element('SoftwareIdentity')
        software_identity.set('xmlns', XMLNS)
        software_identity.set('name', pi.package)
        software_identity.set('uniqueId', _create_unique_id(os_info, pi, environment.get_architecture()))

        software_identity.set('version', pi.version)
        software_identity.set('versionScheme', VERSION_SCHEME)

        entity = ET.SubElement(software_identity, 'Entity')
        entity.set('name', entity_name)
        entity.set('regid', regid)
        entity.set('role', ROLE)

        if full:
            pi.files = environment.get_files_for_package(pi.package)
            payload_tag = _create_payload_tag(pi)
            software_identity.append(payload_tag)

        swidtag_flat = ET.tostring(software_identity, method='xml').replace('\n', '')
        yield swidtag_flat