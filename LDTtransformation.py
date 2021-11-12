# import of libraries
from PySide2 import QtWidgets, QtGui
import os
import pandas as pd
import math
import lxml.etree as ET
import uuid

# import of functions
import gui_functions as gf
import LDTselection as sel
import TWOd_operations as TWOd

def checkIfStringIsNumber(self, string, t=float):
    """checks if string can be converted to a number"""
    try:
        t(string)
        return True
    except:
        msg = 'Unable to safe! "' + string + '" is not a valid input.'
        gf.messageBox(self, 'ERROR', msg)
        return False



def onSave(self):
    """to self user entered building parameters"""
    # get index of comboBox
    if self.cB_curBuilding.currentIndex() != 0:
        index = getIndexFromBuildingDict(self, self.cB_curBuilding.currentText())
    else:
        index = -1
    # gather all data
    params = {}

    # buildingHeight
    if self.txtB_buildingHeight.text() != '' and checkIfStringIsNumber(self, self.txtB_buildingHeight.text()):
        params["bHeight"] = float(self.txtB_buildingHeight.text())
    else:
        params["bHeight"] = None

    # roofHeight
    if self.txtB_roofHeight.text() != '':
        # check if statement ist valid formula
        text = self.txtB_roofHeight.text()
        if '/' in text:
            splits = text.split('/')
            if len(splits) == 2 and splits[0] == "bHeight":
                pass
            else:
                print("wrong formatting of formula")
        elif '*' in text:
            splits = text.split('*')
            if len(splits) == 2 and "bHeight" in splits:
                pass
            else:
                print("wrong formatting of formula")
        elif checkIfStringIsNumber(self, self.txtB_roofHeight.text()):
            params["rHeight"] = float(self.txtB_roofHeight.text())
        
    else:
        params["rHeight"] = None

    # roofType
    if self.cB_roofType.currentIndex() != 0:
        params["rType"] = self.cB_roofType.currentText()[-4:]
        if params["rHeight"] == 0 and params["rType"] != "1000":
            print(params["rType"])
            print(type(params["rType"]))
            gf.messageBox(self, "Warning", "Roof height can only be 0m when selecting a flat roof")
    else:
        params["rType"] = None
    
    # roofHeading
    if self.cB_heading.currentIndex() != 0:
        params["rHeading"] = self.cB_heading.currentText()
    else:  
        params["rHeading"] = None


    # buildingFunction
    if self.cB_buildingFunction.currentIndex() != 0:
        params["bFunction"] = self.cB_buildingFunction.currentText()[-4:]
    else:
        params["bFunction"] = None

    # YOC
    if self.txtB_yearOfConstruction.text() !=  '':
        params["YOC"] = self.txtB_yearOfConstruction.text()
    else:
        params["YOC"] = None

    # SAG
    if self.txtB_SAG.text() !=  '' and checkIfStringIsNumber(self, self.txtB_SAG.text(), int):
        params["SAG"] = int(self.txtB_SAG.text())
    else:
        params["SAG"] = None

    # SBG
    if self.txtB_SBG.text() != '' and checkIfStringIsNumber(self, self.txtB_SBG.text(), int):
        params["SBG"] = int(self.txtB_SBG.text())
    else:
        params["SBG"] = None

    if self.overWriteFlag == True:
        self.buildingOverWrDict[index] = params
    else:    
        self.buildingParamsDict[index] = params


def select_expPath(self):
    """func to select folder"""
    path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
    if path:
        self.expPath = path
        self.txtB_outDir.setText(self.expPath)
    else:
        gf.messageBox(self, "Important", "Valid Exportfolder not selected")


def getIndexFromBuildingDict(self, buildingname):
    """gets the index of the building within the buildingDict"""
    for key in self.buildingDict:
        if buildingname.split("/")[1] == self.buildingDict[key]["buildingname"]:
            return key


def transformationStart(self, targetLoD, selAll):
    """starting the LoD transformation"""

    # get data
    dataForFrame = []
    for index in self.buildingDict:
        splits = self.buildingDict[index]["buildingname"].split('/')
        if len(splits) > 1:
            bpname = splits[1]
        else:
            bpname = ''
        row = [self.buildingDict[index]["filename"], splits[0], bpname, self.buildingDict[index]["selected"]]
        sets = self.buildingDict[index]["values"]
        row.append(sets["LoD"])

        # checks which data is present with highest priority on file, then individual building save, then all building save
        for i in [ 'bHeight', 'rHeight',  'rType', 'rHeading', 'bFunction', 'YOC', 'SAG', 'SBG']:
            if (index in self.buildingOverWrDict) and (self.buildingOverWrDict[index][i] != None):
                print("buildingwise")
                print(self.buildingOverWrDict[index][i])
                row.append(self.buildingOverWrDict[index][i])
            elif (self.buildingOverWrDict[-1][i] != None):
                print("all building over")
                print(self.buildingOverWrDict[-1][i])
                print(type(self.buildingOverWrDict[-1][i]))
                row.append(self.buildingOverWrDict[-1][i])
            elif sets[i] != 'N/D':
                # if already set by building
                row.append(sets[i])
            elif (index in self.buildingParamsDict) and (self.buildingParamsDict[index][i] != None):
                # set by building on individual building
                row.append(self.buildingParamsDict[index][i])
            else:
                # set as default for all buildings
                row.append(self.buildingParamsDict[-1][i])

            

            # overwrite for rHeading
            if i == 'rHeading':
                if sets[i] != 'N/D':
                    if (index in self.buildingParamsDict) and (self.buildingParamsDict[index][i] != None):
                        # from individual building
                        row[-1]= self.buildingParamsDict[index][i]
                    else:
                        # from all buildings default
                        row[-1]= self.buildingParamsDict[-1][i]

                    
        dataForFrame.append(row)


    df = pd.DataFrame(dataForFrame, columns=['filename', 'buildingID', 'bpID', 'selected', 'LoD', 'buildingHeight', 'roofHeight', 'roofType', 'roofHeading', 'function', 'YOC', 'SAG', 'SBG'])
    # only consider buildings which are not in the target LoD
    df = df.loc[df['LoD'] != targetLoD]
    # print('df after LoD clearing')
    if df.empty:
        msg = 'No buildings to transform'
        gf.messageBox(self, 'Error', msg)
        return

    if not selAll:
        df = df.loc[df["selected"] == True]
    else:
        # all files and buildings
        pass


    # for catching missing data
    dfProblematic = df.loc[df['LoD'] < targetLoD]
    for index, row in dfProblematic.iterrows():
        if targetLoD == 2 and row["LoD"] == 0:
            neededParams = ['buildingHeight', 'roofHeight', 'roofType', 'roofHeading']
            if checkNeededData(self, row, neededParams) == False:
                return
        elif targetLoD == 2 and row["LoD"] == 1:
            neededParams = ['roofHeight', 'roofType', 'roofHeading']
            if checkNeededData(self, row, neededParams) == False:
                return
        elif targetLoD == 1 and row["LoD"] == 0:
            neededParams = ['buildingHeight']
            if checkNeededData(self, row, neededParams) == False:
                return
        else:
            # should pretty much be all good in the other cases 
            pass


    filesToWorkOn = list(dict.fromkeys(df["filename"].to_list()))
    for i, filename in enumerate(filesToWorkOn):
        print("transforming file:", filename)
        dfFile = df.loc[df["filename"] == filename]
        # do the shenanigans here
        transformFile(self, filename, targetLoD, dfFile)
        gf.progressTransfrom(self, (i + 1)/len(filesToWorkOn)*100)



def transformFile(self, filename, targetLoD, dfFile):
    """transforms 'filename' to 'targetLoD' where 'builidngs' is either a list of building names or set to 'all'"""

    # parsing file
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(os.path.join(self.inpDir, filename), parser)
    root_E = tree.getroot()
    nss = root_E.nsmap
    
    nroot_E, nnss, nLcorner_E, nUcorner_E, minimum, maximum = getNewTree(self, filename)

    # iterate over all buildings in the file
    num_of_buildings = len(root_E.findall('core:cityObjectMember/bldg:Building', nss))
    i = 0
    while i < num_of_buildings:
        building_E = nroot_E.findall('core:cityObjectMember/bldg:Building', nnss)[i]
        building_ID = building_E.attrib['{http://www.opengis.net/gml}id']
        dfBuild = dfFile.loc[dfFile["buildingID"] == building_ID]

        dfMain = dfBuild.loc[dfBuild['bpID'] == '']


        # check if building is selected (dfBuild has an entry -> the file should be transformed)
        if len(dfBuild.index) != 0:
            # adding description
            describ_E = building_E.find("gml:description", nnss)
            if describ_E != None:
                if 'transformed using the RWTH e3d City-LDT' not in describ_E.text:
                    describ_E.text += "\n                       transfromed using the RWTH e3d City-LDT"
                else:
                    # transformed description is already present in element
                    pass
            else:
                describ_E = ET.SubElement(building_E, ET.QName(nnss["gml"], 'description'))
                describ_E.text = 'transformed using the RWTH e3d City-LDT'
                building_E.insert(0, describ_E)
            
            # check if new attributes have been set
            if len(dfMain.index>1):
                setBuildingElements(building_E, nnss, dfMain)
            
            # get groundSurface coordinates
            groundCoor = sel.getGroundSurfaceCoorOfBuild(building_E, nss)            
            if groundCoor != '':
                minimum, maximum = new_min_max(groundCoor, minimum, maximum)

                # tags to delete
                to_delete = ['bldg:lod0FootPrint', 'bldg:lod0RoofEdge', 'bldg:lod1Solid', 'bldg:lod2Solid', 'bldg:boundedBy']
                geomIndex = 0
                for tag in to_delete:
                    target_Es = building_E.findall(tag, nnss)
                    for target_E in target_Es:
                        if geomIndex == 0:
                            geomIndex = building_E.index(target_E)
                        building_E.remove(target_E)

                if targetLoD == 0:
                    addLoD0FootPrint(building_E, nnss, geomIndex, groundCoor)
                    deleteTerrainIntersection(building_E, nss)

                elif targetLoD == 1:
                    bHeight = getInfoForLoD1(dfMain, building_E, nss)
                    addLoD1Solid(building_E, nnss, geomIndex, groundCoor, bHeight)
                    deleteTerrainIntersection(building_E, nss)
                    # copyTerrainIntersection(building_E, nss)

                elif targetLoD == 2:
                    bHeight, rHeight, rType, rHeading = getInfoForLoD2(dfMain, building_E, nss)
                    addLoD2Solid(self, building_E, nnss, geomIndex, groundCoor, bHeight, rHeight, rType, rHeading, building_ID)
                    deleteTerrainIntersection(building_E, nss)
                    # copyTerrainIntersection(building_E, nss)

                else:
                    print('')
                    print("HUGE ERROR")
                    print('')


            for co_bp_E in building_E.findall('./bldg:consistsOfBuildingPart', nnss):
                bp_E = co_bp_E.find('bldg:BuildingPart', nnss)
                bp_gC = sel.getGroundSurfaceCoorOfBuild(bp_E, nnss)
                minimum, maximum = new_min_max(bp_gC, minimum, maximum)
                bpID = bp_E.attrib['{http://www.opengis.net/gml}id']

                dfBP = dfBuild.loc[dfBuild["bpID"] == bpID]

                setBuildingElements(bp_E, nnss, dfBP)

                # tags to delete
                to_delete = ['bldg:lod0FootPrint', 'bldg:lod0RoofEdge', 'bldg:lod1Solid', 'bldg:lod2Solid', 'bldg:boundedBy']
                geomIndex = 0
                for tag in to_delete:
                    target_Es = bp_E.findall(tag, nnss)
                    for target_E in target_Es:
                        if geomIndex == 0:
                            geomIndex = bp_E.index(target_E)
                        bp_E.remove(target_E)

                if targetLoD == 0:
                    addLoD0FootPrint(bp_E, nnss, geomIndex, bp_gC)
                    deleteTerrainIntersection(bp_E, nnss)

                elif targetLoD == 1:
                    bHeight = getInfoForLoD1(dfBP, bp_E, nss)
                    addLoD1Solid(bp_E, nnss, geomIndex, bp_gC, bHeight)
                    deleteTerrainIntersection(bp_E, nss)
                    # copyTerrainIntersection(bp_E, nss)

               
                elif targetLoD == 2:
                    bHeight, rHeight, rType, rHeading = getInfoForLoD2(dfBP, bp_E, nss)
                    addLoD2Solid(self, bp_E, nnss, geomIndex, bp_gC, bHeight, rHeight, rType, rHeading, building_ID)
                    # deleteTerrainIntersection(bp_E, nss)
                    # copyTerrainIntersection(bp_E, nss)
                
                else:
                    print('')
                    print("HUGE ERROR")
                    print('')
            

        else:
            # df is empty skipping building transformation
            if self.rB_oldAndNew.isChecked():
                # building can stay as is
                pass
            else:
                # building is not needed for new file
                # getting parent (cityObjectMember) of building 
                com_to_delete_E = building_E.getparent()
                # deleting cityObjectMember (including building)
                com_to_delete_E.getparent().remove(com_to_delete_E)
                num_of_buildings -= 1
                continue


        if self.rB_individualFiles.isChecked():
            # first save tree to file
            baseName = os.path.splitext(filename)[0]
            exportName = baseName + "_" + building_ID + "_LoD" + str(targetLoD) + "_e3d_LDT.gml"
            writeTree(self, nroot_E, nnss, nLcorner_E, nUcorner_E, minimum, maximum, baseName, exportName)
            # then create a new root
            nroot_E, nnss, nLcorner_E, nUcorner_E, minimum, maximum = getNewTree(self, filename)

        i -=- 1
    

    if not self.rB_individualFiles.isChecked():
        # need to safe file here
        baseName = os.path.splitext(filename)[0]
        exportName = baseName + "_LoD" + str(targetLoD) + "_e3d_LDT.gml"
        writeTree(self, nroot_E, nnss, nLcorner_E, nUcorner_E, minimum, maximum, baseName, exportName)
        
    print("seems like I am done with one file")




def checkNeededData(self, row, neededParams):
    """checks if all needed Params are defined in a row"""
    for value in neededParams:
        if row[value] == None and not ((value == 'roofHeight' or value == "roofHeading") and row["roofType"] == "1000"):
            # this wonderful if statement checks if the data is given or not. and ignores cases for flat roofs, because for them neither roofHeight nor roofHeading are needed
            msg = "Missing data '" + value + "' in file '" + row["filename"] + "' for building '" + row["buildingID"] + "'"
            print("problem with ", row , "and ", value)
            print(row[value])
            gf.messageBox(self, 'Error', msg)
            return False
    return True


def getNewTree(self, filename):
    """reads file again to get a new modifiable tree"""
    # parsing file
    parser = ET.XMLParser(remove_blank_text=True)
    ntree = ET.parse(os.path.join(self.inpDir, filename), parser)
    nroot_E = ntree.getroot()
    nnss = nroot_E.nsmap

    # get envelope elements
    envelope_E = nroot_E.find('./gml:boundedBy/gml:Envelope', nnss)
    nLcorner_E = envelope_E.find('gml:lowerCorner', nnss)
    nUcorner_E = envelope_E.find('gml:upperCorner', nnss)
    
    description_already = False     # flag noting if file already has a description element referenecing the CityLDT
    description_LDT_E = nroot_E.findall('gml:description', nnss)
    for des_E in description_LDT_E:
        if des_E.text == 'created using the e3D CityLDT':
            description_already = True
            break
    
    if description_already == False:
        description_E = ET.SubElement(nroot_E, ET.QName(nnss["gml"], 'description'), nsmap={'gml': nnss["gml"]}, )
        description_E.text = 'created using the e3D CityLDT'
        nroot_E.insert(0, description_E)
    
    return nroot_E, nnss, nLcorner_E, nUcorner_E, [math.inf, math.inf, math.inf], [-math.inf, -math.inf, -math.inf]



def setBuildingElements(building_E, nss, df):
    """sets some of the default elements"""

    # sBOrder list contains elements in the desired order. running the loop will add their last index if present to the dict, allowing other elements to be appended in the right place
    sBOrder = {'gml:description': -1, 'gml:name': -1, 'core:creationDate': -1, "core:externalReference": -1, 'core:relativeToTerrain': -1, 'gen:measureAttribute': -1, 'gen:stringAttribute': -1, 'bldg:class': -1, 'bldg:function': -1, 'bldg:usage': -1, 'bldg:yearOfConstruction': -1, 'bldg:roofType': -1, 'bldg:measuredHeight': -1, 'bldg:storeysAboveGround': -1, 'bldg:storeysBelowGround': -1, 'bldg:lod0FootPrint': -1, 'bldg:lod0RoofEdge': -1, 'bldg:lod1Solid': -1, 'bldg:lod2Solid': -1, 'bldg:boundedBy': -1, 'bldg:lod1TerrainIntersection': -1, 'bldg:lod2TerrainIntersection': -1, "bldg:address": -1}
    for tag in sBOrder:
        target = building_E.findall(tag, nss)
        if target != []:
            index = building_E.index(target[-1])
            sBOrder[tag] = index
    
    # running through all optional elements and adding if necessary
    prefix = "bldg"
    for tagName, dfName in [["function", "function"], ["yearOfConstruction", "YOC"], ["roofType", "roofType"], ["measuredHeight", "buildingHeight"], ["storeysAboveGround", "SAG"], ["storeysBelowGround", "SBG"]]:
        preTag = prefix + ":" + tagName
        
        found = False
        insertIndex = 0
        for tag in sBOrder:
            if tag == preTag:
                found = True
                sBOrder[tag] = insertIndex +1
                continue
            if not found:
                if sBOrder[tag] != -1 and sBOrder[tag] > insertIndex:
                    insertIndex = sBOrder[tag]
            else:
                if sBOrder[tag] != -1:
                    sBOrder[tag] -=- 1

        if (df.iloc[0][dfName] != None) and (not pd.isna(df.iloc[0][dfName])):
            check = building_E.find(preTag, nss)
            if check != None:
                check.text = str(df.iloc[0][dfName])
            else:
                new_E = ET.Element(ET.QName(nss[prefix], tagName))
                new_E.text = str(df.iloc[0][dfName])
                building_E.insert(insertIndex + 1, new_E)        


def new_min_max(new_values, old_min=[math.inf, math.inf, math.inf], old_max=[-math.inf, -math.inf, -math.inf]):
    """calculates new min and max values for envelope"""
    x_es = [i[0] for i in new_values]
    y_es = [i[1] for i in new_values]
    z_es = [i[2] for i in new_values]
    new_min = [min(x_es), min(y_es), min(z_es)]
    for i, value in enumerate(new_min):
        if value < old_min[i]:
            old_min[i] = value
    new_max = [max(x_es), max(y_es), max(z_es)]
    for i, value in enumerate(new_max):
        if value > old_max[i]:
            old_max[i] = value
    return old_min, old_max



def addLoD0FootPrint(targetElement, nss, geomIndex, coordinates):
    """adds a LoD0 footprint form the coordinates to the target element using the namespaces"""
    footPrint_E = ET.Element(ET.QName(nss["bldg"], 'lod0FootPrint'))
    multiSurface_E = ET.SubElement(footPrint_E, ET.QName(nss["gml"], 'MultiSurface'))
    surfaceMember_E = ET.SubElement(multiSurface_E, ET.QName(nss["gml"], 'surfaceMember'))
    polygon_E = ET.SubElement(surfaceMember_E, ET.QName(nss["gml"], 'Polygon'))
    exterior_E = ET.SubElement(polygon_E, ET.QName(nss["gml"], 'exterior'))
    linearRing_E = ET.SubElement(exterior_E, ET.QName(nss["gml"], 'LinearRing'))
    for point in coordinates:
        # converting floats to string to join
        stringed = [str(j) for j in point]
        ET.SubElement(linearRing_E, ET.QName(nss["gml"], 'pos')).text = ' '.join(stringed)
    targetElement.insert(geomIndex, footPrint_E)



def addLoD1Solid(targetElement, nss, geomIndex, groundCoor, bHeight):
    """creates lod1solid element and requiered child elements"""
    # calculate points first
    cornerPoints = [i[0:2] for i in groundCoor]
    baseHeight = groundCoor[0][2]
    bWithRoof = baseHeight + bHeight
    roofPoints = [i + [bWithRoof] for i in cornerPoints]
    roofPoints.reverse()
    surfaces = [groundCoor, roofPoints]

    # walls
    for i in range(len(cornerPoints) - 1):
        wall = [cornerPoints[i] + [baseHeight], cornerPoints[i] + [bWithRoof], cornerPoints[i+1] + [bWithRoof], cornerPoints[i+1] + [baseHeight]]
        wall.append(wall[0])
        surfaces.append(wall)

    # create required elements
    lod1Solid_E = ET.Element(ET.QName(nss["bldg"], 'lod1Solid'))
    solid_E = ET.SubElement(lod1Solid_E, ET.QName(nss['gml'], 'Solid'))
    exterior0_E = ET.SubElement(solid_E, ET.QName(nss['gml'], 'exterior'))
    compositeSurf_E = ET.SubElement(exterior0_E, ET.QName(nss['gml'], 'CompositeSurface'))

    # add surfaces
    for surface in surfaces:
        surfMem_E = ET.SubElement(compositeSurf_E, ET.QName(nss['gml'], 'surfaceMember'))
        polygon_E = ET.SubElement(surfMem_E, ET.QName(nss['gml'], 'Polygon'))
        exterior1_E = ET.SubElement(polygon_E, ET.QName(nss['gml'], 'exterior'))
        linRing_E = ET.SubElement(exterior1_E, ET.QName(nss['gml'], 'LinearRing'))
        t = ''
        for point in surface:
            stringed = [str(j) for j in point]
            t += ' '.join(stringed) + ' '
            # ET.SubElement(linRing_E, ET.QName(nss['gml'], 'pos')).text = ' '.join(stringed)
        ET.SubElement(linRing_E, ET.QName(nss['gml'], 'posList'), srsDimension= '3' ).text = t
    targetElement.insert(geomIndex, lod1Solid_E)



def addLoD2Solid(self, targetElement, nss, geomIndex, groundCoor, bHeight, rHeight, rType, rHeading, buildingID):
    """creates lod2solid elements and requiered child elements"""
    # calculate points first
    cornerPoints = [i[0:2] for i in groundCoor]
    baseHeight = groundCoor[0][2]
    if rHeight == None:
        rHeight = 0
    bWithRoof = baseHeight + bHeight
    if bHeight > rHeight:
        bWithWall = baseHeight + bHeight - rHeight
    else:
        bWithWall = baseHeight


    # calculating  3d ground surface
    gS_3d = []
    for i in cornerPoints:
        y = i.copy()
        y.append(baseHeight)
        gS_3d.append(y)
    gS_dict = {'Base Surface': gS_3d}

    wall_dict = {}
    roof_dict = {}

    heading_index = -1
    # something about the heading_index
    if rType != "1000":
        if rHeading == '':
            heading_index = 0
        else:
            if rHeading == 'NORTHish':
                roof_angle = 0
            elif rHeading == 'EASTish':
                roof_angle = 90
            elif rHeading == 'SOUTHish':
                roof_angle = 180
            elif rHeading == 'WESTish':
                roof_angle = 270
            else:
                try:
                    roof_angle = float(rHeading)
                except:
                    heading_index = 0
                    print('ERROR with ' + buildingID + '. Unable to set roof heading. Defaulting to 0.')
            
            if heading_index == -1 and len(cornerPoints) == 5:
                gS_list = cornerPoints.copy()
                x_center, y_center = TWOd.calc_center(gS_list)
                # getting rotation direction
                direction = TWOd.rotationDirection([x_center, y_center], gS_list[0], gS_list[1])
                
                # calculating angles of orthogonals on the wallsurfaces
                # and taking wall surface which has the smallest diviation from the interpolated angle as heading_index
                gS_list.append(gS_list[0])
                min_dif = 360
                for i in range(4):
                    new_angle = TWOd.angle(gS_list[i], gS_list[i+1])
                    corrected_angle = TWOd.correct_angle(new_angle, direction)
                    if abs(corrected_angle - roof_angle) < min_dif:
                        min_dif = abs(corrected_angle - roof_angle)
                        heading_index = i 



    if len(cornerPoints) != 5 and str(rType) != '1000' and str(rType) != '1070' and str(rType) != '3500':
        msg = 'The building "' + buildingID + '" has a unsupported number of coordinates for the roof type "' + str(rType) + '".\nA flat roof will instead be used for modelling.'
        rType = '1000'
        roof_E = targetElement.find("bldg:roofType", nss)
        roof_E.text = "1000"

        gf.messageBox(self, 'WARNING', msg)

    supportedRoofTypes = ['1000', '1010', '2100', '1020', '2200', '1030', '3100', '1040', '3200', '1070', '3500']
    if str(rType) not in supportedRoofTypes:
        msg = 'The building "' + buildingID + '" has a unsupported roof type "' + str(rType) + '".\nA flat roof will instead be used for modelling.'
        rType = '1000'
        gf.messageBox(self, 'WARNING', msg)

    # calculating walls and roofs
    if str(rType) == '1000':
    # calculating wall surfaces
        for i in range(len(cornerPoints) - 1):
            name = 'Outer Wall ' + str(i+1)
            wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithRoof], cornerPoints[i] + [bWithRoof]]
            wall.append(wall[0])
            wall_dict[name]= wall

        if str(rType) == '1000':
            # calculating roof surface
            rS_3d = []
            for i in cornerPoints:
                y = i.copy()
                y.append(bWithRoof)
                rS_3d.append(y)
            roof_dict = {'Roof 1': rS_3d}


    elif str(rType) == '1010' or str(rType) == '2100':
        # calculating wall surfaces
        # assuming the heading equals the wall with the lower side of the roof
        highPoints = []
        for i in range(4):
            name = 'Outer Wall ' + str(i+1)
            if i == heading_index:
                # both low
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], cornerPoints[i] + [bWithWall]]
            elif i - heading_index == 2 or i - heading_index == -2:
                # both high
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithRoof], cornerPoints[i] + [bWithRoof]]
                highPoints = [cornerPoints[i], cornerPoints[i+1]]
            elif (heading_index + 1) % 4 - (i + 1) == - 1:
                # i low     i+1 high
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithRoof], cornerPoints[i] + [bWithWall]]
            else:
                # i high    i+1 low
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], cornerPoints[i] + [bWithRoof]]


            wall.append(wall[0])
            wall_dict[name]= wall

        # calculating roof surface
        rS_3d = []
        for i in cornerPoints:
            y = i.copy()
            if y in highPoints:
                y.append(bWithRoof)
            else:
                y.append(bWithWall)
            rS_3d.append(y)
        roof_dict = {'Roof 1': rS_3d}


    elif str(rType) == '1020' or str(rType) == '2200': 
        # calculating wall surfaces
        # assuming the heading equals the side with the higher roof
        sH_pHalfRoof = bWithRoof - (rHeight / 3)
        highPoints = []
        lowPoints = []
        for i in range(4):
            name = 'Outer Wall ' + str(i+1)
            if i == heading_index:
                # wall on which the higher roof is ending
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], cornerPoints[i] + [bWithWall]]
                highPoints = [cornerPoints[i], cornerPoints[i+1]]
            elif i - heading_index == 2 or i - heading_index == -2:
                # wall on which the lower roof is ending
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], cornerPoints[i] + [bWithWall]]
                lowPoints = [cornerPoints[i], cornerPoints[i+1]]
            elif (heading_index + 1) % 4 - (i + 1) == - 1:
                # first half height than full height
                center0 = TWOd.calc_center(cornerPoints[i:i+2])
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], center0 + [sH_pHalfRoof], center0 + [bWithRoof] ,cornerPoints[i] + [bWithWall]]
            else:
                # first full height than half height
                center1 = TWOd.calc_center(cornerPoints[i:i+2])
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], center1 + [bWithRoof], center1 + [sH_pHalfRoof] ,cornerPoints[i] + [bWithWall]]
            
            wall.append(wall[0])
            wall_dict[name]= wall

        # for the wall between the two roof surfaces
        wall = [center0 + [sH_pHalfRoof], center1 + [sH_pHalfRoof], center1 + [bWithRoof], center0 + [bWithRoof]]
        wall.append(wall[0])
        name = 'Outer Wall ' + str(len(wall_dict) + 1)
        wall_dict[name] = wall

        # calculating roof surfaces
        # for roof with higher points
        roof = [highPoints[0] + [bWithWall], highPoints[1] + [bWithWall], center0 + [bWithRoof], center1 + [bWithRoof]]
        roof.append(roof[0])
        name = 'Roof ' + str(len(roof_dict) + 1)
        roof_dict[name] = roof
        # for roof with lower points
        roof = [lowPoints[0] + [bWithWall], lowPoints[1] + [bWithWall], center1 + [sH_pHalfRoof], center0 + [sH_pHalfRoof]]
        roof.append(roof[0])
        name = 'Roof ' + str(len(roof_dict) + 1)
        roof_dict[name] = roof


    elif str(rType) == '1030' or str(rType) == '3100':
        # calculating wall surfaces
        # assuming the heading equals one of the 4 sided walls
        for i in range(4):
            name = 'Outer Wall ' + str(i+1)
            if i == heading_index or i - heading_index == 2 or i - heading_index == -2:
                # square surfaces
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], cornerPoints[i] + [bWithWall]]
            else:
                # surfaces with "5th", higher point
                wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], TWOd.calc_center(cornerPoints[i:i+2]) + [bWithRoof], cornerPoints[i] + [bWithWall]]

            wall.append(wall[0])
            wall_dict[name]= wall
        
        if heading_index % 2 == 0:
            # square first, 5th second
            C0 = TWOd.calc_center(cornerPoints[1:3])
            C1 = TWOd.calc_center(cornerPoints[3:5])
            roof_dict['Roof 1'] = [cornerPoints[0]+ [bWithWall], cornerPoints[1]+ [bWithWall], C0 + [bWithRoof], C1 + [bWithRoof], cornerPoints[0]+ [bWithWall]]
            roof_dict['Roof 2'] = [cornerPoints[2]+ [bWithWall], cornerPoints[3]+ [bWithWall], C1 + [bWithRoof], C0 + [bWithRoof], cornerPoints[2]+ [bWithWall]]
        else:
            # 5th first, square second
            C0 = TWOd.calc_center(cornerPoints[0:2])
            C1 = TWOd.calc_center(cornerPoints[2:4])
            roof_dict['Roof 1'] = [cornerPoints[1]+ [bWithWall], cornerPoints[2]+ [bWithWall], C1 + [bWithRoof], C0 + [bWithRoof], cornerPoints[1]+ [bWithWall]]
            roof_dict['Roof 2'] = [cornerPoints[3]+ [bWithWall], cornerPoints[0]+ [bWithWall], C0 + [bWithRoof], C1 + [bWithRoof], cornerPoints[3]+ [bWithWall]]


    elif str(rType) == '1040' or str(rType) == '3200':
        # calculating wall surfaces
        for i in range(4):
            name = 'Outer Wall ' + str(i+1)
            wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], cornerPoints[i] + [bWithWall]]
            wall.append(wall[0])
            wall_dict[name]= wall

        # calculating the roof surfaces based the assumption that the gabel is colinear to the longer side of the roof
        help_array = []
        for i in range(2):
            help_array.append(TWOd.distance(cornerPoints[i], cornerPoints[i+1]))
        
        gabel_length = abs(help_array[0] - help_array[1])
        center_to_gabel = (max(help_array) - gabel_length) / 2

        # list of groundSurface coordinates but with (baseHeight + wallHeight) as 3d coordinate
        sH_pWall_list = [i + [bWithWall] for i in cornerPoints.copy()]
        if help_array[0] > help_array[1]:
            # longside first
            # getting some info about the heading of the roof
            shortCenter = TWOd.calc_center(cornerPoints[1:3])
            gabel_vector = TWOd.normedDirectionVector(cornerPoints[2], cornerPoints[3])
            # corners of roof
            C0 = [shortCenter[0] + center_to_gabel * gabel_vector[0], shortCenter[1] + center_to_gabel * gabel_vector[1], bWithRoof]
            C1 = [shortCenter[0] + (center_to_gabel + gabel_length) * gabel_vector[0], shortCenter[1] + (center_to_gabel + gabel_length) * gabel_vector[1], bWithRoof]
            #  roof surfaces
            roof_dict['Roof 1'] = [sH_pWall_list[0], sH_pWall_list[1], C0, C1, sH_pWall_list[0]]
            roof_dict['Roof 2'] = [sH_pWall_list[1], sH_pWall_list[2], C0, sH_pWall_list[1]]
            roof_dict['Roof 3'] = [sH_pWall_list[2], sH_pWall_list[3], C1, C0, sH_pWall_list[2]]
            roof_dict['Roof 4'] = [sH_pWall_list[3], sH_pWall_list[0], C1, sH_pWall_list[3]]

        else:
            # short side first
            # getting some info about the heading of the roof
            shortCenter = TWOd.calc_center(cornerPoints[0:2])
            gabel_vector = TWOd.normedDirectionVector(cornerPoints[1], cornerPoints[2])
            # corners of roof
            C0 = [shortCenter[0] + center_to_gabel * gabel_vector[0], shortCenter[1] + center_to_gabel * gabel_vector[1], bWithRoof]
            C1 = [shortCenter[0] + (center_to_gabel + gabel_length) * gabel_vector[0], shortCenter[1] + (center_to_gabel + gabel_length) * gabel_vector[1], bWithRoof]
            # roof surfaces
            roof_dict['Roof 1'] = [sH_pWall_list[0], sH_pWall_list[1], C0, sH_pWall_list[0]]
            roof_dict['Roof 2'] = [sH_pWall_list[1], sH_pWall_list[2], C1, C0, sH_pWall_list[1]]
            roof_dict['Roof 3'] = [sH_pWall_list[2], sH_pWall_list[3], C1, sH_pWall_list[2]]
            roof_dict['Roof 4'] = [sH_pWall_list[3], sH_pWall_list[0], C0, C1, sH_pWall_list[3]]

    elif str(rType) == '1070' or str(rType) == '3500':
        # calculating wall surfaces
        for i in range(len(cornerPoints) - 1):
            name = 'Outer Wall ' + str(i+1)
            wall = [cornerPoints[i] + [baseHeight], cornerPoints[i+1] + [baseHeight], cornerPoints[i+1] + [bWithWall], cornerPoints[i] + [bWithWall]]
            wall.append(wall[0])
            wall_dict[name]= wall
        
        # calculating roof surface
        roof_center = TWOd.calc_center(cornerPoints[0:-1])

        for i in range(len(cornerPoints)-1):
            name = 'Roof ' + str(i+1)
            roof = [cornerPoints[i] + [bWithWall], cornerPoints[i+1] + [bWithWall], roof_center + [bWithRoof]]
            roof.append(roof[0])
            roof_dict[name]= roof

    # lodnSolid_E = ET.SubElement(targetElement, ET.QName(nss['bldg'], 'lod2Solid'))
    lodnSolid_E = ET.Element(ET.QName(nss['bldg'], 'lod2Solid'))
    targetElement.insert(geomIndex, lodnSolid_E)
    geomIndex -=- 1
    solid_E = ET.SubElement(lodnSolid_E, ET.QName(nss['gml'], 'Solid'))
    exterior_E = ET.SubElement(solid_E, ET.QName(nss['gml'], 'exterior'))
    compositeSurface_E = ET.SubElement(exterior_E, ET.QName(nss['gml'], 'CompositeSurface'))

    
    # checking if there are duplicates
    p = 0
    while p < len(wall_dict):
        key = list(wall_dict.keys())[p]
        wall = wall_dict[key]
        for i in wall:
            if TWOd.has_duplicates2(wall):
                # wall with duplicate points
                q = 0
                while q < len(wall)-1:
                    if wall[q] == wall[q+1]:
                        del wall[q+1]
                    else:
                        q -=- 1
        if len(wall) < 4:
            del wall_dict[key]
            print("deleted wall from list because of number of points")
        else:
            p -=- 1

    ### here something to loop through the surfaceMembers    in order: wall, roof, base
    exteriorSurfaces = [wall_dict, roof_dict, gS_dict]
    polyIDs = []
    n = 0
    UUID = uuid.uuid1()
    for dictionary in exteriorSurfaces:
        for key in dictionary:
            ID = "PolyID" + str(UUID) + '_' + str(n)
            polyIDs.append(ID)
            hashtagedID = '#' + ID
            ET.SubElement(compositeSurface_E, ET.QName(nss['gml'], 'surfaceMember'), attrib={ET.QName(nss['xlink'], 'href'): hashtagedID})
            n -=- 1


     # for keeping track of used IDs
    m = 0

    # for walls
    for i in range(len(exteriorSurfaces)):
        if i == 0:
            surfaceType = 'WallSurface'
        elif i == 1:
            surfaceType = 'RoofSurface'
        elif i == 2:
            surfaceType = 'GroundSurface'

        for key in exteriorSurfaces[i]:
            # boundedBy_E = ET.SubElement(targetElement, ET.QName(nss['bldg'], 'boundedBy'))
            boundedBy_E = ET.Element(ET.QName(nss['bldg'], 'boundedBy'))
            targetElement.insert(geomIndex, boundedBy_E)
            geomIndex -=- 1
            ### somthing in the naming of the surface id
            wallSurfaceID = "GML_" + str(uuid.uuid1())
            wallRoofGround_E = ET.SubElement(boundedBy_E, ET.QName(nss['bldg'], surfaceType), attrib={ET.QName(nss['gml'], 'id'): wallSurfaceID})
            ET.SubElement(wallRoofGround_E, ET.QName(nss['gml'], 'name')).text = key
            """here something about the lod needs to be done"""
            lodnMultisurface_E = ET.SubElement(wallRoofGround_E, ET.QName(nss['bldg'], 'lod2MultiSurface'))
            multiSurface_E = ET.SubElement(lodnMultisurface_E, ET.QName(nss['gml'], 'MultiSurface'))
            surfaceMember_E = ET.SubElement(multiSurface_E, ET.QName(nss['gml'], 'surfaceMember'))
            """this needs to be identical to the surfaceMember id in the exteriorSurfaces"""
            polyID = polyIDs[m]
            m -=- 1
            polygon_E = ET.SubElement(surfaceMember_E, ET.QName(nss['gml'], 'Polygon'), attrib={ET.QName(nss['gml'], 'id'): polyID})
            # reusing variable, might cause some troubles
            exterior_E = ET.SubElement(polygon_E, ET.QName(nss['gml'], 'exterior'))
            ring_id = polyID + '_0'
            linearRing_E = ET.SubElement(exterior_E, ET.QName(nss['gml'], 'LinearRing'), attrib={ET.QName(nss['gml'], 'id'): ring_id})
            for point in exteriorSurfaces[i][key]:
                # converting floats to string to join
                stringed = [str(j) for j in point]
                ET.SubElement(linearRing_E, ET.QName(nss['gml'], 'pos')).text = ' '.join(stringed)



def deleteTerrainIntersection(building_E, nss):
    """deleting terrainIntersections"""
    targets = ['bldg:lod1TerrainIntersection', 'bldg:lod2TerrainIntersection']
    for target in targets:
        target_E = building_E.find(target, nss)
        if target_E != None:
            building_E.remove(target_E)



def copyTerrainIntersection(searchElement, nss):
    """copies an existing terrain intersection to the new building model"""
    lod1Intersection_E = searchElement.find('bldg:lod1TerrainIntersection', nss)
    if lod1Intersection_E != None:
        lod1Intersection_E.tag = ET.QName(nss["bldg"], "lod2TerrainIntersection")
        return

    lod2Intersection_E = searchElement.find('bldg:lod2TerrainIntersection', nss)
    if lod2Intersection_E != None:
        lod2Intersection_E.tag = ET.QName(nss["bldg"], "lod1TerrainIntersection")
        return



def getInfoForLoD1(df, searchElement, nss):
    """gathers all required info for LoD1 model creation"""
    # getting building height
    try:
        bHeight = df.iloc[0]['buildingHeight']
    except:
        measuredHeight_E = searchElement.find('bldg:measuredHeight', nss)
        if measuredHeight_E != None:
            bHeight =  float(measuredHeight_E.text)
        else:
            print("Error finding building height")
    
    return bHeight



def getInfoForLoD2(df, searchElement, nss):
    """gathers all required info for LoD2 model creation"""
    # getting building height
    bHeight = getInfoForLoD1(df, searchElement, nss)

    # getting roof height
    rHeight = df.iloc[0]['roofHeight']

    # getting roof type
    rType_E = searchElement.find('bldg:roofType', nss)
    if rType_E != None:
        rType = rType_E.text
    else:
        rType = df.iloc[0]['roofType']

    rHeading = df.iloc[0]['roofHeading']

    return bHeight, rHeight, rType, rHeading



def writeTree(self, rootElement, nss, lcorner, ucorner, minimum, maximum, baseName, exportName):
    """writes tree to file and updates bounding box"""
    lcorner.text = ' '.join(map(str, minimum))
    ucorner.text = ' '.join(map(str, maximum))

    name_E = rootElement.find('gml:name', nss)
    if name_E != None:
        if name_E.text == baseName:
            name_E.text = exportName.split(".gml")[0]


    if os.path.isdir(self.expPath):
        pass
    else:
        os.mkdir(self.expPath)
    tree = ET.ElementTree(rootElement)
    tree.write(os.path.join(self.expPath, exportName), pretty_print = True, xml_declaration=True, 
                encoding='utf-8', standalone='yes', method="xml")
    toFZKViewer = True
    if toFZKViewer:
        fullFilename = os.path.join(self.expPath, exportName)
        with open(fullFilename, 'r') as f:
            content = f.read()
        content = content.replace('http://www.opengis.net/citygml/1.0', 'http://www.opengis.net/citygml/2.0')
        with open(fullFilename, 'w') as f:
            f.write(content)
