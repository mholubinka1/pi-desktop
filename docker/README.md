# Docker

## Setup








## Running Containers

### 1. Docker Compose



### 2. Running Bullseye Containers on Buster

Problems may be experienced on _Stretch_ or _Buster_ based Linux systems when running containers built on a _Bullseye (Debian 11)_ distribution. Ultimately, the best solution to this problem upgrading to the latest version of the operating system. In certain circumstances, where applications (eg. RetroPie is only available for _Buster_) are not yet compatible with _Bullseye_ based distributions, for example, these issues can be fixed a full scale upgrade.

#### 2.1. Upgrading `libseccomp2`

A script is available which is designed to only run on systems which have this problem and where a fix can be safely applied:

```
curl -sL https://raw.githubusercontent.com/sdr-enthusiasts/Buster-Docker-Fixes/main/libseccomp2-checker.sh | bash
```

Follow the command line instructions and, once the upgrade is complete, restart any running containers.

## Building ARM Images

Any Docker image have the corresponding processor architecture if it going to run successfully. Given the current requirements for 32-bit _Buster_, this means that images must be built for the ``linux\arm\v7`` platform. There are a couple of ways for this to be achieved:

- Using ``buildx`` which emulates the processor architecture during the image build
- Building the image natively on the required platform

### 1. ARMv7 and .Net

.Net versions up to and included 7 fully support ARMv7 architectures. It is likely that .Net 8 will no longer support 32-bit ARM instead choosing to only support ARM64. This is unsurprising given the entire Raspberry Pi family supports the new 64-bit version of RaspbianOS and other Internet-of-Things (IOT) devices also support and run with 64-bit distributions.

Unfortunately, due to the 32-bit _Buster_ distribution required by RetroPie, ARMv7 images are required when running a Raspberry Pi as a multi-purpose home entertainment server. .Net 7 also no longer supports _Buster_ base images for creating Docker images which further complicates matters.

In addition .Net 7 and, in the future, .Net 8 do not and will not support ``qemu`` which is required by ``buildx`` to emulate the ``linux\arm\v7`` platform. Attempting to use ``buildx`` will fail for such builds and there is no work around.

The only solution is therefore a self-hosted runner to build the required images for [Hueshift2](https://github.com/mholubinka1/hueshift2). The above upgrade for `libseccomp2` is also required. In order to configure a self-hosted runner for Github select the repository requiring the runner:

> **Settings** >> **Actions** >> **Runners**

And select **New self-hosted runner**. Select the **Linux** tab and the **ARM** architecture drop the drop down menu for complete instructions.

Once installation and configuration is complete:

```
./run.sh
```

The runner will start with logging attached to the open terminal window. Return to the previous **Runners** window in the browser and confirm that the runner that was just started appears with status **Idle**.

Next, configure the runner as a service to start on boot. Stop the runner with ``ctrl+c`` and then install the service:

```
sudo ./svc.sh install
```

This will create a service with a very ugly name. Crucially the proper name of the service is everything between:

```
/etc/systemd/system/<THIS IS THE SERVICE NAME>.service
```

In order to start the runner on boot:

```
sudo systemctl enable --now <service-name>
```

The self-hosted runner is now ready to accept build jobs for the ``linux\arm\v7`` platform.