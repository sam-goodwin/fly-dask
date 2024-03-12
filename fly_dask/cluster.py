from typing import Any, cast
import dask
from dask_cloudprovider.generic.vmcluster import (
    VMCluster,
)
from fly_dask.scheduler import FlyMachineScheduler
from fly_dask.sdk.constants import FlyRegion, GPUKind, MachineSize
from fly_dask.worker import FlyMachineWorker


class FlyMachineCluster(VMCluster):
    """Cluster running on Fly.io Machines.

    VMs in Fly.io (FLY) are referred to as machines. This cluster manager constructs a Dask cluster
    running on VMs.

    .. note::
        By default, the cluster will instantiate a new Fly.io app. The app will be deleted when
        the cluster is closed. If you want to use an existing app, you can pass the app name to the
        ``app_name`` parameter.

    When configuring your cluster you may find it useful to install the ``flyctl`` tool for querying the
    CLY API for available options.

    https://fly.io/docs/hands-on/install-flyctl/

    Parameters
    ----------
    region: str
        The FLY region to launch your cluster in. A full list can be obtained with ``flyctl platform regions``.
    vm_size: str
        The VM size slug. You can get a full list with ``flyctl platform sizes``.
        The default is ``shared-cpu-1x`` which is 256GB RAM and 1 vCPU
    image: str
        The Docker image to run on all instances.

        This image must have a valid Python environment and have ``dask`` installed in order for the
        ``dask-scheduler`` and ``dask-worker`` commands to be available. It is recommended the Python
        environment matches your local environment where ``FlyMachineCluster`` is being created from.

        By default the ``ghcr.io/dask/dask:latest`` image will be used.
    worker_module: str
        The Dask worker module to start on worker VMs.
    n_workers: int
        Number of workers to initialise the cluster with. Defaults to ``0``.
    worker_module: str
        The Python module to run for the worker. Defaults to ``distributed.cli.dask_worker``
    worker_options: dict
        Params to be passed to the worker class.
        See :class:`distributed.worker.Worker` for default worker class.
        If you set ``worker_module`` then refer to the docstring for the custom worker class.
    scheduler_options: dict
        Params to be passed to the scheduler class.
        See :class:`distributed.scheduler.Scheduler`.
    extra_bootstrap: list[str] (optional)
        Extra commands to be run during the bootstrap phase.
    env_vars: dict (optional)
        Environment variables to be passed to the worker.
    silence_logs: bool
        Whether or not we should silence logging when setting up the cluster.
    asynchronous: bool
        If this is intended to be used directly within an event loop with
        async/await
    security : Security or bool, optional
        Configures communication security in this cluster. Can be a security
        object, or True. If True, temporary self-signed credentials will
        be created automatically. Default is ``False``.
    debug : bool, optional
        More information will be printed when constructing clusters to enable debugging.

    Examples
    --------

    Create the cluster.

    >>> from dask_cloudprovider.fly import FlyMachineCluster
    >>> cluster = FlyMachineCluster(n_workers=1)
    Starting scheduler on dask-e058d78e-scheduler
    [fly.io] Trying to create app dask-122f0e5f
    [fly.io] Created app dask-122f0e5f
    Creating scheduler instance
    [fly.io] Created machine name=dask-e058d78e-scheduler id=6e82d4e6a02d58
    Waiting for scheduler to run at 6e82d4e6a02d58.vm.dask-122f0e5f.internal:8786
    Scheduler is running
    Scheduler running at tcp://[fdaa:1:53b:a7b:112:2bed:ccd1:2]:8786
    Creating worker instance
    [fly.io] Created machine name=dask-e058d78e-worker-7b24cb61 id=32873e0a095985

    Connect a client.

    >>> from dask.distributed import Client
    >>> client = Client(cluster)

    Do some work.

    >>> import dask.array as da
    >>> arr = da.random.random((1000, 1000), chunks=(100, 100))
    >>> arr.mean().compute()
    0.5001550986751964

    Close the cluster

    >>> client.close()
    >>> cluster.close()
    [fly.io] Terminated machine dask-e058d78e-worker-7b24cb61
    [fly.io] Terminated machine dask-e058d78e-scheduler
    [fly.io] Deleted app dask-122f0e5f

    You can also do this all in one go with context managers to ensure the cluster is
    created and cleaned up.

    >>> with FlyMachineCluster(n_workers=1) as cluster:
    ...     with Client(cluster) as client:
    ...         print(da.random.random((1000, 1000), chunks=(100, 100)).mean().compute())
    Starting scheduler on dask-e058d78e-scheduler
    [fly.io] Trying to create app dask-122f0e5f
    [fly.io] Created app dask-122f0e5f
    Creating scheduler instance
    [fly.io] Created machine name=dask-e058d78e-scheduler id=6e82d4e6a02d58
    Waiting for scheduler to run at 6e82d4e6a02d58.vm.dask-122f0e5f.internal:8786
    Scheduler is running
    Scheduler running at tcp://[fdaa:1:53b:a7b:112:2bed:ccd1:2]:8786
    Creating worker instance
    [fly.io] Created machine name=dask-e058d78e-worker-7b24cb61 id=32873e0a095985
    0.5000558682356162
    [fly.io] Terminated machine dask-e058d78e-worker-7b24cb61
    [fly.io] Terminated machine dask-e058d78e-scheduler
    [fly.io] Deleted app dask-122f0e5f

    """

    def __init__(
        self,
        app_name: str,
        api_token: str,
        image: str,
        region: FlyRegion,
        vm_size: MachineSize | None = None,
        memory_mb: int = 512,
        cpus: int = 1,
        gpus: int = 0,
        gpu_kind: GPUKind = "a100-pcie-40gb",
        debug: bool = False,
        **kwargs: Any,
    ):
        self.config = dask.config.get("cloudprovider.fly", {})
        self.scheduler_class = FlyMachineScheduler
        self.worker_class = FlyMachineWorker
        self.debug = debug
        self.app_name = app_name
        self._client = None
        self.options = {
            "cluster": self,
            "config": self.config,
            "region": region.value,
            "vm_size": vm_size.value
            if vm_size is not None
            else self.config.get("vm_size"),
            "image": image,
            "token": api_token,
            "memory_mb": memory_mb,
            "cpus": cpus,
            "gpus": gpus,
            "gpu_kind": gpu_kind,
            "app_name": self.app_name,
            "protocol": self.config.get("protocol", "tcp"),
            "security": self.config.get("security", False),
            "host": "fly-local-6pn",
        }
        self.worker_options = {
            **self.options,
            "gpus": gpus,
            "gpu_kind": gpu_kind,
        }
        self.api_token = cast(str, self.options["token"])
        self.security = cast(bool, self.options["security"])
        super().__init__(
            debug=debug,
            security=self.security,
            worker_options={**self.options},
            scheduler_options={**self.options},
            **kwargs,
        )

    @property
    def dashboard_link(self) -> str:
        """Return the URL of the Dask dashboard."""
        import re

        host = re.search(r"tcp://\[([^\]]+)\]", self.scheduler.address).group(1)  # type: ignore
        return f"http://[{host}]:8787/status"
