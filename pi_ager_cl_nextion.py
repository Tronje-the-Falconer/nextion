#!/usr/bin/python3
"""
    thread for nextion HMI display

    mainfile for communication between Pi-Ager and HMI Display via serial port
    Serial port has to be enabled and login disabled using raspi-config
    
"""
if __name__ == '__main__':
    import globals
    # init global threading.lock
    globals.init()

import time
import asyncio
import signal
import logging
import random
import RPi.GPIO as gpio

import pi_ager_database
import pi_ager_names
import pi_ager_gpio_config

from messenger.pi_ager_cl_messenger import cl_fact_logic_messenger
from main.pi_ager_cl_logger import cl_fact_logger
from nextion import Nextion, EventType

import threading

class pi_ager_cl_nextion( threading.Thread ):

    def __init__( self ):
        super().__init__() 
        
        self.client = None
        self.waiter_task = None
        self.stop_event = None
        self.button_event = None
        # self.original_sigint_handler = signal.getsignal(signal.SIGINT)
        self.data = None
        self.type_ = None
        self.loop = None
        self.current_page_id = None
        self.current_theme = 'steak'
        
    def nextion_event_handler(self, type_, data):
        self.data = data
        self.type_ = type_
        if type_ == EventType.STARTUP:
            print('We have booted up!')
        elif type_ == EventType.TOUCH:
            print('A button (id: %d) was touched on page %d' % (data.component_id, data.page_id))
            self.current_page_id = data.page_id
            
        self.loop.call_soon_threadsafe(self.button_event.set)
        # self.button_event.set()
        logging.info('Event %s data: %s', type_, str(data))
    
    async def control_light_status(self):
        light_status = await self.client.get('values.status_light.val')  
        if light_status == 1:
            gpio.output(pi_ager_gpio_config.gpio_light, False)
        else:
            gpio.output(pi_ager_gpio_config.gpio_light, True)
            
    async def button_waiter(self, event):
        try:
            while True:
                print('waiting for button pressed ...')
                await self.button_event.wait()
                print('... got it!')

                if self.data.page_id == 1 and self.data.component_id == 9:
                    await self.control_light_status()
                elif self.data.page_id == 1 and self.data.component_id == 8:
                    await self.client.command('page 2')
                    self.current_page_id = 2
                elif self.data.page_id == 2 and self.data.component_id == 6:
                    await self.control_light_status()    
                elif self.data.page_id == 2 and self.data.component_id == 1:
                    await self.client.command('page 1')
                    self.current_page_id = 1                    
                elif self.data.page_id == 2 and self.data.component_id == 2:
                    await self.client.command('page 3')
                    self.current_page_id = 3  
                elif self.data.page_id == 2 and self.data.component_id == 3:
                    await self.client.command('page 4')
                    self.current_page_id = 4  
                elif self.data.page_id == 2 and self.data.component_id == 4:
                    await self.client.command('page 7')
                    self.current_page_id = 7  
                elif self.data.page_id == 2 and self.data.component_id == 5:
                    await self.client.command('page 6')
                    self.current_page_id = 6  
                elif self.data.page_id == 2 and self.data.component_id == 7:
                    if (self.current_theme == 'steak'):
                        self.current_theme = 'fridge'
                        await self.client.command('page 2')
                        self.current_page_id = 2 
                    else:
                        self.current_theme = 'steak'
                        await self.client.command('page 10')
                        self.current_page_id = 10
                elif self.data.page_id == 3 and self.data.component_id == 1:
                    await self.control_light_status()
                elif self.data.page_id == 3 and self.data.component_id == 10:
                    await self.client.command('page 2')
                    self.current_page_id = 2                    
                elif self.data.page_id == 3 and self.data.component_id == 11:
                    await self.client.command('page 1')
                    self.current_page_id = 1                    
                elif self.data.page_id == 4 and self.data.component_id == 1:
                    await self.control_light_status()
                elif self.data.page_id == 4 and self.data.component_id == 2:
                    await self.client.command('page 2')
                    self.current_page_id = 2
                elif self.data.page_id == 4 and self.data.component_id == 11:
                    await self.client.command('page 1')
                    self.current_page_id = 1
                elif self.data.page_id == 6 and self.data.component_id == 1:
                    await self.control_light_status()
                elif self.data.page_id == 6 and self.data.component_id == 2:
                    await self.client.command('page 2')
                    self.current_page_id = 2
                elif self.data.page_id == 6 and self.data.component_id == 7:
                    await self.client.command('page 1')
                    self.current_page_id = 1
                elif self.data.page_id == 7 and self.data.component_id == 1:
                    await self.control_light_status()
                elif self.data.page_id == 7 and self.data.component_id == 2:
                    await self.client.command('page 2')
                    self.current_page_id = 2
                elif self.data.page_id == 7 and self.data.component_id == 7:
                    await self.client.command('page 1')
                    self.current_page_id = 1
                elif self.data.page_id == 9 and self.data.component_id == 8:
                    await self.client.command('page 10')
                    self.current_page_id = 10
                elif self.data.page_id == 9 and self.data.component_id == 9:
                    await self.control_light_status()
                elif self.data.page_id == 10 and self.data.component_id == 7:
                    await self.control_light_status()
                elif self.data.page_id == 10 and self.data.component_id == 1:
                    await self.client.command('page 9')
                    self.current_page_id = 9
                elif self.data.page_id == 10 and self.data.component_id == 3:
                    await self.client.command('page 12')
                    self.current_page_id = 12
                elif self.data.page_id == 10 and self.data.component_id == 2:
                    await self.client.command('page 11')
                    self.current_page_id = 11
                elif self.data.page_id == 10 and self.data.component_id == 6:
                    if (self.current_theme == 'steak'):
                        self.current_theme = 'fridge'
                        await self.client.command('page 2')
                        self.current_page_id = 2 
                    else:
                        self.current_theme = 'steak'
                        await self.client.command('page 10')
                        self.current_page_id = 10
                elif self.data.page_id == 10 and self.data.component_id == 4:
                    await self.client.command('page 15')
                    self.current_page_id = 15
                elif self.data.page_id == 10 and self.data.component_id == 5:
                    await self.client.command('page 14')
                    self.current_page_id = 14
                elif self.data.page_id == 11 and self.data.component_id == 8:
                    await self.client.command('page 10')
                    self.current_page_id = 10                                        
                elif self.data.page_id == 11 and self.data.component_id == 18:
                    await self.client.command('page 9')
                    self.current_page_id = 9                                             
                elif self.data.page_id == 11 and self.data.component_id == 9:
                    await self.control_light_status()   
                elif self.data.page_id == 12 and self.data.component_id == 1:
                    await self.client.command('page 10')
                    self.current_page_id = 10                     
                elif self.data.page_id == 12 and self.data.component_id == 10:
                    await self.client.command('page 9')
                    self.current_page_id = 9                     
                elif self.data.page_id == 12 and self.data.component_id == 11:
                    await self.control_light_status()   
                elif self.data.page_id == 14 and self.data.component_id == 1:
                    await self.client.command('page 10')
                    self.current_page_id = 10            
                elif self.data.page_id == 14 and self.data.component_id == 6:
                    await self.client.command('page 9')
                    self.current_page_id = 9            
                elif self.data.page_id == 14 and self.data.component_id == 7:
                    await self.control_light_status()   
                elif self.data.page_id == 15 and self.data.component_id == 7:
                    await self.client.command('page 10')
                    self.current_page_id = 10            
                elif self.data.page_id == 15 and self.data.component_id == 5:
                    await self.client.command('page 9')
                    self.current_page_id = 9            
                elif self.data.page_id == 15 and self.data.component_id == 6:
                    await self.control_light_status()   

                    
                self.button_event.clear()
                logging.info('button pressed processed')
        except Exception as e:
            logging.error(str(e))
            pass    

    async def process_page1(self):
        status_piager = pi_ager_database.get_table_value(pi_ager_names.current_values_table, pi_ager_names.status_pi_ager_key )
        
        temp_ist = pi_ager_database.get_table_value(pi_ager_names.current_values_table, pi_ager_names.sensor_temperature_key)
        humidity_ist = pi_ager_database.get_table_value(pi_ager_names.current_values_table, pi_ager_names.sensor_humidity_key)
        dewpoint_ist = pi_ager_database.get_table_value(pi_ager_names.current_values_table, pi_ager_names.sensor_dewpoint_key)
        temp_soll = pi_ager_database.get_table_value(pi_ager_names.config_settings_table, pi_ager_names.setpoint_temperature_key)
        humitidy_soll = pi_ager_database.get_table_value(pi_ager_names.config_settings_table, pi_ager_names.setpoint_humidity_key)
        
        await self.client.set('txt_temp_set.txt', "%.1f" % (temp_soll))
        await self.client.set('txt_humid_set.txt', "%.1f" % (humitidy_soll))        
        if status_piager == 0:
            await self.client.set('txt_temp.txt', '--.-')
            await self.client.set('txt_humid.txt', '--.-')
            await self.client.set('txt_dew.txt', '--.-')
        else:
            await self.client.set('txt_temp.txt', "%.1f" % (temp_ist))
            await self.client.set('txt_humid.txt', "%.1f" % (humidity_ist))        
            await self.client.set('txt_dew.txt', "%.1f" % (dewpoint_ist))  
            
    async def process_page2(self):
        pass
    
    async def run_client(self):
        self.button_event = asyncio.Event()
        self.stop_event = asyncio.Event()
        # self.waiter_task = asyncio.create_task(self.button_waiter(self.button_event))
        self.waiter_task = self.loop.create_task(self.button_waiter(self.button_event))   
        
        self.client = Nextion('/dev/ttyS0', 9600, self.nextion_event_handler, self.loop)
        logging.info('client generated')
        try:
            await self.client.connect()
            logging.info('client connected')
        except Exception as e:
            logging.error(str(e))
            while not self.stop_event.is_set():
                await asyncio.sleep(1)
            
        print(await self.client.get('sleep'))
        
        self.current_page_id = 1
        await self.client.command('page 1')

        while not self.stop_event.is_set():
            # test what happens, when object is not in page
            #try:
            #    await self.client.set('txt_temp.txt', "%.1f" % (random.randint(0, 1000) / 10))
            #except Exception as e:
            #    logging.error(str(e))
            #    pass 
            try:
                if self.current_page_id == 1:
                    await self.process_page1()
                elif self.current_page == 2:
                    await self.process_page2()
            except Exception as e:
                logging.error(str(e))
            
            # await self.client.set('values.temp_cur.txt', "%.1f" % (random.randint(0, 1000) / 10))
            # await self.client.set('values.humidity_cur.txt', "%.1f" % (random.randint(0, 1000) / 10))
            # await self.client.set('values.dewpoint_cur.txt', "%.1f" % (random.randint(0, 1000) / 10))
            # await self.client.set('values.temp_set.txt', "%.1f" % (random.randint(0, 1000) / 10))
            # await self.client.set('values.humidity_set.txt', "%.1f" % (random.randint(0, 1000) / 10))
            # await self.client.set('values.dewpoint_set.txt', "%.1f" % (random.randint(0, 1000) / 10))
            # await self.client.set('values.status_uv.val', 1)
            # await self.client.command('page dp')
            await asyncio.sleep(2)
       
        print('finished')
        
    def inner_ctrl_c_signal_handler(self, sig, frame):
        self.stop_event.set()
        # signal.signal(signal.SIGINT, self.original_sigint_handler)
        
    def init_gpio(self):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(pi_ager_gpio_config.gpio_light, gpio.OUT)   
        
    def run(self):
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.DEBUG,
            handlers=[
                logging.StreamHandler()
            ])
        
        self.init_gpio()
    
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        asyncio.ensure_future(self.run_client())
    
        try:
            self.loop.run_forever()
        
        # except KeyboardInterrupt:
        #    print('ctrl+C pressed')
        # tasks = [task for task in asyncio.all_tasks(self.loop) if not task.done()]
        # for task in tasks:
        #     task.cancel()
            logging.info('run_forever stopped')
            tasks = asyncio.all_tasks(self.loop)
            for t in [t for t in tasks if not (t.done() or t.cancelled())]:
                self.loop.run_until_complete(t)

        # self.loop.run_until_complete(asyncio.gather(*tasks, loop=self.loop))
        # for task in tasks:
        #     if not task.cancelled() and task.exception() is not None: 
        #         self.loop.call_exception_handler({
        #         'message': 'Unhandled exception during Client.run shutdown.',
        #         'exception': task.exception(),
        #         'task': task
        #         })
        # except Exception as e:
        #    logging.info('in run at exception')
        #    logging.info(str(e))
            
        finally:
            #logging.info('after finally')
            self.loop.close()
            
    def stop_loop(self):
        #logging.info('in stop_loop')
        tasks = asyncio.all_tasks(self.loop)
        for t in tasks:
            t.cancel()
        self.loop.stop()
        #logging.info('after self.loop.stop')

        
        
def main():
    nextion_thread = pi_ager_cl_nextion()
    # signal.signal(signal.SIGINT, nextion_thread.inner_ctrl_c_signal_handler)
    nextion_thread.start()
    
    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Ctrl-c received! Sending Stop to thread...")
        # nextion_thread.stop_event.set()
        nextion_thread.loop.call_soon_threadsafe(nextion_thread.stop_event.set)
        # time.sleep(2)
        nextion_thread.stop_loop()
            
    nextion_thread.join()
    print('thread finished.')
    
if __name__ == '__main__':
    main()
        