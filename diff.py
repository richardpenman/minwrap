# -*- coding: utf-8 -*-

import csv
import deepdiff


class DiffWriter:
    def __init__(self, filename):
        self.writer = csv.writer(open(filename, 'w'))
        self.seen = {}
        self.header = []

    def __del__(self):
        pass # XXX write header
        self.writer.writerow(self.header)

    def parse(self, diff):
        old_record, new_record = {}, {}
        last_key = None
        for key, result in diff['values_changed'].items():
            match = re.search("'([^\]]*?)'\]$", key)
            if match:
                key = match.groups()[0]
                if key in old_record and last_key != key:
                    print 'new row:', key
                    # time to write values
                    self.write(old_record)
                    self.write(new_record)
                    old_record, new_record = {}, {}
                # add values to records
                if key not in self.header:
                    self.header.append(key)

                for record, value in (old_record, result['oldvalue']), (new_record, result['newvalue']):
                    value = common.unescape(unicode(value))
                    record[key] = record[key] + '|' + value if key in record else value
                last_key = key
            else:
                print 'no match:', key
        # write current versions 
        self.write(old_record)
        self.write(new_record)

    def write(self, record):
        """Write row to CSV if not seen before
        """
        if record:
            row = [record.get(field) for field in self.header]
            h = hash(tuple(row))
            if h not in self.seen:
                self.seen[h] = True
                #print row
                self.writer.writerow(row)



class AjaxAbstraction:
    def __init__(self):
        """
        status = False
        for reply, matches in self.transitions:
            # update query string
            params = collections.OrderedDict(reply.url().queryItems())
            for method, key, text_parser, original_input in matches:
                if method == GET:
                    params[key] = params[key].replace(text_parser(original_input), text_parser(current_input))
                elif method == POST:
                    pass # XXX
                else:
                    raise AjaxError('Unrecognized method: {}'.format(method))

            url = reply.url().toString().split('?')[0] + '?' + urllib.urlencode(params)
            #'&'.join('{}={}'.format(key, value) for key, value in params.items())
            print reply.url().toString(), '->', url
            from webscraping import download
            #print 'init ratio:', difflib.SequenceMatcher(a=download.Download().get(reply.url().toString()), b=reply.response).ratio()

            html = download.Download().get(url)
            parsed_response = parser.parse(html)
            if parsed_response is not None:
                diff = deepdiff.DeepDiff(reply.parsed_response, parsed_response)
                pprint.pprint(diff)
                #DiffWriter('rows.csv').parse(diff)
            else:
                print 'failed to parse:', url
            #s = difflib.SequenceMatcher(a=reply.response, b=html)
            #print 'ratio:', s.ratio()
            #for operation, i1, i2, j1, j2 in s.get_opcodes():
            #    if operation == 'replace':
            #        print reply.response[i1:i2], '->', html[j1:j2]
            status = True
        return status
        """
