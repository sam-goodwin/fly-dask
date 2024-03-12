from typing import TYPE_CHECKING, Any, TypedDict
import asyncio
from dask_cloudprovider.generic.vmcluster import (
    SchedulerMixin,
)
from distributed.core import Status
from distributed.scheduler import Scheduler as _Scheduler
from distributed.utils import cli_keywords

from fly_dask.machine import FlyMachine

if TYPE_CHECKING:
    from fly_dask.cluster import FlyMachineCluster


class SchedulerOptions(TypedDict):
    cluster: "FlyMachineCluster"
    config: dict[str, Any]
    region: tuple[str, ...]
    vm_size: None
    image: str
    token: str
    memory_mb: int
    cpus: int
    app_name: str
    protocol: str
    security: bool
    host: str


class FlyMachineScheduler(SchedulerMixin, FlyMachine):
    """Scheduler running on a Fly.io Machine."""

    def __init__(
        self,
        *args: list[Any],
        scheduler_options: SchedulerOptions,
        **kwargs: Any,
    ):
        super().__init__(
            *args,
            **kwargs,
            cluster=scheduler_options["cluster"],
            image=scheduler_options["image"],
            config=scheduler_options["config"],
            region=scheduler_options["region"],
            vm_size=scheduler_options["vm_size"],
            cpus=scheduler_options["cpus"],
            memory_mb=scheduler_options["memory_mb"],
            # env_vars={
            #     "DASK_SCHEDULER__INHERIT_CONFIG": dask.config.serialize(
            #         dask.config.global_config
            #     )
            # },
        )
        self.name = f"dask-{self.cluster.uuid}-scheduler"
        self.port = scheduler_options.get("port", 8786)
        self.command = [
            "./.venv/bin/python",
            "-m",
            "distributed.cli.dask_scheduler",
            "--host",
            "fly-local-6pn",
        ]
        # + cli_keywords(
        #     {
        #         k: scheduler_options[k]
        #         for k in scheduler_options.keys()
        #         if k not in ["cluster", "config", "region"]
        #     },
        #     cls=_Scheduler,
        # )

    async def start(self):
        self.cluster._log(f"Starting scheduler on {self.name}")
        if not await self._fly().is_app_exists(self.app_name):
            await self.create_app()
        await self.start_scheduler()
        self.status = Status.running

    async def start_scheduler(self):
        self.cluster._log("Creating scheduler instance")
        address, external_address = await self.create_vm()
        await self.wait_for_scheduler()
        self.cluster._log(f"Scheduler running at {address}")
        self.cluster.scheduler_internal_address = address
        self.cluster.scheduler_external_address = external_address
        self.cluster.scheduler_port = self.port

    async def close(self):
        await super().close()
        # if self.cluster.app_name is not None:
        #     await self.delete_app()

    async def create_app(self):
        """Create a Fly.io app."""
        app_name = self.cluster.app_name
        try:
            self.cluster._log(f"[fly.io] Trying to create app {app_name}")
            self.app = await self._fly().create_app(app_name=app_name)
            self.cluster._log(f"[fly.io] Created app {app_name}")
        except Exception as e:
            self.cluster._log(f"[fly.io] Failed to create app {app_name}")
            self.app = "failed"
            raise e

    async def delete_app(self):
        """Delete a Fly.io app."""
        await self._fly().delete_app(app_name=self.cluster.app_name)
        self.cluster._log(f"[fly.io] Deleted app {self.cluster.app_name}")

    async def wait_for_app(self) -> None:
        """Wait for the Fly.io app to be ready."""
        while not await self._fly().is_app_exists(self.app_name):
            self.cluster._log("[fly.io] Waiting for app to be created")
            await asyncio.sleep(1)
