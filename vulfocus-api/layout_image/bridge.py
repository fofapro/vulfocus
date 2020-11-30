"""
bridge to docker-compose
"""

import logging
from os.path import normpath
from compose import __version__ as compose_version
from compose.container import Container
from compose.cli.utils import get_version_info
from compose.cli.command import get_project as compose_get_project, get_config_path_from_options, get_config_from_options
from compose.config.config import get_default_config_files
from compose.config.environment import Environment

from compose.cli.docker_client import docker_client
from compose.const import API_VERSIONS, COMPOSEFILE_V3_0


logging.info(get_version_info('full'))


def ps_(project):
    """
    containers status
    """
    logging.info('ps ' + project.name)
    running_containers = project.containers(stopped=True)

    items = [{
        'name': container.name,
        'name_without_project': container.name_without_project,
        'command': container.human_readable_command,
        'state': container.human_readable_state,
        'labels': container.labels,
        'ports': container.ports,
        'volumes': get_volumes(get_container_from_id(project.client, container.id)),
        'is_running': container.is_running} for container in running_containers]

    return items


def get_container_from_id(my_docker_client, container_id):
    """
    return the docker container from a given id
    """
    return Container.from_id(my_docker_client, container_id)


def get_volumes(container):
    """
    retrieve container volumes details
    """
    mounts = container.get('Mounts')
    return [dict(source=mount['Source'], destination=mount['Destination']) for mount in mounts]


def get_yml_path(path):
    """
    get path of docker-compose.yml file
    """
    return get_default_config_files(path)[0]


def get_project(path):
    """
    get docker project given file path
    """
    logging.debug('get project ' + path)

    environment = Environment.from_env_file(path)
    config_path = get_config_path_from_options(path, dict(), environment)
    project = compose_get_project(path, config_path)
    return project


def containers():
    """
    active containers
    """
    return client().containers()


def info():
    """
    docker info
    """
    docker_info = client().info()
    return dict(compose=compose_version,info=docker_info['ServerVersion'], name=docker_info['Name'])


def client():
    """
    docker client
    """
    return docker_client(Environment(), API_VERSIONS[COMPOSEFILE_V3_0])


def project_config(path):
    """
    docker-compose config
    """
    norm_path = normpath(path)
    return get_config_from_options(norm_path, dict())
