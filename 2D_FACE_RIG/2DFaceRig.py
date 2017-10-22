# -*- encoding: utf-8 -*-
from pymel.core import *
from os import listdir
from os.path import isfile, join
import pymel.core.datatypes

path=r'P:\LOCAL\ES_SCRIPTS\RIG'
if not path in sys.path:
	sys.path.append(path)

path=r'I:\guithub\CofcofStudiosPipeline\RIG\UTIL'
if not path in sys.path:
	sys.path.append(path)

import UTILITIES



def move2 ( parent_ , child ):
    parentC = parentConstraint ( parent_ , child  )
    delete ( parentC )

def upLocGrpMaker ( upLoc , headBBoxCenter ):
    '''
    Crea transform para el upLoc.

    Return upLocGrp , upLoc
    '''
    print 'upLocGrpMaker'
    upLocGrpName     = loc2TrfsNewName( upLoc  )
    upLocGrp      = group( em = True , n = upLoc + '_TRF' )
    parent(   upLoc , upLocGrp.name())
    upLocGrp.translate.set ( headBBoxCenter[0] , headBBoxCenter[1] , headBBoxCenter[2] )
    return upLocGrp , upLoc

def loc2TrfsNewName( obj  ):
    '''
    Genera un nombre a partir de un nombre con sufijo.

    Return nombreNuevoSinSufijo
    '''
    print 'loc2TrfsNewName', repr (obj)
    splitString = '_'
    if not '_' in obj:
        newName = obj.name()
    else:
        newName = '_'.join(obj.name().split(splitString)[:-1:])
	print '                 loc2TrfsNewName OK'
    return newName

def customTransforms ( obj , trfs=[] ):
	'''
	Crea transforms desde el mas interior hasta el root, por lo que el orden de los elementos de trfs es relevante.
	Return [trf1,trf2,trf3,...]
	'''
	print 'customTransforms' , obj
	newName    = loc2TrfsNewName ( obj )
	trfsReturn = []
	lastTrf  = group ( em = True , n = newName + '_' + trfs[-1])
	print 'lastTrf ' , lastTrf
	trfsReturn.insert (0, lastTrf)
	print 'insert' , obj,lastTrf ############################# ver q tienen estas variables
	move2(obj,lastTrf)
	print 'move2'
	parent (obj , lastTrf)
	print 'parent'
	for index in range( len(trfs) )[1:-1][::-1]:
		ztr  = group ( em = True , n = newName + '_' + trfs[index] )
		move2 ( lastTrf , ztr )
		parent( lastTrf , ztr)
		lastTrf = ztr
		trfsReturn.insert (0, lastTrf)
	rootTrf  = group ( em = True , n = newName + '_' + trfs[0])
	parent ( lastTrf , rootTrf )
	trfsReturn.insert (0, rootTrf)
	print  trfsReturn
	print '           customTransforms OK'
	return trfsReturn

def createAimSystem ( systemName , follower , target ,  headBBoxCenter ):
	'''
	crea sistema de aim con la posibilidad de twist.
	systemName		: nombre del sistema.
	follower		: objeto que mira al target.
	target			: objeto al que mira el follower.
	headBBoxCenter	: centro del BoundingBox

	El RETURN puede ser utilizado para conectar la rotacionZ del upLocatorGrp a algun atributo.
	Return targetLocator , upLocatorGrp
	'''
	print 'createAimSystem'
	systemGrp_  = group ( em=1 , n = systemName + '_AimSystem_GRP' )
	controlGrp_ = group ( em=1 , n = systemName + '_Controls_GRP')
	locUpGrp_   = group ( em=1 , n = systemName + '_LocUp_GRP')
	locAim   = spaceLocator( n=systemName+'_Target_LOC' )
	locAimUp = spaceLocator( n=systemName+'_Up_LOC' )
	# renombro followwer . le pongo prefijo del systemName.
	rename ( follower , systemName+'_'+follower.name() )
	print 'follower ' , follower
	#locAim.visibility.set(0)
	locAim.translate.set  ( headBBoxCenter[0] , headBBoxCenter[1]    , headBBoxCenter[2] +1)
	locAimUp.translate.set( headBBoxCenter[0] , headBBoxCenter[1]+1  , headBBoxCenter[2]   )
	# creo transforms para el placer
	ztrOffTrf3DPlacer = customTransforms ( follower , ['ZTR','AIM','TRF']) # creo transforms para aim y orient constraints
	# creo transforms para el locUp
	upLocGroup        = upLocGrpMaker ( locAimUp , headBBoxCenter )
	# creo transforms para el target
	targetGroup = customTransforms ( locAim , ['ZTR','TRF','CNT']) # creo transforms para aim y orient constraints
	# parentando groupo del locUp al grupo root
	parent ( upLocGroup[0] , locUpGrp_ )
	# parentando el locator target al transform CNT
	parent (locAim , targetGroup[2])
	# parentando el locator target al transform de controles.
	parent (targetGroup[0] , controlGrp_)
	# parentando a la carpeta general del sistema.
	parent ( controlGrp_ , locUpGrp_ , ztrOffTrf3DPlacer[0] , systemGrp_ )
	# constraint : projection mira al locator target
	aimConst=aimConstraint( locAim ,ztrOffTrf3DPlacer[1],mo=0,n=locAim.name()+'_AIMC',aim=[0,0,1],wut='object',wuo=upLocGroup[1] )
	move2 ( target , locAim )
	return locAim , upLocGroup[0]


































































def constraintObj2Cnt (sel,cnts):
    for o in sel:
        for cnt in cnts[0]:
            if o.split('JNT')[0] == cnt.split('CNT')[0]:
                cmds.parentConstraint(cnt,o,mo=True,n=cnt.split('CNT')[0]+'_HCNT')

def renameMakeNurbCircle( makeNode ):
    oCurve = listConnections( makeNode , sh=1)[0]
    newNameMakeCircle = oCurve.split('Shape')[0] + '_makeNCircle'
    return rename ( makeNode , newNameMakeCircle )

def asignText ( imgSeq , fPath ) :
    '''
    asigna textura al nodo file.
    '''
    if isfile ( fPath ):
        try:
            imgSeq.fileTextureName.set ( fPath )
        except:
            pass

def connectUV2File( uvNode , fileNode ):
    atrs = {'.outUV': '.uvCoord',
            '.coverage':'.coverage',
            '.mirrorU':'.mirrorU',
            '.mirrorV':'.mirrorV',
            '.noiseUV':'.noiseUV',
            '.offset':'.offset',
            '.repeatUV':'.repeatUV',
            '.rotateUV':'.rotateUV',
            '.stagger':'.stagger',
            '.translateFrame':'.translateFrame',
            '.wrapU':'.wrapU',
            '.wrapV':'.wrapV',
            '.outUvFilterSize':'.uvFilterSize',
            '.vertexCameraOne':'.vertexCameraOne',
            '.vertexUvOne':'.vertexUvOne',
            '.vertexUvThree':'.vertexUvThree',
            '.vertexUvTwo':'.vertexUvTwo'
            }
    for k in atrs.keys():
        connectAttr ( uvNode + k , fileNode + atrs[k] )

def create2DUvNode( name ):
    uvNode = createNode ( 'place2dTexture' , n = name + '_2DP')
    uvNode.wrapU.set(0)
    uvNode.wrapV.set(0)
    return uvNode

def createFacePart ( filePath , pos , layerTex , createAt , projScale ,uvNode):
	'''
	filePath  : path del archivo
	pos       : posicion que corresponde al layer en el layeredTexture.
	layerTex  : nombre del layer.
	createAt  : centro de la cabeza.
	projScale : depth del BoundingBox.
	uvNode    : nodo de uv compartido entre las texturas.

	RETURN  projector , imgSeq , texturePlacer , pos
	'''

	layer = filePath.split('\\')[-1].split('.')[0]
	projector      = createNode ( 'projection' ,     n = layer + '_PRJ'    )
	projector.projType.set(3)
	projector.uAngle.set(100)
	projector.vAngle.set(0)
	imgSeq         = createNode ( 'file'       ,     n = layer + '_FILE'   )
	imgSeq.useFrameExtension.set(True)
	texturePlacer  = createNode ( 'place3dTexture' , n = layer + '_3DP')  # repr(texturePlacer) help(nt.Place3dTexture)
	texturePlacer.inheritsTransform.set(True)
	texturePlacer.translate.set ( createAt )
	texturePlacer.rotateOrder.set(2)
	#texturePlacer.visibility.set (0)
	connectAttr ( texturePlacer + '.worldInverseMatrix[0]' , projector + '.placementMatrix' , f = 1 )  # conecto matrices
	# asigno textura al file.
	asignText ( imgSeq , filePath )
	# conecto el nodo uv2d a la imagen
	connectUV2File( uvNode , imgSeq )
	# conecto color y alfa de secuencia de imagen a projector
	connImg2ProjColor ( imgSeq , projector  )
	return projector , imgSeq , texturePlacer , pos

def connImg2ProjColor ( imgSeq , projector  ):
    '''
    Conecta color de imgSeq a projector.
    '''
    connectAttr ( imgSeq + '.outColor'     , projector + '.image' )

def locChooser (layer,locs):
    '''
    Determina cuál locator se va a usar para crear los controles.
    '''
    if layer == 'l_ojo' or layer == 'l_pupila' or layer ==  'l_parpado' or layer ==  'extras':
        choosenLoc = locs[0]
    else:
        choosenLoc = locs[1]
    return choosenLoc

def getLocation ( ): # del bBoxCentera
    sel = ls(sl=1)
    if len ( sel )== 1 and nodeType( sel[0].getShape() )== 'mesh' :
        if sel[0]  :
            bBoxCenter = sel[0].getBoundingBox().center()
            return bBoxCenter
    else:
        warning ( ' Selection is null or multiple. Positioning at (0,0,0) ' )
        return dt.Vector([0.0, 0.0, 0.0])

def createIfNeeded( node_Name , node_Type ):
    if not objExists ( node_Name ) :
        nodeRet  =   createNode ( node_Type , n = node_Name )
    else:
        nodeRet   = node_Name
    return nodeRet

def connectAlphas ( layeredTextureDic ):#alphas[7] pos=7
    for pos in layeredTextureDic.keys():
        print ( layeredTextureDic[ alphas[pos] ][1] , layeredTextureDic[alphas[pos] ][0] )
        connImg2ProjAlpha ( layeredTextureDic[ alphas[pos] ][1] , layeredTextureDic[alphas[pos] ][0] )

def connImg2ProjAlpha ( imgSeq , projector  ):
    '''
    Conecta  alfa de imgSeq a projector.
    '''
    # conecto con el alfa q necesito que recorte.
    for channel in ('R','G','B'):
        connectAttr ( imgSeq.name()  + '.outAlpha' , projector + '.transparency' + channel )

def selValidation ( selObjects ):  # selObjects = ls(sl=1)
    counter = { 'locators': 0 , 'meshes': 0 , 'controls': 0 }
    if len (selObjects) == 3:
        for s in selObjects:
            if nodeType( s.getShape() ) == 'locator':
                counter['locators'] = counter['locators']+1
            elif nodeType( s.getShape() ) == 'mesh':
                counter['meshes'] = counter['meshes']+1
            elif nodeType( s.getShape() ) == 'nurbsCurve':
                counter['controls'] = counter['controls']+1
        return counter['locators']==1 and counter['meshes']==1 and counter['controls']==1
    else:
        return False

def getLocation ( meshS ): # del bBoxCentera
    bBoxCenter = meshS.getBoundingBox().center()  # repr (ls(sl=1)[0].getBoundingBox() ) help( dt.BoundingBox ) help( nt.Transform )
    return bBoxCenter

def validateInitLocButtCmd(*args):
    if len(ls(sl=1))==1 and nodeType( ls(sl=1)[0].getShape() ) == 'mesh':
        return createInitialLocators( ls(sl=1)[0] )
    else:
        warning ('Please, select the head mesh.')

def createInitialLocators(sel):
    '''
    Crea locators para posicion inicial de projectores.
    '''
    location = getLocation (  sel )
    locationOffsetX = sel.getBoundingBox().width() / 4 # help (nt.Transform)   help (dt.BoundingBox)   ls(sl=1)[0].translate.set ( 1,1,1)
    locationOffsetY = sel.getBoundingBox().height()/ 4
    locationOffsetZ = sel.getBoundingBox().depth() / 2
    select(cl=1)
    posX = location[0] + locationOffsetX
    posY = location[1] - locationOffsetY
    posZ = location[2] + locationOffsetZ
    pEyeX , pEyeY , pEyeZ , pMouthX , pMouthY , pMouthZ = (0,)*6
    if not objExists( 'L_Eye_LOC' ):
        loc1 = spaceLocator( n='L_Eye_LOC')
        loc1.translate.set ( posX , location[1] , posZ )
        pEyeX = posX
        pEyeY = location[1]
        pEyeZ = posZ
    else:
        pEyeX = getAttr('L_Eye_LOC.translateX')
        pEyeY = getAttr('L_Eye_LOC.translateY')
        pEyeZ = getAttr('L_Eye_LOC.translateZ')
    if not objExists( 'Mouth_LOC' ):
        loc2 = spaceLocator( n='Mouth_LOC')
        loc2.translate.set ( location[0] , posY , posZ )
    else:
        pMouthX = getAttr('Mouth_LOC.translateX')
        pMouthY = getAttr('Mouth_LOC.translateY')
        pMouthZ = getAttr('Mouth_LOC.translateZ')

    return { 'L_Eye_LOC': [pEyeX , pEyeY , pEyeZ ]  , 'Mouth_LOC': [ pMouthX , pMouthY , pMouthZ ]  }

def deleteHelpLocators (s):
    for o in ('L_Eye_LOC', 'Mouth_LOC' , s):
        delete (o)

def connProj2LayTexture( projector , layerTex , chNumber  , layeredTextureDic):#chNumber=8 type( layeredTextureDic[chNumber] )
    '''
    Conecta el projector al layeredTexture al canal X. si no esta disponible, lo conecta al proximo disponible.
    '''
    alphas = {7:12 , 8:15 , 9:12 , 10:12 , 11:12 , 12:12 , 13:13 , 14:15 , 15:15 } # que layer usa el alfa de q layer. el 10 usa el 10, el 11 usa el 12, el 13 usa el 13, el 14 usa el 15,,,
    projMultDiv = createNode ('multiplyDivide', name=projector + '_multD')
    connectAttr ( projector.outAlpha , projMultDiv.input1X )
    connectAttr ( layeredTextureDic[ alphas[chNumber] ][0] + '.outAlpha' , projMultDiv.input2X )
    # armo alfa y conecto
    if chNumber==8: # si es extra del ojo, tengo que restar el alfa del parpado.
        minusNode = createNode ('plusMinusAverage', name=projector + '_MIN')
        minusNode.operation.set(2)
        connectAttr ( projMultDiv.outputX , minusNode.input2D[0].input2Dx  )
        connectAttr ( layeredTextureDic[ 13 ][0] + '.outAlpha' , minusNode.input2D[1].input2Dx  )
        connectAttr ( minusNode.output2D.output2Dx , layerTex + '.inputs[' + str(chNumber) + '].alpha' )
    else:
        connectAttr ( projMultDiv.outputX , layerTex + '.inputs[' + str(chNumber) + '].alpha' )
    # conecto rgb
    connectAttr ( projector + '.outColor'  , layerTex + '.inputs[' + str(chNumber) + '].color' )
    return chNumber

def parentControls ( networkDic ) :
    parent ( networkDic[10][3][1][0] , networkDic[12][3][0][0] ) # a_diente child de boca
    delete ( networkDic[10][3][3][0] )                           # borro ROT de a_diente
    parent ( networkDic[11][3][1][0] , networkDic[12][3][0][0] ) # b_diente child de boca
    delete ( networkDic[11][3][3][0] )                           # borro ROT de b_diente
    parent ( networkDic[9][3][1][0] , networkDic[12][3][0][0] )  # lengua child de boca
    delete ( networkDic[9][3][3][0]  )                           # borro ROT de lengua
    parent ( networkDic[8][3][1][0] , networkDic[15][3][0][0] )  # extras child de pupila
    delete ( networkDic[8][3][3][0]  )                           # borro ROT de extras
    for n in range(13,15):
        parent ( networkDic[n][3][1][0] , networkDic[15][3][0][0]  )
        delete ( networkDic[n][3][3][0] )

def placerControl(headSize, upLocTrf , objs=[],placer3d='',nameSuf='ZTR',nameTrf='TRF',nameCNT='CNT',rad=2): #objs=texturePlacer
    '''
    Crea controles para objectos.
    Returns [ [Controls 's name] , [ZTRs 's name]  ]
    '''
    select(cl=1)
    select( objs )
    objs = cmds.ls(sl=1)
    cntsRet     = []
    ztrs        = []
    makeCircles = []
    roots       = []
    for obj in objs: # obj = 'r_pupila_3DP'
        print 'OBJ: ' + obj
        if '|' in obj:
            obj=obj.split('|')[-1]
        if '_' in obj:
            newName=obj.split(obj.split('_')[-1:][0])[0]
        else:
            newName=obj

        ztr=cmds.group(em=True,n=str(newName+nameSuf))
        pcns=cmds.parentConstraint(obj,ztr)[0]
        scns=cmds.scaleConstraint(obj,ztr)[0]
        cmds.delete(pcns,scns)
        trf=cmds.duplicate(ztr,n=str(newName+nameTrf))[0]
        cmds.parent(trf,ztr)
        cntl=cmds.circle(radius=rad,nr=(0,0,1),name=str(newName+nameCNT)) # creo cnt
        cnt=cntl[0]
        pcns=cmds.parentConstraint(trf,cnt) # constraints
        scns=cmds.scaleConstraint(trf,cnt)
        cmds.delete(pcns,scns)              # borro constraints
        cmds.parent(cnt,trf)
        cntsRet.append(cnt)
        ztrs.append (ztr)
        cmds.parent( obj , cnt )
        maya.mel.eval ('DeleteHistory ' + cnt )

        if 'l_ojo' in obj or 'boca' in obj:                               # tamaños para cada tipo
            ccLook (cntl,rad,3,5)
        elif 'l_pupila' in obj or 'lengua' in obj:
            ccLook (cntl,rad*0.6,1,1)
        elif 'l_parpado' in obj :
            ccLook (cntl,rad*1.2,1,1)
        elif 'extras_LOC' == obj :
            ccLook (cntl,rad*0.3,1,4)

        placer3d.scaleX.set(rad)
        placer3d.scaleY.set(rad)
        placer3d.scaleZ.set(headSize)
        scaleConstraint ( cnt , placer3d , mo=1 , skip='z')         # el cnt controla scaleXY solamente



        print 'orientConst'
        orientConstraint ( cnt , upLocTrf , mo=1 , skip=('x','y') )   # el cnt controla rotateZ

        root = cmds.group(em=True,n=str(newName+'ROT'))
        roots.append (root)
        cmds.parent( ztr , root )

        print 'placerControl OK'
    return cntsRet,ztrs,makeCircles,roots

def ccLook ( circ , controlSize , degree , sections ): # apariencia del controlador
    ccShape = listRelatives ( circ )[0]
    ccTrf   = ccShape.getTransform()
    ccTrf.getShape().inputs()[0].radius.set( controlSize )
    ccTrf.getShape().inputs()[0].degree.set(degree)
    ccTrf.getShape().inputs()[0].sections.set(sections)



####### ####### ####### ####### ####### ####### ####### #######

def create2DFacialRig ( *args ): #del s
    selection = ls(sl=1)
    if selValidation ( selection ):
        for s in selection:
            if nodeType( s.getShape() ) == 'locator':
                locSize = s.scale.get()[0]
                print s
                scaleRef = s
            elif nodeType( s.getShape() ) == 'mesh':
                print s
                sel = s
                headSize = s.getBoundingBox().depth() / 2
            elif nodeType( s.getShape() ) == 'nurbsCurve':
                print s
                headControl = s
        location_locators = createInitialLocators(sel)  #createInitialLocators(ls(sl=1)[0])
        mypath       = 'O:\EMPRESAS\RIG_FACE2D\PERSONAJES\MILO\FACES'
        ordenLayers  = { 'extras2' : 7 , 'extras' : 8 , 'lengua' : 9 , 'b_diente' : 10 , 'a_diente' : 11 , 'boca' : 12 , 'l_parpado' : 13 , 'l_pupila' : 14 , 'l_ojo': 15 }
        dirsFiles    = UTILITIES.dirs_files_dic( mypath ,'png')
        layeredTextureDic = {}
        layerTex     =   createIfNeeded ( 'Face_LTX' , 'layeredTexture' )
        faceShader   = createIfNeeded ( 'Face_SHD' , 'aiStandard' )
        headCenter    = sel.getBoundingBox().center()
        print 'sel: ' + sel
        uvNode = create2DUvNode( sel )
        try:
            connectAttr ( layerTex + '.outColor'  , faceShader+ '.color' )
        except:
            pass
        for k in dirsFiles.keys(): # k='O:\EMPRESAS\RIG_FACE2D\PERSONAJES\MILO\FACES\l_ojo'
            layer = k.split('\\')[-1]
            #if 'r_' != layer[0:2] and dirsFiles[k]!=[]:
            if 'l_ojo' == layer:
                # determina cuál locator se va a usar para crear los controles.
                loc = locChooser ( layer , location_locators.keys() )
                # path de secuencia
                filePath = k + '\\' + dirsFiles[k][0]
                # crea projector,file y placer conectados al canal especificado
                projectorImagePlacerInput = createFacePart ( filePath , ordenLayers[ layer ] , layerTex  , headCenter  , headSize , uvNode)
                # guardo parte en dic
                layeredTextureDic [ ordenLayers[ layer ]   ] = projectorImagePlacerInput [ : -1 ]
                # creo sistema Aim. Argumentos: layer, nombreDelPlacer , locatorParaUbicar.translate
                locAim = createAimSystem ( layer , projectorImagePlacerInput[2] , loc , headCenter )
                # creo control para el Aim
                #ccCnt = placerControl ( headSize, locAim[1],objs=locAim , rad = locSize , placer3d = projectorImagePlacerInput[2]  )
                # guardo control
                #layeredTextureDic [ projectorImagePlacerInput[3]  ] = layeredTextureDic [ projectorImagePlacerInput[3]  ] + tuple( [ ccCnt ] )
        # conecto projection a un layer determinado o el siguiente disponible.
        #for k in layeredTextureDic.keys():
        #    connProj2LayTexture( layeredTextureDic[k][0] , layerTex , k , layeredTextureDic)  # (nt.Projection(u'l_ojo_PRJ'), nt.LayeredTexture(u'Face_LTX'), 15)
        #parentControls ( layeredTextureDic )
        #deleteHelpLocators (scaleRef)
    else:
        warning ( '  Selection is null or multiple. Select head mesh ' )

if cmds.window ('win2dFacialRig',exists=1):
    cmds.deleteUI ( 'win2dFacialRig' )
win = cmds.window('win2dFacialRig', title="2D Facial Rig! v1.0" , menuBar=0 , w=400 , s=1 , height= 50, bgc=(0.1,0.1,0.1) , resizeToFitChildren=1 )
col1 = cmds.columnLayout( columnAttach=('left', 5), adjustableColumn=True , rowSpacing=5, cal= "center" , columnWidth=100 , p=win , bgc=(0.15,0.15,0.15)  )
cmds.button('Selecciona el mesh de la cabeza y clickeame.',p=col1,c=validateInitLocButtCmd , w=400) #validateInitLocButtCmd()
cmds.text('Ubica los locators en la boca y ojo.',align='center' , p=col1)
cmds.text('Rotaciones son consideradas.',align='center' , p=col1)
c1 =   cmds.columnLayout( columnAttach=('left', 5), adjustableColumn=True , rowSpacing=5,  cal= "center", columnWidth=550 , p=win , bgc=(0.2,0.2,0.2) )
cmds.text('\nCrea un locator y escalalo como queres los controles:',p=c1)
r0 = cmds.rowLayout( numberOfColumns=1, adjustableColumn=1, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0)] ,p=c1)
cmds.button( label = 'Crear Locator.' , command = 'cmds.spaceLocator(n="scaleReference_LOC")' , p = c1 )
c2 =   cmds.columnLayout( columnAttach=('left', 5) , adjustableColumn=True , rowSpacing=5,  cal= "center", columnWidth=550 , p=win , bgc=(0.2,0.2,0.2) )
cmds.text('Selecciona el scaleReference_LOC , el mesh de la cabeza y el controlador de la cabeza.',p=c2)
r1 = cmds.rowLayout( numberOfColumns=2, columnWidth2=(200, 200), adjustableColumn=1, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0)], p=c2 , bgc=(0.2,0.2,0.2))
cmds.text('y clickea:  ' , p = r1 )
cmds.button( label = 'RIG HEAD' , command = create2DFacialRig , p = r1 )
cmds.showWindow (win)



sistemaAim = 'l_ojo'
cubo     = polyCube( sx=1, sy=1, sz=1, h=1 )[0]
headCurveControl = circle(n='head_CNT')
#cubo.translateY.set(3)

target     = spaceLocator (n='target_LOC')
target.translateZ.set(3)
