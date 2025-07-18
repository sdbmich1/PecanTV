# -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
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
"""Helpers for flags in commands working with Anthos Multi-Cloud on Attached."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import arg_parsers


def AddPlatformVersion(parser, required=True):
  """Adds platform version flag.

  Args:
    parser: The argparse.parser to add the arguments to.
    required: Indicates if the flag is required.
  """

  help_text = """
Platform version to use for the cluster.

To retrieve a list of valid versions, run:

  $ gcloud alpha container attached get-server-config --location=LOCATION

Replace ``LOCATION'' with the target Google Cloud location for the cluster.
"""

  parser.add_argument('--platform-version', required=required, help=help_text)


def GetPlatformVersion(args):
  return getattr(args, 'platform_version', None)


def AddIssuerUrl(parser, required=False):
  parser.add_argument(
      '--issuer-url',
      required=required,
      help='Issuer url of the cluster to attach.',
  )


def GetIssuerUrl(args):
  return getattr(args, 'issuer_url', None)


def AddOidcJwks(parser):
  parser.add_argument('--oidc-jwks', help='OIDC JWKS of the cluster to attach.')


def GetOidcJwks(args):
  return getattr(args, 'oidc_jwks', None)


def AddHasPrivateIssuer(parser):
  help_text = """Indicates no publicly routable OIDC discovery endpoint exists
for the Kubernetes service account token issuer.

If this flag is set, gcloud will read the issuer URL and JWKs from the cluster's
api server.
"""
  parser.add_argument(
      '--has-private-issuer', help=help_text, action='store_true'
  )


def GetHasPrivateIssuer(args):
  return getattr(args, 'has_private_issuer', None)


def AddOidcConfig(parser):
  """Adds Oidc Config flags.

  Args:
    parser: The argparse.parser to add the arguments to.
  """

  group = parser.add_group('OIDC config', required=True)
  AddIssuerUrl(group, required=True)
  AddOidcJwks(group)


def AddRegisterOidcConfig(parser):
  group = parser.add_mutually_exclusive_group('OIDC config', required=True)
  AddIssuerUrl(group)
  AddHasPrivateIssuer(group)


def AddDistribution(parser, required=False):
  help_text = """
Set the base platform type of the cluster to attach.

Examples:

  $ {command} --distribution=aks
  $ {command} --distribution=eks
  $ {command} --distribution=generic
"""
  parser.add_argument('--distribution', required=required, help=help_text)


def GetDistribution(args):
  return getattr(args, 'distribution', None)


def AddAdminUsersForUpdate(parser):
  """Adds admin user configuration flags for update.

  Args:
    parser: The argparse.parser to add the arguments to.
  """

  group = parser.add_group('Admin users', mutex=True)
  AddAdminUsers(group)
  AddClearAdminUsers(group)


def AddAdminUsers(parser):
  help_txt = """
Users that can perform operations as a cluster administrator.
"""

  parser.add_argument(
      '--admin-users',
      type=arg_parsers.ArgList(),
      metavar='USER',
      required=False,
      help=help_txt,
  )


def AddClearAdminUsers(parser):
  """Adds flag for clearing admin users.

  Args:
    parser: The argparse.parser to add the arguments to.
  """

  parser.add_argument(
      '--clear-admin-users',
      action='store_true',
      default=None,
      help='Clear the admin users associated with the cluster',
  )


def GetAdminUsers(args):
  if not hasattr(args, 'admin_users'):
    return None
  if args.admin_users:
    return args.admin_users
  return None


def AddKubectl(parser):
  group = parser.add_group('kubectl config', required=True)
  AddKubeconfig(group)
  AddContext(group)


def AddKubeconfig(parser):
  help_txt = """Path to the kubeconfig file.

If not provided, the default at ~/.kube/config will be used.
"""
  parser.add_argument('--kubeconfig', help=help_txt)


def GetKubeconfig(args):
  return getattr(args, 'kubeconfig', None)


def AddContext(parser):
  help_txt = """Context to use in the kubeconfig."""
  parser.add_argument('--context', required=True, help=help_txt)


def GetContext(args):
  return getattr(args, 'context', None)


def AddProxySecretName(parser, required=False):
  help_txt = """
Name of the Kubernetes secret that contains the HTTP/HTTPS
proxy configuration.
"""
  parser.add_argument(
      '--proxy-secret-name',
      required=required,
      help=help_txt,
  )


def GetProxySecretName(args):
  return getattr(args, 'proxy_secret_name', None)


def AddProxySecretNamespace(parser, required=False):
  help_txt = """
Namespace of the Kubernetes secret that contains the HTTP/HTTPS
proxy configuration.
"""
  parser.add_argument(
      '--proxy-secret-namespace',
      required=required,
      help=help_txt,
  )


def GetProxySecretNamespace(args):
  return getattr(args, 'proxy_secret_namespace', None)


def AddProxyConfig(parser):
  """Adds Proxy Config flags.

  Args:
    parser: The argparse.parser to add the arguments to.
  """

  group = parser.add_group('Proxy config', required=False)
  AddProxySecretName(group, required=True)
  AddProxySecretNamespace(group, required=True)


def AddSkipClusterAdminCheck(parser):
  """Adds --skip-cluster-admin-check flag to parser.

  Args:
    parser: The argparse.parser to add the arguments to.
  """
  help_text = """\
When this hidden flag is set, the cluster admin check will be skipped.
"""
  parser.add_argument(
      '--skip-cluster-admin-check',
      hidden=True,
      help=help_text,
      action='store_true',
  )


def GetSkipClusterAdminCheck(args):
  return getattr(args, 'skip_cluster_admin_check', None)


def AddSystemComponentLabels(parser):
  """Adds --system-component-labels flag to parser.

  Args:
    parser: The argparse.parser to add the arguments to.
  """
  help_text = """\
Kubernetes labels to be applied to system component pods.
"""
  parser.add_argument(
      '--system-component-labels',
      help=help_text,
      type=arg_parsers.ArgDict(),
      metavar='LABEL',
  )


def GetSystemComponentLabels(args):
  return getattr(args, 'system_component_labels', None)


def AddSystemComponentTolerations(parser):
  """Adds --system-component-tolerations flag to parser.

  Args:
    parser: The argparse.parser to add the arguments to.
  """
  help_text = """\
Kubernetes tolerations to be applied to system component pods.
"""
  parser.add_argument(
      '--system-component-tolerations',
      type=arg_parsers.ArgList(),
      help=help_text,
      metavar='TOLERATION',
  )


def GetSystemComponentTolerations(args):
  tolerations = getattr(args, 'system_component_tolerations', None)
  if tolerations:
    tol = [ParseSystemComponentToleration(t) for t in tolerations]
    return tol
  return None


def ParseSystemComponentToleration(toleration):
  """Parses a system component toleration string.

  Args:
    toleration: The toleration string to parse.

  Returns:
    A list of (key, value, operator, effect).
  """
  parts = toleration.split(':')
  if len(parts) != 3:
    raise ValueError(
        'System component toleration must be in the format of'
        ' key=value:operator:effect, key:operator:effect, or :operator:effect,'
        ' got %s' % toleration
    )
  if not parts[0]:
    return ['', '', parts[1], parts[2]]
  key_value = parts[0].split('=')
  if not key_value:
    return ['', '', parts[1], parts[2]]
  elif len(key_value) == 1:
    return [key_value[0], '', parts[1], parts[2]]
  elif len(key_value) == 2:
    return [key_value[0], key_value[1], parts[1], parts[2]]
  else:
    raise ValueError(
        'System component toleration must be in the format of'
        ' key=value:operator:effect, key:operator:effect, or :operator:effect,'
        ' got %s' % toleration
    )
