#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-
"""
pi-ager dry aging fridge control

this is the control for a self-made dry aging fridge
"""

# Importieren der Module
import os
import time
 
#Zuerst Datenbank pr�fen
import pi_ager_database_check
pi_ager_database_check.check_and_update_database()

#import pi_ager_logging
from main.pi_ager_cl_logger import cl_fact_logger
#pi_ager_logging.create_logger('main.py')
import pi_ager_loop
import pi_ager_init
import pi_ager_organization
import pi_ager_names
import pi_ager_database
import pi_ager_database_check
import pi_revision
from messenger.pi_ager_cl_alarm import cl_fact_logic_alarm
from messenger.pi_ager_cl_messenger import cl_fact_logic_messenger
from sensors.pi_ager_cl_sensor_type import cl_fact_main_sensor_type
####Display
from main.pi_ager_cl_nextion import pi_ager_cl_nextion
####
#global logger
####Display
# Aktivieren des Displays
pi_ager_cl_nextion.get_instance()
####
pi_ager_names.create_json_file()
pi_ager_database_check.check_and_update_database()
pi_ager_init.set_language()
#logger = pi_ager_logging.create_logger('main')
#logger.debug('logging initialised')
cl_fact_logger.get_instance().debug(('logging initialised __________________________'))
#logger.info(pi_ager_names.logspacer)
cl_fact_logger.get_instance().info((pi_ager_names.logspacer))

pi_revision.get_and_write_revision_in_database()

pi_ager_init.setup_GPIO()
#pi_ager_init.set_sensortype()
cl_fact_main_sensor_type().get_instance()._is_valid()
pi_ager_init.set_system_starttime()

os.system('sudo /var/sudowebscript.sh pkillscale &')
time.sleep(2)
os.system('sudo /var/sudowebscript.sh startscale &')
#logger.debug('scale restart done')
cl_fact_logger.get_instance().debug(('scale restart done'))

exception_known = True
# Send a start message
try:
    cl_fact_logic_messenger().get_instance().handle_event('Pi-Ager_started', None) #if the second parameter is empty, the value is take from the field envent_text in table config_messenger_event 
except Exception as cx_error:
    exception_known = cl_fact_logic_messenger().get_instance().handle_exception(cx_error)
    pass

try:
    
    pi_ager_loop.autostart_loop()

except KeyboardInterrupt:
    #logger.warning(_('KeyboardInterrupt'))
    cl_fact_logger.get_instance().debug(_('KeyboardInterrupt'))
    
    pass

except Exception as cx_error:
    exception_known = cl_fact_logic_messenger().get_instance().handle_exception(cx_error)
    pass

finally:
    if exception_known == False:
        pi_ager_init.loopcounter = 0
        pi_ager_database.write_stop_in_database(pi_ager_names.status_pi_ager_key)
        os.system('sudo /var/sudowebscript.sh pkillscale &')
        os.system('sudo /var/sudowebscript.sh pkillmain &')
        pi_ager_organization.goodbye()