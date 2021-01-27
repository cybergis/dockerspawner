import os
from traitlets import Unicode, Any
from .dockerspawner import DockerSpawner


async def pre_spawn_create_folder_in_hub_container(spawner):

    auth_state = await spawner.user.get_auth_state()
    spawner.log.info('pre_spawn_create_folder_in_hub_container auth_state:%s' % auth_state)
    # storage_base_path_in_hub_container should be mounted at hub in yml
    storage_base_path_in_hub_container = spawner.storage_base_path_in_hub_container
    user_folder = os.path.join(storage_base_path_in_hub_container, spawner.template_namespace()["safe_username"])
    spawner.environment["KERNEL_SAFE_USERNAME"] = spawner.template_namespace()["safe_username"]

    try:
        # create a user folder in hub container
        # which will be mounted to /home/jovyan/work in notebook container
        spawner.log.info("Trying to create folder {} in hub container".format(user_folder))
        os.makedirs(user_folder)
        os.chmod(user_folder, 0o777)
    except Exception as e:
        spawner.log.info(e)
        spawner.log.warning("Could not create folder {} in hub container".format(user_folder))

    try:
        # copy example notebooks to user_folder/examples/ in hub container
        # so they can be accessed later at /home/jovyan/work/examples in notebook container

        # example notebooks folder should be mounted in hub container in yml
        example_folder_path_in_hub = "/mnt/notebooks"
        if os.path.isdir(example_folder_path_in_hub):
            example_folder = os.path.join(user_folder, "examples")
            os.system('mkdir -p {}'.format(example_folder))
            # example notebooks folder should be mounted in hub container at /mnt/notebooks
            os.system('cp -n -r /mnt/notebooks/* {}'.format(example_folder))
            # even inside jupyterhub container uses Root to perform
            # on a NFS mount Root is treated as nobody:nogroup
            # whose premission is not sufficient to change ownership
            # os.system('chown -R 1000:100 {}'.format(example_folder)
            # but can change mode
            os.system('chmod -R 777 {}'.format(example_folder))
    except Exception as ex:
        spawner.log.info(ex)
        spawner.log.warning("Could not copy example folder")

    try:
        # Save HydroShare OAuth token at user_folder/.hs_auth in hub container
        # So later it can be accessed at /home/jovyan/work/.hs_auth in notebook container

        if "HS_AUTH" in spawner.environment:
            hs_auth = os.path.join(user_folder, '.hs_auth')
            with open(hs_auth, "w") as f:
                f.write(spawner.environment["HS_AUTH"])
            os.system('chmod -R 777 {}'.format(hs_auth))
            spawner.log.info("Saved HS Auth at {}".format(hs_auth))
    except Exception as ex:
        spawner.log.info(ex)
        spawner.log.warning("Failed to save HS Auth to file")


class DockerSpawner_CyberGIS(DockerSpawner):

    storage_base_path_in_hub_container = Unicode(default_value="/var/nfs").tag(config=True)

    pre_spawn_hook = Any(
        default_value=pre_spawn_create_folder_in_hub_container
    ).tag(config=True)

