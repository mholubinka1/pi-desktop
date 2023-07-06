# **RetroPie**

## **1. Install RetroPie as an Application**

RetroPie is most commonly found installed as a distribution on its own. This, however, is unnecessary and Raspbian is more than capable of providing a versatile experience. RetroPie can be installed from source as an application. The first dependency is ``git``.

Ensure the system is up to date:

```
sudo apt update
sudo apt upgrade
```

Next, install ``git``:

```
sudo apt install git
```

With ``git`` installed, create a folder to house repositories for easy access:

```
mkdir /home/pi/git
```

Navigate to this new folder and clone the RetroPie repository:

```
git clone https://github.com/RetroPie/RetroPie-Setup.git`
```

Change folder and make `retropie_setup.sh` executable:

```
chmod +x retropie_setup.sh
```

RetroPie can now be installed from the setup script:

```
sudo ./retropie_setup.sh
```

Some additional packages may be installed and, once this is done, the setup menu will appear. Select **OK** to close the introduction screen and then choose **I. Basic  install** from the options menu. This will install all of the packages from the core and main RetroPie projects.

Select **Yes** to proceed and wait as the suite of emulators is installed. This will take a while.

Once the installation is complete, the setup menu will appear again.

## **2. Enable Xbox 360 Controller Support**

Now it is time to enable controller support. The primary Xbox 360 controller driver - ``xboxdrv`` - has had recent issues rendering images usable. Fortunately, the updated ``xpad`` driver works as well for Xbox 360 contollers. Install the driver by navigating back through the setup menu

> **Manage Packages >> Manage Driver Packages >> Xpad**

> **Install from source >> Confirm**

This will install the driver from source. Once this is complete, navigate back to the main setup menu and reboot the system: **R. Perform Reboot**.

The Hotkey shortcuts are as follows:

```
Select+Start: Exit
Select+Right Shoulder: Save
Select+Left Shoulder: Load
Select+Right: Input State Slot Increase
Select+Left: Input State Slot Decrease
Select+X: RGUI Menu
Select+B: Reset
```

## **3. Configure RetroPie**

### **3.1. Install Themes**

First thing to do with a clean installation of RetroPie is select the theme. [Epic Noir](https://github.com/c64-dev/es-theme-epicnoir) is my preferred choice.

Create a folder for new themes:

```
mkdir ~/.emulationstation.themes
```

Navigate to this folder and clone the theme repository into it:

```
git clone https://github.com/c64-dev/es-epicnoir.git --branch master
```

Finally, open ``emulationstation``:

```
emulationstation
```

Since this is the first time, ``emulationstation`` has been run and the Xbox 360 Controller is now recognised by RetroPie, the software will guide you through the controller configuration process.

``emulationstation`` should open with the **Epic Noir** theme. Quit back to the Raspberry Pi desktop as now is the time to load the ROMS and BIOS files into RetroPie so games can be played. 

### **3.2. ROM and BIOS Setup**

#### **3.2.1. Symlinks**

In order to save space on the interal SD Card, it is advisable to store the ROM files on an external drive. Unfortunately, RetroPie requires the ROMs location to be set manually for each system through the ``es_systems.cfg`` file. The simplest way around this is to set up a symbolic link between ``/home/pi/RetroPie/roms`` folder and the external folder where all the ROMs are present:

First, navigate to the RetroPie folder:

```
cd /home/pi/RetroPie
```

Next, set up the symbolic link between this folder and the folder containing the ROMs files for each system

```
sudo ln -s /mnt/pi-media/RetroPie/roms .
```

Use the file explorer to confirm that the symlink is working as expected.

#### **3.2.2. BIOS Files**

The next step is to add the correct BIOS files for the emulators. A complete pack can be found [here](https://github.com/Abdess/retroarch_system/releases/download/1.0.0/RetroPie.zip). Copy these files into the relevant folders on the system.

Now, open ``emulationstation`` and navigate to:

> **Menu >> Scraper**

To categorise ROMs and start playing.

## **4. Advanced**

### **4.1. Install Experimental Packages**

#### **4.1.1. Steamlink**

The Steamlink package is available directly through the RetroPie setup script. Run the setup script as before and navigate to:

> **Manage Packages >> Manage Experimental Packages >> steamlink**

Confirm and install from the pre-compiled binary. Allow the installation to complete and the menu will appear again, select the option to **Update** in case any package updates have been released since the last version of the pre-compiled binary.

Next, open ``emulationstation``, **Steamlink** will be found under the **Ports** section. Run it.

It is likely, the error message below will appear:

_'You are running with less than 128 MB video memory, you may need to go to the Raspberry Pi Configuration and increase your GPU memory.'_

Select _OK_ and continue. Once the Steamlink application has opened, quit back to ``emulationstation`` and exit back to desktop. It is best to fix the memory issue before proceeding. Open the Raspberry Pi configuration file:

```
sudo nano /boot/config.txt
```

Add the following line to the end of the file:

    gpu_mem=256

Reboot the system and once completed, run ``emulationstation`` once again. Navigate to the Steamlink application again and run it - the error message has gone! Now configure Steamlink following the onscreen instructions: it will find the local computer running Steam and then request a pin to be entered on it. Once this is done, the two devices are paired and Steam games can be streamed through the Raspberry Pi.

#### **4.1.2. Dreamcast (Redream)**

The next experimental package to install is **Redream**, this can be done through the setup script as above. Navigate to:

> **Manage Packages >> Manage Experimental Packages >> redream**

Once again, install from the pre-compiled binary and wait for the installation to complete. The next step is to improve emulator performance by overclocking the Raspberry Pi 4. This means modifying the configuration file again:

```
sudo nano /boot/config.txt
```

Add the following lines to the bottom of the file:

    #OVERCLOCK v3d_freq = 750
    over_voltage=6
    v3d_freq=750
    hdmi_enable_4kp60=1
    arm_freq=2000

Restart the device to check that the overclocking profile does not cause any boot issues.

#### **4.1.3. Playstation Portable**

The final emulator to install is that for the Playstation Portable (PSP). Again, run the Retropie setup script and this time navigate to:

> **Manage Packages >> Manage Optional Packages >> ppsspp**

This time select the **S. Install from source** option. Confirm and let the installation complete.

### **5. Tweaks**

#### **5.1. Playstation (PSX)**


#### **5.2. PSP (ppsspp)**

#### **5.3. Nintendo 64**

#### **5.4. Sega Megadrive**

There can be issues around scraping Megadrive/Genesis games from TheGamesDB. The easiest solution is to modify ``es_systems.cfg``.

``sudo nano /etc/emulationstation/es_systems.cfg``

Change the section for the ``megadrive`` system to:

    <system>
        <name>megadrive</name>
        <fullname>Sega Mega Drive</fullname>
        <path>/home/pi/RetroPie/roms/megadrive</path>
        <extension>.7z .smd .bin .gen .md .sg .zip .7Z .SMD .BIN .GEN .MD .SG .ZIP</extension>
        <command>/opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ megadrive %ROM%</command>
        <platform>megadrive, genesis</platform>
        <theme>megadrive</theme>
    </system>

This adds the ``genesis`` system into the search when running the scraper, which results in a much larger pool of games being found.

### **6. RetroPie-Manager** 

RetroPie-Manager provides a suite of tools direct through the browser which allow for:

- Monitoring
- ROM and BIOS Management
- Configuration

These are all accessible directly through the browser on another machine.

In order to install RetroPie-Manager, run the RetroPie-Setup script again:

```
sudo ./retropie_setup.sh
```

Or, directly through ``emulationstation`` UI, access:

> **Options >> RetroPie Setup**

Select:

> **Manage Packages >> Manage Experimental Packages >> retropie-manager**

Install this from source and when the installation is complete select **C. Configuration / Options** and then **3. Enable RetroPie-Manager on Boot**.

  










