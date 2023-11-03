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
from math import *

# Brain should be defined by default
brain=Brain()

#controller
controller = Controller()

#motors

lMotor1 = Motor(Ports.PORT8, GearSetting.RATIO_6_1, True)
lMotor2 = Motor(Ports.PORT11, GearSetting.RATIO_6_1, True)
ltMotor = Motor(Ports.PORT6, GearSetting.RATIO_6_1, True) #PTO motor
rMotor1 = Motor(Ports.PORT3, GearSetting.RATIO_6_1, False)
rMotor2 = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
rtMotor = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False) #PTO motor
cataMotor = Motor(Ports.PORT10,GearSetting.RATIO_36_1, True) #motor for only cata
intakeMotor = Motor(Ports.PORT12,GearSetting.RATIO_36_1, False) #intake

PTOpiston = DigitalOut(brain.three_wire_port.a)
flipperPiston = DigitalOut(brain.three_wire_port.b)
wingsSolenoid = DigitalOut(brain.three_wire_port.c)
intakeSolenoid =DigitalOut(brain.three_wire_port.d)

#variables
PTOvar = 1 #0 = speed, 1 = cata, 2 = switching
buttonPrev = True
brain.screen.print("Hello V5")
pistBool = False
button = False


def drivetrain(lInput, rInput):
    global PTOvar  
    if lInput == rInput == 0:
        lMotor1.stop()
        rMotor1.stop()
        lMotor2.stop()
        rMotor2.stop()
        if PTOvar ==0:
            ltMotor.stop()
            rtMotor.stop()
    else:


        lSpeed = lInput / 8
        rSpeed = rInput / 8

        lMotor1.spin(FORWARD,lSpeed,VOLT)
        lMotor2.spin(FORWARD,lSpeed,VOLT)
        rMotor1.spin(FORWARD,rSpeed,VOLT)
        rMotor2.spin(FORWARD,rSpeed,VOLT)

        if PTOvar == 0:
            ltMotor.spin(FORWARD,lSpeed,VOLT)    
            rtMotor.spin(FORWARD,rSpeed,VOLT)


def PTOswitcher():
    global PTOvar
    global buttonPrev
    global pistBool
    button = controller.buttonRight.pressing()

    if button == True and buttonPrev == False:
        if pistBool == False: pistBool = True
        else: pistBool = False
    
    if button == True: #while the button is held
        PTOvar = 2 #stop the motors
        ltMotor.stop()
        rtMotor.stop()
    else:
        if pistBool == True: #switching to catapult
            PTOvar = 0
            PTOpiston.set(False)
        else: #switching to drive
            PTOvar = 1
            PTOpiston.set(True)
    
    buttonPrev = button
    
def cataMotors(s):
    print("spinning cata at " + str(s))
    if abs(s) <= 1: #to stop the motors & make sure it doesn't go backwards
        ltMotor.stop()
        rtMotor.stop()
        cataMotor.stop()
    else:
        cataMotor.spin(REVERSE,s,VOLT)  
        if PTOvar == 1:
            ltMotor.spin(FORWARD,s,VOLT)    
            rtMotor.spin(FORWARD,s,VOLT)

def catapult():
    global PTOvar
    running = True
    global cataTrig
    cataTrig = False #temp delete later
    cataMotor.set_position(0,DEGREES)
    n = 0
    while True:
        wait(0.01,SECONDS)
        if controller.buttonR1.pressing() and PTOvar == 1:
            cataMotors(12)
            wait(0.2,SECONDS)
            cataMotors(0)
            wait(0.2,SECONDS)
            s = 600
            ltMotor.spin(FORWARD,s,RPM)    
            rtMotor.spin(FORWARD,s,RPM)
            cataMotor.spin(REVERSE,(s/3),RPM)  

            pos = (cataMotor.position(DEGREES) % 360)
            
            while 340 > pos > 0:
                pos = (cataMotor.position(DEGREES) % 360)
                print(pos)
                wait(0.01,SECONDS)
                if controller.buttonR2.pressing(): break

            cataMotors(0)
        elif controller.buttonR2.pressing():
            cataMotors(controller.axis2.position()/8)
            cataMotor.set_position(0,DEGREES)
            

        """


        if controller.buttonR1.pressing(): 
            running = True
            cataTrig = True
        wait(0.01,SECONDS)
        while running == True:
            wait(0.01,SECONDS)
            pos = (cataMotor.position(DEGREES) % 360)
            if cataTrig == True:
                cataMotors(12)
                wait(1,SECONDS)
                cataTrig = False
                print("aaa")
            else:
                n = pos #- 10
                if n > 12: n = 12
                cataMotors(n)
                print(n)
            if controller.buttonLeft.pressing(): running = False

        """

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
        print(totalDiff)
        wait(0.01,SECONDS)
        #converting from deg to inch
        rPos = (rMotor1.position(DEGREES) * (3 / 5)) * 0.02836160034 #3-5 ratio gearing on the wheels
        lPos = (lMotor1.position(DEGREES) * (3 / 5)) * 0.02836160034 #3-5 ratio gearing on the wheels
        #wheels have 3.25 inch diameter, circ = 10.2101761242, 0.02836160034 inches per degree

        DR = rInput - rPos
        DL = lInput - lPos #diffs
        totalDiff = abs(DR) + abs(DL)
        print("d" + str(DR))
        print(DL)
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

    

#control functions
def pre_autonomous():
    wingsSolenoid.set(False)
    PTOpiston.set(True) #start with cata mode
    #pre auton
    #note to self add an auton side select thing
    brain.screen.clear_screen()
    brain.screen.print("pre auton code")
    #auton side value
    global n
    n = 3 #change value to change starting side, 1=L, 2=R, 3=driver

    #t1 = Thread(PTOswitcher)
    t2 = Thread(catapult)
    
    rMotor1.set_stopping(HOLD)
    rMotor2.set_stopping(HOLD)
    rtMotor.set_stopping(HOLD)
    lMotor1.set_stopping(HOLD)
    lMotor2.set_stopping(HOLD)
    ltMotor.set_stopping(HOLD)

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
    #auton
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    global n # 1 = Left, 2 = Right, 3 = Double
    print(n)
    
    n = 2

    #if n == 2:
        #driveInches(-60,-60,80,80)
    if n == 10:
        print("left side")
        driveInches(-22,-22,50,50)
        driveInches(4.4,-4.4,50,50)
        driveInches(-25,-25,50,50)
        driveInches(4.4,-4.4,50,50)
        driveInches(-10,-10,40,40)
        driveInches(1,4,30,50)
        driveInches(-1,-1,100,100)
        wait(0.5,SECONDS)
        cataMotors(12)
        wait(0.4,SECONDS)
        cataMotors(0)
    elif n == 2:
        print("just pickup")
        driveInches(-13,-13,50,50)
        driveInches(4.6,-4.6,50,50)
        intakeMotor.spin(FORWARD,12,VOLT) 
#        driveInches(15,15,30,30)
        lMotor1.spin(FORWARD,5,VOLT)
        lMotor2.spin(FORWARD,5,VOLT)
        rMotor1.spin(FORWARD,5,VOLT)
        rMotor2.spin(FORWARD,5,VOLT)
        wait(4,SECONDS)
        lMotor1.stop()
        rMotor1.stop()
        lMotor2.stop()
        rMotor2.stop()
        driveInches(-5,-5,50,50)
        driveInches(6,-6,60,60)
        driveInches(-48,-48,50,50)

def user_control():
    #user control
    brain.screen.clear_screen()
    controller.screen.print("user")

    global button

    ltMotor.set_stopping(HOLD)
    rtMotor.set_stopping(HOLD)
    cataMotor.set_stopping(HOLD)

    #init piston values
    buttonYPrev = True
    wingsBool = False
    buttonXPrev = True
    flipperBool = False
    buttonUpPrev = True
    intakeBool = False
    macroPrev = False
    macroBool = False
    tempVar =False
    while True:

        wait(0.1,SECONDS) #switch to 100cps later

        #drivetrain
        lSpeed = controller.axis3.position() + controller.axis1.position()
        rSpeed = controller.axis3.position() - controller.axis1.position()
        drivetrain(lSpeed,rSpeed)

        #pistons
        PTOswitcher()
        if controller.buttonY.pressing() and buttonYPrev == False:
            if wingsBool == False: wingsBool = True
            else: wingsBool = False #wings
            wingsSolenoid.set(wingsBool)
        buttonYPrev = controller.buttonY.pressing()

        if controller.buttonX.pressing() and buttonXPrev == False:
            if flipperBool == False: flipperBool = True
            else: flipperBool = False #flipper
            flipperPiston.set(flipperBool)
        buttonXPrev = controller.buttonX.pressing()

        if controller.buttonUp.pressing() and buttonUpPrev == False:
            if intakeBool == False: intakeBool = True
            else: intakeBool = False #intake
            intakeSolenoid.set(intakeBool)
        buttonUpPrev = controller.buttonUp.pressing()

        if controller.buttonDown.pressing() and controller.buttonB.pressing():
            tempVar = True
        while tempVar == True:
            cataMotors(10)
            if controller.buttonLeft.pressing():
                tempVar = False

        #intake
        if controller.buttonL1.pressing(): intakeMotor.spin(FORWARD,12,VOLT)
        elif controller.buttonL2.pressing(): intakeMotor.spin(REVERSE,12,VOLT)
        else: intakeMotor.stop()

        #drivetrain(lSpeed, rSpeed)

        brain.screen.clear_screen()
        brain.screen.set_cursor(1,1)
        xSpeed = controller.axis2.position() / 8
        brain.screen.print(cataMotor.position(DEGREES) % 360)

        #cataMotors(xSpeed)



#triggers

pre_autonomous()
if True: #set true for competition
    comp = Competition(user_control, autonomous)
else:
    autonomous()
    user_control()