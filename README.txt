==== CK2 LINUX LAUNCHER ====

This software is distributed under the GNU General Public License v.3.0 (LICENSE.txt).
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under the conditions of the GNU GPL v.3.0.


==== REQUIREMENTS ====

To be able to run the launcher you need python2 (should allready be installed in any 
distro) and wxpython bindings. To install wxpython on Ubuntu use:
  sudo apt-get install python-wxgtk2.8

For ArchLinux use:
  sudo pacman -S wxpython
  
For other distros refer to your distros documentation.

You also need to grant 'ck2launcher.py' executable permissons:
  chmod +x ck2launcher.py
  
or using your file browser's 'file properties' window.


==== CONFIGURATION ====

You no longer need to edit the configuration file manually, use the configuration window
in the launcher.

 -- GAMEPATH --
  Points to the CK2 game directory. Default: '~/.local/share/Steam/SteamApps/common/Crusader Kings II'
  where '~' is your home directory.

 -- MODPATH --
  Points to your mod directory. Default: '~/Documents/Paradox Interactive/Crusader Kings II/mod'
  where '~' is your home directory.
  
 -- GAMEBINARY --
  The binary file to execute when clicking the "Run CK2" button. Default: 'ck2'

 -- PREPEND --
  Comands to prepend before the game executable.
  Default: ''
  Bumblebee user can set it to 'optirun' so the game is run using the nVidia grapics card.
    
    
    
==== TROUBLESHOOTING ====

When the launcher does not do what he is suposed to you have two options:
  1. Run it in a terminal so you can see the programm output.
  2. Open the 'ck2launcher.log' to see what went wrong.
