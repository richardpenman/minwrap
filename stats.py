import csv, os
from time import time


class RenderStats:
    """Keep track of rendering statistics
    """
    def __init__(self, output_file='output/stats.csv'):
        header = ['Status', 'Wrapper', 'Website', 'Time (sec)', 'Bandwidth (bytes)', 'Num requests']
        self.writer = self.open_file(output_file, header)
        self.reset()
    
    def open_file(self, output_file, header):
        if os.path.exists(output_file):
            # append to existing stats file
            writer = csv.writer(open(output_file, 'a'))
        else:
            # create new stats file with header
            writer = csv.writer(open(output_file, 'w'))
            writer.writerow(header)
        return writer
   
        
    def reset(self):
        self.wrapper = self.status = self.start_time = None
        self.response_size = self.num_requests = 0

    def start(self, wrapper, status):
        self.reset()
        self.wrapper, self.status = wrapper, status
        self.start_time = time()

    def stop(self):
        if self.status != None:
            total_time = time() - self.start_time
            row = self.status, self.wrapper_name(), self.wrapper.website, '{:.2f}'.format(total_time), self.response_size, self.num_requests
            self.writer.writerow(row)
            self.reset()

    def add_response(self, content):
        self.num_requests += 1
        self.response_size += len(content)

    def wrapper_name(self):
        return self.wrapper.__name__ if hasattr(self.wrapper, '__name__') else self.wrapper.__module__

    def save_models(self, wrapper, models, model_file='output/models.csv'):
        self.wrapper = wrapper
        header = ['Wrapper', 'Website'] + ['Model {}'.format(i+1) for i in range(len(models))]
        writer = self.open_file(model_file, header)
        writer.writerow([self.wrapper_name(), self.wrapper.website] + [str(model) for model in models])
