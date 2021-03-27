#!python2

import time
import sys
import serial
import pyautogui
import msvcrt
import winsound
import visa

from colorama import init
init()
from colorama import Fore, Back, Style



'''
##################################################
##### AUTOMATED TERAPULSE INTERFACE CONTOL #######
#### T E R A P U L S E   A U T O M A T I O N #####
##################################################

author:     Mario U. Gaimann

version:    3.2
            (fully integrated version)
            (stable build)
date:       21/09/2017

Programme to control TeraPulse by automated input
and reading of screen, mouse and keyboard, motor
as well as temperature controller.
##################################################
'''
version= "3.2"




'''##############'''
'''INITIAL VALUES'''
'''##############'''


#safety parameters, do not alter
pyautogui.PAUSE = 1          #duration after each call of pyautogui in [s]
pyautogui.FAILSAFE = False   #failsafe option: move mouse in upper left hand corner to break


#TeraPulse interface
pos_startbutton = (71,121)                       #position of the start button
pos_stopbutton = (149,121)                       #position of the stop button
pos_savebutton = (42, 62)                        #position of the save button
pos_namefield = (1660,218)                       #position of the name field
pos_acquiresample = (1666,683)                   #position of the acquire sample button
pos_clearreference= (1666,652)                   #position of the clear reference button
pos_acquirereference= (1666,621)                 #position of the acquire reference button
pos_scrollsectionright= (1828,338)               #position of the right hand side scrollable area
pos_loadingbarend= (1204,123)                    #position of a green pixel at the end of the loading bar
col_loadingbarend= (40,204,58)                   #colour of the green pixel at the end of the loading bar


#motor initialisation parameters
rn=" \r\n"
VA_SP = 'VA SP = 50000'
rc = 'rc = 100'
vi = 'vi = 500'
vm = 'vm = 40000'
a = '30000'
d = 'd = 20000'
p = 'p = 0'
motor_init= [VA_SP, rc, vi, vm, a, d, p]


#coefficients for automated centering
TM_intercept= 21065
TM_gradient= -187.25



'''###############'''
'''SELECT EDITION'''
'''###############'''



print(Fore.GREEN + Style.BRIGHT+"\n\n#####################################\n####### TERA PULSE AUTOMATION #######\n#####################################")
print(Fore.GREEN+ Style.NORMAL+"                        Version "+ version+ "              ")
print(Style.RESET_ALL)
time.sleep(2)

print("\n\nPress CTRL + C to terminate the programme at any time.\n")
time.sleep(2)


#SELECT GLOBAL FLAGS
  
time.sleep(0.5)  
while 1:  
  flag_referencerun_select=str(raw_input("\n\t* Please select the mode:\n\t  -Classic mode, multiple temperatures and references:\tType \"1\"\n\t  -Time Series mode, contin. measurements at fixed T:\tType \"2\"\n\t\t\t\t\t"))
  if flag_referencerun_select=="1":
    flag_referencerun= True
    break
  elif flag_referencerun_select=="2":
    flag_referencerun= False
    break
  
time.sleep(0.5)  
while 1:  
  flag_multcentering_select=str(raw_input("\n\t* Please select the centering mode:\n\t  -Multiple center positions, automatically adapted:\tType \"a\"\n\t  -One center position for all temperatures:\t\tType \"b\"\n\t\t\t\t\t"))
  if flag_multcentering_select=="a":
    flag_multcentering= True
    break
  elif flag_multcentering_select=="b":
    flag_multcentering= False
    break


# flags may be disabled for future versions of the programme
flag_tempcontrol= True
flag_motor= True
  


#print edition banners
time.sleep(1)
if flag_motor==True and flag_referencerun==False:
  print(Fore.CYAN+ Style.NORMAL+"\n\n\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\nT I M E    S E R I E S    E D I T I O N\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
  print(Style.RESET_ALL)
elif flag_motor==True and flag_referencerun==True:
  print(Fore.YELLOW+ Style.NORMAL+"\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n~  C L A S S I C    E D I T I O N  ~\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  print(Style.RESET_ALL)
time.sleep(2)





'''#############'''
'''CHECK SYSTEM'''
'''#############'''



#check version
pythonversion= sys.version
pythonversion= pythonversion.split(" ",1)[0]
print("\nPython Version:\t"+pythonversion+"\t\tcorrect")
time.sleep(0.5)


#check screen parameter
screenwidth, screenheight = pyautogui.size()
if (screenwidth != 1920) or (screenheight != 1080):
  print("Resolution:\t"+str(screenwidth)+ " x "+ str(screenheight)+ "\twrong\n")
  print("This programme requires a resolution of 1920 x 1080 to run properly.\n\n")   #terminate programme if resolution is wrong
  time.sleep(5)                                                                     #clicking the buttons will not work for wrong resolution
  assert (screenwidth == 1920) and (screenheight == 1080)
print("Resolution:\t"+str(screenwidth)+ " x "+ str(screenheight)+ "\tcorrect")
time.sleep(0.5)


# check port
if flag_motor==True:
  port = "COM3"
  try:
    ser = serial.Serial(port, 9600)
    assert ser.is_open == True
    print("Serial Port:\taccess\t\tcorrect")      
  except:
    print("Serial Port:\tno access\twrong")
    print("\nPort "+port+ " could not be accessed. Make sure to close the IMS Terminal.\n\n")   #terminate programme if port cannot be accessed
    time.sleep(5)
    raise  
  time.sleep(0.5)
  

# temperature initialisation
if flag_tempcontrol== True:
  try:
    rm = visa.ResourceManager()
    res= rm.list_resources()
    LSconnect1= 'GPIB0::12::INSTR'
    
    for LSconnect1 in res:
      raiseflag= False
    if raiseflag== True:
      raise
    
    LS331= rm.open_resource('GPIB0::12::INSTR')
    LS331ident= LS331.query("*IDN?")
    LS331connect2= LS331ident.find('MODEL331S')    
    assert LS331connect2 != -1 
    
    print("GPIB:\t\taccess\t\tcorrect")
    
    #insert PID parameter
    #LS331.query('PID 1,60,3,1')   #Loop=1, P=60, I=3, D=0
    
    
  except:
    print("GPIB:\t\tno access\twrong")
    print("\nLake Shore Model 331 temperature controller could not be accessed.\n Make sure to connect everything correctly, set \"12\" as GPIB address and\n do not choose Model 330 emulation mode.\n\n")   #terminate programme if port cannot be accessed
    time.sleep(5)
    raise  
  time.sleep(0.5)




'''#########'''
'''FUNCTIONS'''
'''#########'''


def waitForUserInput(string):       #function to wait for user enter the correct string to proceed
  while 1:
    print("\nType \"" + string+"\"  to proceed:")
    check = str(raw_input("\t\t\t\t\t"))        #get input from user
    #if check == "exit":
    #  break
    if check == string:             #if the input string matches the required string, the loop breaks
      break
    else:
      time.sleep(1)                 #if the string does not match, the loop continues until the right
      continue                      #string is entered



def initialiseMotor(motor_init):
  i= 0
  r= 1
  for i in range(len(motor_init)):
    if r%2==0:
      ser.write(motor_init[i] +rn)   #write the command "ma 0" for example  
      time.sleep(0.75)                  #give the motor time to respond        
                                   #this part is to process the output properly
    out = ser.readline()           #read one line of output
    out = list(out)                #convert output to list of characters
    
    removeitems = ("\n", "\r", " ", "?")
    out = [e for e in out if e not in removeitems]    #remove items from out list
    
    out = ''.join(out)             #combine the items of the list to a string
    print("[motor]\t\t"+str(out))
    r+=1
  print('[motor]\t\tMotor initialised')




def motorMovement(pos):    
  ser.reset_output_buffer()
  ser.reset_input_buffer()
  time.sleep(1)
  ser.write("ma "+ str(pos) +rn)   #write the command "ma 0" for example
                                   #move motor to appropriate position
  r=1
  
  while 1:
    time.sleep(0.75)                  #give the motor time to respond        
                                   #this part is to process the output properly
    out = ser.readline()           #read one line of output
    out = list(out)                #convert output to list of characters
    
    removeitems = ("\n", "\r", " ", "?")
    out = [e for e in out if e not in removeitems]    #remove items from out list
    
    out = ''.join(out)             #combine the items of the list to a string
    #print("[motor]\t\t"+str(out))
    #print("aim: "+ str(pos))     
    if str(pos) == str(out):       #break if motor reaches desired position
    
      print("[motor]\t\tReached position "+str(pos))
      break
    if r%2==0:                     #prevents that pr p is called too often
      ser.write("pr p"+rn)         #give the command to give out position
    r+=1                           



def interruptMeasurement(pressedKey_bool):                              #if a key is being hit in the process
  if pressedKey_bool==True:
    #winsound.PlaySound('SystemQuestion',winsound.SND_ALIAS) #play some sound
    msvcrt.putch(msvcrt.getch())                            #print the character to get it out of the buffer
    
    while 1:
      check= str(raw_input("\nType \"REPEAT\" to terminate the current iteration.\nTzpe \"CONTINUE\" to proceed with the current iteration: ")) 
      if check == "REPEAT":                                   #ask for repeating the current iteration or continueing
        pyautogui.doubleClick(pos_stopbutton, button="left")
        print("[system]\tMeasurement \""+str(setname)+"\" terminated\n")
        return True
      
      elif check == "CONTINUE":
        print(Fore.YELLOW + Style.NORMAL+"\nPlease return to the TeraView window immediately!")
        print(Style.RESET_ALL)
        time.sleep(3)
        print("\n[system]\tContinuing measurement \""+str(setname)+"\".\n\t\tPress any key to interrupt the current measurement")
        LS331.query('ALARM B,0')
        break
    
    
    
def adjustTemperature(setpoint, temp_tolerance, interruptMeasurement):        #requires setpoint parameter
  LS331.query('SETP 1,' + str(setpoint))        #loop 1, setpoint
  time.sleep(0.5)
  LS331.query('RANGE 3')                #sets heater to High Range
  time.sleep(0.5)
  print('[tcontrol]\tSetpoint '+ LS331.query('SETP? 1'))    #setpoint query
  time.sleep(0.5)
  PID_para= LS331.query('PID? 1')       #gets the PID values of loop 1, calculate duration of one oscillation period
  P_para= PID_para.split(',')[0]        #first entry: P value
  time.sleep(float(P_para) )                #P value is usually half of the oscillation time, take 1.5 instead of 2 as no whole oscillation for PID
  
  while 1:                              #if temperature is constant within the tolerance over 15 seconds, proceed
    print('[tcontrol]\tWaiting for stable temperature...')
    
    T1= float(LS331.query('KRDG? B'))              #queries input B
    time.sleep(5)
    T2= float(LS331.query('KRDG? B'))              #queries input B
    time.sleep(5)
    T3= float(LS331.query('KRDG? B'))              #queries input B
    time.sleep(5)
    T4= float(LS331.query('KRDG? B'))              #queries input B
    
    temp_check= [t for t in [T1,T2,T3,T4] if 0.7*(t - int(setpoint)) > int(temp_tolerance)] #if difference is too large, check array has items
    
    #check for keyboard input
    pressedKey_bool= msvcrt.kbhit()  
    interrupt_bool= interruptMeasurement(pressedKey_bool)       #and deal with interruption
    
    if len(temp_check) == 0:                #no elements in array
      print('[tcontrol]\tStable temperature at setpoint reached')
      time.sleep(1)
      break
    elif interrupt_bool==True:                 #if user wants to interrupt the current measurement
      return True                             #control flag, for skipping next steps



# parameters from centre hole positions plot
def temp_pos_function(temp):
  #as the zero position should be given by the user as measured at 
  #room temp, we have to add the pos at 298K to compensate for this
  RToffset= TM_intercept+ TM_gradient * 298
  out= round((TM_intercept + float(temp)* TM_gradient)- RToffset)
  return(int(out))
  
 


        
# NEW VERSION: WAIT UNTIL THE LAST PIXEL OF THE LOADING BAR TURNS GREEN
# NEW: can return a repeat flag to completely terminate a measurement
def waitForCompletedProcess(pos, col, setname, setpoint, temp_tolerance, interruptMeasurement):
                                                              #replaces the variable processing_time and substitutes waitOrRepeat
                                                              #with the optimized function waitOrRepeatImgRec
  time.sleep(10)                                              #give the software some time to remove previous full loading bars
  
  while 1:
    time.sleep(1)
    screen= pyautogui.screenshot()                            #takes a screenshot
    pixelcolour= screen.getpixel(pos)                         #gets RGB code of pixel at the end of the loading bar
    
    current_temp= float(LS331.query('KRDG? B'))
    
    
    if abs(current_temp - int(setpoint)) > 0.8* int(temp_tolerance):     #warn for high temperatures
      time.sleep(0.5)
      LS331.query('ALARM B,1') 
      time.sleep(0.5)
      LS331.query('BEEP 1')                                         #emit beeping sound to warn user
      print('[tcontrol]\tWARNING: Current Temperature close to exceeding tolerance!')
      time.sleep(1)
      LS331.query('BEEP 0')
      time.sleep(3)
      
      
    if abs(current_temp - int(setpoint)) > int(temp_tolerance):    #cancel measurement for high temperatures
      pyautogui.doubleClick(pos_stopbutton, button="left")
      time.sleep(1)
      pyautogui.click(pos_namefield, button="left")                     #make user aware of error in interface
      pyautogui.hotkey("ctrl", "a")           #select the whole integer
      pyautogui.press("delete")               #delete selected integer
      pyautogui.typewrite('ERROR # PLEASE OPEN CONSOLE')
      
      print("[tcontrol]\tTolerance exceeded!")
      print("[tcontrol]\tMeasurement \""+str(setname)+"\" terminated")
      LS331.query('BEEP 1')
      time.sleep(0.5)
      LS331.query('BEEP 0')
      time.sleep(0.5)
      LS331.query('BEEP 1')
      time.sleep(0.5)
      LS331.query('BEEP 0')
      LS331.query('BEEP 1')
      time.sleep(2)
      LS331.query('BEEP 0')
      return True
    
    
    pressedKey_bool= msvcrt.kbhit()                                #check for keyboard input
    interrupt_bool= interruptMeasurement(pressedKey_bool)       #and deal with interruption
    
    #waits until the measurement is done or interrupted
    if pixelcolour== col:                                     #compare RGB codes of pixel
      del screen                                              #deletes screen variable to save memory
      #winsound.PlaySound('SystemHand',winsound.SND_ALIAS )
      return False                                           #breaks loop if measurement is done
    
    elif interrupt_bool==True:                 #if user wants to interrupt the current measurement
      return True                                #raise the flag
  
    


def stopDialogue(waitForUserInput, setname):
  print('\n\t* To interrupt the programme during a measurement,\n\t  open the Command Prompt and press any key.\n\t  Please allow some time for the programme to react.')
  time.sleep(4)
  print('\n\t* To end this programme,\n\t  open the Command Prompt and press CTRL + C.')
  time.sleep(4)
  
  print(Fore.CYAN + Style.BRIGHT + '\n\n\t* Be aware that mouse and keyboard will conduct movements\n\t  automatically!')
  time.sleep(3)
  print('\n\t  Do not use this PC while this code is running!\n\t  Failing to do so might result in unforeseen consequences.')
  time.sleep(4)
  print('\n\t  Do not leave the whole measurement set-up unattended at any time!')
  print(Style.RESET_ALL)
  time.sleep(6)
  

  print('\n\t* The next measurement will be '+ setname+'.')
  time.sleep(2)
  
  print(Fore.YELLOW + Style.BRIGHT + "\n\nPlease open the TeraPulse window IMMEDIATELY after the next step!")
  print(Style.RESET_ALL) 
  time.sleep(2)
  waitForUserInput("START")

  print(Fore.YELLOW + Style.BRIGHT+ "\nOPEN TERAPULSE WINDOW NOW!")
  print(Style.RESET_ALL)
  time.sleep(5)


        

'''#####################'''
'''INITIALISING DIALOGUE'''
'''#####################'''

try:
  
  #warning dialogues
  if flag_motor==True:                                        #warning for possible crash of motor
    print(Fore.YELLOW + Style.BRIGHT+"\n\n\n\t!!! CAUTION: CONFIRM THAT THE MOTOR HAS BEEN INITIALIZED AND SET\n\n\t!!! MANUALLY TO THE CENTRE OF THE REFERENCE USING THE IMS TERMINAL.\n\n\t!!! FAILING TO DO SO MIGHT END IN MOTOR FAILURE!\n")
    time.sleep(5)
    waitForUserInput("CONFIRM")
    print(Style.RESET_ALL) #resets yellow colour
  
  #if flag_motor==True and flag_referencerun==False:           #warning for time series measurement
  #  print(Fore.YELLOW + Style.NORMAL+"\n\tDo not reach measurement temperature yet!")
   # print(Style.RESET_ALL)
   # time.sleep(2)
  
  
  print("\n\nINITIAL VALUES:")
  time.sleep(1)
  
  print("\n\t* Make sure you entered the following scan settings:\n\t\t-Measurement Mode:\tCoreTransmission\n\t\t-Scanner Type:\t\tHiResScannerSeries\n\t  and check your Acquisition Parameters.")
  time.sleep(5)
  print('\n\t* Make sure you created a new TeraPulse project file\n\t  and TeraPulse is running in the background with the\n\t  Acquisition Setup window open.')
  time.sleep(3)
  
  #enter central position of the second hole
  if flag_motor==True:
    while 1:
      try:
        print('\n\t* The reference hole centre position will be set to zero.')
        time.sleep(3)
        pos_initial= 0
        pos_final_ini = int(raw_input("\n\t* Enter the motor position for sample centre (room temp.)\n\t  (integer, default: 1220000):\n\t\t\t\t\t"))
        assert pos_initial < pos_final_ini
        #assert type(pos_final).find('int') != -1
        break
      except AssertionError:
        print("\nCheck your input. Make sure your final motor position is larger than zero.")
        time.sleep(2)
  
  #NAME = PREFIX + TEMPERATURE ( + TIME STAMP)
  name_prefix= str(raw_input("\n\t* Enter a name (prefix) for the measurements (e.g. BSA3),\n\t  the temperature for each measurement will be automatically added.\n\t  Press ENTER if you do not wish any prefix:\n\t\t\t\t\t"))
  if name_prefix!='':               #adds underscore if prefix is requested
    name_prefix= name_prefix + '_'
  
  if flag_tempcontrol==True:
    while 1:
      try:
        temp_init = str(raw_input("\n\t* Enter EITHER\n\t\t-All temperatures to measure at, delimited by space, in an\n\t\t ascending order (e.g. 200 220 300)\n\t\tOR\n\t\t-For ntervals, give temperatures in the form\n\t\t Start>Increment>End (e.g. 100>20>240):\n\t\t\t\t\t"))
        if temp_init.find('>') != -1:   # for incremental temperatures
          temp_initial, temp_increment, temp_final= temp_init.split('>')
          temparray=[]
          for i in range(int(temp_initial), int(temp_final)+ int(temp_increment), int(temp_increment)):
            temparray.append(i)
        else:                           # for single temperature
          temparray= temp_init.split(' ')
        #assert temp_init > 80
        #assert type(temp_ini).find('int') != -1
        
        temp_tolerance= str(raw_input("\n\t* You may enter a tolerance for the temperature readout in Kelvin\n\t  (integer, default: 5):\n\t\t\t\t\t"))
        if temp_tolerance== '':
          temp_tolerance= 5
        break
      except AssertionError:
        print('Error')
        
        
  
  print("\n\t* Please check your initial values before initializing.\n")
  time.sleep(3)
  waitForUserInput("CONTINUE")
  
  
  #make sure reference is only taken once if flag is not raised
  if flag_referencerun==False:
    singlerefrun= 1
  else:
    singlerefrun= 99999
  
  
  
  '''#########'''
  '''MAIN LOOP'''
  '''#########'''
  
  iteration= 0    #counts interations for temp_array
  
  #construct name for current measurement for the first run
  setname= name_prefix + str(temparray[iteration]) + "K"
  
  #give initial warnings, how to terminate measurement etc.
  stopDialogue(waitForUserInput, setname)
  LS331.query('ALARM B,0')            #turns alarm condition off
  
  # initialise motor
  #if flag_motor==True:
    #initialiseMotor(motor_init)
  
  
  print("\n\n\nMAIN LOOP:\n\n")
  time.sleep(1)
  
  #MAIN WHILE LOOP
  while iteration < len(temparray):
    
    #start TeraPulse live data
    pyautogui.click(pos_startbutton, button="left")
    
    #REFERENCE WHILE LOOP
    #breaks automatically if repeat flag is not raised
    while 1:
      if singlerefrun > 0:      #execute only, if multiple references are required, otherwise once
                                #(singlerefrun) is then set to 1 
        #disable alarm
        LS331.query('ALARM B,0')
        
        
        #set temperature to first temperature in temparray
        flag_repeat= adjustTemperature(temparray[iteration], temp_tolerance, interruptMeasurement)
        if flag_repeat==True:
          break
        
        #calculate new centre position in case of multcentering
        if flag_multcentering==True:
          pos_initial= temp_pos_function(int(temparray[iteration]))
          print('[autocent]\tReference centre for T= '+str(temparray[iteration])+'K: p='+str(pos_initial))
        else:
          pos_initial= 0
      
      
        #move motor (back) to reference
        if flag_motor==True:
          print("[motor]\t\tMoving to reference position...")
          motorMovement(pos_initial)
          print("[motor]\t\tReference position reached")
        
        
        #get zerotime for time series measurement
        if flag_referencerun==False:
          zerotime= time.time()       #set t=0 for time series measurement
          print('[system]\tTime: 0s')  
        
        #construct name for current measurement
        setname= name_prefix + str(temparray[iteration]) + "K"
        
        
        #click in the right hand side area and scroll upwards
        #to ensure the coordinates of the respective fields match
        pyautogui.click(pos_scrollsectionright, button= "left")
        pyautogui.scroll(+200)
        time.sleep(1)
        
        
        #go to Clear Reference, press enter
        pyautogui.click(pos_clearreference, button="left")
        pyautogui.press("enter")
        time.sleep(1)
        
        #go to Acquire Reference, click
        pyautogui.click(pos_acquirereference, button="left")
        flag_repeat= waitForCompletedProcess(pos_loadingbarend, col_loadingbarend, setname, temparray[iteration], temp_tolerance, interruptMeasurement)
        
        #for successful measurement, loop breaks
        if flag_repeat==False:
          print("[system]\tAcquired reference for measurement \""+ str(setname)+ "\".")
          
          #go to save button, click and press enter
          pyautogui.doubleClick(pos_savebutton, button="left")
          time.sleep(0.5)
          pyautogui.press("enter")
          break
        else:
          stopDialogue(waitForUserInput,setname)
          continue

      if flag_repeat==True:
        continue
      

    
    #SAMPLE WHILE LOOP
    #breaks automatically if repeat flag is not raised
    while 1:
      
      #disable alarm
      LS331.query('ALARM B,0')
      
      #calculate new centre position in case of multcentering
      if flag_multcentering==True:
        pos_final= pos_final_ini + temp_pos_function(temparray[iteration])
        print('[autocent]\tSample centre for T= '+str(temparray[iteration])+'K: p='+str(pos_final))
      else:
        pos_final= pos_final_ini
      
      if flag_motor==True and singlerefrun > 0:
        #singlerefrun > 0 for time series safety, no movement necessary anymore
        print("[motor]\t\tMoving to sample position...")
        motorMovement(pos_final)
        print("[motor]\t\tSample position reached")
      
      #disable taking any more references if flag_referencerun is not raised for time series 
      singlerefrun-=1
      
      
      #go to Name field, click, erase previous data and type in name of dataset
      #the name of the current measurement shall be its temperature
      pyautogui.click(pos_namefield, button="left")
      pyautogui.hotkey("ctrl", "a")           #select the whole integer
      pyautogui.press("delete")               #delete selected integer
  
      if flag_referencerun==False and flag_motor==True:   #for time series option
        timestamp= time.time()-zerotime+1                 #+1 to compensate for waiting 1 second, you could also consider
                                                          #waiting time between every execution
        timestamp= str(int(round(timestamp,0))) + "s"
        print("[system]\tTime: "+ timestamp)
        timestamp= "_"+ timestamp
        setname= name_prefix + str(temparray[iteration])+'K' + timestamp
      else:
        setname= name_prefix + str(temparray[iteration])+'K'   #for normal names without time stamp
       
      pyautogui.typewrite(str(setname))       #enter measurement name
      time.sleep(1)
      
      
      
      #go to Acquire Sample, click
      pyautogui.click(pos_acquiresample, button="left")
      flag_repeat= waitForCompletedProcess(pos_loadingbarend, col_loadingbarend, setname, temparray[iteration], temp_tolerance, interruptMeasurement)
      
      if flag_repeat==False:
        #go to Save button, click and press Enter
        time.sleep(1)
        pyautogui.doubleClick(pos_savebutton, button="left")
        pyautogui.press("enter")
        print("[system]\tAcquired spectrum for measurement \""+ str(setname)+ "\".\n")
        
        if flag_referencerun==False:              #if time series is activated
          continue                                #start aquiring next sample with time stamp
        else:                                     #otherwise go to next temperature
          iteration+= 1  
          break
      else:
        stopDialogue(waitForUserInput,setname)
        continue
      
          
finally:

  if flag_motor==True:
      
    #turn heater off  
    LS331.query('RANGE 0')
    
    #return to initial position p= 0
    print("[motor]\t\tReturning to initial position...")
    pos_initial= 0
    motorMovement(pos_initial)
  
    #close port
    ser.close()
    time.sleep(1)
  
  cattime=0.25
  
  print("\nThank you for using TeraPulseAutomation Version "+ version+"!")
  time.sleep(3)
  print('\n\n\n Designed by:')
  time.sleep(1.5)
  print('\n\n Mario U. Gaimann')
  time.sleep(1.5)
  print('\n DAAD RISE Worldwide Summer Research Intern')
  time.sleep(1.5)  
  print('\n mug502@alumni.york.ac.uk')
  time.sleep(3)
  print('\n\n Terahertz Applications Group')
  time.sleep(cattime)
  print('\n Department of Chemical Engineering and Biotechnology')
  time.sleep(cattime)
  print('\n University of Cambridge')
  time.sleep(4)
  #print('\n                           ,       ')
  #time.sleep(cattime)
  print('                        _/((       ')
  time.sleep(cattime)
  print('               _.---. .\'   `\      ')
  time.sleep(cattime)
  print('             .\'      `     ^ T    ')
  time.sleep(cattime)
  print('            /     \       .--\'     ')
  time.sleep(cattime)
  print('           |      /       )\'-.     ')
  time.sleep(cattime)
  print('           ; ,   <__..-(   \'-.)    ')
  time.sleep(cattime)
  print('            \ \-.__)    ``--._)    ')
  time.sleep(cattime)
  print('             \'.\'-.__.-.    ')
  time.sleep(cattime)
  print('               \'-...-\')     teracat')
  time.sleep(cattime)
time.sleep(7)
