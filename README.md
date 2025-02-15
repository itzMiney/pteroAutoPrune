# Ptero Auto Prune
This small handy tool lets you auto prune Pterodactyl Servers that have been offline for too long after a given threshold

## How to install
First make sure you have all the needed dependencies.
This tool only needs python and a couple python packages.
```sh
# Example on Debian or Ubuntu
sudo apt install python3 python3-pip
```

Once you made sure that python and pip are installed, we need to clone the repository:
```sh
cd ~
git clone https://github.com/itzminey/pteroAutoPrune.git
cd pteroAutoPrune
```

Now we'll install the required python packages:
```sh
pip install -r requirements.txt
```

Then, create the .env file:
```sh
cp example.env .env
nano .env
```

This file will look something like this:
```env
# API KEYS
APPLICATION_API_KEY="ptla_yourApplicationAPIkey"
CLIENT_API_KEY="ptlc_yourClientAPIkey"

#API ENDPOINT
PANEL_URL="https://panel.domain.com"

# CLEANUP CONFIG
CHECK_INTERVAL_SECONDS=300
# Default interval 5 minutes (300)
PURGE_THRESHOLD_SECONDS=604800
# Default threshold 7 days (604800)

#EXCEPTED SERVERS (UUIDs)
EXCEPTED_SERVERS="excepted-server-one,excepted-server-two"
```
Go to `https://panel.domain.com/admin/api` to get yourself an Application API Key for your panel.
For the CLient API Key you'll need to go onto your account settings in the panel and create one there.
Then you can set up the check interval and prune threshold to your liking or leave it as the default values.
You can also add servers to the excepted list by adding a list of comma-separated server uuids as the value of `EXCEPTED_SERVERS`.
And just like that the .env setup is done!

# Running
Running this tool is as simple as just running the main.py file:
```sh
chmod +x main.py
python3 main.py
```

If you want to run it in the background you can use a tool like [screen](https://linuxize.com/post/how-to-use-linux-screen/) or make it a systemd service:
```
sudo nano /etc/systemd/system/pteroprune.service
```

```service
# Pterodactyl Auto Prune
# ----------------------------------

[Unit]
Description=Pterodactyl Auto Prune
After=wings.service

[Service]
User=root
Group=root
Restart=always
ExecStart=/path/to/main.py
StartLimitInterval=180
StartLimitBurst=30
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

```sh
sudo systemctl enable --now pteroprune.service
```
