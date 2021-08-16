###########################
###########################
####### Acoubot GUI #######
###########################
###########################

from typing import ItemsView
from PyQt5 import QtCore, QtGui, QtWidgets

#from sumenu import Ui_MenuWindow
import newroom as nr
import os
import StationaryUnit as SU
import socket
port=10000
ip='192.168.1.200'
benchmark_num=0
entered_room=''
#entered_room=''
newroom_flag=0
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class Ui_Connection(object):
    def setupUi(self, Connection):
        Connection.setObjectName("Connection")
        Connection.setWindowModality(QtCore.Qt.ApplicationModal)
        Connection.resize(800, 600)
        Connection.setAutoFillBackground(False)
        Connection.setStyleSheet("background-color: rgb(35, 47, 52);")
        self.centralwidget = QtWidgets.QWidget(Connection)
        self.centralwidget.setObjectName("centralwidget")
        self.checkconnection = QtWidgets.QPushButton(self.centralwidget)
        self.checkconnection.setGeometry(QtCore.QRect(320, 300, 160, 40))
        self.checkconnection.setAutoFillBackground(False)
        self.checkconnection.setStyleSheet("background-color: rgb(52, 73, 85);\n"
        "color: rgb(255, 255, 255);")
        self.checkconnection.setObjectName("checkconnection")
        self.main_continue = QtWidgets.QPushButton(self.centralwidget)
        self.main_continue.setEnabled(False)
        self.main_continue.setGeometry(QtCore.QRect(420, 450, 100, 38))
        self.main_continue.setCheckable(False)
        self.main_continue.setChecked(False)
        self.main_continue.setObjectName("main_continue")
        self.main_continue.clicked.connect(self.continue_pressed)
        self.main_instruct = QtWidgets.QLabel(self.centralwidget)
        self.main_instruct.setGeometry(QtCore.QRect(90, 80, 620, 170))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main_instruct.sizePolicy().hasHeightForWidth())
        self.main_instruct.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.main_instruct.setFont(font)
        self.main_instruct.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.main_instruct.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.checkconnection.clicked.connect(self.connectclicked)                                                                  
        self.main_instruct.setFrameShape(QtWidgets.QFrame.Panel)
        self.main_instruct.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_instruct.setLineWidth(1)
        self.main_instruct.setObjectName("main_instruct")
        Connection.setCentralWidget(self.centralwidget)
        self.actionconnected = QtWidgets.QAction(Connection)
        self.actionconnected.setObjectName("actionconnected")

        self.connection_back = QtWidgets.QPushButton(self.centralwidget)
        self.connection_back.setEnabled(True)
        self.connection_back.setGeometry(QtCore.QRect(280, 450, 100, 38))
        self.connection_back.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        font = QtGui.QFont()
        font.setPointSize(9)
        self.connection_back.setFont(font)
        self.connection_back.setCheckable(False)
        self.connection_back.setChecked(False)
        self.connection_back.setObjectName("bb_back")
        #BeginBench.setCentralWidget(self.centralwidget)
        #self.bb_continue.clicked.connect(self.beginbench_clicked)
        self.connection_back.clicked.connect(self.back_clicked)




        self.retranslateUi(Connection)
        QtCore.QMetaObject.connectSlotsByName(Connection)

    def retranslateUi(self, Connection):
        _translate = QtCore.QCoreApplication.translate
        Connection.setWindowTitle(_translate("Connection", "Connection"))
        self.checkconnection.setText(_translate("Connection", "Check Connection"))
        self.main_continue.setText(_translate("Connection", "Continue"))
        self.main_instruct.setText(_translate("Connection", 
        "To continue, do the following steps:\n"
        "1. Turn on the robot and wait for 2 minutes\n"
        "2. Press the button below"))
        
        #"To continue, do the following steps:\n"
        #"1. Place the robot in the middle of the classroom towards the board\n"
        #"2. Turn on the robot and wait for 2 minutes\n"
        #"3. Press the button below"))        
        self.actionconnected.setText(_translate("Connection", "connected"))
        self.connection_back.setText(_translate("Connection", "Back"))
    def connectclicked(self):
        global sock,port
        try:
           ## Create a TCP/IP socket
           #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           ## Connect the socket to the port where the server is listening
           #server_address = ('192.168.1.200', port)
           #print('connecting to %s port %s' % server_address)
           #sock.connect(server_address)
           connect_status=True
        except:
            print('MU not found')
            connect_status=False
        #connect_status=SU.connection()
        #print('connect pressed')
        #connect_status=True
        if connect_status is True:
            self.main_continue.setEnabled(True)
            self.main_continue.setStyleSheet("background-color: rgb(52, 73, 85);\n"
            "color: rgb(255, 255, 255);")                                          
            self.checkconnection.setEnabled(False)
    def back_clicked(self):
        global newroom_flag,sock
        if newroom_flag==1:
            self.NewRoomWindow = QtWidgets.QMainWindow()
            self.ui = Ui_NewRoomWindow()
            self.ui.setupUi(self.NewRoomWindow)
            app.closeAllWindows()          
            self.NewRoomWindow.show()
            try:
                SU.closeconnection_command(sock)
            except OSError as err:
                print("OS error: {0}".format(err))
            except ValueError:
                print("Could not convert data to an integer.")
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
        else:
            self.Benchlist = QtWidgets.QMainWindow()
            self.ui = Ui_Benchlist()
            self.ui.setupUi(self.Benchlist)
            app.closeAllWindows()
            self.Benchlist.show()
            try:
                SU.closeconnection_command(sock)
            except OSError as err:
                print("OS error: {0}".format(err))
            except ValueError:
                print("Could not convert data to an integer.")
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

    #def openWindow(self):


    def continue_pressed(self):
        #print('pressed')
        #self.MenuWindow = QtWidgets.QMainWindow()
        #self.ui = Ui_MenuWindow()
        #self.ui.setupUi(self.MenuWindow)
        #app.closeAllWindows
        #self.MenuWindow.show()
        self.BeginBench = QtWidgets.QMainWindow()
        self.ui = Ui_BeginBench()
        self.ui.setupUi(self.BeginBench)
        app.closeAllWindows()          
        self.BeginBench.show() 
#end of connection
   
class Ui_MenuWindow(object):
    def setupUi(self, MenuWindow):
        MenuWindow.setObjectName("MenuWindow")
        MenuWindow.resize(800, 600)
        MenuWindow.setStyleSheet("background-color: rgb(35, 47, 52);")
        MenuWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MenuWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.newroom_button = QtWidgets.QPushButton(self.centralwidget)
        self.newroom_button.setGeometry(QtCore.QRect(240, 330, 121, 61))
        self.newroom_button.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.newroom_button.setStyleSheet("background-color: rgb(52, 73, 85);\n"
        "color: rgb(255, 255, 255);")
        self.newroom_button.setObjectName("newroom_button")
        self.oldroom_button = QtWidgets.QPushButton(self.centralwidget)
        self.oldroom_button.setGeometry(QtCore.QRect(430, 330, 121, 61))
        self.oldroom_button.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.oldroom_button.setObjectName("oldroom_button")
        self.acoubot_logo = QtWidgets.QLabel(self.centralwidget)
        self.acoubot_logo.setGeometry(QtCore.QRect(590, 450, 171, 111))
        self.acoubot_logo.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.acoubot_logo.setText("")
        self.acoubot_logo.setPixmap(QtGui.QPixmap("./GUI visual/logo.png"))
        self.acoubot_logo.setScaledContents(True)
        self.acoubot_logo.setObjectName("logo")        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(120, 90, 541, 171))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.label.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.label.setFrameShape(QtWidgets.QFrame.Panel)
        self.label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label.setLineWidth(1)
        self.label.setObjectName("label")
        MenuWindow.setCentralWidget(self.centralwidget)
        self.newroom_button.clicked.connect(self.newroom_clicked)
        self.oldroom_button.clicked.connect(self.oldroom_clicked)
        self.retranslateUi(MenuWindow)
        QtCore.QMetaObject.connectSlotsByName(MenuWindow)

    def retranslateUi(self, MenuWindow):
        _translate = QtCore.QCoreApplication.translate
        MenuWindow.setWindowTitle(_translate("MenuWindow", "MenuWindow"))
        self.newroom_button.setText(_translate("MenuWindow", "New room"))
        self.oldroom_button.setText(_translate("MenuWindow", "Existing room"))
        self.label.setText(_translate("MenuWindow", "Welcome to ACOUBOT\n\n""If the room is tested for the first time,\n"
                            "press the \"New room\" button\n"
                            "if the room has been tested press the \"Existing room\"\n"
                            "button to see previous benchmarks of the room"))

    def oldroom_clicked(self):
        global newroom_flag
        newroom_flag=0
        self.ExistingRoom = QtWidgets.QMainWindow()
        self.ui = Ui_ExistingRoom()
        self.ui.setupUi(self.ExistingRoom)
        app.closeAllWindows()          
        self.ExistingRoom.show()

    def newroom_clicked(self):
        global newroom_flag
        newroom_flag=1
        self.NewRoomWindow = QtWidgets.QMainWindow()
        self.ui = Ui_NewRoomWindow()
        self.ui.setupUi(self.NewRoomWindow)
        app.closeAllWindows()          
        self.NewRoomWindow.show()
#end of menu window

class Ui_NewRoomWindow(object):
    def setupUi(self, NewRoomWindow):
        NewRoomWindow.setObjectName("NewRoomWindow")
        NewRoomWindow.resize(800, 600)
        NewRoomWindow.setStyleSheet("background-color: rgb(35, 47, 52);")
        NewRoomWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(NewRoomWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.nrintstruct = QtWidgets.QLabel(self.centralwidget)
        self.nrintstruct.setGeometry(QtCore.QRect(220, 100, 371, 151))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nrintstruct.sizePolicy().hasHeightForWidth())
        self.nrintstruct.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.nrintstruct.setFont(font)
        self.nrintstruct.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.nrintstruct.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.nrintstruct.setFrameShape(QtWidgets.QFrame.Panel)
        self.nrintstruct.setFrameShadow(QtWidgets.QFrame.Raised)
        self.nrintstruct.setLineWidth(1)
        self.nrintstruct.setObjectName("nrintstruct")
        self.nrtext = QtWidgets.QLineEdit(self.centralwidget)
        self.nrtext.setGeometry(QtCore.QRect(270, 280, 251, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.nrtext.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.nrtext.setFont(font)
        self.nrtext.setAutoFillBackground(False)
        self.nrtext.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.nrtext.setText("")
        self.nrtext.setObjectName("nrtext")
        self.nr_continue = QtWidgets.QPushButton(self.centralwidget)
        self.nr_continue.setEnabled(True)
        self.nr_continue.setStyleSheet("background-color: rgb(52, 73, 85);\n"
           "color: rgb(255, 255, 255);")                 
        self.nr_continue.setGeometry(QtCore.QRect(420, 400, 100, 38))
        self.nr_back = QtWidgets.QPushButton(self.centralwidget)
        self.nr_back.setEnabled(True)
        self.nr_back.setStyleSheet("background-color: rgb(52, 73, 85);\n"
           "color: rgb(255, 255, 255);")                 
        self.nr_back.setGeometry(QtCore.QRect(280, 400, 100, 38))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.nr_continue.setFont(font)
        self.nr_continue.setCheckable(False)
        self.nr_continue.setChecked(False)
        self.nr_continue.setObjectName("nr_continue")
        
        self.nr_back.setFont(font)
        self.nr_back.setCheckable(False)
        self.nr_back.setChecked(False)
        self.nr_back.setObjectName("nr_back")

        NewRoomWindow.setCentralWidget(self.centralwidget)
        self.nr_continue.clicked.connect(self.clicked_continue)
        self.nr_back.clicked.connect(self.clicked_back)
        self.retranslateUi(NewRoomWindow)
        QtCore.QMetaObject.connectSlotsByName(NewRoomWindow)
    #new room

    def retranslateUi(self, NewRoomWindow):
        _translate = QtCore.QCoreApplication.translate
        NewRoomWindow.setWindowTitle(_translate("NewRoomWindow", "NewRoomWindow"))
        self.nrintstruct.setText(_translate("NewRoomWindow", "Enter a room name and press continue"))
        self.nr_continue.setText(_translate("NewRoomWindow", "Continue"))
        self.nr_back.setText(_translate("NewRoomWindow", "Back"))

    def clicked_continue(self):
        global entered_room,benchmark_num
        entered_room=self.nrtext.text()
        if entered_room == '':
            print('enter room name')
        elif os.path.isdir('./Room/'+entered_room) == False:
            benchmark_num=SU.create_directory(entered_room)
            #move to new window that will begin scan
            #transfer benchmark_num and entered_room to new window
            #self.BeginBench = QtWidgets.QMainWindow()
            #self.ui = Ui_BeginBench()
            #self.ui.setupUi(self.BeginBench)
            #app.closeAllWindows()          
            #self.BeginBench.show()
            self.Connection = QtWidgets.QMainWindow()
            self.ui = Ui_Connection()
            self.ui.setupUi(self.Connection)
            app.closeAllWindows()          
            self.Connection.show()         
        else:
            print('Room already exists')
    
    def clicked_back(self):
        self.MenuWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MenuWindow()
        self.ui.setupUi(self.MenuWindow)
        app.closeAllWindows()
        self.MenuWindow.show()   
#end of newroom

class Ui_BeginBench(object):
    def setupUi(self, BeginBench):
        BeginBench.setObjectName("BeginBench")
        BeginBench.resize(800, 600)
        BeginBench.setStyleSheet("background-color: rgb(35, 47, 52);")
        BeginBench.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(BeginBench)
        self.centralwidget.setObjectName("centralwidget")
        self.bsintstruct = QtWidgets.QLabel(self.centralwidget)
        self.bsintstruct.setGeometry(QtCore.QRect(180, 30, 440, 150))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bsintstruct.sizePolicy().hasHeightForWidth())
        self.bsintstruct.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.bsintstruct.setFont(font)
        self.bsintstruct.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.bsintstruct.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.bsintstruct.setFrameShape(QtWidgets.QFrame.Panel)
        self.bsintstruct.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bsintstruct.setLineWidth(1)
        self.bsintstruct.setObjectName("bsintstruct")
        self.bb_continue = QtWidgets.QPushButton(self.centralwidget)
        self.bb_continue.setEnabled(True)
        self.bb_continue.setGeometry(QtCore.QRect(420, 520, 100, 38))
        self.bb_continue.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        font = QtGui.QFont()
        font.setPointSize(9)
        self.bb_continue.setFont(font)
        self.bb_continue.setCheckable(False)
        self.bb_continue.setChecked(False)
        self.bb_continue.setObjectName("bb_continue")

        self.bb_back = QtWidgets.QPushButton(self.centralwidget)
        self.bb_back.setEnabled(True)
        self.bb_back.setGeometry(QtCore.QRect(280, 520, 100, 38))
        self.bb_back.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        font = QtGui.QFont()
        font.setPointSize(9)
        self.bb_back.setFont(font)
        self.bb_back.setCheckable(False)
        self.bb_back.setChecked(False)
        self.bb_back.setObjectName("bb_back")
        BeginBench.setCentralWidget(self.centralwidget)
        self.bb_continue.clicked.connect(self.beginbench_clicked)
        self.bb_back.clicked.connect(self.back_clicked)
        
        self.bench_pic = QtWidgets.QLabel(self.centralwidget)
        self.bench_pic.setGeometry(QtCore.QRect(234, 220, 332, 262))
        self.bench_pic.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.bench_pic.setText("")
        self.bench_pic.setPixmap(QtGui.QPixmap("./GUI visual/instruct.png"))
        self.bench_pic.setScaledContents(True)
        self.bench_pic.setObjectName("map_map")
        
        
        
        self.retranslateUi(BeginBench)
        QtCore.QMetaObject.connectSlotsByName(BeginBench)

    def retranslateUi(self, BeginBench):
        _translate = QtCore.QCoreApplication.translate
        BeginBench.setWindowTitle(_translate("BeginBench", "BeginBench"))
        self.bsintstruct.setText(_translate("BeginBench", "  1. Place the mobile unit 1-1.5 meters away from\n      "
                                    "the speaker\n\n  2. Point the mobile unit's microphone pole towards the\n      "
                                    "speaker\n\n  3. Press The Begin Scan button and leave the room"))
        self.bb_continue.setText(_translate("BeginBench", "Begin Scan"))
        self.bb_back.setText(_translate("BeginBench", "Back"))
    
    def beginbench_clicked(self):
        global entered_room,benchmark_num,sock,newroom_flag,port
        if newroom_flag == 1:
            SU.benchmark(port,entered_room,benchmark_num,sock)
            sock.close()
        else:
            benchmark_num=SU.create_directory(entered_room)       
            SU.benchmark(port,entered_room,benchmark_num,sock)
            sock.close()
        
        #print(entered_room+' '+benchmark_num)

    def back_clicked(self):
        #global newroom_flag
        #if newroom_flag==1:
        #    self.NewRoomWindow = QtWidgets.QMainWindow()
        #    self.ui = Ui_NewRoomWindow()
        #    self.ui.setupUi(self.NewRoomWindow)
        #    app.closeAllWindows()          
        #    self.NewRoomWindow.show()
        #else:
        #    self.Benchlist = QtWidgets.QMainWindow()
        #    self.ui = Ui_Benchlist()
        #    self.ui.setupUi(self.Benchlist)
        #    app.closeAllWindows()
        #    self.Benchlist.show()
        self.Connection = QtWidgets.QMainWindow()
        self.ui = Ui_Connection()
        self.ui.setupUi(self.Connection)
        app.closeAllWindows()          
        self.Connection.show()  
        try:
            SU.closeconnection_command(sock)
        except OSError as err:
            print("OS error: {0}".format(err))
        except ValueError:
            print("Could not convert data to an integer.")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise 
#end of begin bench

class Ui_ExistingRoom(object):
    def setupUi(self, ExistingRoom):
        ExistingRoom.setObjectName("ExistingRoom")
        ExistingRoom.setWindowModality(QtCore.Qt.NonModal)
        ExistingRoom.resize(800, 600)
        ExistingRoom.setStyleSheet("background-color: rgb(35, 47, 52);")
        ExistingRoom.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(ExistingRoom)
        self.centralwidget.setObjectName("centralwidget")
        self.existing_back = QtWidgets.QPushButton(self.centralwidget)
        self.existing_back.setGeometry(QtCore.QRect(280, 500, 100, 38))
        self.existing_back.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.existing_back.setStyleSheet("background-color: rgb(52, 73, 85);\n"
        "color: rgb(255, 255, 255);")
        self.existing_back.clicked.connect(self.back_clicked)
        self.existing_back.setObjectName("existing_back")
        self.existing_continue = QtWidgets.QPushButton(self.centralwidget)
        self.existing_continue.setGeometry(QtCore.QRect(420, 500, 100, 38))
        self.existing_continue.setStyleSheet("background-color: rgb(35, 47, 52);\n"
        "color: rgb(255, 255, 255);")
        self.existing_continue.setEnabled(False)
        self.existing_continue.setObjectName("existing_continue")
        self.existingroom_label = QtWidgets.QLabel(self.centralwidget)
        self.existingroom_label.setGeometry(QtCore.QRect(200, 70, 400, 90))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.existingroom_label.sizePolicy().hasHeightForWidth())
        self.existingroom_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.existingroom_label.setFont(font)
        self.existingroom_label.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.existingroom_label.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.existingroom_label.setFrameShape(QtWidgets.QFrame.Panel)
        self.existingroom_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.existingroom_label.setLineWidth(1)
        self.existingroom_label.setObjectName("existingroom_label")
        self.existingroom_list = QtWidgets.QListWidget(self.centralwidget)
        self.existingroom_list.setGeometry(QtCore.QRect(270, 210, 260, 250))
        self.existingroom_list.setObjectName("existingroom_list")
        roomlist=SU.existing_directory()
        self.existingroom_list.addItems(roomlist)
        self.existingroom_list.setStyleSheet("background-color: rgb(52, 73, 85);\n"
        "color: rgb(255, 255, 255);")
        #self.existing_continue.clicked.connect(self.itemClicked_event)
        self.existingroom_list.itemClicked.connect(self.item_click)
        ExistingRoom.setCentralWidget(self.centralwidget)

        self.retranslateUi(ExistingRoom)
        QtCore.QMetaObject.connectSlotsByName(ExistingRoom)

    def retranslateUi(self, ExistingRoom):
        _translate = QtCore.QCoreApplication.translate
        ExistingRoom.setWindowTitle(_translate("ExistingRoom", "ExistingRoom"))
        self.existing_back.setText(_translate("ExistingRoom", "Back"))
        self.existing_continue.setText(_translate("ExistingRoom", "Continue"))
        self.existingroom_label.setText(_translate("ExistingRoom", "Choose a room from the list and press Continue"))

    
    def item_click(self, item):
        global entered_room
        entered_room=str(item.text())
        self.existing_continue.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.existing_continue.setEnabled(True)
        self.existing_continue.clicked.connect(self.continue_clicked)
    
    def continue_clicked(self):
        global entered_room
        self.Benchlist = QtWidgets.QMainWindow()
        self.ui = Ui_Benchlist()
        self.ui.setupUi(self.Benchlist)
        app.closeAllWindows()
        self.Benchlist.show()
    
    def back_clicked(self):
        self.MenuWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MenuWindow()
        self.ui.setupUi(self.MenuWindow)
        app.closeAllWindows()
        self.MenuWindow.show()   
#end of existingRoom

class Ui_Benchlist(object):
    def setupUi(self, Benchlist):
        global entered_room
        benchlist=SU.existing_bench(entered_room)
        Benchlist.setObjectName("Benchlist")
        Benchlist.setWindowModality(QtCore.Qt.NonModal)
        Benchlist.resize(800, 600)
        Benchlist.setStyleSheet("background-color: rgb(35, 47, 52);")
        Benchlist.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(Benchlist)
        self.centralwidget.setObjectName("centralwidget")
        self.bench_back = QtWidgets.QPushButton(self.centralwidget)
        self.bench_back.setGeometry(QtCore.QRect(200, 500, 100, 38))
        self.bench_back.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.bench_back.setStyleSheet("background-color: rgb(52, 73, 85);\n"
        "color: rgb(255, 255, 255);")
        self.bench_back.setObjectName("bench_back")
        self.bench_New = QtWidgets.QPushButton(self.centralwidget)
        self.bench_New.setGeometry(QtCore.QRect(500, 500, 100, 38))
        self.bench_New.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.bench_New.setObjectName("bench_New")
        self.bench_label = QtWidgets.QLabel(self.centralwidget)
        self.bench_label.setGeometry(QtCore.QRect(200, 70, 400, 90))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bench_label.sizePolicy().hasHeightForWidth())
        self.bench_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.bench_label.setFont(font)
        self.bench_label.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.bench_label.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.bench_label.setFrameShape(QtWidgets.QFrame.Panel)
        self.bench_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bench_label.setLineWidth(1)
        self.bench_label.setObjectName("bench_label")
        self.bench_list = QtWidgets.QListWidget(self.centralwidget)
        self.bench_list.setGeometry(QtCore.QRect(270, 210, 260, 250))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 47, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 47, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 47, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 47, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 47, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 47, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 47, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 47, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 47, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.bench_list.setPalette(palette)
        self.bench_list.setObjectName("bench_list")
        self.bench_Display = QtWidgets.QPushButton(self.centralwidget)
        self.bench_Display.setGeometry(QtCore.QRect(350, 500, 100, 38))
        #self.bench_Display.setStyleSheet("color: rgb(255, 255, 255);\n"
        #"background-color: rgb(52, 73, 85);")
        self.bench_Display.setStyleSheet("background-color: rgb(35, 47, 52);\n"
        "color: rgb(255, 255, 255);")
        self.bench_Display.setEnabled(False)        
        self.bench_Display.setObjectName("bench_Display")
        Benchlist.setCentralWidget(self.centralwidget)
        self.bench_back.clicked.connect(self.back_clicked)
        self.bench_New.clicked.connect(self.New_clicked)
        self.bench_list.addItems(benchlist)
        self.bench_list.setStyleSheet("background-color: rgb(52, 73, 85);\n"
        "color: rgb(255, 255, 255);")
        self.retranslateUi(Benchlist)
        QtCore.QMetaObject.connectSlotsByName(Benchlist)

        self.bench_list.itemClicked.connect(self.selected_bench)

    def retranslateUi(self, Benchlist):
        _translate = QtCore.QCoreApplication.translate
        Benchlist.setWindowTitle(_translate("Benchlist", "Benchlist"))
        self.bench_back.setText(_translate("Benchlist", "Back"))
        self.bench_New.setText(_translate("Benchlist", "New Benchmark"))
        self.bench_label.setText(_translate("Benchlist", "Select a benchmark from the benchmark list below\n"
        "to display results, or perform a new benchmark"))
        self.bench_Display.setText(_translate("Benchlist", "Display Results"))
    
    def selected_bench(self, item):
        global benchmark_num
        benchmark_num=str(item.text())
        self.bench_Display.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.bench_Display.setEnabled(True)
        self.bench_Display.clicked.connect(self.Show_Room)


    def back_clicked(self):
        self.ExistingRoom = QtWidgets.QMainWindow()
        self.ui = Ui_ExistingRoom()
        self.ui.setupUi(self.ExistingRoom)
        app.closeAllWindows()          
        self.ExistingRoom.show()

    def New_clicked(self):
        #move to new window that will begin scan
        #transfer benchmark_num and entered_room to new window
        #self.BeginBench = QtWidgets.QMainWindow()
        #self.ui = Ui_BeginBench()
        #self.ui.setupUi(self.BeginBench)
        #app.closeAllWindows()          
        #self.BeginBench.show()   
        self.Connection = QtWidgets.QMainWindow()
        self.ui = Ui_Connection()
        self.ui.setupUi(self.Connection)
        app.closeAllWindows()          
        self.Connection.show()        
    
    def Show_Room(self):
        self.Display_Map = QtWidgets.QMainWindow()
        self.ui = Ui_Display_Map()
        self.ui.setupUi(self.Display_Map)
        app.closeAllWindows()
        self.Display_Map.show()
        
#end of benchlist    

class Ui_Display_Map(object):
    def setupUi(self, Display_Map):
        Display_Map.setObjectName("Display_Map")
        Display_Map.setWindowModality(QtCore.Qt.NonModal)
        Display_Map.resize(800, 600)
        Display_Map.setStyleSheet("background-color: rgb(35, 47, 52);")
        Display_Map.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(Display_Map)
        self.centralwidget.setObjectName("centralwidget")
        self.map_new = QtWidgets.QPushButton(self.centralwidget)
        self.map_new.setGeometry(QtCore.QRect(420, 500, 100, 38))
        self.map_new.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.map_new.setObjectName("map_new")
        self.map_label = QtWidgets.QLabel(self.centralwidget)
        self.map_label.setGeometry(QtCore.QRect(240, 105, 320, 90))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.map_label.sizePolicy().hasHeightForWidth())
        self.map_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.map_label.setFont(font)
        self.map_label.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.map_label.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.map_label.setFrameShape(QtWidgets.QFrame.Panel)
        self.map_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.map_label.setLineWidth(1)
        self.map_label.setObjectName("map_label")
        
        self.map_room_label = QtWidgets.QLabel(self.centralwidget)
        self.map_room_label.setGeometry(QtCore.QRect(275, 30, 250, 50))
        self.map_room_label.setFont(font)
        self.map_room_label.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.map_room_label.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.map_room_label.setFrameShape(QtWidgets.QFrame.Panel)
        self.map_room_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.map_room_label.setLineWidth(1)
        self.map_room_label.setObjectName("map_room_label")

        self.map_roomlist = QtWidgets.QPushButton(self.centralwidget)
        self.map_roomlist.setGeometry(QtCore.QRect(280, 500, 100, 38))
        self.map_roomlist.setStyleSheet("color: rgb(255, 255, 255);\n"
        "background-color: rgb(52, 73, 85);")
        self.map_roomlist.setObjectName("map_roomlist")
        self.map_map = QtWidgets.QLabel(self.centralwidget)
        self.map_map.setGeometry(QtCore.QRect(234, 220, 332, 262))
        self.map_map.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.map_map.setText("")
        self.map_map.setPixmap(QtGui.QPixmap("./GUI visual/Picture1.png"))
        self.map_map.setScaledContents(True)
        self.map_map.setObjectName("map_map")
        self.point1 = QtWidgets.QPushButton(self.centralwidget)
        self.point1.setGeometry(QtCore.QRect(483, 320, 42, 42))
        self.point1.setStyleSheet("background:transparent;")
        self.point1.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./GUI visual/point 1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.point1.setIcon(icon)
        self.point1.setIconSize(QtCore.QSize(30, 30))
        self.point1.setObjectName("point1")
        
        self.point2 = QtWidgets.QPushButton(self.centralwidget)
        self.point2.setGeometry(QtCore.QRect(275, 320, 42, 42))
        self.point2.setStyleSheet("background:transparent;")
        self.point2.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("./GUI visual/point 2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.point2.setIcon(icon1)
        self.point2.setIconSize(QtCore.QSize(30, 30))
        self.point2.setObjectName("point2")
        self.point4 = QtWidgets.QPushButton(self.centralwidget)
        self.point4.setGeometry(QtCore.QRect(275, 420, 42, 42))
        self.point4.setStyleSheet("background:transparent;")
        self.point4.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("./GUI visual/point 4.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.point4.setIcon(icon2)
        self.point4.setIconSize(QtCore.QSize(30, 30))
        self.point4.setObjectName("point4")
        self.point5 = QtWidgets.QPushButton(self.centralwidget)
        self.point5.setGeometry(QtCore.QRect(483, 420, 42, 42))
        self.point5.setStyleSheet("background:transparent;")
        self.point5.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("./GUI visual/point 5.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.point5.setIcon(icon3)
        self.point5.setIconSize(QtCore.QSize(30, 30))
        self.point5.setObjectName("point5")
        self.point3 = QtWidgets.QPushButton(self.centralwidget)
        self.point3.setGeometry(QtCore.QRect(379, 370, 42, 42))
        self.point3.setStyleSheet("background:transparent;")
        self.point3.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("./GUI visual/point 3.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.point3.setIcon(icon4)
        self.point3.setIconSize(QtCore.QSize(30, 30))
        self.point3.setObjectName("point3")
        Display_Map.setCentralWidget(self.centralwidget)
        self.point1.clicked.connect(self.point1_pressed)
        self.point3.clicked.connect(self.point3_pressed)
        self.retranslateUi(Display_Map)
        QtCore.QMetaObject.connectSlotsByName(Display_Map)

    def retranslateUi(self, Display_Map):
        global benchmark_num,entered_room
        _translate = QtCore.QCoreApplication.translate
        Display_Map.setWindowTitle(_translate("Display_Map", "Display_Map"))
        self.map_new.setText(_translate("Display_Map", "New Benchmark"))
        self.map_label.setText(_translate("Display_Map", "Click on the points to display problems\n"
        "and solutions."))
        self.map_room_label.setText(_translate("Display_Map",entered_room+' - '+benchmark_num))
        self.map_roomlist.setText(_translate("Display_Map", "Room List"))
    
    def point1_pressed(self):
        
        self.point1 = QtWidgets.QFrame()
        self.ui = Ui_point1()
        self.ui.setupUi(self.point1)
        self.point1.show()
    def point3_pressed(self):
        
        self.point3 = QtWidgets.QFrame()
        self.ui = Ui_point3()
        self.ui.setupUi(self.point3)
        self.point3.show()        
        
    

class Ui_point1(object):
    def setupUi(self, point1):
        point1.setObjectName("point1")
        point1.resize(442, 158)
        self.label = QtWidgets.QLabel(point1)
        self.label.setGeometry(QtCore.QRect(50, 20, 351, 81))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(point1)
        self.pushButton.setGeometry(QtCore.QRect(320, 110, 75, 23))
        self.pushButton.setObjectName("pushButton")
        #self.pushButton.clicked.connect(self.point1_clicked)
        self.pushButton.clicked.connect(point1.close)
        self.retranslateUi(point1)
        QtCore.QMetaObject.connectSlotsByName(point1)

    def retranslateUi(self, point1):
        _translate = QtCore.QCoreApplication.translate
        point1.setWindowTitle(_translate("point1", "point1"))
        self.label.setText(_translate("point1", "Loud noise detected at this point\n"
        "\n"
        "Check the Air Conditioner to reduce noise"))
        self.pushButton.setText(_translate("point1", "Close"))

class Ui_point3(object):
    def setupUi(self, point3):
        point3.setObjectName("point3")
        point3.resize(442, 158)
        self.label = QtWidgets.QLabel(point3)
        self.label.setGeometry(QtCore.QRect(50, 20, 351, 81))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(point3)
        self.pushButton.setGeometry(QtCore.QRect(320, 110, 75, 23))
        self.pushButton.setObjectName("pushButton")
        #self.pushButton.clicked.connect(self.point3_clicked)
        self.pushButton.clicked.connect(point3.close)
        self.retranslateUi(point3)
        QtCore.QMetaObject.connectSlotsByName(point3)

    def retranslateUi(self, point3):
        _translate = QtCore.QCoreApplication.translate
        point3.setWindowTitle(_translate("point3", "point 3"))
        self.label.setText(_translate("point3", "High Revebration Time\n"
        "\n"
        "Hang on the wall 15 [m^2] of 2 [inch] acoustic foam\npanel to reduce Reverbration time"))
        self.pushButton.setText(_translate("point3", "Close"))
    

    #def close(self):
    #   self.point1.close()

    
#end of Display Map



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MenuWindow = QtWidgets.QMainWindow()
    ui = Ui_MenuWindow()
    ui.setupUi(MenuWindow)
    MenuWindow.show()
    sys.exit(app.exec_())
   
    
    
    
    
    