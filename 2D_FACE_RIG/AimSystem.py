# -*- encoding: utf-8 -*-

from pymel.core import *


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
    print 'loc2TrfsNewName'
    splitString = '_'
    if not '_' in obj:
        newName = obj.name()
    else:
        newName = '_'.join(obj.name().split(splitString)[:-1:])
    return newName

def customTransforms ( obj , trfs=[] ):
    '''
    Crea transforms desde el mas interior hasta el root, por lo que el orden de los elementos de trfs es relevante.
    Return [trf1,trf2,trf3,...]
    '''
    print 'customTransforms'
    newName    = loc2TrfsNewName ( obj )
    trfsReturn = []
    lastTrf  = group ( em = True , n = newName + '_' + trfs[-1])
    trfsReturn.insert (0, lastTrf)
    move2(obj,lastTrf)
    parent (obj , lastTrf)
    for index in range( len(trfs) )[1:-1][::-1]:
        ztr  = group ( em = True , n = newName + '_' + trfs[index] )
        move2 ( lastTrf , ztr )
        parent( lastTrf , ztr)
        lastTrf = ztr
        trfsReturn.insert (0, lastTrf)
    rootTrf  = group ( em = True , n = newName + '_' + trfs[0])
    parent ( lastTrf , rootTrf )
    trfsReturn.insert (0, rootTrf)
    print 'return:\\n '
    print  trfsReturn
    return trfsReturn

def createAimSystem ( systemName , follower , target ,  headBBoxCenter ):
    '''
    crea sistema de aim con la posibilidad de twist.
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

#testing:

sistemaAim = 'l_ojo'
esfera     = polyCube( sx=1, sy=1, sz=1, h=1 )[0]
target     = spaceLocator (n='taget_LOC')
target.translateZ.set(3)
centroXYZ     = esfera.getBoundingBox().center()
createAimSystem (sistemaAim, esfera, target,  centroXYZ)
#delete(target)
