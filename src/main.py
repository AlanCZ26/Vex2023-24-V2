# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       alan                                                         #
# 	Created:      7/10/2023, 1:26:00 PM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# Brain should be defined by default
brain=Brain()

#controller
controller = Controller()


"""controls:
x = shoot, hold x to continue shooting
l1 = intake in
l2 = intake out
r1 = wings toggle
up = pto/lifter up
down = lifter down/pto
downarrow = ratchet down
rightarrow = ratchet up
r2 = toggle side flipper thing

"""



defaultBrakeMode = BRAKE
#motors
lMotor1 = Motor(Ports.PORT6 , GearSetting.RATIO_6_1, True)
lMotor2 = Motor(Ports.PORT7 , GearSetting.RATIO_6_1, True)
ltMotor = Motor(Ports.PORT1 , GearSetting.RATIO_6_1, True) #PTO motor
rMotor1 = Motor(Ports.PORT8 , GearSetting.RATIO_6_1, False)
rMotor2 = Motor(Ports.PORT9, GearSetting.RATIO_6_1, False)
rtMotor = Motor(Ports.PORT10, GearSetting.RATIO_6_1, False)#PTO motor

intMotor = Motor(Ports.PORT11, GearSetting.RATIO_6_1, True)
cataMotor = Motor(Ports.PORT14, GearSetting.RATIO_36_1, True)
liftSens = Rotation(Ports.PORT19)
cataDist = Distance(Ports.PORT13)
catapultLoadDist = Distance(Ports.PORT12)
gyro = Inertial(Ports.PORT2)

wireExpander = Triport(Ports.PORT20)

PTOpiston =     DigitalOut(wireExpander.a)
wingsSolenoid2= DigitalOut(wireExpander.g)
wingsSolenoid = DigitalOut(wireExpander.h)
sidePiston =    DigitalOut(wireExpander.b)
ratchPiston =   DigitalOut(wireExpander.c)
intakePiston =  DigitalOut(brain.three_wire_port.h)


#variables
PTOvar = 1 #0 = speed, 1 = cata, 2 = switching
brain.screen.print("Hello V5")
button = False
autoCata = False
liftVar = 0

def setDriveStopping(s):
    rMotor1.set_stopping(s)
    rMotor2.set_stopping(s)
    lMotor1.set_stopping(s)
    rMotor2.set_stopping(s)

def drivetrain(lInput, rInput):
    global PTOvar
    lSpeed = lInput / 8
    rSpeed = rInput / 8
    if abs(lInput) < 5:
        lMotor1.stop()
        lMotor2.stop()
        if PTOvar ==0:
            ltMotor.stop()
    if abs(rInput) < 5:
        rMotor1.stop()
        rMotor2.stop()
        if PTOvar ==0:
            rtMotor.stop()
    else:
        lMotor1.spin(FORWARD,lSpeed,VOLT)
        lMotor2.spin(FORWARD,lSpeed,VOLT)
        rMotor1.spin(FORWARD,rSpeed,VOLT)
        rMotor2.spin(FORWARD,rSpeed,VOLT)
        if PTOvar == 0:
            ltMotor.spin(FORWARD,lSpeed,VOLT)    
            rtMotor.spin(FORWARD,rSpeed,VOLT)

def PTOswitcher(i): #t = speed, f = lifter
    global PTOvar
    if i:
        PTOvar = 0 #speed
        PTOpiston.set(True)
        ltMotor.stop()
        rtMotor.stop()
    else:
        PTOvar = 1 #lifter
        PTOpiston.set(False)
        ltMotor.stop()
        rtMotor.stop()

def PTOmotors(s):
    if PTOvar == 1:
        if s == 0: #to stop the motors
            ltMotor.stop()
            rtMotor.stop()
        else:
            ltMotor.spin(FORWARD,s,VOLT)
            rtMotor.spin(FORWARD,s,VOLT)
shootCommand = False
infiniteCata = False

def catapult():
    stallVariable = 0
    global infiniteCata
    global autoCata
    global shootCommand
    while True:
        #stallVariable += 1
        wait(0.01,SECONDS)
        #if not (controller.buttonX.pressing() or (cataDist.object_distance(MM) < 20 and autoCata == True) or shootCommand):
        if infiniteCata == False: cataMotor.stop()
        if (controller.buttonUp.pressing() 
            or (cataDist.object_distance(MM) < 50 and autoCata == True) 
            or (shootCommand)
            or (autoCata == True and stallVariable > 100)):
            #if not controller.buttonX.pressing(): wait(0.05,SECONDS)
            cataMotor.spin(FORWARD,12,VOLT)
            wait(0.3,SECONDS)
            timer = 80
            while (catapultLoadDist.object_distance(MM) > 90) and timer > 0:
                wait(0.01,SECONDS)
                timer -= 1
            if timer == 0:
                cataMotor.spin(REVERSE,12,VOLT)
                wait(0.1,SECONDS)
                cataMotor.stop()
            else:
                shootCommand = False
            stallVariable = 0
            
def lifter():
    global liftVar #1 = up, 2 = down, 0 = none
    global autoCata
    while True:
        wait(0.1,SECONDS)
        if (controller.buttonY.pressing()#controller.axis2.position() > 96 
            or liftVar == 1):
            setDriveStopping(BRAKE)
            PTOswitcher(False)
            ratchPiston.set(False)
            
            controller.screen.print("F")
            wait(0.2,SECONDS)
            controller.screen.set_cursor(0,0)
            ltMotor.set_stopping(BRAKE)
            rtMotor.set_stopping(BRAKE)
            PTOmotors(12) #loop to make it go up until limit
            i = 0
            while (liftSens.position() % 360) < 100 and i < 30:
                wait(0.1,SECONDS)
                i+=1
            wait(0.05,SECONDS)
            PTOmotors(0)
            liftVar = 0
            autoCata = True
        elif (controller.axis2.position() < -96 or liftVar == 2):
            autoCata = False
            PTOmotors(-12) #same as above but in reverse  
            ltMotor.set_stopping(COAST)
            rtMotor.set_stopping(COAST)
            setDriveStopping(defaultBrakeMode)
            i = 0          
            while (liftSens.position() % 360) > 10 and i < 30:
                wait(0.1,SECONDS)
                i+=1
                if i >=25:
                    ratchPiston.set(True)
            wait(0.05 ,SECONDS)
            PTOmotors(0)
            PTOswitcher(True)
            liftVar = 0
        elif (controller.buttonRight.pressing() or liftVar == 3):
            setDriveStopping(BRAKE)
            PTOswitcher(False)
            ratchPiston.set(False)
            controller.screen.print("F")
            controller.screen.set_cursor(0,0)
            ltMotor.set_stopping(HOLD)
            rtMotor.set_stopping(HOLD)
            PTOmotors(12) #loop to make it go up until limit
            i = 0
            while (liftSens.position() % 360) < 50 and i < 30:
                wait(0.1,SECONDS)
                i+=1
            #wait(0.05,SECONDS)
            PTOmotors(0)
            liftVar = 0

def driveInches(lInput,rInput,lSpd,rSpd):
    global PTOvar
    print("""new drive
          -
          -
          -""")
    rMotor1.set_position(0,DEGREES)
    lMotor1.set_position(0,DEGREES)

    if lInput != 0: ldir = lInput/abs(lInput)
    else: ldir = rInput/abs(rInput)
    if rInput != 0: rdir = rInput/abs(rInput)
    else: rdir = ldir


    totalDiff = 3
    while totalDiff >= 2: #2 inches
        #print(totalDiff)
        wait(0.01,SECONDS)
        #converting from deg to inch
        rPos = (rMotor1.position(DEGREES) * (3 / 5)) * 0.02836160034 #3-5 ratio gearing on the wheels
        lPos = (lMotor1.position(DEGREES) * (3 / 5)) * 0.02836160034 #3-5 ratio gearing on the wheels
        #wheels have 3.25 inch diameter, circ = 10.2101761242, 0.02836160034 inches per degree

        DR = rInput - rPos
        DL = lInput - lPos #diffs
        totalDiff = abs(DR) + abs(DL)
        print("r" + str(DR))
        print("l" + str(DL))
        print(totalDiff)
        if abs(DR) >= 1:
            rMotor1.spin(FORWARD,rSpd*rdir,PERCENT)
            rMotor2.spin(FORWARD,rSpd*rdir,PERCENT)
            if PTOvar == 0: rtMotor.spin(FORWARD,rSpd*rdir,PERCENT)
        else:
            rMotor1.stop()
            rMotor2.stop()
            if PTOvar == 0: rtMotor.stop()
        if abs(DL) >= 1:
            lMotor1.spin(FORWARD,lSpd*ldir,PERCENT)
            lMotor2.spin(FORWARD,lSpd*ldir,PERCENT)
            if PTOvar == 0: ltMotor.spin(FORWARD,lSpd*ldir,PERCENT)
        else:
            lMotor1.stop()
            lMotor2.stop()
            if PTOvar == 0: ltMotor.stop()
    drivetrain(0,0)
    wait(0.3,SECONDS)

def driveDist(target):
    driveFunction(target,1.25,0,5,1,2)

def driveFunction(target,Kp,Ki,Kd,intKickin,mv):
    print("New PID instruction: " + str(target))
    lMotor1.reset_position()
    lMotor2.reset_position()
    rMotor1.reset_position()
    rMotor2.reset_position()
    proportional = 3000
    integral = 0
    prevProp = 0
    previousGyro = gyro.rotation()
    error = target + 0.1
    errorPrev = abs(target)
    timer = (abs(target) * 5) + 50
    startingTimer = timer
    listTrueError = []
    listOut = []
    listP = []
    listI = []
    listD = []
    while abs(errorPrev) > 0.5 and (error != errorPrev) and timer > 0:
        timer -= 1
        wait(0.01,SECONDS)
        measure = (lMotor1.position(DEGREES)+lMotor2.position(DEGREES)+rMotor1.position(DEGREES)+rMotor2.position(DEGREES))*0.00425424005
        #to inches: 3.25 (diameter) * pi / 360 / 4

        proportional = target - measure
        if abs(proportional) < intKickin: integral += proportional
        derivative = proportional - prevProp
        prevProp = proportional

        error = proportional * Kp + integral * Ki + derivative * Kd
        listTrueError.append(round(target-measure,2))
        listP.append(round(proportional * Kp,2))
        listI.append(round(integral * Ki,2))
        listD.append(round(derivative * Kd,2))
        errorRot = (gyro.rotation() - previousGyro) * 0.3
        lOut = error - errorRot
        rOut = error + errorRot
        if 0 < lOut < mv: lOut = mv #min values
        elif 0 > lOut > -mv: lOut = -mv
        if 0 < rOut < mv: rOut = mv
        elif 0 > rOut > -mv: rOut = -mv
        drivetrain(lOut*8.3,rOut*8.3)
        listOut.append(round((lOut+rOut)/2,2))
        #print(errorRot)
        print(str(timer)+"0 MS; "+ str(error))
        errorPrev = (errorPrev * 9 + abs(proportional)) / 10
    drivetrain(0,0)
    if timer !=0: print("TOOK "+str(startingTimer-timer)+"0 MS")
    else: print("TIMED OUT")
    """
    wait(1,SECONDS)
    print("-------------")
    print(listTrueError)
    wait(0.2,SECONDS)
    print("-------------")
    print(listP)
    wait(0.2,SECONDS)
    print("-------------")
    print(listI)
    wait(0.2,SECONDS)
    print("-------------")
    print(listD)
    wait(0.2,SECONDS)
    print("-------------")
    print(listOut)
    wait(1,SECONDS)
    wait(0.05,SECONDS)
    """
def driveDist2(target,velo):
    print("New PID instruction: " + str(target))
    lMotor1.reset_position()
    lMotor2.reset_position()
    rMotor1.reset_position()
    rMotor2.reset_position()
    proportional = 3
    integral = 0
    prevProp = 0
    previousGyro = gyro.rotation()
    Kp = velo
    Ki = 0
    Kd = 0
    error = target + 0.1
    errorPrev = abs(target)
    timer = (abs(target) * 3) + 50
    while abs(errorPrev) > 1.5 and (error != errorPrev) and timer > 0:
        timer -= 1
        wait(0.01,SECONDS)
        measure = (lMotor1.position(DEGREES)+lMotor2.position(DEGREES)+rMotor1.position(DEGREES)+rMotor2.position(DEGREES))*0.00425424005
        #to inches: 3.25 (diameter) * pi / 360 / 4

        proportional = target - measure
        integral += proportional
        derivative = proportional - prevProp
        prevProp = proportional

        error = proportional * Kp + integral * Ki + derivative * Kd
        errorRot = (gyro.rotation() - previousGyro) * 0.1
        lOut = error - errorRot
        rOut = error + errorRot
        min = 3
        if 0 < lOut < min: lOut = min #min values
        elif 0 > lOut > -min: lOut = -min
        if 0 < rOut < min: rOut = min
        elif 0 > rOut > -min: rOut = -min
        drivetrain(lOut*8.3,rOut*8.3)
        #print(errorRot)
        print(error)
        errorPrev = (errorPrev * 9 + abs(proportional)) / 10
    drivetrain(0,0)
    wait(0.05,SECONDS)

absoluteAngle = 0
def rotCall(target):
    if True:#abs(target) == 90: #tuned 90 degree turn, 700ms either direction
        rotDeg(target, 0.25, 0.0, 1.2, 200, 3.5, 5)
        #rotDeg(target,0.6,0,0,0,3,0) rotDeg(target, 0.19, 0.0, 1, 80, 2, 5)
        #Ku = 2, Tu = 400 MS
        #Tu data: 103 - 81 - 63, 144 - 122 - 103
    else: #default
        rotDeg(target, 0.19, 0.0, 1, abs(target * 1.5) + 10, 2, 5)

def rotCall2(target,p,d):
    if True:#abs(target) == 90: #tuned 90 degree turn, 700ms either direction
        rotDeg(target, p, 0.0, d, 200, 3.5, 5)
        #rotDeg(target,0.6,0,0,0,3,0) rotDeg(target, 0.19, 0.0, 1, 80, 2, 5)
        #Ku = 2, Tu = 400 MS
        #Tu data: 103 - 81 - 63, 144 - 122 - 103
    else: #default
        rotDeg(target, 0.19, 0.0, 1, abs(target * 1.5) + 10, 2, 5)

def rotDeg(target, Kp, Ki, Kd, timer, mv, iw):
    global absoluteAngle
    inPrinter = target
    absoluteAngle += target
    print("New rotation instruction: " + str(target))
    target = absoluteAngle
    print("New absolute angle: "+ str(absoluteAngle))
    print("Current rotation: " + str(gyro.rotation()))
    error = 100
    integral = 0
    prevErr = abs(target - gyro.rotation()) 
    realPrevErr = prevErr
    startingTime = timer
    testing = False
    if testing == True:
        listP = []
        listI = []
        listD = []
        listO = []
        listR = []
    while abs(prevErr) > 0.5 and timer > 0: #and prevErr != error:
        timer -= 1
        wait(0.01,SECONDS)
        rot = gyro.rotation()
        error = target - rot
        integral += error
        if (integral * Ki) > iw: integral = iw / Ki
        derivative = error - realPrevErr
        realPrevErr = error
        output = (error * Kp) + (integral * Ki) + (derivative * Kd)
        #if output > sub: output -= sub
        #elif output < -sub: output += sub
        if output > 0 and output < mv: output = mv #min values
        elif output < 0 and output > -mv: output = (-1*mv)
        if False:
            listP.append(round(error * Kp,2))
            listI.append(round(integral * Ki,2))
            listD.append(round(derivative * Kd,2))
            listO.append(round(error,2))
            listR.append(round(output,2))        
        drivetrain(output*8,output*-8)
        print(str(timer)+"0MS, "+str(error))
        prevErr = (prevErr * 1 + abs(error)) / 2
    if timer == 0: print("TIMED OUT")
    else:
        print("COMMAND: " + str(inPrinter)) 
        print("TOOK " + str(startingTime - timer) + "0 MS")
    drivetrain(0,0)
    wait(0.05,SECONDS)
    if False:
        wait(0.2,SECONDS)
        #print(listP)
        print("-----------------------")
        wait(0.2,SECONDS)
        print(listI)
        print("-----------------------")
        wait(0.2,SECONDS)
        print(listD)
        print("-----------------------")
        wait(0.2,SECONDS)
        print(listO)
        print("-----------------------")
        wait(0.2,SECONDS)
        print(listR)
        print("-----------------------")
        wait(0.2,SECONDS)



#control functions
def pre_autonomous():
    global shootCommand
    gyro.calibrate
    wingsSolenoid.set(False) #start with wings in
    wingsSolenoid2.set(False)
    PTOpiston.set(False) #start with lift mode
    sidePiston.set(False) #start with side up
    ratchPiston.set(False) #start with ratchet up
    
    #pre auton
    brain.screen.clear_screen()
    brain.screen.print("pre auton code")
    #auton side value
    global n
    n = 3 #change value to change starting side, 1=L, 2=R, 3=driver
    t2 = Thread(catapult)
    t3 = Thread(lifter)
    setDriveStopping(defaultBrakeMode)
    rMotor1.stop()
    rMotor2.stop()
    lMotor1.stop()
    lMotor2.stop()

    cataMotor.set_stopping(HOLD)
    intMotor.set_stopping(HOLD)
    wait(2,SECONDS)
    intakePiston.set(True)
    shootCommand = True
    Select = True #set to true to not run the loop
    if Select == False: #auton select menu
        n = 1
        upPressedPrev = False
        downPressedPrev = False        
        controller.screen.clear_screen
        controller.screen.set_cursor(1,10)
        controller.screen.print("Left")
        controller.screen.set_cursor(2,10)
        controller.screen.print("Right")   
        #controller.screen.set_cursor(0,10)
        #controller.screen.print("Double")
        controller.screen.set_cursor(3,10)
        controller.screen.print("Manual")
        controller.screen.set_cursor(1,1)
        while Select == False:
            wait(0.1,SECONDS) #cycle time
            if controller.buttonUp.pressing(): upPressed = True
            else: upPressed = False
            if controller.buttonDown.pressing(): downPressed = True
            else: downPressed = False
            if downPressed != downPressedPrev and downPressed == True:
                controller.screen.set_cursor(n,5) #clear previous cursor
                controller.screen.print(" ")
                n += 1 #change value
                if n > 3: n = 3
                controller.screen.set_cursor(n,5) #update cursor
                controller.screen.print(">")
            if upPressed != upPressedPrev and upPressed == True:
                controller.screen.set_cursor(n,5) #clear previous cursor
                controller.screen.print(" ")
                n -= 1 #change value
                if n < 1: n = 1
                controller.screen.set_cursor(n,5) #update cursor
                controller.screen.print(">  ")
            upPressedPrev = upPressed #update prev values
            downPressedPrev = downPressed
            #press 2 buttons to confirm
            if controller.buttonRight.pressing() and controller.buttonY.pressing():
                if 0 <= n <= 3: Select = True #make sure n is in the range [1,3]
                print(n)# 1 = Left, 2 = Right, n/a = Double, 3 = driver
                Select = True #exit the loop
                controller.screen.clear_screen()

def autonomous():
    global infiniteCata
    global autoCata
    global liftVar
    global absoluteAngle
    global shootCommand
    setDriveStopping(BRAKE)
    intakePiston.set(False)
    
    #auton
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    #right side: push in alliance ball, grab left ball, put in front of goal, 
    #get center ball that's touching bar, turn, push that one along with the middle one and the other one in with wings
    #left side: push alliance ball in, get ball out of corner, let go of ball, go touch pole
    if False: #ballrush nearside
        if True:
            wait(0.1,SECONDS)
            wingsSolenoid2.set(True)
            wait(0.5,SECONDS)
            wingsSolenoid2.set(False)
            intMotor.spin(FORWARD,12,VOLT)
            driveDist(49)
            rotCall(90)
            intMotor.stop()
            intMotor.spin(REVERSE,12,VOLT)
            wingsSolenoid2.set(True)
            driveDist(22)
            intakePiston.set(True)
            wait(0.3,SECONDS)
            driveDist(-5)
            intakePiston.set(False)
            wingsSolenoid2.set(False)
            intMotor.stop()
            rotCall(-50)
            driveDist(-64)
            intMotor.spin(REVERSE,12,VOLT)
            intakePiston.set(True)
            rotCall(-40)
            wingsSolenoid2.set(True)
            drivetrain(100,100)
            wait(0.5,SECONDS)
            drivetrain(0,0)
            wingsSolenoid2.set(False)
            intMotor.stop()
            rotCall(-15)
            driveDist(-28)
            wingsSolenoid2.set(True)
            rotCall(-435)
    else: 
        gyro.set_rotation(0)
        if   False: #skills auto
            shootCommand = True
            intMotor.spin(FORWARD,12,VOLT)
            wait(0.1,SECONDS)
            rotCall(-27)
            intMotor.stop()
            driveDist(20)
            rotCall(27) #get in front of the goal
            if False:
                intakePiston.set(True)
                wait(0.6,SECONDS)
                driveDist(-6)
                rotCall(180)
                drivetrain(-100,-100)
                wait(0.6,SECONDS)
                drivetrain(0,0)
                driveDist(8)
                rotCall(-90)
            else:
                drivetrain(-100,-100)
                intakePiston.set(True)
                intMotor.spin(REVERSE,12,VOLT)
                wait(0.1,SECONDS)
                drivetrain(100,100)
                wait(0.6,SECONDS)
                drivetrain(0,0)
                intMotor.stop()
                driveDist(-12)
                rotCall(90)
            intakePiston.set(False)
            drivetrain(-50,-50)
            wait(0.5,SECONDS)
            drivetrain(100,100)
            wait(0.1,SECONDS)
            drivetrain(0,0)
            liftVar = 3
            
            rotCall(-25)
            sidePiston.set(True)
            ratchPiston.set(True)
            autoCata = True
            #infiniteCata = True
            #cataMotor.spin(REVERSE,12,VOLT)
            drivetrain(-50,-20)
            wait(0.5,SECONDS)
            rotCall(-5)
            drivetrain(-20,-20)
            wait(0.5,SECONDS)
            wait(24,SECONDS) #25 or 28 ----------
            ratchPiston.set(False)
            wait(2,SECONDS)
            sidePiston.set(False)
            liftVar = 2
            
            wait(0.1,SECONDS)
            driveDist(3)
            cataMotor.stop()
            autoCata = False 
            #infiniteCata = False
            rotCall(65)
            shootCommand = True
            driveDist(33)
            rotCall(-216)

            #driveDist(-78) #across
            driveDist(-82)

            intakePiston.set(True)
            PTOswitcher(True)

            if False:
                rotCall(-34)
                driveDist(-22)
                rotCall(-55)
            else:
                sidePiston.set(True)
                rotCall(-20)
                drivetrain(-100,-50)
                wait(1,SECONDS)
            sidePiston.set(True)
            drivetrain(100,100)
            wait(0.2,SECONDS)
            drivetrain(-100,-100)
            wait(0.6,SECONDS)
            drivetrain(100,100)
            wait(0.2,SECONDS)
            drivetrain(-100,-100)
            wait(0.6,SECONDS)
            rotCall(-70)
            driveDist(15)
            sidePiston.set(False)
            rotCall(-60)
            driveDist(-45)
            rotCall(60)

            #first push
            driveDist(-20)
            rotCall(-90)
            wingsSolenoid.set(True)
            wingsSolenoid2.set(True)
            wait(0.2,SECONDS)
            drivetrain(100,100)
            wait(0.9,SECONDS)
            drivetrain(-70,-70)
            wingsSolenoid.set(False)
            wingsSolenoid2.set(False)
            wait(0.1,SECONDS)
            rotCall(0)
            driveDist(-24)
            rotCall(90)
            driveDist(-30)
            rotCall(-70)
            wingsSolenoid.set(True)
            wingsSolenoid2.set(True)
            wait(0.1,SECONDS)
            drivetrain(100,100)
            wait(0.9,SECONDS)
            drivetrain(-100,-100)
            wait(0.3,SECONDS)
            rotCall(-20)
            drivetrain(100,100)
            wait(0.6,SECONDS)
            wingsSolenoid.set(False)
            wingsSolenoid2.set(False)
            driveDist(-7)
            rotCall(-90)
            driveDist(53)
            rotCall(-70)
            #side in
            drivetrain(-50,-100)
            wait(1,SECONDS)
            drivetrain(100,100)
            wait(0.4,SECONDS)
            rotCall(50)
            drivetrain(-100,-100)
            wait(1,SECONDS)
            drivetrain(100,100)
            wait(0.4,SECONDS)
            rotCall(0)
            drivetrain(-100,-100)
            wait(1,SECONDS)
            drivetrain(100,100)
            wait(0.4,SECONDS)
            drivetrain(0,0)
        elif False: #bad (not working) 6 ball
            intMotor.spin(FORWARD,12,VOLT)
            driveDist(3)
            wait(0.2,SECONDS)
            driveDist2(-35,0.5)
            intMotor.stop()
            rotCall(135)
            sidePiston.set(True)
            driveDist(15)
            drivetrain(-80,80)
            intMotor.spin(REVERSE,12,VOLT)
            wait(0.3,SECONDS)
            sidePiston.set(False)
            wait(0.4,SECONDS)
            drivetrain(0,0)
            rotCall(-180)
            sidePiston.set(True)
            drivetrain(-100,-50)
            wait(0.8,SECONDS)
            drivetrain(-100,-100)
            wait(0.2,SECONDS)
            intakePiston.set(True)
            intMotor.spin(REVERSE,12,VOLT)
            drivetrain(100,100)
            wait(0.25,SECONDS)
            drivetrain(-100,-100)
            wait(0.6,SECONDS)
            drivetrain(0,0)
            intMotor.stop()
            driveDist(8)
            rotCall(85)
            intakePiston.set(False)
            driveDist(56)
            intMotor.spin(FORWARD,12,VOLT)
            rotCall(140)
            intMotor.spin(REVERSE,6,VOLT)
            wait(0.3,SECONDS)
            rotCall(-55)
            intMotor.spin(FORWARD,12,VOLT)
            driveDist(24)
            rotCall(100)
        elif True: #left side auto
            intMotor.spin(FORWARD,12,VOLT)
            sidePiston.set(True)
            wait(0.1,SECONDS)
            rotCall(-30)
            intMotor.stop()
            rotCall(10)
            sidePiston.set(False)
            rotCall2(-90,0.35,1.2)
            driveDist(20)
            rotCall(-25)
            driveDist(28)
            rotCall(-90)
            #driveDist(18)
            drivetrain(100,100)
            intMotor.spin(REVERSE,11,VOLT)
            intakePiston.set(True)
            wait(0.6,SECONDS)
            drivetrain(-100,-100)
            wait(0.2,SECONDS)
            drivetrain(0,0)
            driveDist(-6)
            intakePiston.set(False)
            rotCall(180)
            wingsSolenoid2.set(True)
            intMotor.spin(REVERSE,11,VOLT)
            wait(0.2,SECONDS)
            driveDist(29)
            wingsSolenoid2.set(False)
            intMotor.stop()
            rotCall(-60)
            driveDist(-58)
            intMotor.spin(REVERSE,12,VOLT)
            rotCall(60)
            intakePiston.set(True)
            driveDist(37)
            intMotor.stop()
            #intakePiston.set(True)
        elif False: #thingie
            driveDist(-14)
            rotCall(-70)
            sidePiston.set(True)
            autoCata = True
            wait(3,SECONDS)
            sidePiston.set(False)
            wait(0.1,SECONDS)
            autoCata = False
            driveDist(3)
            rotCall(55)
            driveDist(18)
            rotCall(-115)
            drivetrain(-80,-80)
            wait(0.8,SECONDS)
            print(absoluteAngle)
            print("ABS ANGLE RESET")
            absoluteAngle = -135
            drivetrain(0,0)
            driveDist(5)
            rotCall(-90)
        elif False: #far side skullbash
            drivetrain(-100,-100)
            wait(1,SECONDS)
            drivetrain(100,100)
            wait(0.3,SECONDS)
            rotCall(0)
            drivetrain(-100,-100)
            wait(1,SECONDS)
            drivetrain(100,100)
            wait(0.3,SECONDS)
            rotCall(0)
            drivetrain(-100,-100)
            wait(1,SECONDS)
            drivetrain(100,100)
            wait(0.3,SECONDS)
            rotCall(0)
        else:
            driveDist(-24)
            driveDist(24)

    """
    if True:
        sidePiston.set(True)
        wait(0.1,SECONDS)
        rotDeg(-30)
        rotDeg(10)
        sidePiston.set(False)
        rotDeg(-90)
        driveDist(20)
        rotDeg(-25)
        driveDist(25)
        rotDeg(-90)
        #driveDist(18)
        drivetrain(80,80)
        wait(0.3,SECONDS)
        intMotor.spin(REVERSE,6,VOLT)
        wait(0.3,SECONDS)
        drivetrain(-60,-60)
        wait(0.2,SECONDS)
        drivetrain(80,80)
        wait(0.2,SECONDS)
        drivetrain(-100,-100)
        wait(0.1,SECONDS)
        driveDist(-6)
        rotDeg(180)
        wingsSolenoid.set(True)
        intMotor.spin(REVERSE,11,VOLT)
        wait(0.5,SECONDS)
        driveDist(30)
        wingsSolenoid.set(False)
        intMotor.stop()
        rotDeg(-90)
        drivetrain(-80,-60)
        wait(1,SECONDS)
        sidePiston.set(True)
        wait(0.1,SECONDS)
        rotDeg(45)
    elif True:
        rotDeg(45)
        driveDist(-16)
        liftVar = 1
        rotDeg(-70)
        sidePiston.set(True)
        autoCata = True
        wait(40,SECONDS)
        autoCata = False
        sidePiston.set(False)        
        wait(0.1,SECONDS)        
        liftVar = 2
        driveDist(5)#backup
        rotDeg(60) #face pole
        driveDist(30)
        rotDeg(-135) #straighten
        drivetrain(-60,-60)
        wait(0.5,SECONDS)
        drivetrain(0,0)
        driveDist(5)
        rotDeg(-93)
        driveDist(-70)
        rotDeg(-45)
        #driveDist(-40)
        #rotDeg(-45)
        drivetrain(-70,-50)
        wait(0.9,SECONDS)
        drivetrain(0,0)
        
        driveDist(-18) #welcome to the jam
        driveDist(12)
        driveDist(-18)
        driveDist(12)
        driveDist(-18)
        driveDist(16)
        
        rotDeg(-60) #face mid
        driveDist(-48)
        rotDeg(-30)
        drivetrain(-40,-40)
        wait(0.8,SECONDS)
        drivetrain(0,0)
        wingsSolenoid.set(True)
        intMotor.spin(REVERSE)
        wait(0.1,SECONDS)
        driveDist(25)
        driveDist(-12)
        driveDist(18)
        driveDist(-12)
        driveDist(18)
    """
    """
    if False: #left side, corner side
        driveInches(-8,0,20,20) #initial turn
        driveInches(-27,-27,30,30) #push ball towards side
        driveInches(8,0,30,30) #rotate to face
        driveInches(-7,-7,100,100) #slam
        driveInches(0,3,80,80) #turn
        driveInches(24,24,70,70) #go tw corner
        driveInches(6.5,-6.5,80,80) #turn
        driveInches(13,13,40,40) #go toward corner
        intakeSolenoid.set(True)
        wait(0.6,SECONDS)
        driveInches(-10,-10,50,50) #leave
        driveInches(8,-8,40,40)
        intakeSolenoid.set(False)
        driveInches(-14,14,40,40)
        #driveInches(-8,8,40,40)
        #driveInches(-5,5,70,70) #turn
        driveInches(30,30,70,70) #square against wall
        driveInches(-3,-3,50,50) #back to turn
        driveInches(-9,9,70,70) #turn
        driveInches(37,37,60,60) #touch pole
    elif False: #skills
        driveInches(-8,0,20,20) #initial turn
        driveInches(-27,-27,30,30) #push ball towards side
        driveInches(8,0,30,30) #rotate to face
        driveInches(2,2,80,80)
        cataAuto(1)
        driveInches(-7,-7,100,100) #slam
        driveInches(9,9,70,70)
        driveInches(0,5,70,70)
        driveInches(-12,12,50,50)
        driveInches(-6,-6,50,50)
        driveInches(2,-2,50,50)
        drivetrain(-2,-2)
        intakeSolenoid.set(True)
        wait(0.8,SECONDS)
        cataAuto(50)
        drivetrain(0,0)
    elif True: #right side, push under
        driveInches(0,-8,20,20) #initial turn
        driveInches(-27,-27,30,30) #push ball towards side
        driveInches(0,8,30,30) #rotate to face
        driveInches(2,2,80,80) #momentum
        driveInches(-7,-7,100,100) #slam
    """
"""
class risingEdgeInput():
    def __init__(self, inputButton, output, startingState) -> None:
        self.inputButton = inputButton
        self.output = output
        self.previous = False
        self.state = startingState
        controller.axis1

    def tick(self,input):
        if self.previous == False and input == True:
            self.state = not self.state
            self.previous = input
            return self.state
"""


def user_control():
    #user control
    brain.screen.clear_screen()
    controller.screen.print("user")
    global button
    global autoCata
    global liftVar

    #ltMotor.set_stopping(HOLD)
    #rtMotor.set_stopping(HOLD)
    intakePiston.set(False)

    tWings = False
    pWings = False
    tFlip = False
    pFlip = False
    tRatch = True
    pRatch = False

    tInt = False
    pInt = False

    if False:
        intMotor.spin(FORWARD,12,VOLT)
        shootCommand = True
        wait(0.1,SECONDS)
        rotCall(-27)
        intMotor.stop()
        driveDist(20)
        rotCall(27) #get in front of the goal
        if False:
            intakePiston.set(True)
            wait(0.6,SECONDS)
            driveDist(-6)
            rotCall(180)
            drivetrain(-100,-100)
            wait(0.6,SECONDS)
            drivetrain(0,0)
            driveDist(8)
            rotCall(-90)
        else:
            drivetrain(-100,-100)
            intakePiston.set(True)
            intMotor.spin(REVERSE,12,VOLT)
            wait(0.1,SECONDS)
            drivetrain(100,100)
            wait(0.6,SECONDS)
            drivetrain(0,0)
            intMotor.stop()
            driveDist(-12)
            rotCall(90)
        intakePiston.set(False)
        drivetrain(-50,-50)
        wait(0.5,SECONDS)
        drivetrain(100,100)
        wait(0.1,SECONDS)
        drivetrain(0,0)
        liftVar = 3
        
        rotCall(-25)
        sidePiston.set(True)
        ratchPiston.set(True)
        autoCata = True
        #infiniteCata = True
        #cataMotor.spin(REVERSE,12,VOLT)
        drivetrain(-50,-20)
        wait(0.5,SECONDS)
        rotCall(-5)
        drivetrain(-20,-20)
        wait(0.5,SECONDS)
        wait(25,SECONDS) #25 or 28 ----------
        ratchPiston.set(False)
        wait(2,SECONDS)
        sidePiston.set(False)
        liftVar = 2
        
        wait(0.1,SECONDS)
        driveDist(3)
        cataMotor.stop()
        autoCata = False 
        #infiniteCata = False
        rotCall(65)
        shootCommand = True
        driveDist(31)
        
    
    while True:
        wait(0.01,SECONDS) #switch to 100cps later

        #drivetrain
        lSpeed = controller.axis3.position() + controller.axis1.position()
        rSpeed = controller.axis3.position() - controller.axis1.position()
        drivetrain(lSpeed,rSpeed)

        #pistons
        if controller.buttonR1.pressing() and pWings == False: 
            if wingsSolenoid.value() == False: 
                wingsSolenoid.set(True)
                wingsSolenoid2.set(True)
            else: 
                wingsSolenoid.set(False)
                wingsSolenoid2.set(False)
        pWings = controller.buttonR1.pressing()
        if controller.buttonR2.pressing() and pFlip == False: 
            if tFlip: 
                sidePiston.set(True)
                tFlip = False
            else: 
                sidePiston.set(False)
                tFlip = True
        pFlip = controller.buttonR2.pressing()
        """if controller.buttonRight.pressing() and pRatch == False: 
            if ratchPiston.value()==0: 
                ratchPiston.set(False)
                tRatch = False
                controller.screen.print("R")
                controller.screen.set_cursor(0,0)
            else: 
                ratchPiston.set(True)
                tRatch = True
                controller.screen.print("F")
                controller.screen.set_cursor(0,0)
        pRatch = controller.buttonRight.pressing()"""

        if controller.buttonX.pressing() and pInt == False:
            if tInt == True: tInt = False
            else: tInt = True
            if tInt: intakePiston.set(True)
            else: intakePiston.set(False)
        pInt = controller.buttonX.pressing()

        if controller.buttonL1.pressing(): intMotor.spin(FORWARD,12,VOLT)
        elif controller.buttonL2.pressing(): intMotor.spin(REVERSE,12,VOLT)
        else: intMotor.stop()

        #if controller.buttonUp.pressing(): PTOswitcher(True)
        #elif controller.buttonDown.pressing(): PTOswitcher(False)
        #PTOmotors(controller.axis2.position()/8)


        """
        if controller.buttonLeft.pressing() and controller.buttonA.pressing():
            lMotor1.temperature()
            lMotor1.temperature()
            lMotor1.temperature()
            rMotor1.temperature()
            lMotor1.temperature()
            lMotor1.temperature()
            brain.screen.print()
        """

#triggers
pre_autonomous()
#user_control()
if True: #set true for competition
    comp = Competition(user_control, autonomous)
else:
    autonomous()
    user_control()