import json
from typing import Any
from dask_cloudprovider.generic.vmcluster import (
    WorkerMixin,
)
from distributed.worker import Worker as _Worker
from distributed.utils import cli_keywords
from fly_dask.machine import FlyMachine


class FlyMachineWorker(WorkerMixin, FlyMachine):
    """Worker running on a Fly.io Machine."""

    def __init__(
        self,
        *args: Any,
        worker_module: str | None = None,
        worker_class: str | None = None,
        worker_options: dict[str, Any] = {},
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        if worker_module is not None:
            self.worker_module = worker_module
            self.command = [
                "python",
                "-m",
                self.worker_module,
                self.scheduler,
                "--name",
                str(self.name),
            ] + cli_keywords(worker_options, cls=_Worker, cmd=self.worker_module)
        if worker_class is None:
            raise ValueError("worker_class must be provided")
        else:
            self.worker_class = worker_class
            self.command = [
                "python",
                "-m",
                "distributed.cli.dask_spec",
                self.scheduler,
                "--spec",
                json.dumps(
                    {
                        "cls": self.worker_class,
                        "opts": {
                            **worker_options,
                            "name": self.name,
                            "host": "fly-local-6pn",
                        },
                    }
                ),
            ]
