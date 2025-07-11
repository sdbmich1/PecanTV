# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Resource definitions for Cloud Platform Apis generated from apitools."""

import enum


BASE_URL = 'https://edgecontainer.googleapis.com/v1alpha/'
DOCS_URL = 'https://cloud.google.com/edge-cloud'


class Collections(enum.Enum):
  """Collections for all supported apis."""

  ORGANIZATIONS = (
      'organizations',
      'organizations/{organizationsId}',
      {},
      ['organizationsId'],
      True
  )
  ORGANIZATIONS_LOCATIONS = (
      'organizations.locations',
      '{+name}',
      {
          '':
              'organizations/{organizationsId}/locations/{locationsId}',
      },
      ['name'],
      True
  )
  ORGANIZATIONS_LOCATIONS_IDENTITYPROVIDERS = (
      'organizations.locations.identityProviders',
      '{+name}',
      {
          '':
              'organizations/{organizationsId}/locations/{locationsId}/'
              'identityProviders/{identityProvidersId}',
      },
      ['name'],
      True
  )
  ORGANIZATIONS_LOCATIONS_OPERATIONS = (
      'organizations.locations.operations',
      '{+name}',
      {
          '':
              'organizations/{organizationsId}/locations/{locationsId}/'
              'operations/{operationsId}',
      },
      ['name'],
      True
  )
  ORGANIZATIONS_LOCATIONS_ZONES = (
      'organizations.locations.zones',
      '{+name}',
      {
          '':
              'organizations/{organizationsId}/locations/{locationsId}/zones/'
              '{zonesId}',
      },
      ['name'],
      True
  )
  ORGANIZATIONS_LOCATIONS_ZONES_ZONALPROJECTS = (
      'organizations.locations.zones.zonalProjects',
      '{+name}',
      {
          '':
              'organizations/{organizationsId}/locations/{locationsId}/zones/'
              '{zonesId}/zonalProjects/{zonalProjectsId}',
      },
      ['name'],
      True
  )
  PROJECTS = (
      'projects',
      'projects/{projectsId}',
      {},
      ['projectsId'],
      True
  )
  PROJECTS_LOCATIONS = (
      'projects.locations',
      '{+name}',
      {
          '':
              'projects/{projectsId}/locations/{locationsId}',
      },
      ['name'],
      True
  )
  PROJECTS_LOCATIONS_CLUSTERS = (
      'projects.locations.clusters',
      '{+name}',
      {
          '':
              'projects/{projectsId}/locations/{locationsId}/clusters/'
              '{clustersId}',
      },
      ['name'],
      True
  )
  PROJECTS_LOCATIONS_CLUSTERS_NODEPOOLS = (
      'projects.locations.clusters.nodePools',
      '{+name}',
      {
          '':
              'projects/{projectsId}/locations/{locationsId}/clusters/'
              '{clustersId}/nodePools/{nodePoolsId}',
      },
      ['name'],
      True
  )
  PROJECTS_LOCATIONS_MACHINES = (
      'projects.locations.machines',
      '{+name}',
      {
          '':
              'projects/{projectsId}/locations/{locationsId}/machines/'
              '{machinesId}',
      },
      ['name'],
      True
  )
  PROJECTS_LOCATIONS_OPERATIONS = (
      'projects.locations.operations',
      '{+name}',
      {
          '':
              'projects/{projectsId}/locations/{locationsId}/operations/'
              '{operationsId}',
      },
      ['name'],
      True
  )
  PROJECTS_LOCATIONS_SERVICEACCOUNTS = (
      'projects.locations.serviceAccounts',
      '{+name}',
      {
          '':
              'projects/{projectsId}/locations/{locationsId}/serviceAccounts/'
              '{serviceAccountsId}',
      },
      ['name'],
      True
  )
  PROJECTS_LOCATIONS_VPNCONNECTIONS = (
      'projects.locations.vpnConnections',
      '{+name}',
      {
          '':
              'projects/{projectsId}/locations/{locationsId}/vpnConnections/'
              '{vpnConnectionsId}',
      },
      ['name'],
      True
  )
  PROJECTS_LOCATIONS_ZONALSERVICES = (
      'projects.locations.zonalServices',
      '{+name}',
      {
          '':
              'projects/{projectsId}/locations/{locationsId}/zonalServices/'
              '{zonalServicesId}',
      },
      ['name'],
      True
  )
  PROJECTS_LOCATIONS_ZONES = (
      'projects.locations.zones',
      'projects/{projectsId}/locations/{locationsId}/zones/{zonesId}',
      {},
      ['projectsId', 'locationsId', 'zonesId'],
      True
  )

  def __init__(self, collection_name, path, flat_paths, params,
               enable_uri_parsing):
    self.collection_name = collection_name
    self.path = path
    self.flat_paths = flat_paths
    self.params = params
    self.enable_uri_parsing = enable_uri_parsing
