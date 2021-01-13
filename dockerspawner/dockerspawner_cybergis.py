import os
from traitlets import Unicode, Any
from .dockerspawner import DockerSpawner


async def pre_spawn_create_folder_in_hub_container(spawner):

    auth_state = await spawner.user.get_auth_state()
    spawner.log.info('pre_spawn_create_folder_in_hub_container auth_state:%s' % auth_state)

    try:
        storage_base_path_in_hub_container = spawner.storage_base_path_in_hub_container
        folder = os.path.join(storage_base_path_in_hub_container, spawner.template_namespace()["safe_username"])
        spawner.log.info("Trying to create folder {} in hub container".format(folder))
        os.makedirs(folder)
        os.chmod(folder, 0o777)
    except Exception as e:
        spawner.log.info(e)
        spawner.log.error("Could not create folder {} in hub container".format(folder))


class DockerSpawner_CyberGIS(DockerSpawner):

    storage_base_path_in_hub_container = Unicode(default_value="/var/nfs")

    pre_spawn_hook = Any(
        default_value=pre_spawn_create_folder_in_hub_container
    ).tag(config=True)

