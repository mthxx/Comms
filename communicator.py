import sys, time, os.path
from PyQt4 import QtGui, QtCore
#from ui_communicator import Ui_hbsCommunicator
from ui_communicator_windows import Ui_hbsCommunicator
from PyQt4.Qt import QApplication
from handler import *
from gui import GUI
from database import Database
from ssh import SSH
from config import Config

class Communicator:
    #Communicator Class Level Variables 
    USER = ""
    USER_PERMISSIONS = []
    ACTIVE_LOG_PATH = ""
    ACTIVE_ROSTER_PATH = ""
    SSH_CONNECTION = SSH.connect_to_ssh()
    LOCAL_CONFIG_DIR_LINUX = "~/.hbs/"
    LOCAL_CONFIG_DIR_WINDOWS = ""
    
    # Channel Update Variables
    LOCAL_LOGS = Config.LOCAL_LOGS
    REMOTE_LOGS = Config.REMOTE_LOGS
    DELTA = []    

    def __init__(self):
        super(Communicator,self).__init__()
  
    def update_active_channel():
        # Call this function to refresh the currently selected channel
        Communicator.populate_channel(Communicator.ACTIVE_LOG_PATH,
                            Communicator.ACTIVE_ROSTER_PATH)
    
    def update_channel(log_path):
        Communicator.populate_channel(log_path,Communicator.ACTIVE_ROSTER_PATH)        

    def update_selected_channels():  
        for i in range(0,len(Communicator.DELTA)):
            for j in range(0,len(GUI.CHANNELS)):
                if(Communicator.DELTA[i] == GUI.CHANNELS[j][0]):
                    GUI.CHANNELS[j][3].setStyleSheet("color:red")

    def populate_channel(log_path,roster_path):
        # Populate the channel with both logs and rosters
        log = SSH.get_active_log(Communicator.SSH_CONNECTION, log_path)
        Communicator.write_to_channel(log_path,log)
        if os.path.isfile(roster_path):
            Communicator.write_to_roster(roster_path)
        else:
            Communicator.write_to_roster_no_roster(roster_path)

    def write_to_channel(current_log_path,log):
        # Write log to the currently selected channel
        GUI.CHANNEL_DISPLAY.setPlainText(log)
        Communicator.ACTIVE_LOG_PATH = current_log_path

        cursor = QtGui.QTextCursor(GUI.CHANNEL_DISPLAY.textCursor())
        cursor.movePosition(QtGui.QTextCursor.End)
        GUI.CHANNEL_DISPLAY.setTextCursor(cursor) 

    def write_to_roster(current_roster_path):
        f = open(current_roster_path, 'r')
        f.close()
        #GUI.ROSTER_DISPLAY.setPlainText(log)
        Communicator.ACTIVE_ROSTER_PATH = current_roster_path
    
    def write_to_roster_no_roster(current_roster_path):
        GUI.ROSTER_DISPLAY.setPlainText("There is currently no roster for this channel\n")
        Communicator.ACTIVE_ROSTER_PATH = current_roster_path

    def write_chat_to_channel():
        # Take chat box text and write it to channel and log.
        chat_input = GUI.CHAT_ENTRY.text()
        if (chat_input != ""):
            log = Communicator.USER + ": " + chat_input
            SSH.write_to_log(Communicator.SSH_CONNECTION,
                                Communicator.ACTIVE_LOG_PATH, log)
            Communicator.update_active_channel()
            GUI.CHAT_ENTRY.setText("")

    def login(username,password,remember):
        # Set user login and permissions
        GUI.LOGIN_STATUS_LABEL.setText("Authenticating...")
        flag, userPermissions, channelPermissions = Database.login(username,password)
        #Communicator.populate_logs()
        if flag:
            # If True, set the username and user permissions. Hide the login and set 
            # the welcome message and announcement. 
            Communicator.USER = username
            Communicator.USER_PERMISSIONS = userPermissions
            GUI.LOGIN_GROUP_BOX.resize(0,0)
            Communicator.populate_channel(GUI.CHANNELS[0][1],GUI.CHANNELS[0][2])
            Communicator.enable_widgets()

            #Code for an automatic login option
            #Communicator.check_dir(Communicator.LOCAL_CONFIG_DIR_LINUX)
                 

            #Code for dynamically applying announcements
            #announcement = SSH.get_log(Communicator.SSH_CONNECTION, Config.c['Logs'] + 'announcement.html')
            #GUI.ANNOUNCEMENT_LABEL.setText(announcement)

    #Code for a "Remember Login" option
    #def check_dir(f):
    #    d = os.path.dirname(f)
    #    if not os.path.exists(d):
    #        os.makedirs(d)

    def enable_widgets():
        GUI.CHAT_ENTRY.setEnabled(True)
        GUI.SUBMIT_BTN.setEnabled(True)
        GUI.CHANNEL_NOTEBOOK.setEnabled(True)
        GUI.CONTENT_NOTEBOOK.setTabEnabled(1, True)
        GUI.USER_BTN.setEnabled(True)

    def check_user_permissions(channel):
        for i in range(0,len(GUI.CHANNELS)):
            if channel == GUI.CHANNELS[i][0]:
                for j in range(len(Communicator.USER_PERMISSIONS)):
                    for k in range(len(GUI.CHANNELS[i][4])):
                        if Communicator.USER_PERMISSIONS[j] == GUI.CHANNELS[i][4][k]:
                            return True
        return False
    
    def invalid_permissions():
        # If user does not have appropriate permissions, print out message.
        GUI.CHANNEL_DISPLAY.setPlainText("You do not have sufficient privileges to view this channel. If you feel this is in error, please contact an administrator")




def main():
    app = QtGui.QApplication(sys.argv)
    hand = Handler()
    com = Communicator()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()

