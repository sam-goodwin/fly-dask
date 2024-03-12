# fly-dask

This is an experimental implementation of a Dask Cluster on [fly.io](https://fly.io).

# Setup 

0. You'll need to set up a [fly.io](https://fly.io) account if you haven't already.
1. Log into your Fly.io CLI
```sh
fly auth login
```

2. Install [WireGuard](https://www.wireguard.com/install/) for proxy connections.

3. Create a wireguard config.
```sh
fly wireguard create
```

> [!NOTE]
> You will be asked to specify a location to store. We recommend `./wireguard.conf`.

4. User the Wireguard CLI to import the wireguard.conf file you created. You are now connected to your fly.io organization's network.

5. Get a

5. Add a `.env` file to the root of your repo.
```toml
FLY_TOKEN={your token value here}
```
6. Create a python file with the following code

```py
from dask.distributed import Client
from dotenv import load_dotenv
from fly_dask import FlyMachineCluster
from fly_dask.sdk.constants import FlyRegion, MachineSize
import dask
import dask.array as da
import os

# load the .env environment variables
load_dotenv()

# we need the FLY_TOKEN to authenticate to the Fly service
FLY_TOKEN = os.environ["FLY_TOKEN"]
if not FLY_TOKEN:
    raise ValueError("FLY_TOKEN is required")

# create a fly cluster, this will boot up a scheduler and single worker
cluster = FlyMachineCluster(
    "packyak-test",
    api_token=FLY_TOKEN,
    n_workers=1,
    cpus=8,
    memory_mb=16 * 1024,
    vm_size=MachineSize.PERFORMANCE_16X,
    image="registry.fly.io/packyak-test:test",
    region=FlyRegion.IAD,
)
client = Client(cluster)
print(f"Dashboard: {cluster.dashboard_link}")

# e.g. scale out to 30 instances
cluster.scale(30)
# e.g. scale nack down to 1
cluster.scale(1)
# e.g. configure adaptive scaling
cluster.adapt(minimum=1, maximum=64)

# Build and Compute your Dask graph here
arr = da.random.random((1000, 1000), chunks=(100, 100))
mean = arr.mean().compute()
print(mean)

# Shutdown the cluster (this will destroy the machines)

client.close()
cluster.close()
```