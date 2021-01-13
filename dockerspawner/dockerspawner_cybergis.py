import os
from traitlets import Unicode, Any
from .dockerspawner import DockerSpawner


async def pre_spawn_create_folder_in_hub_container(spawner):

    auth_state = await spawner.user.get_auth_state()

    spawner.log.error('pre_spawn_start auth_state:%s' % auth_state)
    parent_folder = auth_state.get("parent_folder", "")
    spawner.parent_folder = parent_folder

    try:
        storage_base_path_in_hub_container = spawner.storage_base_path_in_hub_container
        folder = os.path.join(storage_base_path_in_hub_container, parent_folder, spawner.user.name)
        spawner.log.info("Trying to create folder {} in JupyterHub container".format(folder))
        os.makedirs(folder)
        os.chmod(folder, 0o777)
    except OSError as e:
        spawner.log.info(e)
        spawner.log.info("Could not create folder {} in JupyterHub container".format(folder))


class DockerSpawner_CyberGIS(DockerSpawner):

    storage_base_path_in_hub_container = Unicode(default_value="/var/nfs")
    parent_folder = Unicode(default_value="")

    pre_spawn_hook = Any(
        default_value=pre_spawn_create_folder_in_hub_container
    ).tag(config=True)

    def template_namespace(self):
        template_namespace_dict = super().template_namespace()
        template_namespace_dict["parent_folder"] = self.parent_folder + "/"
        return template_namespace_dict
