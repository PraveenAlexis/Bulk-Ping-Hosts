import platform
import os
import json
import logging
import subprocess
import time
import datetime

FORMAT = '%(asctime)-15s - %(levelname)s: %(message)s'
logging.basicConfig(filename='log.txt',filemode='w',format=FORMAT,encoding='utf-8', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('BULK_PING')

#System variables
no_ping_packets = 1
ping_timeout = 1000 #in miliseconds

try:
    logger.info("modules imported successfully")
    from prettytable import PrettyTable
    from tqdm import tqdm
except ImportError as e:
    logger.error("modules not installed")
    logger.debug(e)
    print("[ERROR]: Please check the log file!")
    input("Press any key to exit..")
    exit()

def main():
    logger.info("-----------------Started Ping Script----------------")
    start_time = time.time()
    print("\n")
    print("Bulk Ping Hosts Script (Windows Only)\n")
    print("NOTE: Add the desired Hosts into the json file.\n")
    print("Author: Praveen Alexis")
    print("Version: 1.3.1\n")

    try:
        # check for json file if not exist create file with default values
        logger.info("checking for host.json file")
        if os.path.isfile('hosts.json'):
            logger.info("located host.json file")
            with open('hosts.json') as json_file:
                data = json.load(json_file)
                logger.info("parsing host.json file")
                count = 0
                count_arr = []
                count_online = 0
                count_offline = 0
                online_hosts = []
                offline_hosts = []                

                for p in tqdm(data['host_list']):
                    count += 1
                    count_arr.append(count)
                
                    res_0 = subprocess.Popen(
                        ['ping', '-n', str(no_ping_packets),'-w',str(ping_timeout), p['ip_addr']], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                    res_0.wait()
                    response_0 = res_0.returncode

                    if(response_0 == 0):
                        # ping OK
                        res_1 = subprocess.Popen(['ping', '-n', str(no_ping_packets),'-w',str(ping_timeout), p['ip_addr'], '|', 'findstr', '/i',
                                                  '"Destination Host Unreachable"'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                        res_1.wait()
                        response_1 = res_1.returncode
                        if(response_1 == 0):
                            # Destination Unreachable DPs (Offline)
                            count_offline += 1
                            online_hosts.append("-")
                            offline_hosts.append(p['host_name']+" ("+p['ip_addr']+")")
                        else:
                            # Online DPs
                            count_online += 1
                            online_hosts.append(p['host_name']+" ("+p['ip_addr']+")")
                            offline_hosts.append("-")

                    elif(response_0 == 1):
                        # First ping Offline
                        res_0 = subprocess.Popen(['ping', '-n', str(no_ping_packets),'-w',str(ping_timeout), p['ip_addr']], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                        res_0.wait()
                        response_0 = res_0.returncode

                        if(response_0 == 0):
                            # Online DPS
                            count_online += 1
                            online_hosts.append(p['host_name']+" ("+p['ip_addr']+")")
                            offline_hosts.append("-")
                        else:
                            # Offline DPs
                            count_offline += 1
                            online_hosts.append("-")
                            offline_hosts.append(p['host_name']+" ("+p['ip_addr']+")")

                print("Loading Results...\n")
                try:
                    logger.info("drawing the output table")
                    table = PrettyTable()
                    table.add_column("No", count_arr)
                    table.add_column(
                        "Online Hosts (" + str(count_online)+")", online_hosts)
                    table.add_column(
                        "Offline Hostss ("+str(count_offline)+")", offline_hosts)
                    table.align = "l"
                    print(table)
                except Exception as e:
                    logger.error("drawing table error")
                    logger.debug(e)
        else:
            logger.warning("host.json file is missing")
            print("json file not found, creating a sample file..")
            try:
                with open("hosts.json", "w", encoding="utf-8") as f:
                    logger.info("creating sample host.json file")
                    data = "{\"host_list\":[{\"host_name\": \"localhost\",\"ip_addr\": \"127.0.0.1\"},{\"host_name\": \"localhost\",\"ip_addr\": \"127.0.0.2\"}]}"
                    json.dump(json.loads(data), f,ensure_ascii=False, indent=4)
            except Exception as e:
                logger.error("cannot create host.json file")
                logger.debug(e)
    except Exception as e:
        logger.error("error in main function")
        logger.debug(e)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("Elapsed Time: ", datetime.timedelta(seconds=elapsed_time))
    logger.info("-----------------End of Ping Script-----------------")


if __name__ == '__main__':
    main()  # run the main function
    while True:
        val = input("Do you want to re-run the script? [y/N]")
        if val == "y" or val == "Y":  
            logger.info("user re-run the script")        
            main()
        elif val == "n" or val == "N" or val == "":
            logger.info("user exited the script")
            exit()
            
