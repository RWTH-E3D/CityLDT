"""
The City-LoD-Transformation-Tool (CityLDT) aims to easily scale CityGML models between differing Levels of Detail (LoD).
The main focus is to enrich lower level buildings to a higher level of detail with user entered data; reducing complexety is also envisioned.
This tool was developed for Python 3.5+ using PySide2. A detailed list of the required libraries can be found in the README.
"""



# import of libraries
import os
import sys
import PySide2
from PySide2 import QtWidgets, QtGui, QtCore
import time

# import of functions
import gui_functions as gf
import LDTselection as sel
import LDTtransformation as ldt


# setting system environment variable
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path



# positions and dimensions of window
posx = 275
posy = 100
width = 800
height = 800
sizefactor = 0
sizer = True

# path of script
pypath = os.path.dirname(os.path.realpath(__file__))


buildingDict = {}
selAll = True
inpDir = ''
buildingOverWrDict = {-1: {'LoD': None, 'rType': None, 'bFunction': None, 'SAG': None, 'SBG': None, 'YOC': None, 'rHeight': None, 'rHeading': None, 'bHeight': None}}
buildingParamsDict = {-1: {'LoD': None, 'rType': None, 'bFunction': None, 'SAG': None, 'SBG': None, 'YOC': None, 'rHeight': None, 'rHeading': None, 'bHeight': None}}



buildingFunctions = {'': 0, 'residential building': 1000, 'tenement': 1010, 'hostel': 1020, 'residential- and administration building': 1030, 'residential- and office building': 1040,
                     'residential- and business building': 1050, 'residential- and plant building': 1060, 'agrarian- and forestry building': 1070, 'residential- and commercial building': 1080,
                     "forester's lodge": 1090, 'holiday house': 1100, 'summer house': 1110, 'office building': 1120, 'credit institution': 1130, 'insurance': 1140, 'business building': 1150,
                     'department store': 1160, 'shopping centre': 1170, 'kiosk': 1180, 'pharmacy': 1190, 'pavilion': 1200, 'hotel': 1210, 'youth hostel': 1220, 'campsite building': 1230,
                     'restaurant': 1240, 'cantine': 1250, 'recreational site': 1260, 'function room': 1270, 'cinema': 1280, 'bowling alley': 1290, 'casino': 1300, 'industrial building': 1310,
                     'factory': 1320, 'workshop': 1330, 'petrol / gas station': 1340, 'washing plant': 1350, 'cold store': 1360, 'depot': 1370, 'building for research purposes': 1380,
                     'quarry': 1390, 'salt works': 1400, 'miscellaneous industrial building': 1410, 'mill': 1420, 'windmill': 1430, 'water mill': 1440, 'bucket elevator': 1450,
                     'weather station': 1460, 'traffic assets office': 1470, 'street maintenance': 1480, 'waiting hall': 1490, 'signal control box': 1500, 'engine shed': 1510,
                     'signal box or stop signal': 1520, 'plant building for air traffic': 1530, 'hangar': 1540, 'plant building for shipping': 1550, 'shipyard': 1560, 'dock': 1570,
                     'plant building for canal lock': 1580, 'boathouse': 1590, 'plant building for cablecar': 1600, 'multi-storey car park': 1610, 'parking level': 1620, 'garage': 1630,
                     'vehicle hall': 1640, 'underground garage': 1650, 'building for supply': 1660, 'waterworks': 1670, 'pump station': 1680, 'water basin': 1690, 'electric power station': 1700,
                     'transformer station': 1710, 'converter': 1720, 'reactor': 1730, 'turbine house': 1740, 'boiler house': 1750, 'building for telecommunications': 1760, 'gas works': 1770,
                     'heat plant': 1780, 'pumping station': 1790, 'building for disposal': 1800, 'building for effluent disposal': 1810, 'building for filter plant': 1820, 'toilet': 1830,
                     'rubbish bunker': 1840, 'building for rubbish incineration': 1850, 'building for rubbish disposal': 1860, 'building for agrarian and forestry': 1870, 'barn': 1880,
                     'stall': 1890, 'equestrian hall': 1900, 'alpine cabin': 1910, 'hunting lodge': 1920, 'arboretum': 1930, 'glass house': 1940, 'moveable glass house': 1950,
                     'public building': 1960, 'administration building': 1970, 'parliament': 1980, 'guildhall': 1990, 'post office': 2000, 'customs office': 2010, 'court': 2020,
                     'embassy or consulate': 2030, 'district administration': 2040, 'district government': 2050, 'tax office': 2060, 'building for education and research': 2070,
                     'comprehensive school': 2080, 'vocational school': 2090, 'college or university': 2100, 'research establishment': 2110, 'building for cultural purposes': 2120,
                     'castle': 2130, 'theatre or opera': 2140, 'concert building': 2150, 'museum': 2160, 'broadcasting building': 2170, 'activity building': 2180, 'library': 2190,
                     'fort': 2200, 'religious building': 2210, 'church': 2220, 'synagogue': 2230, 'chapel': 2240, 'community center ': 2250, 'place of worship': 2260, 'mosque': 2270,
                     'temple': 2280, 'convent': 2290, 'building for health care': 2300, 'hospital': 2310, 'healing centre or care home': 2320, 'health centre or outpatients clinic': 2330,
                     'building for social purposes': 2340, 'youth centre': 2350, 'seniors centre': 2360, 'homeless shelter': 2370, 'kindergarten or nursery': 2380, 'asylum seekers home': 2390,
                     'police station': 2400, 'fire station': 2410, 'barracks': 2420, 'bunker': 2430, 'penitentiary or prison': 2440, 'cemetery building': 2450, 'funeral parlor': 2460,
                     'crematorium': 2470, 'train station': 2480, 'airport building': 2490, 'building for underground station': 2500, 'building for tramway': 2510, 'building for bus station': 2520,
                     'shipping terminal': 2530, 'building for recuperation purposes': 2540, 'building for sport purposes': 2550, 'sports hall': 2560, 'building for sports field': 2570,
                     'swimming baths': 2580, 'indoor swimming pool': 2590, 'sanatorium': 2600, 'zoo building': 2610, 'green house': 2620, 'botanical show house': 2630, 'bothy': 2640,
                     'tourist information centre': 2650, 'others': 2700}



class mainWindow(QtWidgets.QWidget):
    """mainWindow class"""
    def __init__(self):
        #initiate the parent
        super(mainWindow,self).__init__()
        self.initUI()


    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer
        if sizer:
            posx, posy, width, height, sizefactor = gf.screenSizer(self, posx, posy, width, height, app)
            sizer = False
        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityLDT - CityGML LoD Transformation Tool - Selection')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)

        # grid layout for file selection
        self.uGrid = QtWidgets.QGridLayout()

        self.btn_selFile = QtWidgets.QPushButton('Select file')
        self.uGrid.addWidget(self.btn_selFile, 0, 0, 1, 1)

        self.btn_selDir = QtWidgets.QPushButton('Select folder')
        self.uGrid.addWidget(self.btn_selDir, 0, 1, 1, 1)

        self.txtB_inPath = QtWidgets.QLineEdit()
        self.txtB_inPath.setPlaceholderText('Path to file or folder')
        self.txtB_inPath.setReadOnly(True)
        self.uGrid.addWidget(self.txtB_inPath, 0, 2, 1, 4)

        self.lbl_scanLoD = QtWidgets.QLabel('LoD scan progress:')
        self.uGrid.addWidget(self.lbl_scanLoD, 1, 0, 1, 1)

        self.pB_scanLoD = QtWidgets.QProgressBar(self)
        self.uGrid.addWidget(self.pB_scanLoD, 1, 1, 1, 5)

        self.vbox.addLayout(self.uGrid)

        # for selecting all or individual buildings
        self.gB_buildings = QtWidgets.QGroupBox('')
        self.vbox.addWidget(self.gB_buildings)
        # self.gB_buildings.setToolTip('When unchecked transformation will be done for all buildings in the file(s)')

        self.bGrid = QtWidgets.QGridLayout()
        self.gB_buildings.setLayout(self.bGrid)

        self.rb_allBuildings = QtWidgets.QRadioButton('Transform all buildings')
        self.bGrid.addWidget(self.rb_allBuildings, 0, 0, 1, 1)
        self.rb_allBuildings.setChecked(selAll)

        self.rb_selectBuildings = QtWidgets.QRadioButton('Select individual buildings')
        self.bGrid.addWidget(self.rb_selectBuildings, 0, 3, 1, 1)
        self.rb_selectBuildings.setChecked(not selAll)


        self.tbl_buildings = QtWidgets.QTableWidget()
        self.tbl_buildings.setColumnCount(4)
        self.tbl_buildings.setHorizontalHeaderLabels(['File Name', 'Name of Building', 'Level of Detail (LoD)', ''])
        self.tbl_buildings.verticalHeader().hide()
        # self.tbl_buildings.horizontalHeader().hide()
        self.tbl_buildings.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl_buildings.setEnabled(False)
        self.tbl_buildings.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tbl_buildings.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tbl_buildings.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.bGrid.addWidget(self.tbl_buildings, 1, 0, 1, 6)

        # Gridbox for lower grid
        self.lGrid = QtWidgets.QGridLayout()

        self.btn_about = QtWidgets.QPushButton('About')
        self.lGrid.addWidget(self.btn_about, 0, 0, 1, 1)

        self.btn_reset = QtWidgets.QPushButton('Reset')
        self.lGrid.addWidget(self.btn_reset, 0, 1, 1, 1)

        self.btn_exit = QtWidgets.QPushButton('Exit')
        self.lGrid.addWidget(self.btn_exit, 0, 2, 1, 1)

        self.btn_next = QtWidgets.QPushButton('Next')
        self.lGrid.addWidget(self.btn_next, 0, 3, 1, 1)
        self.btn_next.setEnabled(False)

        self.vbox.addLayout(self.lGrid)

        self.btn_selFile.clicked.connect(self.func_selectFile)
        self.btn_selDir.clicked.connect(self.func_selectDir)
        self.rb_selectBuildings.toggled.connect(self.func_selB)

        self.btn_about.clicked.connect(self.func_about)
        self.btn_reset.clicked.connect(self.func_reset)
        self.btn_exit.clicked.connect(self.func_exit)
        self.btn_next.clicked.connect(self.func_next)




        # setting some defaults
        self.inpPath = ''
        self.inpDir = inpDir
        self.expPath = ''
        self.buildingDict = {}
        self.completedLoD = 0
        self.cBoxes = []

        # table row index to comboBox index
        self.tableDict = {}

        global buildingDict
        if self.inpDir != '':
            self.txtB_inPath.setText(self.inpDir)
        if buildingDict != {}:
            self.btn_next.setEnabled(True)
            resultsDict = {}
            selected = []
            for i in buildingDict:
                if buildingDict[i]["filename"] not in resultsDict:
                    resultsDict[buildingDict[i]["filename"]] = {}
                else:
                    pass
                resultsDict[buildingDict[i]["filename"]][buildingDict[i]["buildingname"]] = buildingDict[i]["values"]
                selected.append(buildingDict[i]['selected'])
            sel.display_file_lod(self, resultsDict)
            for i, state in enumerate(selected):
                self.cBoxes[i].setChecked(state)
            gf.progressLoD(self, 100)




    def func_selectFile(self):
        res = sel.select_gml(self)
        if res:
            self.inpPath = res
            self.inpDir = os.path.dirname(res)
            sel.get_files(self)
        else:
            pass


    def func_selectDir(self):
        res = sel.select_folder(self)
        if res:
            self.inpPath = res
            self.inpDir = res
            sel.get_files(self)
        else:
            pass


    def func_selB(self):
        if self.rb_selectBuildings.isChecked():
            self.tbl_buildings.setEnabled(True)
        else:
            self.tbl_buildings.setEnabled(False)


    def func_about(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, about(), False)


    def func_reset(self):
        global posx, posy
        self.reset_variables()
        posx, posy = gf.dimensions(self)
        gf.next_window(self, mainWindow())


    def reset_variables(self):
        self.inpPath = ''
        self.inpDir = ''
        self.buildingDict = {}
        self.completedLoD = 0
        self.cBoxes = []



    def func_exit(self):
        gf.close_application(self)

    
    def func_next(self):
        global buildingDict, selAll, inpDir, posx, posy
        inpDir = self.inpDir
        selAll = self.rb_allBuildings.isChecked()
        buildingDict = self.buildingDict
        selection = 0
        for key in buildingDict:
            selection += buildingDict[key]["selected"]
        if selAll or selection > 0:
            posx, posy = gf.dimensions(self)
            gf.next_window(self, transformation())
        else:
            gf.messageBox(self, "Important", "Please select at least one building.")



    def onStateChanged(self):
        """gets called when a checkbox for a building is (un)checked to update the buildingDict"""
        ch = self.sender()
        ix = self.tbl_buildings.indexAt(ch.pos())
        self.buildingDict[ix.row()]["selected"] = ch.isChecked()
        curText = self.tbl_buildings.item(ix.row(), 1).text().split('/')[0]
        for i in range(self.tbl_buildings.rowCount()):
            if i != ix.row():
                if self.tbl_buildings.item(i, 1).text().split('/')[0] == curText:
                    self.cBoxes[i].setChecked(ch.isChecked())
                    self.buildingDict[i]["selected"] = ch.isChecked()




class transformation(QtWidgets.QWidget):
    """window for transformation options"""
    def __init__(self):
        super(transformation, self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer, buildingParamsDict
        if sizer:
            posx, posy, width, height, sizefactor = gf.screenSizer(self, posx, posy, width, height, app)
            sizer = False
        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityLDT - CityGML LoD Transformation Tool - Transformation')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)

        self.uGrid = QtWidgets.QGridLayout()

        self.vbox.addLayout(self.uGrid)
        

        ttl = 'Building parameters - ' + str(len(buildingDict)) + ' buildings'
        # building parameters
        self.gB_buildingParameters = QtWidgets.QGroupBox(ttl)
        self.vbox.addWidget(self.gB_buildingParameters)
        self.vBox_forBPgB = QtWidgets.QVBoxLayout()
        self.gB_buildingParameters.setLayout(self.vBox_forBPgB)

        # building selection
        self.pGrid = QtWidgets.QGridLayout()

        self.lbl_curBuilding = QtWidgets.QLabel('Current building:')
        self.pGrid.addWidget(self.lbl_curBuilding, 0, 0, 1, 1)

        self.cB_curBuilding = QtWidgets.QComboBox()
        self.cB_curBuilding.addItems(['all (selected) buildings'])
        self.pGrid.addWidget(self.cB_curBuilding, 0, 1, 1, 2)

        presenetLoDs = []
        # adding selected buildings to the comboBox
        for key in buildingDict:
            if selAll:
                self.cB_curBuilding.insertItem(self.cB_curBuilding.count(), buildingDict[key]["filename"] + "/" + buildingDict[key]["buildingname"])
                if buildingDict[key]["values"]["LoD"] not in presenetLoDs:
                    presenetLoDs.append(buildingDict[key]["values"]["LoD"])
            elif buildingDict[key]["selected"]:
                self.cB_curBuilding.insertItem(self.cB_curBuilding.count(), buildingDict[key]["filename"] + "/" + buildingDict[key]["buildingname"])
                if buildingDict[key]["values"]["LoD"] not in presenetLoDs:
                    presenetLoDs.append(buildingDict[key]["values"]["LoD"])
            else:
                pass
        self.buildingDict = buildingDict
        
        # update title of groubbox according to number of buildings
        ttl = 'Building parameters - ' + str(self.cB_curBuilding.count()-1) + ' buildings'
        self.gB_buildingParameters.setTitle(ttl)



        self.vBox_forBPgB.addLayout(self.pGrid)

        # geometry properties
        self.gB_geometry = QtWidgets.QGroupBox('Geometry parameters')
        self.vBox_forBPgB.addWidget(self.gB_geometry)

        self.gGrid = QtWidgets.QGridLayout()
        self.gB_geometry.setLayout(self.gGrid)

        self.lbl_buildingHeight = QtWidgets.QLabel('Building height:')
        self.gGrid.addWidget(self.lbl_buildingHeight, 0, 0, 1, 1)

        self.txtB_buildingHeight = QtWidgets.QLineEdit('')
        self.txtB_buildingHeight.setPlaceholderText('Building height in m')
        self.txtB_buildingHeight.setToolTip('Difference in height from base plate to the highest point of the roof')
        self.gGrid.addWidget(self.txtB_buildingHeight, 0, 1, 1, 1)

        self.lbl_roofHeight = QtWidgets.QLabel('Roof height:')
        self.gGrid.addWidget(self.lbl_roofHeight, 0, 2, 1, 1)

        self.txtB_roofHeight = QtWidgets.QLineEdit('')
        self.txtB_roofHeight.setPlaceholderText('Roof height in m')
        self.txtB_roofHeight.setToolTip('Difference in height from lowest to highest point of the roof')
        self.gGrid.addWidget(self.txtB_roofHeight, 0, 3, 1, 1)

        self.lbl_roofType = QtWidgets.QLabel('Roof type:')
        self.gGrid.addWidget(self.lbl_roofType, 1, 0, 1, 1)

        self.cB_roofType = QtWidgets.QComboBox()
        self.cB_roofType.setFont(QtGui.QFont("Consolas"))
        self.cB_roofType.setToolTip('List of available roof types')
        self.cB_roofType.addItems(['', 'flat roof :      1000', 'monopitch roof : 1010', 'dual pent roof : 1020', 'gabled roof :    1030', 'hipped roof :    1040', 'pavilion roof :  1070'])
        self.gGrid.addWidget(self.cB_roofType, 1, 1, 1, 1)

        self.lbl_roofHeading = QtWidgets.QLabel('Roof heading:')
        self.gGrid.addWidget(self.lbl_roofHeading, 1, 2, 1, 1)

        self.cB_heading = QtWidgets.QComboBox()
        self.cB_heading.setToolTip('Orientation of the roof ridge')
        self.gGrid.addWidget(self.cB_heading, 1, 3, 1, 1)
        self.cB_heading.addItems(['', 'NORTHish', 'EASTish', 'SOUTHish', 'WESTish'])

        # building info
        self.gB_attrib = QtWidgets.QGroupBox('Building attributes')
        self.vBox_forBPgB.addWidget(self.gB_attrib)

        self.aGrid = QtWidgets.QGridLayout()
        self.gB_attrib.setLayout(self.aGrid)
        
        self.lbl_buildingFunction = QtWidgets.QLabel('Building function:')
        self.aGrid.addWidget(self.lbl_buildingFunction, 0, 0, 1, 1)

        self.cB_buildingFunction = QtWidgets.QComboBox()
        self.cB_buildingFunction.setFont(QtGui.QFont("Consolas"))
        self.cB_buildingFunction.setToolTip('List of available building functions')
        self.cB_buildingFunction.addItems(gf.createListForComboBox(buildingFunctions, 40))
        self.aGrid.addWidget(self.cB_buildingFunction, 0, 1, 1, 1)

        self.lbl_yearOfConstruction = QtWidgets.QLabel('Year of construction:')
        self.aGrid.addWidget(self.lbl_yearOfConstruction, 0, 2, 1, 1)

        self.txtB_yearOfConstruction = QtWidgets.QLineEdit()
        self.aGrid.addWidget(self.txtB_yearOfConstruction, 0, 3, 1, 1)
        
        self.lbl_SAG = QtWidgets.QLabel('Storeys above ground:')
        self.aGrid.addWidget(self.lbl_SAG, 1, 0, 1, 1)

        self.txtB_SAG = QtWidgets.QLineEdit('')
        self.txtB_SAG.setToolTip('Sets the value for the storeysAboveGround CityGML attribute')
        self.aGrid.addWidget(self.txtB_SAG, 1, 1, 1, 1)

        self.lbl_SBG = QtWidgets.QLabel('Storeys below ground:')
        self.aGrid.addWidget(self.lbl_SBG, 1, 2, 1, 1)
        
        self.txtB_SBG = QtWidgets.QLineEdit('')
        self.txtB_SBG.setToolTip('Sets the value for the storeysBelowGround CityGML attribute')
        self.aGrid.addWidget(self.txtB_SBG, 1, 3, 1, 1)

        self.p2Grid = QtWidgets.QGridLayout()

        self.spacer = QtWidgets.QLabel('')
        self.p2Grid.addWidget(self.spacer, 0, 0, 1, 2)

        self.btn_overwrite = QtWidgets.QPushButton('Enable overwrite')
        self.p2Grid.addWidget(self.btn_overwrite, 0, 0, 1, 1)
        self.btn_overwrite.setEnabled(True)

        self.btn_saveBuildingParams = QtWidgets.QPushButton('Save building parameters')
        self.p2Grid.addWidget(self.btn_saveBuildingParams, 0, 3, 1, 1)

        self.vBox_forBPgB.addLayout(self.p2Grid)


        # export GUI elements
        self.lGrid = QtWidgets.QGridLayout()

        self.lbl_export  = QtWidgets.QLabel('Save buildings:')
        self.lGrid.addWidget(self.lbl_export, 0, 0, 1, 3)

        self.rB_oldAndNew = QtWidgets.QRadioButton('Transformed and remaining buildings')
        self.lGrid.addWidget(self.rB_oldAndNew, 0, 3, 1, 3)

        self.rB_onlyTransformed = QtWidgets.QRadioButton('Only transformed buildings')
        self.lGrid.addWidget(self.rB_onlyTransformed, 0, 6, 1, 3)
        self.rB_onlyTransformed.setChecked(True)

        self.rB_individualFiles = QtWidgets.QRadioButton('Individual files per building')
        self.lGrid.addWidget(self.rB_individualFiles, 0, 9, 1, 3)
        # self.rB_individualFiles.setEnabled(False)

        self.btn_outDir = QtWidgets.QPushButton('Select output path')
        self.lGrid.addWidget(self.btn_outDir, 2, 0, 1, 4)

        self.txtB_outDir = QtWidgets.QLineEdit()
        self.txtB_outDir.setPlaceholderText('Path to which new file should be written')
        self.lGrid.addWidget(self.txtB_outDir, 2, 4, 1, 8)

        self.expPath = os.path.join(inpDir, 'e3D_CityLDT')
        self.txtB_outDir.setText(self.expPath)


        self.btn_toZero = QtWidgets.QPushButton('Transform to LoD 0')
        self.lGrid.addWidget(self.btn_toZero, 3, 0, 1, 4)
        self.btn_toZero.setToolTip("requires ground surface coordinates")
        if 1 in presenetLoDs or 2 in presenetLoDs:
            self.btn_toZero.setEnabled(True)
        else:
            self.btn_toZero.setEnabled(False)

        self.btn_toOne = QtWidgets.QPushButton('Transform to LoD 1')
        self.lGrid.addWidget(self.btn_toOne, 3, 4, 1, 4)
        self.btn_toOne.setToolTip("requires ground surface coordinates and building height")
        if 0 in presenetLoDs or 2 in presenetLoDs:
            self.btn_toOne.setEnabled(True)
        else:
            self.btn_toOne.setEnabled(False)

        self.btn_toTwo = QtWidgets.QPushButton('Transform to LoD 2')
        self.lGrid.addWidget(self.btn_toTwo, 3, 8, 1, 4)
        self.btn_toOne.setToolTip("requires ground surface coordinates, building height (and roof height)")
        if 0 in presenetLoDs or 1 in presenetLoDs:
            self.btn_toTwo.setEnabled(True)
        else:
            self.btn_toTwo.setEnabled(False)

        self.lbl_transPG = QtWidgets.QLabel('Transformation Progress')
        self.lGrid.addWidget(self.lbl_transPG, 4, 0, 1, 4)

        self.pB_transformation = QtWidgets.QProgressBar(self)
        self.lGrid.addWidget(self.pB_transformation, 4, 4, 1, 8)

        self.vbox.addLayout(self.lGrid)

        self.l2Grid = QtWidgets.QGridLayout()

        self.btn_about = QtWidgets.QPushButton('About')
        self.l2Grid.addWidget(self.btn_about, 0, 0, 1, 1)

        self.btn_reset = QtWidgets.QPushButton('Reset')
        self.l2Grid.addWidget(self.btn_reset, 0, 1, 1, 1)

        self.btn_exit = QtWidgets.QPushButton('Exit')
        self.l2Grid.addWidget(self.btn_exit, 0, 2, 1, 1)

        self.btn_back = QtWidgets.QPushButton('Back')
        self.l2Grid.addWidget(self.btn_back, 0, 3, 1, 1)

        self.vbox.addLayout(self.l2Grid)


        self.btn_saveBuildingParams.clicked.connect(self.func_save)
        self.btn_overwrite.clicked.connect(self.func_overwrite)
        self.btn_toZero.clicked.connect(self.func_toZero)
        self.btn_toOne.clicked.connect(self.func_toOne)
        self.btn_toTwo.clicked.connect(self.func_toTwo)
        self.btn_about.clicked.connect(self.func_about)
        self.btn_reset.clicked.connect(self.func_reset)
        self.btn_exit.clicked.connect(self.func_exit)
        self.btn_back.clicked.connect(self.func_back)

        self.cB_curBuilding.currentTextChanged.connect(self.func_curBuildingChanged)

        self.completedTransform = 0
        self.inpDir = inpDir
        self.buildingParamsDict = buildingParamsDict
        self.buildingOverWrDict = buildingOverWrDict
        self.overWriteFlag = False
        self.previousDisabled = []



    def func_curBuildingChanged(self):
        """gets called when the current building changes"""
        self.overWriteFlag = False
        if self.cB_curBuilding.currentIndex() != 0:
            try:
                index = ldt.getIndexFromBuildingDict(self, self.cB_curBuilding.currentText())
            except:
                index = -1
        else:
            index = -1

        # get SET values from LoDScan
        try:
            sets = self.buildingDict[index]['values']
        except:
            sets = {-1: {'LoD': None, 'rType': None, 'bFunction': None, 'SAG': None, 'SBG': None, 'YOC': None, 'rHeight': None, 'rHeading': None, 'bHeight': None}}

        # values from previous overwrite
        if index in self.buildingOverWrDict:
            setX = self.buildingOverWrDict[index]
            for i in setX:
                if setX[i] == None:
                    setX[i] = sets[i]
            sets = setX


        # get values from saving
        if index in self.buildingParamsDict:
            # values from previous safe
            values = self.buildingParamsDict[index]
        else:
            # values from "all (selected) buildings"
            values = self.buildingParamsDict[-1]


        if sets["bHeight"] != 'N/D':
            self.txtB_buildingHeight.setText(str(sets["bHeight"]))
            self.txtB_buildingHeight.setEnabled(False)
        else:
            self.txtB_buildingHeight.setText('')
            self.txtB_buildingHeight.setEnabled(True)
            if values["bHeight"] != None:
                self.txtB_buildingHeight.setText(str(values["bHeight"]))

        if sets["rHeight"] != 'N/D':
            self.txtB_roofHeight.setText(str(sets["rHeight"]))
            self.txtB_roofHeight.setEnabled(False)
        else:
            self.txtB_roofHeight.setText('')
            self.txtB_roofHeight.setEnabled(True)
            if values["rHeight"] != None:
                self.txtB_buildingHeight.setText(str(values["rHeight"]))

        self.cB_roofType.clear()
        if sets["rType"] != 'N/D':
            self.cB_roofType.addItem(sets["rType"])
            self.cB_roofType.setEnabled(False)
        else:
            self.cB_roofType.addItems(['', 'flat roof :      1000', 'monopitch roof : 1010', 'dual pent roof : 1020', 'gabled roof :    1030', 'hipped roof :    1040', 'pavilion roof :  1070'])
            self.cB_roofType.setCurrentIndex(0)
            self.cB_roofType.setEnabled(True)
            if values["rType"] != None:
                helpDict = {'1000': 1, '1010': 2, '1020': 3, '1030': 4, '1040': 5, '1070': 6}
                self.cB_roofType.setCurrentIndex(helpDict[values["rType"]])


        self.cB_heading.clear()
        if sets["rType"] == '1000' or sets["rType"] == '1040' or sets["rType"] == '1070':
            self.cB_heading.setEnabled(False)
        elif sets["rHeading"] == 'N/D':
            self.cB_heading.addItems(['', 'NORTHish', 'EASTish', 'SOUTHish', 'WESTish'])
            self.cB_heading.setEnabled(True)
            if values["rHeading"] != None:
                helpDict = {'NORTHish': 1, 'EASTish': 2, 'SOUTHish': 3, 'WESTish': 4}
                self.cB_heading.setCurrentIndex(helpDict[values["rHeading"]])
        elif type(sets["rHeading"]) == list:
            self.cB_heading.addItems(sets["rHeading"])
            self.cB_heading.setEnabled(True)
        else:
            self.cB_heading.addItem(str(sets["rHeading"]))
            self.cB_heading.setEnabled(False)
            
        
        self.cB_buildingFunction.clear()
        if sets["bFunction"] != 'N/D':
            self.cB_buildingFunction.addItem(sets["bFunction"])
            self.cB_buildingFunction.setEnabled(False)
        else:
            self.cB_buildingFunction.addItems(gf.createListForComboBox(buildingFunctions, 40))
            self.cB_buildingFunction.setEnabled(True)
            if values["bFunction"] != None:
                helpDict = {}
                self.cB_buildingFunction.setCurrentIndex(helpDict[values["bFunction"]])

        
        if sets["YOC"] != 'N/D':
            self.txtB_yearOfConstruction.setText(sets["YOC"])
            self.txtB_yearOfConstruction.setEnabled(False)
        else:
            self.txtB_yearOfConstruction.setText('')
            self.txtB_yearOfConstruction.setEnabled(True)
            if values["YOC"] != None:
                self.txtB_yearOfConstruction.setText(values["YOC"])

        if sets["SAG"] != 'N/D':
            self.txtB_SAG.setText(str(sets["SAG"]))
            self.txtB_SAG.setEnabled(False)
        else:
            self.txtB_SAG.setText('')
            self.txtB_SAG.setEnabled(True)
            if values["SAG"] != None:
                self.txtB_SAG.setText(str(values["SAG"]))

        if sets["SBG"] != 'N/D':
            self.txtB_SBG.setText(str(sets["SBG"]))
            self.txtB_SBG.setEnabled(False)
        else:
            self.txtB_SBG.setText('')
            self.txtB_SBG.setEnabled(True)
            if values["SBG"] != None:
                self.txtB_SAG.setText(str(values["SBG"]))






    def overwriteChange(self, state):
        if state:
            self.btn_overwrite.setText('Disable overwrite')
            color = "green"
        else:
            self.btn_overwrite.setText('Enable overwrite')
            color = "light gray"
        txt = "background-color: " + color
        self.btn_overwrite.setStyleSheet(txt)
        self.overWriteFlag = state
        toChange = [self.txtB_buildingHeight, self.txtB_roofHeight, self.txtB_yearOfConstruction, self.txtB_SAG, self.txtB_SBG]
        
        if state:
            self.previousDisabled = []
            for i in toChange:
                if not i.isEnabled():
                    self.previousDisabled.append(i)
                    i.setEnabled(True)
        else:
            for i in self.previousDisabled:
                i.setEnabled(False)




    def func_overwrite(self):
        self.overwriteChange(not self.overWriteFlag)
        


    def func_toZero(self):
        print("to zero")
        start = time.time()
        ldt.transformationStart(self, 0, selAll)
        end = time.time()
        print(end - start)

    def func_toOne(self):
        print("to one")
        start = time.time()
        ldt.transformationStart(self, 1, selAll)
        end = time.time()
        print(end - start)


    def func_toTwo(self):
        print("to two")
        start = time.time()
        ldt.transformationStart(self, 2, selAll)
        end = time.time()
        print(end - start)

    def func_about(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, about(), False)


    def func_reset(self):
        self.buildingParamsDict = {-1: {'LoD': None, 'rType': None, 'bFunction': None, 'SAG': None, 'SBG': None, 'YOC': None, 'rHeight': None, 'rHeading': None, 'bHeight': None}}
        self.buildingOverWrDict = {-1: {'LoD': None, 'rType': None, 'bFunction': None, 'SAG': None, 'SBG': None, 'YOC': None, 'rHeight': None, 'rHeading': None, 'bHeight': None}}
        self.cB_curBuilding.setCurrentIndex(0)
        self.cB_roofType.setCurrentIndex(0)
        self.cB_heading.setCurrentIndex(0)
        self.cB_buildingFunction.setCurrentIndex(0)
        self.txtB_buildingHeight.setText('')
        self.txtB_roofHeight.setText('')
        self.txtB_yearOfConstruction.setText('')
        self.txtB_SAG.setText('')
        self.txtB_SBG.setText('')

        self.rB_onlyTransformed.setChecked(True)

        self.completedTransform = 0
        self.overWriteFlag = False
        self.previousDisabled = []
        self.pB_transformation.setValue(0)

        self.expPath = os.path.join(inpDir, 'e3D_CityLDT')
        self.txtB_outDir.setText(self.expPath)


    def func_exit(self):
        gf.close_application(self)


    def func_save(self):
        ldt.onSave(self)
        self.overwriteChange(False)

    def func_back(self):
        global posx, posy, buildingParamsDict, buildingOverWrDict
        buildingParamsDict = self.buildingParamsDict
        buildingOverWrDict = self.buildingOverWrDict
        posx, posy = gf.dimensions(self)
        gf.next_window(self, mainWindow())








class about(QtWidgets.QWidget):
    def __init__(self):
        super(about, self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor

        gf.windowSetup(self, posx + 10, posy + 10, width, height, pypath, 'CityBIT - About')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)

        self.textwidget = QtWidgets.QTextBrowser()
        self.vbox.addWidget(self.textwidget)
        self.textwidget.setFontPointSize(14)
        with open(os.path.join(pypath, 'about/about.txt'), 'r') as file:
            text = file.read()
        self.textwidget.setText(text)

        self.lGrid = QtWidgets.QGridLayout()

        self.btn_repo = QtWidgets.QPushButton('Open repository')
        self.lGrid.addWidget(self.btn_repo, 0, 0, 1, 1)

        self.btn_close = QtWidgets.QPushButton('Close')
        self.lGrid.addWidget(self.btn_close, 0, 1, 1, 1)

        self.vbox.addLayout(self.lGrid)

        self.btn_repo.clicked.connect(self.open_repo)
        self.btn_close.clicked.connect(self.close_about)


    def open_repo(self):
        os.startfile('www.e3d.rwth-aachen.de')

    def close_about(self):
        self.hide()
        



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet("QLabel{font-size: 10pt;} QPushButton{font-size: 10pt;} QRadioButton{font-size: 10pt;} QGroupBox{font-size: 10pt;} QComboBox{font-size: 10pt;} QLineEdit{font-size: 10pt;}")
    widget = mainWindow()
    widget.show()
    sys.exit(app.exec_())