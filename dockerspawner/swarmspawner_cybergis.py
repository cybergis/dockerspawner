from docker.errors import APIError
from tornado import gen
from .dockerspawner_cybergis import DockerSpawner_CyberGIS


class SwarmSpawner_CyberGIS(DockerSpawner_CyberGIS):

    # Drew: fix load-test failure
    # retry to find service with desired state
    # See another fix: https://github.com/jupyterhub/dockerspawner/issues/343
    @gen.coroutine
    def get_task(self):
        self.log.debug("Getting task of service '%s'", self.service_name)
        if self.get_object() is None:
            return None
        try:
            tasks = []
            count = 0
            dt = 1.0
            while len(tasks) == 0 and count < 5:
                tasks = yield self.docker(
                    "tasks",
                    filters={"service": self.service_name, "desired-state": "running"},
                )
                count += 1
                yield gen.sleep(dt)
                dt = min(dt * 1.5, 11)

            if len(tasks) == 0:
                self.log.error(
                    "Falied to find service {} with desired state {}".format(self.service_name, "running"))
                return None
            elif len(tasks) > 1:
                raise RuntimeError(
                    "Found more than one running notebook task for service '{}'".format(
                        self.service_name
                    )
                )
            task = tasks[0]
        except APIError as e:
            if e.response.status_code == 404:
                self.log.info("Task for service '%s' is gone", self.service_name)
                task = None
            else:
                self.log.error("SwarmSpawner_CyberGIS.get_task error 1: {}".format(e))
                raise
        except Exception as ex:
            self.log.error("SwarmSpawner_CyberGIS.get_task error 2: {}".format(ex))
            raise
        return task