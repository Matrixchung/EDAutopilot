from utils import *
pyautogui.PAUSE = 1
pyautogui.FAILSAFE = True

align = False
targetX=targetY=navCenter=-1
coordArray = None
isAligned = 0
remainJumps = 0
status = None
trueStatus = []
exitButton = "templates/exit.png"
exitButtonHL = "templates/exit_highlight.png"
launchButton = "templates/autolaunch.png"
launchButtonHL = "templates/autolaunch_highlight.png"
map_bookmark = "templates/map_bookmark.png"
map_bookmarkHL = "templates/map_bookmark_highlight.png"
map_sothis = "templates/map_sothis.png"
map_sothisHL = "templates/map_sothis_highlight.png"
map_robigo = "templates/map_robigo.png"
map_robigoHL = "templates/map_robigo_highlight.png"
map_plotroute = "templates/map_plot_route.png"
map_plotrouteHL = "templates/map_plot_route_highlight.png"
def setDest(guiFocus,dest):
    # if journal['target'] == None:
    if 1:
        if guiFocus != 'GalaxyMap': 
            sendKey('UI_OpenGalaxyMap') # Toggle Map
            time.sleep(3)
        bookmarkLoc=locateImageOnScreen(map_bookmark)
        if bookmarkLoc[0] == -1: 
            print('Error in setDest():Bookmark button not found')
            return
        pyautogui.click(bookmarkLoc)
        time.sleep(1)
        bookmarkLoc=locateImageOnScreen(map_bookmarkHL) # Entered bookmark screen
        if bookmarkLoc[0] == -1:
            print('Error in setDest():Bookmark highlight not found')
            return
        if dest == 'Sothis': destLoc = locateButtons(map_sothis,map_sothisHL)
        elif dest == 'Robigo': destLoc = locateButtons(map_robigo,map_robigoHL)
        else : return
        time.sleep(1)
        pyautogui.click(destLoc)
        time.sleep(1)
        sendKey('space')
        time.sleep(3)
        plotRoute = locateButtons(map_plotroute,map_plotrouteHL)
        if plotRoute[0] != -1:
            time.sleep(1)
            pyautogui.click(plotRoute)
            time.sleep(2)
            sendKey('space')
            time.sleep(3)
            sendKey('UI_OpenGalaxyMap')
            return


def autoJump():
    global remainJumps,trueStatus,guiFocus,align
    if remainJumps>0:
        sendKey('SpeedZero')
        time.sleep(1)
        # sendKey('TargetAhead')
        # time.sleep(1)
        align = True
        autoAlign()
        time.sleep(1)
        # sendKey('Speed100',hold=2)
        while 'FSDCooldown' in trueStatus:
            trueStatus,guiFocus = update()
            time.sleep(0.1)
        if 'FSDMassLocked' not in trueStatus:
            sendKey('EnableFSD')
            time.sleep(2)
            trueStatus,guiFocus = update()
            time.sleep(1)
            if 'FSDCharging' in trueStatus:
                if 'Supercruise' not in trueStatus:
                    print('Ready to boost')
                    sendDelay(20)
                    sendKey('EngineBoost')
                else :
                    print ('Ready to Speed100')
                    sendDelay(20)
                    sendKey('Speed100')
                while ('FSDJump' in trueStatus and 'FSDCharging' in trueStatus) or 'Supercruise' not in trueStatus or 'FSDCooldown' not in trueStatus: # Waiting for jumping
                    trueStatus,guiFocus = update()
                    time.sleep(0.1)
                remainJumps -= 1
                return
                
def guiBack():
    sendKey('UI_Left',repeat=5)
    sendDelay(0.5)
    sendKey('UI_Down',repeat=5)
    sendDelay(0.5)
    sendKey('space')
def guiBackToMain(guiFocus):
    if guiFocus == 'StationServices':
        locExit = locateButtons(locExit,locExitHL,confidence2=0.8)
        if locExit[0] == -1 : # In Secondary Menu (like Passenger Lounge)
            guiBack()
            time.sleep(2)
            trueStatus,guiFocus = update()
            if guiFocus == 'StationServices':
                locExit = locateButtons(locExit,locExitHL,confidence2=0.8) # try again
                if locExit[0] != -1: pyautogui.click(locExit)
                else :
                    print("Error in guiBackToMain()") # Both Buttons Not Found
                    return
        else: pyautogui.click(locExit) # In Primary Menu (in station)
def launch(guiFocus):
    if guiFocus == 'NoFocus':
        locLaunchHL = locateImageOnScreen(launchButtonHL,confidence=0.9)
        if locLaunchHL[0]!=-1: # Cursor on Auto Launch Button
            sendKey('space')
            return
        else:
            locLaunch = locateImageOnScreen(launchButton,confidence=0.8)
            if locLaunch[0]!=-1: # On Main Panel
                sendKey('UI_Down',repeat=2)
                time.sleep(1)
                sendKey('space')
                return
            else: # GUI NoFocus, but can't find both of the HL Button and normal
                print("Error in launch()")
def update():
    global remainJumps,status
    setJournal()
    trueStatus = showAllTrueStatus()
    guiFocus = getGuiFocus()
    remainJumps = journal['remainingJumpsInRoute']
    status = journal['status']
    return trueStatus,guiFocus
if __name__ == "__main__":
    # cv2.namedWindow('hsv')
    # cv2.createTrackbar('lowH','hsv',0,179,callback)
    # cv2.createTrackbar('lowS','hsv',0,254,callback)
    # cv2.createTrackbar('lowV','hsv',0,254,callback)
    # cv2.createTrackbar('upH','hsv',0,179,callback)
    # cv2.createTrackbar('upS','hsv',0,254,callback)
    # cv2.createTrackbar('upV','hsv',0,254,callback)
    #################################################################### Robigo Cycle Init Starts
    stage1 = stage2 = stage3 = stage4 = False
    isInCycle = False
    #################################################################### Robigo Cycle Init Ends
    # Multiprocessing Init
    print("Creating shared memory block...")
    shrCoord,coordArray = createSharedCoordsBlock()
    c1=Process(target=eventsHandler,args=(eventsQueue,)) # Initialize Events Handler
    c2=Process(target=imageProcessing,args=(shrCoord.name,))
    c1.daemon=True
    c2.daemon=True
    c2.start()
    c1.start()

    statusImg = np.zeros((300,1200,3),np.uint8) # 初始化一个黑色的状态显示界面
    
    while 1:
        targetX,targetY,navCenter,isAligned,isFocused = coordArray
        
        trueStatus,guiFocus = update()
        
        cv2.putText(statusImg,'GUIFocus:%s'%guiFocus,(10,30),cv2.FONT_HERSHEY_DUPLEX,1,(0,255,0))
        cv2.putText(statusImg,"align:%s"%isAligned,(400,30),cv2.FONT_HERSHEY_DUPLEX,1,(0,255,0))
        cv2.putText(statusImg,'state:%s'%trueStatus,(10,60),cv2.FONT_HERSHEY_DUPLEX,1,(0,255,0))
        cv2.putText(statusImg,'Status:%s'%status,(10,90),cv2.FONT_HERSHEY_DUPLEX,1,(0,255,0))
        cv2.putText(statusImg,'Loc:%s'%journal['location'],(310,90),cv2.FONT_HERSHEY_DUPLEX,1,(0,255,0))
        cv2.putText(statusImg,'Target:%s'%journal['target'],(700,90),cv2.FONT_HERSHEY_DUPLEX,1,(0,255,0))
        cv2.putText(statusImg,'remainJumps:%s'%remainJumps,(10,120),cv2.FONT_HERSHEY_DUPLEX,1,(0,255,0))

        if isFocused == 0: cv2.putText(statusImg,'LOST FOCUS',(1000,30),cv2.FONT_HERSHEY_DUPLEX,1,(0,255,0))
        else:
            # if targetX != -1.0 and targetY !=-1.0 and navCenter != -1.0 and align:
            #     offsetX = abs(targetX-navCenter)
            #     offsetY = abs(targetY-navCenter)
            #     if (offsetX>alignDeadZone or offsetY>alignDeadZone): 
            #         alignWithPos(navCenter,targetX,targetY,offsetX=offsetX,offsetY=offsetY)
            #     if offsetX<alignDeadZone and offsetY<alignDeadZone and isAligned==1: # Align completed
            #         align = False
            #         print('Align Completed')
            autoAlign()
            if keyboard.is_pressed('o'):
                align = True
                time.sleep(0.1)
            
            if keyboard.is_pressed('k'):
                if status == 'Docked' and state1 == False:
                    guiBackToMain(guiFocus)
                    print('Backed to main panel')
                    time.sleep(3)
                    trueStatus,guiFocus = update()
                    time.sleep(1)
                    launch(guiFocus)
                    state1=True
                # if status == 'normal':
                if status == 'normal' and state1 == True and state2 == False:
                    sendKey('SpeedZero')
                    time.sleep(1)
                    sendKey('ThrustUp',hold=20)
                    time.sleep(20)
                    print ('Thrust up')
                    trueStatus,guiFocus = update()
                    if 'FSDMassLocked' in trueStatus: # Thrust Again
                        sendKey('ThrustUp',hold=20)
                        time.sleep(20)
                        print ('Thrust up')
                    sendKey('TargetAhead')
                    time.sleep(1)
                    align = True
                    autoAlign()
                    time.sleep(1)
                    sendKey('EnableFSD') # Start Jump
                    time.sleep(2)
                    trueStatus,guiFocus = update()
                    time.sleep(1)
                    if 'FSDCharging' in trueStatus:
                        print('Ready to boost')
                        sendDelay(20)
                        sendKey('EngineBoost')
                        state2 = True
                        while ('FSDJump' in trueStatus and 'FSDCharging' in trueStatus) or 'Supercruise' not in trueStatus or 'FSDCooldown' not in trueStatus: # Waiting for jumping
                            trueStatus,guiFocus = update()
                            time.sleep(0.1)
                        while status!='finishJump': 
                            trueStatus,guiFocus = update()
                            time.sleep(0.1)
                        time.sleep(1)
                        sunAvoiding()
                        align = True
                        autoAlign()
                    
            if keyboard.is_pressed('end'): # test
                # guiBackToMain(guiFocus)
                # time.sleep(1)
                # launch(guiFocus)
                # sunAvoiding()
                autoJump()
                # setDest(guiFocus,'Sothis')
                
            if keyboard.is_pressed('home'): # Screen Capturing
                screenCapture()
                time.sleep(0.1)
            if keyboard.is_pressed('p'):
                cv2.destroyAllWindows()
                closeHandler()
                c1.terminate()
                c2.terminate()
                break

        cv2.imshow("status",statusImg)
        statusImg.fill(0)
        cv2.waitKey(1)
        