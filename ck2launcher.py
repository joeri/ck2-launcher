#! /usr/bin/python2

""" Crusader Kings II Linux Launcher
    2013  Robin C. Thomas <rc.thomas90@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>."""

import os, sys, glob, re, wx, datetime, ConfigParser
from subprocess import Popen

APPNAME = 'Crusader Kings II Launcher' 	#: Application name
VERSION = '0.3.1-28012013'		#: Application version

LOGFILE = sys.path[0] + '/ck2launcher.log'	#: Logfile path

# Console colors
HEADERCOLOR = '\033[95m'	#: Color for headers shown in console
INFOCOLOR = '\033[94m'		#: Color for info messages shown in console
OKCOLOR = '\033[92m'		#: Color for confirmation messages shown in console
WARNINGCOLOR = '\033[93m'	#: Color for warning messages in console
ERRORCOLOR = '\033[91m'		#: Color for error messages in console
ENDCOLOR = '\033[0m'		#: String to end color usage

CONFIG_FILE = sys.path[0] + '/ck2launcher.conf'	#: Path and filename of the configuration file

#: Will hold the configuration parser (ConfigParser)
config = None

#: Will hold the Popen object that launches the game
ck2Process = None

#: Will hold the main launcher window
launcher = None

#: Open logfile
logfile = open(LOGFILE, 'a')


def log(entry):
  '''Creates an entry in the logfile
  
  Arguments:
  entry --- The entry to add to the logfile
  
  '''
  global logfile
  logfile.write('[{0}] {1}\n'.format(str(datetime.datetime.now()), entry))


def header(text):
  '''Shows a header in the console and adds it to the logfile
  
  Arguments:
  text --- Text of the header
  
  '''
  print('{0}{1}{2}'.format(HEADERCOLOR, text, ENDCOLOR))
  log(text)



def infoMsg(text):
  '''Shows an information message in ther console and adds it to the logfile
  
  Arguments:
  text --- Message to show
  
  '''
  print('    {0}{1}{2}'.format(INFOCOLOR, text, ENDCOLOR))
  log(text)
  

def warningMsg(text, parent=None):
  '''Shows a warning message in the console and in a dialog. Also adds it to the logfile.
  
  Arguments:
  text --- Message to show
  parent --- The parent window of the dialog
  
  '''
  print('    {0}WARNING: {1}{2}'.format(WARNINGCOLOR, text, ENDCOLOR))
  log('WARNING: {0}'.format(text))
  wx.MessageDialog(parent, 'WARNING: {0}'.format(text), APPNAME, wx.OK | wx.ICON_WARNING).ShowModal()


def errorMsg(text, parent=None):
  '''Shows an error message in the console and in a dialog. Also adds it to the logfile.
  
  Arguments:
  text --- Message to show
  parent --- Parent window of the dialog
  
  '''
  print('    {0}ERROR: {1}{2}'.format(ERRORCOLOR, text, ENDCOLOR))
  log('ERROR: {0}'.format(text))
  wx.MessageDialog(parent, 'ERROR: {0}'.format(text), APPNAME, wx.OK | wx.ICON_ERROR).ShowModal()
  
  
def okMsg(text):
  '''Shows a confirmation message in the console and adds it to the logfile.
  
  Arguments:
  text --- Message to show
  
  '''
  print('    {0}{1}{2}'.format(OKCOLOR, text, ENDCOLOR))
  log(text)
  

class Mod:
  '''Represents a mod
  
  '''
  
  def __init__(self, filename):
    ''' Creates a new mod
    
    Arguments:
    filename --- The file the mod is contained in mod
    
    '''
    infoMsg('Found modfile: "{0}".'.format(filename))
    
    self.filename = filename	#: The file the mod is contained in
    self.name = ''		#: The name of the mod
    self.directory = ''		#: The directory the mod saves data in (savegames, configuration , ...)
    
    # Get mod information
    self.getModInfo()
    
    if len(self.directory) > 0:
      # This mod should have a directory to store data in, checking if it exists
      if not os.path.exists(self.directory):
	#No, create it
	os.mkdir(self.directory)
	okMsg('Created data directory for mod "{0}": "{1}"'.format(self.name, self.directory))
    
  
  # Opens the modfile of the current mod and gets it's name and user_dir
  def getModInfo(self):
    '''Gets all needed information about this mod
    '''
    global config, launcher
    
    # Try opening the modfile
    try:
      modfile = open(config.get('launcher', 'modpath') + '/' + self.filename)
    except IOError:
      # Unable to open modfile
      errorMsg('Unable to load modfile "{0}"! Check permissions.'.format(self.filename), launcher)
      self.name = self.filename
      return
    
    moddata = modfile.read()
    
    # Get mod name
    try:
      self.name = re.search('^name[ \t]*=[ \t]*"(.*)"', moddata, re.MULTILINE).group(1)
    except AttributeError:
      # Modname not found
      warningMsg('Could not find mod name for modfile "{0}". Using "{0}" as name.'.format(self.filename), launcher)
      self.name = self.filename
      
    # Get mod directory (if available)
    self.directory = re.search('^user_dir[ \t]*=[ \t]*"(.*)"', moddata, re.MULTILINE)
    if (hasattr(self.directory, 'group')):
      self.directory = os.path.dirname(config.get('launcher', 'modpath')) + '/' + self.directory.group(1)
    else:
      self.directory = ''
    
# END CLASS Mod



class DLC:
  '''Represents a DLC
  '''
  
  def __init__(self, dlcfile):
    '''Creates a new dlc object
    
    Arguments:
    dlcfile --- The file the dlc is stored in
    
    '''
    infoMsg('Found DLC file: "{0}"'.format(dlcfile))
    self.filename = dlcfile	#: The file the dlc is stored in
    self.name = ''		#: The name of the dlc
    
    # Get information about this dlc
    self.getDLCInfo()
    
  
  
  def getDLCInfo(self):
    '''Gets information about the current dlc
    '''
    global launcher
    
    # Open dlc file
    try:
      dlcfile = open(self.filename)
    except IOError:
      # Unable to open dlcfile
      errorMsg('Unable to open DLC file "{0}". Check permissions.'.format(self.filename), launcher)
      self.name = self.filename
      return
    
    dlcdata = dlcfile.read()
    
    # Extract name
    try:
      self.name = re.search('^name[ \t]*=[ \t]*"(.*)"', dlcdata, re.MULTILINE).group(1)
    except AttributeError:
      # DLC name not found, use filename as name
      warningMsg('Could not find dlc name for dlcfile "{0}". Using "{0}" as name.'.format(self.filename), launcher)
      self.name = self.filename
    
  
# END CLASS dlc


# The main launher window
class Launcher(wx.Frame):
  '''The main launcher window
  '''
  
  def __init__(self, parent, title):
    '''Creates a new launcher window
    
    Parameters:
    parent --- The parent of the window
    title --- The tile of the window
    
    '''
    wx.Frame.__init__(self, parent, title=title, style=wx.CAPTION|wx.CLOSE_BOX)
    
    # Initialize the UI
    self.initUI()
    
    
  
  def initUI(self):
    '''Initializes the UI
    '''
    
    #: The main container for the window
    self.panel = wx.Panel(self, -1)
    
    #: The Sizer for the main window
    self.box = wx.BoxSizer(wx.VERTICAL)
    
    # CK2 logo
    logoBitmap = wx.Image(sys.path[0] + '/ck2.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
    logo = wx.StaticBitmap(self.panel, bitmap=logoBitmap, size=(-1, 125))
    
    # Labels for the mod and dlc lists
    labelFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    modLabel = wx.StaticText(self.panel, label='Mods:', size=(260, -1))
    modLabel.SetFont(labelFont)
    dlcLabel = wx.StaticText(self.panel, label='DLC\'s:')
    dlcLabel.SetFont(labelFont)
    labelSizer = wx.BoxSizer(wx.HORIZONTAL)
    labelSizer.Add(modLabel)
    labelSizer.Add(dlcLabel)
    
    # Font for the mod and dlc lists
    listFont = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
    
    #: The mod list
    self.modList = wx.CheckListBox(self.panel, size=(260, 200), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
    self.modList.SetFont(listFont)
    
    #: The DLC list
    self.dlcList = wx.CheckListBox(self.panel, size=(260, 200), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
    self.dlcList.SetFont(listFont)
    
    #: Sizer for the mod and dlc lists
    self.listSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.listSizer.Add(self.modList)
    self.listSizer.Add(self.dlcList)
    
    # Horizontal sizer to hold the Configuration and Run buttons
    buttonBox = wx.BoxSizer(wx.HORIZONTAL)
    
    #: Configuration button
    self.confButton = wx.Button(self.panel, label='&Configuration', size=(150, 30))
    self.confButton.Bind(wx.EVT_BUTTON, self.confButtonClick)
    
    #: Run Button
    self.runButton = wx.Button(self.panel, label='&Run CK2', size=(150, 30))
    self.runButton.Bind(wx.EVT_BUTTON, self.runButtonClick)
    
    # Add controls to sizer
    buttonBox.Add(self.confButton)
    buttonBox.Add(self.runButton)
    self.box.Add(logo, flag=wx.ALIGN_CENTER)
    self.box.Add(labelSizer, flag=wx.ALIGN_CENTER)
    self.box.Add(self.listSizer)
    self.box.Add(buttonBox, flag=wx.ALIGN_RIGHT)
    
    self.panel.SetSizer(self.box)
    
    # Bind the frame close event to its event handler
    self.Bind(wx.EVT_CLOSE, self.frameClose)
    
    # Load mods and DLC's into their respective lists
    self.loadMods()
    self.loadDlcs()
    
    # Fit all elements in the window
    self.box.Fit(self)
    
    # Center window on screen
    self.Centre()
    
    
    
  # Loads the mod list
  def loadMods(self):
    '''Loads the mod list of the main laucher window
    '''
    
    global config
    
    # Detect mods
    okMsg('Detecting mods...')
    self.mods = detectMods()		#: List of mods available in the mod directory
    okMsg('Done. Found {0} mods'.format(str(len(self.mods))))
    
    # Get list of mods that were checked last time (if available)
    checkedMods = []
    if config.has_option('launcher', 'selectedmods'):
      checkedMods = config.get('launcher', 'selectedmods').split(',')
    
    # Insert all mods into mod list
    self.modList.Clear()
    count = 0
    for mod in self.mods:
      self.modList.Append(mod.name)
      if mod.filename in checkedMods:
	self.modList.Check(count, True)
	
      count += 1
      
  
  # Loads the dlc list
  def loadDlcs(self):
    '''Loads the list of DLC's in the main window
    '''
    
    global config
    
    okMsg('Detecting DLC\'s...')
    self.dlcs = detectDlcs()		#: List of available DLC's in the dlc directory
    okMsg('Done. Found {0} DLC\'s'.format(str(len(self.dlcs))))
    
    # Get dlcs that where checked on the last run, if not defined check all
    checkAll = True
    selectedDlcs = []
    if config.has_option('launcher', 'selecteddlcs'):
      checkAll = False
      selectedDlcs = config.get('launcher', 'selecteddlcs').split(',')
    
    # Insert all dlcs into dlc list
    self.dlcList.Clear()
    count = 0
    for dlc in self.dlcs:
      self.dlcList.Append(dlc.name)
      if dlc.filename in selectedDlcs or checkAll:
	self.dlcList.Check(count, True)
      
      count += 1
    
    
  
  def confButtonClick(self, event):
    '''Event handler for the configuration button click event
    
    Arguments:
    event --- Button click event
    
    '''
    confFrame = Configuration(self)
    confFrame.MakeModal(True)
    confFrame.Show()
    
  
  
  def frameClose(self, event):
    '''Event hanler for the frame close event
    
    Arguments:
    event --- Frame close event
    
    '''
    global config
    
    # Save all selected mods
    selectedMods = []
    for index in self.modList.GetChecked():
      selectedMods.append(self.mods[index].filename)
      
    config.set('launcher', 'selectedMods', ','.join(selectedMods))
    
    # Save all selected dlc
    selectedDlcs = []
    for index in self.dlcList.GetChecked():
      selectedDlcs.append(self.dlcs[index].filename)
    
    config.set('launcher', 'selecteddlcs', ','.join(selectedDlcs))
    
    config.write(open(CONFIG_FILE, 'w'))
    
    # Continue closing frame
    event.Skip()
  
  
  
  def runButtonClick(self, event):
    '''Event handler for the run button click event
    
    Arguments:
    event --- The click event
    
    '''
    global config, ck2Process
    
    # Get selected mods from list
    selectedMods = []
    for index in self.modList.GetChecked():
      selectedMods.append(self.mods[index])
    
    # Prepare command to execute
    command = []
    if len(config.get('launcher', 'prepend').strip()) > 0:
      command = config.get('launcher', 'prepend').split(' ')
    command.append(config.get('launcher', 'gamepath') + '/' + config.get('launcher', 'gamebinary'))
    
    # Decide which mods to load
    if (len(selectedMods) == 0):
      # No mods selected, run vanilla game
      okMsg("No mod selected, running vanilla game...")
    else:
      # Append selected mods to command
      okMsg(str(len(selectedMods)) + " mods selected:")
      for mod in selectedMods:
	okMsg('\t{0} ({1})'.format(mod.name, mod.filename))
	command.append('-mod=mod/' + mod.filename)
	
    # Exclude unchecked DLC's
    for index in range(0, len(self.dlcs)):
      if not self.dlcList.IsChecked(index):
	# This dlc is not checked, exclude it
	infoMsg('Excluding unchecked DLC "{0}".'.format(self.dlcs[index].name))
	command.append('-exclude_dlc=dlc/' + self.dlcs[index].filename)
    
    # Execute prepared command
    infoMsg('Running "{0}"...'.format(' '.join(command)))
    try:
      ck2Process = Popen(command)
      okMsg('Done. Have fun! :D')
    except OSError:
      # Failure, executable not found
      errorMsg('Unable to run command "{0}". Please check that the GAMEPATH is set correctly and that the commands in PREPEND are correct.'
		.format(' '.join(command)), self)
      
      # Return to launcher
      return
    
    self.Close()
     
    
# END CLASS Launcher



class Configuration(wx.Frame):
  '''Configuration window
  '''
  def __init__(self, parent, title='{0} - Configuration'.format(APPNAME)):
    '''Creates a new configuration window
    '''
    wx.Frame.__init__(self, parent, title=title, style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
    self.initUI()
    
  
  
  def initUI(self):
    '''Initializes the UI
    '''
    global config
    
    # Connect frame close event to handler
    self.Bind(wx.EVT_CLOSE, self.frameClose)
    
    # Create UI elements
    self.panel = wx.Panel(self, -1)		#: The main container panel
    self.vsizer = wx.BoxSizer(wx.VERTICAL)	#: The main container sizer
    self.panel.SetSizer(self.vsizer)
    
    # Default font for the labels
    labelFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    
    # Game path label, input, choose button and sizer
    gpSizer = wx.BoxSizer(wx.HORIZONTAL)
    gpLabel = wx.StaticText(self.panel, label=' Game path:', size=(160, -1))
    gpLabel.SetFont(labelFont)
    
    #: Input field for the game path
    self.gpInput = wx.TextCtrl(self.panel, value=config.get('launcher', 'gamepath'), size=(325, -1))
    
    #: Button to open the directory dialog for the game path
    self.gpChooseBtn = wx.Button(self.panel, label='Choose folder...')
    
    gpSizer.Add(gpLabel, flag=wx.ALIGN_CENTER_VERTICAL)
    gpSizer.Add(self.gpInput, flag=wx.ALIGN_CENTER_VERTICAL)
    gpSizer.Add(self.gpChooseBtn, flag=wx.ALIGN_CENTER_VERTICAL)
    
    # Connect game path choose button click event to handler
    self.gpChooseBtn.Bind(wx.EVT_BUTTON, self.gpChooseBtnClick)
    
    # Mod path label, input, choose button and sizer
    mpSizer = wx.BoxSizer(wx.HORIZONTAL)
    mpLabel = wx.StaticText(self.panel, label=' Mod path:', size=(160, -1))
    mpLabel.SetFont(labelFont)
    
    #: Input field for the mod path
    self.mpInput = wx.TextCtrl(self.panel, value=config.get('launcher', 'modpath'), size=(325, -1))
    
    #: Button to open the directory dialog for the mod path
    self.mpChooseBtn = wx.Button(self.panel, label='Choose folder...')
    
    mpSizer.Add(mpLabel, flag=wx.ALIGN_CENTER_VERTICAL)
    mpSizer.Add(self.mpInput, flag=wx.ALIGN_CENTER_VERTICAL)
    mpSizer.Add(self.mpChooseBtn, flag=wx.ALIGN_CENTER_VERTICAL)
    
    # Connect mod path choose button click event to handler
    self.mpChooseBtn.Bind(wx.EVT_BUTTON, self.mpChooseBtnClick)
    
    # Game binary label, input and sizer
    gbSizer = wx.BoxSizer(wx.HORIZONTAL)
    gbLabel = wx.StaticText(self.panel, label=' Game binary:', size=(160, -1))
    gbLabel.SetFont(labelFont)
    
    #: The input field for the binary name
    self.gbInput = wx.TextCtrl(self.panel, value=config.get('launcher', 'gamebinary'), size=(435, -1))
    
    gbSizer.Add(gbLabel, flag=wx.ALIGN_CENTER_VERTICAL)
    gbSizer.Add(self.gbInput, flag=wx.ALIGN_CENTER_VERTICAL)
    
    # Prepend label, input and sizer
    ppSizer = wx.BoxSizer(wx.HORIZONTAL)
    ppLabel = wx.StaticText(self.panel, label=' Prepend commands:', size=(160, -1))
    ppLabel.SetFont(labelFont)
    
    #: Input field for the prepended commands
    self.ppInput = wx.TextCtrl(self.panel, value=config.get('launcher', 'prepend'), size=(435, -1))
    ppSizer.Add(ppLabel, flag=wx.ALIGN_CENTER_VERTICAL)
    ppSizer.Add(self.ppInput, flag=wx.ALIGN_CENTER_VERTICAL)
    
    # Cancel and save button
    buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.cancelButton = wx.Button(self.panel, label='&Cancel')		#: Configuration cancel button
    self.saveButton = wx.Button(self.panel, label='&Save')		#: Configuration save button
    buttonSizer.Add(self.cancelButton)
    buttonSizer.Add(self.saveButton)
    
    # Connect cancel and save button click events to their handler
    self.cancelButton.Bind(wx.EVT_BUTTON, self.cancelButtonClick)
    self.saveButton.Bind(wx.EVT_BUTTON, self.saveButtonClick)
    
    # Add ui elements to frame sizer
    self.vsizer.Add(gpSizer)
    self.vsizer.Add(mpSizer)
    self.vsizer.Add(gbSizer)
    self.vsizer.Add(ppSizer)
    self.vsizer.Add(buttonSizer, flag=wx.ALIGN_RIGHT)
    
    # Fit all elements into the configuration window
    self.vsizer.Fit(self)
    
    # Center configuration window on screen
    self.Centre()
    
  
  
  def frameClose(self, event):
    '''Event handler for the frame close event
    
    Arguments:
    event --- The close event
    
    '''
    self.MakeModal(False)
    event.Skip()
    
  
  
  def gpChooseBtnClick(self, event):
    '''Event handler for the game path choose button click event
    
    Arguments:
    event --- The click event
    
    '''
    global config
    
    # Open directory selection dialog and copy new path into input field if new path selected
    dirDialog = wx.DirDialog(self, 'Choose CK2 game directory...', config.get('launcher', 'gamepath'), wx.DD_DIR_MUST_EXIST)
    if dirDialog.ShowModal() == wx.ID_OK:
      self.gpInput.SetValue(dirDialog.GetPath())
      
      
  
  def mpChooseBtnClick(self, event):
    '''Event handler for the mod path choose button click event
    
    Arguments:
    event --- The click event
    
    '''
    global config
    
    # Open directory selection dialog and copy new path into input field if new path selected
    dirDialog = wx.DirDialog(self, 'Choose CK2 mod directory...', config.get('launcher', 'modpath'), wx.DD_DIR_MUST_EXIST)
    if dirDialog.ShowModal() == wx.ID_OK:
      self.mpInput.SetValue(dirDialog.GetPath())
      
    
  
  def cancelButtonClick(self, event):
    '''Event handler for the cancel button click event
    
    Arguments:
    event --- The click event
    
    '''
    self.Close()
    
    
    
  
  def saveButtonClick(self, event):
    '''Event handler for the save button click event
    
    Arguments:
    event --- The click event
    
    '''
    # Does the game binary and the mod path exists where specified?
    if not os.path.isfile(self.gpInput.GetValue() + '/' + self.gbInput.GetValue()):
      errorMsg('Game binary "{0}" not found in "{1}"!'.format(self.gbInput.GetValue(), self.gpInput.GetValue()), self)
      return
    
    if not os.path.exists(self.mpInput.GetValue()):
      errorMsg('Mod path "{0}" does not exist!'.format(self.mpInput.GetValue()), self)
      return
    
    # Change configuration and save
    config.set('launcher', 'gamepath', self.gpInput.GetValue())
    config.set('launcher', 'modpath', self.mpInput.GetValue())
    config.set('launcher', 'prepend', self.ppInput.GetValue())
    config.set('launcher', 'gamebinary', self.gbInput.GetValue())
    config.write(open(CONFIG_FILE, 'w'))
    
    # Configuration may have changed, reload mod and dlc list
    self.Parent.loadMods()
    self.Parent.loadDlcs()
    
    # Close configuration window
    self.Close()
  
  
# END CLASS Configuration


def detectMods():
  '''Detects all available mods in the mod directory
  '''
  global config, launcher
  
  # Go into mod directory
  try:
    os.chdir(config.get('launcher', 'modpath'))
  except OSError:
    # The mod directory does not exist
    errorMsg('Could not find mod directory "{0}". Please check configuration.'.format(config.get('launcher', 'modpath')), launcher)
    return []
  
  # Search modfiles
  modfiles = glob.glob('*.mod')
  
  # Create mod object for each found modfile
  mods = []
  for modfile in modfiles:
    mod = Mod(modfile)
    mods.append(mod)
    infoMsg('Found mod "{0}" in file "{1}".'.format(mod.name, mod.filename))
    
  return mods

# END detectMods()



def detectDlcs():
  '''Detects all available DLC in the dlc directory
  '''
  global config
  
  # Go into dlc directory
  try:
    os.chdir(config.get('launcher', 'gamepath') + '/dlc')
  except OSError:
    # Unable to enter dlc directory
    errorMsg('Could not find dlc directory "{0}". Please check configuration.'.format(config.get('launcher', 'gamepath') + '/dlc'), launcher)
    return []
  
  # Search for DLC files
  dlcfiles = glob.glob('*.dlc')
  
  # Create a dlc object for each found DLC
  dlcs = []
  for dlcfile in dlcfiles:
    dlc = DLC(dlcfile)
    dlcs.append(dlc)
    infoMsg('Found DLC "{0}" in file "{1}".'.format(dlc.name, dlc.filename))
    
  return dlcs
  
# END detectDlcs()



def loadConfiguration():
  '''Opens the configuration file and uses the ConfigParser to read it
  '''
  global config
  
  # If the configuration does not exists, create it
  if not os.path.exists(CONFIG_FILE):
    open(CONFIG_FILE, 'w').close()
  
  # Load configuration from file
  config = ConfigParser.SafeConfigParser()
  config.read(CONFIG_FILE)
  
  # Check if all needed configurations are present, if not add them and set default values
  if not config.has_section('launcher'):
    config.add_section('launcher')
    
  if not config.has_option('launcher', 'gamepath'):
    config.set('launcher', 'gamepath', '~/.local/share/Steam/SteamApps/common/Crusader Kings II'.replace('~', os.path.expanduser('~')))
  
  if not config.has_option('launcher', 'modpath'):
    config.set('launcher', 'modpath', '~/Documents/Paradox Interactive/Crusader Kings II/mod'.replace('~', os.path.expanduser('~')))
    
  if not config.has_option('launcher', 'prepend'):
    config.set('launcher', 'prepend', '')
    
  if not config.has_option('launcher', 'gamebinary'):
    config.set('launcher', 'gamebinary', 'ck2')
    
  # Save configuration to file
  config.write(open(CONFIG_FILE, 'w'))
    
# END loadConfiguration()


def main():
  global ck2Process, launcher
  
  app = wx.App(False)
  
  # Greet user
  header('Crusader Kings 2 Linux Launcher')
  infoMsg('Version {0}'.format(VERSION))
  
  # Load configuration
  loadConfiguration()
  
  # Create user interface
  launcher = Launcher(None, APPNAME)
  launcher.Show()
  app.MainLoop()
  
  # If game started wait for process to end
  launcher = None
  if ck2Process != None:
    exitCode = ck2Process.wait()
    if exitCode == 0:
      # Game closed correctly
      okMsg('Game closed without error.')
    else:
      # Something went wrong
      errorMsg('Process closed with error code {0}. Please check configuration.'.format(str(exitCode)))
      
      # At this point it is too late to reuse the current launcher
      # Launch another instance
      os.chdir(sys.path[0])
      Popen(sys.argv[0])
  
  exit(0)
  
# END main()

  
if __name__ == "__main__":
  main()
  
  
