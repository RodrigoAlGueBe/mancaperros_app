import subprocess
import threading
import time
import logging

# Azure information
RESOURCE_GROUP = "erynfitresource"
MYSQL_SERVER = "erynfit"

mode_prod = False

if mode_prod:
    def wake_database():
        try:
            logging.info("Waking up the database...")
            subprocess.run([
                "az", "mysql", "flexible-server", "start",
                "--name", MYSQL_SERVER,
                "--resource-group", RESOURCE_GROUP
            ], check=True)
            logging.info("Database is awake.")

            # Turn off the database after 2 hours
            timer = threading.Timer(2 * 60 * 60, stop_database)
            timer.start()

        except subprocess.CalledProcessError as e:
            logging.error(f"Error waking up the database: {e}")


    def stop_database():
        try:
            logging.info("Stopping the database...")
            subprocess.run([
                "az", "mysql", "flexible-server", "stop",
                "--name", MYSQL_SERVER,
                "--resource-group", RESOURCE_GROUP
            ], check=True)
            logging.info("Database is stopped.")

        except subprocess.CalledProcessError as e:
            logging.error(f"Error stopping the database: {e}")

else:
    def wake_database():
        logging.info("Database is in local mode. No action needed.")

    def stop_database():
        logging.info("Database is in local mode. No action needed.")