from typing import TYPE_CHECKING, Any
import dask
import asyncio
from dask_cloudprovider.generic.vmcluster import (
    VMInterface,
)

from fly_dask.socket import is_socket_open
from fly_dask.sdk.constants import MachineSize
from fly_dask.sdk.models import machines
from fly_dask.sdk.fly import Fly

if TYPE_CHECKING:
    from fly_dask.cluster import FlyMachineCluster


class FlyMachine(VMInterface):
    def __init__(
        self,
        cluster: "FlyMachineCluster",
        image: str,
        config: dict[str, Any] | None = None,
        region: str | None = None,
        vm_size: MachineSize | None = None,
        cpus: int = 1,
        memory_mb: int = 256,
        env_vars: dict[str, str] = {},
        metadata: dict[str, str] | None = None,
        restart: dict[str, str] | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)  # type: ignore
        self.app = None
        self.machine = None
        self.cluster = cluster
        self.config = config
        self.region = region
        self.vm_size = vm_size
        self.cpus = cpus
        self.memory_mb = memory_mb
        self.image = image
        self.gpu_instance = False
        self.bootstrap = True
        self.env_vars = env_vars
        self.metadata = metadata
        self.restart = restart
        self.app_name = self.cluster.app_name
        self.env_vars["DASK_INTERNAL__INHERIT_CONFIG"] = dask.config.serialize(
            dask.config.global_config
        )
        self.api_token = self.cluster.api_token
        self._client = None

    async def create_vm(self):
        machine_config = machines.FlyMachineConfig(
            env=self.env_vars,
            image=self.image,
            metadata=self.metadata,
            restart=self.restart,
            init=machines.FlyMachineConfigInit(entrypoint=self.command),
            services=[
                machines.FlyMachineConfigServices(
                    ports=[
                        machines.FlyMachineRequestConfigServicesPort(port=8786),
                    ],
                    protocol="tcp",
                    internal_port=8786,
                ),
                machines.FlyMachineConfigServices(
                    ports=[
                        machines.FlyMachineRequestConfigServicesPort(
                            port=80, handlers=["http"]
                        ),
                        machines.FlyMachineRequestConfigServicesPort(
                            port=443, handlers=["http", "tls"]
                        ),
                        machines.FlyMachineRequestConfigServicesPort(
                            port=8787, handlers=["http", "tls"]
                        ),
                    ],
                    protocol="tcp",
                    internal_port=8787,
                ),
            ],
            guest=machines.FlyMachineConfigGuest(
                cpu_kind="shared",
                cpus=self.cpus,
                memory_mb=self.memory_mb,
            ),
            metrics=None,
            processes=[
                machines.FlyMachineConfigProcess(
                    name="app",
                    cmd=self.command,
                    env=self.env_vars,
                )
            ],
        )
        self.machine = await self._fly().create_machine(
            app_name=self.cluster.app_name,  # The name of the new Fly.io app.
            config=machine_config,  # A FlyMachineConfig object containing creation details.
            name=self.name,  # The name of the machine.
            region=self.region,  # The deployment region for the machine.
        )
        self.host = f"{self.machine.id}.vm.{self.cluster.app_name}.internal"
        self.internal_ip = self.machine.private_ip
        self.port = 8786
        self.address = (
            f"{self.cluster.protocol}://[{self.machine.private_ip}]:{self.port}"
        )
        # self.external_address = f"{self.cluster.protocol}://{self.host}:{self.port}"
        log_attributes = {
            "name": self.name,
            "machine": self.machine.id,
            "internal_ip": self.internal_ip,
            "address": self.address,
        }
        if self.external_address is not None:
            log_attributes["external_address"] = self.external_address
        logline = "[fly.io] Created machine " + " ".join(
            [f"{k}={v}" for k, v in log_attributes.items()]
        )
        self.cluster._log(logline)
        return self.address, self.external_address

    async def destroy_vm(self):
        if self.machine is None:
            self.cluster._log(
                "[fly.io] Not Terminating Machine: Machine does not exist"
            )
            return
        await self._fly().delete_machine(
            app_name=self.cluster.app_name,
            machine_id=self.machine.id,
            force=True,
        )
        self.cluster._log(f"[fly.io] Terminated machine {self.name}")

    async def wait_for_scheduler(self) -> None:
        self.cluster._log(f"Waiting for scheduler to run at {self.address}")
        while not await is_socket_open(self.internal_ip, self.port):
            await asyncio.sleep(1)
        self.cluster._log("Scheduler is running")

    # async def wait_for_app(self) -> None:
    #     self.cluster._log("[fly.io] Waiting for app to be created...")
    #     while self.app is None:
    #         await asyncio.sleep(1)

    def _fly(self):
        if self._client is None:
            self._client = Fly(api_token=self.api_token)
        return self._client
