# fly-dask

This is an experimental implementation of a Dask Cluster on [fly.io](https://fly.io). It de

# Setup 

Clone this repo an

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

5. Store your fly auth token in the `.env`
```sh
token=$(fly auth token)
echo "FLY_TOKEN=$token" >> .env
```

6. Open the [example.ipynb](./example.ipynb) Notebook to try it out. 