#!/usr/bin/python
import serial
from datetime import datetime
import time
import urllib
import pdb
import pi_ager_names

from main.pi_ager_cl_logger import cl_fact_logger

class pi_ager_cl_nextion:
    __o_instance = None
    port = None
    eof = None
    
    @classmethod        
    def get_instance(self):
        """
        Factory method to get the nextion instance
        """
        cl_fact_logger.get_instance().debug(cl_fact_logger.get_instance().me())
        if pi_ager_cl_nextion.__o_instance is None:
            pi_ager_cl_nextion.__o_instance = pi_ager_cl_nextion()
        return(pi_ager_cl_nextion.__o_instance)

    def __init__(self):
        global port
        global eof
        
        cl_fact_logger.get_instance().debug(cl_fact_logger.get_instance().me())
        port=serial.Serial(port='/dev/serial0',baudrate=9600, timeout=1.0)
        logstring = 'Serial Interface init: ' + str(port)
        cl_fact_logger.get_instance().debug(logstring)
        eof_n = 255
        eof=bytes([eof_n])+bytes([eof_n])+bytes([eof_n])
        self.sendCmdToDisplay('page boot')
        #temp
        temperature = ""
        #cmd1 = "https://api.thingspeak.com/apps/thinghttp/send_request?api_key=Your API Key from ThinkSpeak.com"
        #conditions
        humidity = ""
        #cmd2 = "https://api.thingspeak.com/apps/thinghttp/send_request?api_key=Your API Key from ThinkSpeak.com" 
        # Page = 0 #page0 is the norm and page 1 is all black with large #'s for easy reading in the AM
        # pic = 0

    def updateDisplay(self, currentStatus):
        self.switchLED(pi_ager_names.main_led_light, currentStatus[pi_ager_names.status_light_key])
        self.switchLED(pi_ager_names.main_led_circulation, currentStatus[pi_ager_names.status_circulating_air_key])
        self.switchLED(pi_ager_names.main_led_exhaust, currentStatus[pi_ager_names.status_exhaust_air_key])
        self.switchLED(pi_ager_names.main_led_heating, currentStatus[pi_ager_names.status_heater_key])
        self.switchLED(pi_ager_names.main_led_cooling, currentStatus[pi_ager_names.status_cooling_compressor_key])
        self.switchLED(pi_ager_names.main_led_humidify, currentStatus[pi_ager_names.status_humidifier_key])
        self.switchLED(pi_ager_names.main_led_dehumidify, currentStatus[pi_ager_names.status_dehumidifier_key])
        self.switchLED(pi_ager_names.main_led_uv, currentStatus[pi_ager_names.status_uv_key])

    def stringToBytes(self,utfString):
        return bytes(utfString,'utf-8')
        
    def wakeUp(self):
        self.sendCmdToDisplay('sleep=0')
        
    def stopRefreshPage(self, pageName):
        self.sendCmdToDisplay('page ' + pageName)
        self.sendCmdToDisplay('ref_stop')
        
    def startRefreshPage(self, pageName):
        self.sendCmdToDisplay('page ' + pageName)
        self.sendCmdToDisplay('ref_star')
        
    def setDisplaySensordata(self,currentTemp,currentHumid,lastTemp,lastHumid):
        strTemp = str(round(currentTemp,1)).replace('.',',')
        strHumid = str(round(currentHumid,1)).replace('.',',')
        #self.stopRefreshPage('main')
        if currentTemp != lastTemp:
            self.setTemperature(strTemp)
        if currentHumid != lastHumid:
            self.setHumidity(strHumid)
        #self.startRefreshPage('main')
        
    def setTemperature(self,temp):
        self.sendDataToDisplay('main',pi_ager_names.main_txt_temperature + '.txt',temp)

    def setHumidity(self,humid):
        self.sendDataToDisplay('main',pi_ager_names.main_txt_humidity + '.txt',humid)
        
    def switchOn(self,nameLED):
        self.switchLED(nameLED,True)
        
    def switchOff(self,nameLED):
        self.switchLED(nameLED,False)
        
    def switchLED(self,nameLED,statusOn):
        if statusOn == 1:
            id_pic=56
        else:
            id_pic=57
        self.sendDataToDisplay('main',nameLED + '.pic',str(id_pic),False)

    def sendDataToDisplay(self,page,target,value,valueTypeString=True):
        global port
        global eof
        
        cmdPage = 'page ' + page
        if valueTypeString:
            value = '"' + value + '"'
        cmdSetValue = target + '=' + value
        logstring = 'Serial Interface: ' + str(port)
        cl_fact_logger.get_instance().debug(logstring)
        self.sendCmdToDisplay(cmdPage)
        self.sendCmdToDisplay(cmdSetValue)
        #port.flush()
        
    def sendCmdToDisplay(self,cmd):
        global port
        
        if cmd != 'sleep=0':
            self.wakeUp()
        port.write(self.stringToBytes(cmd) + eof)
        logstring = 'Value sent to Display: ' + cmd
        cl_fact_logger.get_instance().debug(logstring)
        # if self.NX_waitok()[0]:
            # logstring = 'Sending command to display was successful.'
        # else:
            # logstring = 'Failure sending command to display.'
        # cl_fact_logger.get_instance().info(logstring)
        
        # while (endcount != 3):
            # try:
                # byte = port.read()
            # except termios.error, e:
                # logger.error(_(u'termios.error in NX_reader: {}').format(e[1]))
            # if byte != '':
                # # Kein Timeout
                # bytecount += 1
                # message['raw'] += byte[0]
                # if (byte[0] == '\xff'):
                    # endcount += 1
                # else:
                    # endcount = 0
            # else:
                # # Timeout, sollen wir stoppen?
                # if stop_event.is_set():
                    # break
                    
    def NX_waitok(self):
        global port

        endcount = 0
        bytecount = 0
        ok = False
        bytes = []

        while True:
            if port.inWaiting() > 0:
                break;
            #cl_fact_logger.get_instance().info(u'Waiting for answer of serial port...')
            time.sleep(0.5)

        while endcount != 3:
            try:
                # logstring = 'Serial Interface NX_waitok: ' + str(port)
                # cl_fact_logger.get_instance().debug(logstring)
                byte = port.read()
                bytes.append(byte)
            except Exception as e:
                raise e
            
            if byte == b'':
                cl_fact_logger.get_instance().info(u'Serial Communication Timeout!')
                break
            elif byte is None:
                cl_fact_logger.get_instance().info(u'Serial Communication failed!')
                break
            bytecount += 1
            #cl_fact_logger.get_instance().debug('byte: ' + str(byte))
            if (byte[0] == '\xff'):
                endcount += 1
            elif (byte[0] == '\x01' and bytecount == 1):
                endcount = 0
                ok = True
            else:
                endcount = 0
                
        return ok,bytes

    def closePort(self):
        global port
        
        port.close()

