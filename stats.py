import csv, os
from time import time


class RenderStats:
    """Keep track of rendering statistics
    """
    def __init__(self, output_file='output/stats.csv'):
        if os.path.exists(output_file):
            # append to existing stats file
            self.writer = csv.writer(open('output/stats.csv', 'a'))
        else:
            # create new stats file with header
            self.writer = csv.writer(open('output/stats.csv', 'w'))
            self.writer.writerow(['Status', 'Wrapper', 'Website', 'Time (sec)', 'Bandwidth (bytes)', 'Num requests'])#, 'Num renders'])
        self.reset()
    
    def reset(self):
        self.wrapper = self.status = self.start_time = None
        self.response_size = self.num_requests = self.num_renders = 0

    def start(self, wrapper, status):
        self.reset()
        self.wrapper, self.status = wrapper, status
        self.start_time = time()

    def stop(self):
        if self.status != None:
            total_time = time() - self.start_time
            name = self.wrapper.__name__ if hasattr(self.wrapper, '__name__') else self.wrapper.__module__
            row = self.status, name, self.wrapper.website, '{:.2f}'.format(total_time), self.response_size, self.num_requests#, self.num_renders
            self.writer.writerow(row)
            self.reset()

    def rendered(self):
        if self.num_requests > 1:
            self.num_renders += 1

    def add_response(self, content):
        self.num_requests += 1
        self.response_size += len(content)
