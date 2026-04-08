import json

class Payload(object):
    def __init__(self, j):
        self.recordMap = None
        self.results = None
        self.__dict__ = json.loads(j)
        # Unwrap the extra value nesting in recordMap
        if self.recordMap:
            for table in self.recordMap:
                if table.startswith('__'):
                    continue
                for id in self.recordMap[table]:
                    if 'value' in self.recordMap[table][id] and 'value' in self.recordMap[table][id]['value']:
                        self.recordMap[table][id]['value'] = self.recordMap[table][id]['value']['value']