import csv
from time import time


class RenderStats:
    """Keep track of rendering statistics
    """
    def __init__(self):
        self.writer = csv.writer(open('output/stats.csv', 'w'))
        self.writer.writerow(['Status', 'Website', 'Time (sec)', 'Bandwidth (bytes)', 'Num requests'])#, 'Num renders'])
        self.reset()
    
    def reset(self):
        self.website = self.status = self.start_time = None
        self.response_size = self.num_requests = self.num_renders = 0

    def start(self, website, status):
        self.reset()
        self.website, self.status = website, status
        self.start_time = time()

    def stop(self):
        if self.status != None:
            total_time = time() - self.start_time
            row = self.status, self.website, total_time, self.response_size, self.num_requests#, self.num_renders
            self.writer.writerow(row)
            self.reset()

    def rendered(self):
        if self.num_requests > 1:
            self.num_renders += 1

    def add_response(self, content):
        self.num_requests += 1
        self.response_size += len(content)
