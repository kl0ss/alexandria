"""Implements the main alexandria crawler code"""

from alexandria.config import config

import alexandria.config
import alexandria.discover
import threading
import logging
import Queue
import time

globalQueue = Queue.Queue()
threadPool = []

class Crawler:
    """I'm a SMB share crawler!"""

    def __init__(self):
        logging.debug("Crawler initialized")

    def run(self):
        """Runs the crawler"""
        logging.info("Crawler starting")
        alexandria.config.loadConfig('crawler.cfg')

        threadCount = config.getint('crawler', 'threads')
        for i in range(0, threadCount):
            worker = CrawlerWorker(i)
            threadPool.append(worker)
            logging.debug("Launching thread %s" % i)
            worker.start()
        logging.info("Launched thread pool with %s threads" % threadCount)
        while 1:
            logging.debug("Crawler polling")
            time.sleep(15)

    def stop(self):
        logging.info("Shutting down thread pool")
        for worker in threadPool:
            worker.stop()
        for worker in threadPool:
            worker.join()
        logging.info("Crawler stopped")


class CrawlerWorker(threading.Thread):
    """I'm the crawler that actually writes to the database!"""

    def __init__(self, id):
        self.shutdown = False
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        while not self.shutdown:
            logging.debug("Worker %s polling" % self.id)
            try:
                host = globalQueue.get(False)
                logging.debug("Worker %s processing host '%s'" % (self.id, host.name))
            except Queue.Empty:
                pass
            time.sleep(5)
        logging.info("Worker %s stopping" % self.id)

    def stop(self):
        self.shutdown = True
        logging.debug("Worker %s set to shutdown" % self.id)