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
x = shoot
l1 = intake in
l2 = intake out
r1 = wings toggle
up = pto/lifter up
down = lifter down/pto
right arrow + y simultaneous = ratchet engage + lift
r2 = toggle side flipper thing

"""


#motors

lMotor1 = Motor(Ports.PORT2, GearSetting.RATIO_6_1, True)
lMotor2 = Motor(Ports.PORT6, GearSetting.RATIO_6_1, True)
ltMotor = Motor(Ports.PORT7, GearSetting.RATIO_6_1, True) #PTO motor
rMotor1 = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False)
rMotor2 = Motor(Ports.PORT3, GearSetting.RATIO_6_1, False)
rtMotor = Motor(Ports.PORT8, GearSetting.RATIO_6_1, False)#PTO motor

intMotor = Motor(Ports.PORT9, GearSetting.RATIO_6_1, True)
cataMotor = Motor(Ports.PORT13, GearSetting.RATIO_36_1, False)
liftSens = Rotation(Ports.PORT12)
cataDist = Distance(Ports.PORT14)
gyro = Inertial(Ports.PORT10)

wireExpander = Triport(Ports.PORT11)
PTOpiston = DigitalOut(wireExpander.h)
wingsSolenoid = DigitalOut(wireExpander.g)
sidePiston = DigitalOut(wireExpander.e)
ratchPiston = DigitalOut(wireExpander.f)
limit = DigitalIn(brain.three_wire_port.h)

#variables
PTOvar = 1 #0 = speed, 1 = cata, 2 = switching
brain.screen.print("Hello V5")
button = False
autoCata = False


def drivetrain(lInput, rInput):
    global PTOvar
    lSpeed = lInput / 8
    rSpeed = rInput / 8
    if lInput == rInput == 0:
        lMotor1.stop()
        lMotor2.stop()
        rMotor1.stop()
        rMotor2.stop()
        if PTOvar ==0:
            ltMotor.stop()
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
        PTOpiston.set(False)
        ltMotor.stop()
        rtMotor.stop()
    else:
        PTOvar = 1 #lifter
        PTOpiston.set(True)
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
    
def cataMotors(s):
    #print("spinning cata at " + str(s))
    if abs(s) <= 1: #to stop the motors & make sure it doesn't go backwards
        cataMotor.stop()
    else:
        if PTOvar == 1:
            cataMotor.spin(FORWARD,s,VOLT)

def catapult():
    global PTOvar
    global autoCata
    while True:
        wait(0.01,SECONDS)
        if controller.buttonX.pressing() or (cataDist.object_distance(MM) < 20 and autoCata == True):
            if not controller.buttonX.pressing(): wait(0.1,SECONDS)
            cataMotors(12)
            wait(0.1,SECONDS)
            cataMotors(0)
            wait(0.05,SECONDS)
            cataMotors(12)
            if controller.buttonX.pressing() == False:
                while limit.value() == 1:
                    wait(0.01,SECONDS)
                cataMotors(0)

def lifter():
    #have this as a thread: once called, control loop up/down until finished, then kill the thread
    while True:
        wait(0.1,SECONDS)
        if controller.axis2.position() > 90:
            PTOswitcher(False)
            ratchPiston.set(False)
            ltMotor.set_stopping(BRAKE)
            rtMotor.set_stopping(BRAKE)
            PTOmotors(12) #loop to make it go up until limit
            i = 0
            while (liftSens.position() % 360) < 100 and i < 30:
                wait(0.1,SECONDS)
                i+=1
            wait(0.05,SECONDS)
            PTOmotors(0)
        elif controller.axis2.position() < -90:
            PTOmotors(-12) #same as above but in reverse  
            ltMotor.set_stopping(COAST)
            rtMotor.set_stopping(COAST)
            i = 0          
            while (liftSens.position() % 360) > 5 and i < 30:
                wait(0.1,SECONDS)
                i+=1
            wait(0.05,SECONDS)
            PTOmotors(0)
            PTOswitcher(True)


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
    print("New PID instruction: " + str(target))
    lMotor1.reset_position()
    lMotor2.reset_position()
    rMotor1.reset_position()
    rMotor2.reset_position()
    proportional = 3
    integral = 0
    prevProp = 0
    gyro.reset_rotation()
    Kp = 0.8
    Ki = 0
    Kd = 0
    error = target + 0.1
    errorPrev = abs(target)
    timer = 200
    while abs(errorPrev) > 3 and (error != errorPrev) and timer > 0:
        timer -= 1
        wait(0.01,SECONDS)
        measure = (lMotor1.position(DEGREES)+lMotor2.position(DEGREES)+rMotor1.position(DEGREES)+rMotor2.position(DEGREES))*0.00425424005
        #to inches: 3.25 (diameter) * pi / 360 / 4

        proportional = target - measure
        integral += proportional
        derivative = proportional - prevProp
        prevProp = proportional

        error = proportional * Kp + integral * Ki + derivative * Kd
        errorRot = gyro.rotation() * 0.1
        lOut = error - errorRot
        rOut = error + errorRot
        if 0 < lOut < 2: lOut = 2 #min values
        elif 0 > lOut > -2: lOut = -2
        if 0 < rOut < 2: rOut = 2
        elif 0 > rOut > -2: rOut = -2
        drivetrain(lOut*8.3,rOut*8.3)
        #print(errorRot)
        print(error)
        errorPrev = (errorPrev * 9 + abs(proportional)) / 10
    drivetrain(0,0)
    wait(0.1,SECONDS)

def rotDeg(target):
    print("New rotation instruction: " + str(target))
    gyro.reset_rotation()
    error = 100
    prevErr = abs(target)
    timer = 150
    while abs(prevErr) > 4 and timer > 0:
        timer -= 1
        wait(0.01,SECONDS)
        rot = gyro.rotation()
        error = target - rot
        output = error * 0.25
        if 0 < output < 3: output = 3 #min values
        elif 0 > output > 3: output = -3
        drivetrain(output*8,output*-8)
        print(error)
        print(timer)
        prevErr = (prevErr * 9 + abs(error)) / 10
    drivetrain(0,0)
    wait(0.1,SECONDS)


#control functions
def pre_autonomous():
    gyro.calibrate
    wingsSolenoid.set(False) #start with wings in
    PTOpiston.set(True) #start with lift mode
    sidePiston.set(False) #start with side up
    ratchPiston.set(False) #start with ratchet up
    #pre auton
    brain.screen.clear_screen()
    brain.screen.print("pre auton code")
    #auton side value
    global n
    n = 3 #change value to change starting side, 1=L, 2=R, 3=driver
    #t1 = Thread(PTOswitcher)
    t2 = Thread(catapult)
    t3 = Thread(lifter)
    rMotor1.stop()
    rMotor2.stop()
    lMotor1.stop()
    lMotor2.stop()

    cataMotor.set_stopping(HOLD)
    intMotor.set_stopping(HOLD)
    wait(2,SECONDS)
    """
    ltMotor.spin(REVERSE,6,VOLT)
    rtMotor.spin(REVERSE,6,VOLT)
    wait(0.6,SECONDS)
    rtMotor.stop()
    ltMotor.stop()
    """
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
    st = BRAKE
    rMotor1.set_stopping(st)
    rMotor2.set_stopping(st)
    rtMotor.set_stopping(st)
    lMotor1.set_stopping(st)
    rMotor2.set_stopping(st)
    ltMotor.set_stopping(st)
    #auton
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    #right side: push in alliance ball, grab left ball, put in front of goal, 
    #get center ball that's touching bar, turn, push that one along with the middle one and the other one in with wings
    #left side: push alliance ball in, get ball out of corner, let go of ball, go touch pole
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
        intMotor.spin(REVERSE,11,VOLT)
        wait(0.3,SECONDS)
        drivetrain(-60,-60)
        wait(0.2,SECONDS)
        drivetrain(80,80)
        wait(0.2,SECONDS)
        drivetrain(-100,-100)
        wait(0.1,SECONDS)
        driveDist(-6)
        intMotor.stop()
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
def user_control():
    st = COAST
    rMotor1.set_stopping(st)
    rMotor2.set_stopping(st)
    rtMotor.set_stopping(st)
    lMotor1.set_stopping(st)
    rMotor2.set_stopping(st)
    ltMotor.set_stopping(st)
    #user control
    brain.screen.clear_screen()
    controller.screen.print("user")
    global button
    global autoCata

    #ltMotor.set_stopping(HOLD)
    #rtMotor.set_stopping(HOLD)

    tWings = False
    pWings = False
    tFlip = False
    pFlip = False
    tRatch = False
    pRatch = False
    pCatAut = False
    while True:
        wait(0.1,SECONDS) #switch to 100cps later

        #drivetrain
        lSpeed = controller.axis3.position() + controller.axis1.position()
        rSpeed = controller.axis3.position() - controller.axis1.position()
        drivetrain(lSpeed,rSpeed)

        #pistons
        if controller.buttonR1.pressing() and pWings == False: 
            if tWings: 
                wingsSolenoid.set(True)
                tWings = False
            else: 
                wingsSolenoid.set(False)
                tWings = True
        if controller.buttonR2.pressing() and pFlip == False: 
            if tFlip: 
                sidePiston.set(True)
                tFlip = False
            else: 
                sidePiston.set(False)
                tFlip = True
        if controller.buttonRight.pressing() and pRatch == False: 
            if tRatch: 
                ratchPiston.set(True)
                tRatch = False
            else: 
                ratchPiston.set(False)
                tRatch = True
        if controller.buttonY.pressing() and pCatAut == False: 
            if autoCata: autoCata = False
            else: autoCata = True
        if controller.buttonL1.pressing(): intMotor.spin(FORWARD,12,VOLT)
        elif controller.buttonL2.pressing(): intMotor.spin(REVERSE,12,VOLT)
        else: intMotor.stop()

        if controller.buttonUp.pressing(): PTOswitcher(True)
        elif controller.buttonDown.pressing(): PTOswitcher(False)
        #PTOmotors(controller.axis2.position()/8)

        pWings = controller.buttonR1.pressing()
        pFlip = controller.buttonR2.pressing()
        pRatch = controller.buttonRight.pressing()

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