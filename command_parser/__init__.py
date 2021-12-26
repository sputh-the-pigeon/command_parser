from enum import Enum
from typing import List, Dict

class Optimize(Enum):
    NORMAL = 0
    MARKDOWN = 1

class State:
    START = 0
    FLAG_NAME = 1
    INPUT = 2

class CommandParser:
    flags: List[str] = []
    optimize: Optimize = Optimize.MARKDOWN
    data: Dict[str, str] = {}
    __accum: Dict[str, str] = {'lastchar':'', 'flag':'', 'lastflag':0, 'lastfname':'', 'inputc':'', 'codelit':None}
    __flagc: bool = True
    __codeblock: bool = False
    __startedc: bool = False
    __consumer: bool = False
    __inputc: bool = False 
    __state: int = State.START 
    def __init__(self, 
                 _flags: List[str] = [], 
                 _optimized_for: Optimize = Optimize.MARKDOWN) -> None:
        self.flags = _flags
        self.data = {key:'' for key in self.flags}
        self.optimize = _optimized_for
    def parse(self, command: str) -> Dict[str, str]:
        for i, ind in zip(command, range(len(command))):
            if self.__state == State.START:
                if not self.__inputc: self.__startedc = False
                self.__flagc = True
                if self.__inputc: self.__accum['inputc'] += i
                if i not in ['-', '`']:
                    if self.__inputc:
                        self.__inputc = False
                        self.data[self.__accum['lastfname']] += self.__accum['inputc']
                        self.__accum['inputc'] = ''
                        self.__accum['lastchar'] = i
                        self.__state = State.INPUT
                    self.__accum['lastchar'] = i
                    continue
                elif i == '`' and not self.__codeblock: 
                    dnext = command[ind+2:]
                    if command[ind-2:ind+1] == '```' and '```' in dnext and ind-2 > 0:
                        self.__codeblock = True
                        self.__accum['codelit'] = '```'
                    elif command[ind-1:ind+1] == '``' and [1 for c, cind in zip(dnext, range(len(dnext))) if c+((dnext+' ')[cind+1]) == '``' and (dnext+'  ')[cind+2] != '`' and dnext[cind-1] != '`' and cind-1 > 0]:
                        self.__codeblock = True
                        self.__accum['codelit'] = '``'
                    elif i == '`' and [1 for c, cind in zip(dnext, range(len(dnext))) if c == '`' and (dnext+' ')[cind+1] != '`' and dnext[cind-1] != '`' and cind-1 > 0]:
                        self.__codeblock = True
                        self.__accum['codelit'] = '`'
                    else: continue
                elif i == '`' and self.__codeblock:
                    if self.__accum['codelit'] == '```' and command[ind:ind+3] == '```':
                        self.__codeblock = False
                        self.__accum['codelit'] = None
                    elif self.__accum['codelit'] == '``' and command[ind:ind+2] == '``' and command[ind+2] != '`':
                        self.__codeblock = False
                        self.__accum['codelit'] = None
                    elif self.__accum['codelit'] == '`' and command[ind+1] != '`':
                        self.__codeblock = False
                        self.__accum['codelit'] = None
                else:
                    if self.__accum['lastchar'] == '-' and not self.__codeblock:
                        if not self.__inputc:
                            self.__accum['lastflag'] = self.__state
                        self.__state = State.FLAG_NAME
                    elif self.__codeblock and self.__inputc:
                        self.__inputc = False
                        self.__state = State.INPUT
                        self.data[self.__accum['lastfname']] += self.__accum['inputc']
                        self.__accum['inputc'] = ''
                    self.__accum['lastchar'] = i
            elif self.__state == State.FLAG_NAME:
                if self.__inputc:
                    self.__accum['inputc'] += i
                if i.isidentifier() and self.__flagc:
                    self.__accum['flag'] += i
                elif i in ['\n', '\t', ' ']: 
                  self.__flagc = False
                elif i == '=':
                    self.__accum['lastflag'] = self.__state
                    if self.__accum['flag'] not in self.flags:
                        self.__state = State.START
                        self.__accum['flag'] = ''
                        if self.__inputc:
                            self.__inputc = False
                            self.data[self.__accum['lastfname']] += self.__accum['inputc']
                            self.__accum['inputc'] = '' 
                            self.__state = State.INPUT         
                        continue
                    self.data[self.__accum['flag']] = ''
                    self.__accum['lastfname'] = self.__accum['flag']
                    self.__accum['flag'] = ''
                    self.__inputc = False
                    self.__consumer = False
                    self.__startedc = False
                    self.__accum['inputc'] = ''
                    self.__state = State.INPUT
                else:
                    self.__accum['flag'] = ''
                    self.__inputc = False
                    if self.__inputc:
                        self.data[self.__accum['lastfname']] += self.__accum['inputc']
                        self.__accum['inputc'] = ''
                        self.__state = State.INPUT         
                        continue
                    else:
                        self.__accum['lastflag'] = self.__state
                        self.__accum['lastfname'] = ''
                        self.__flagc = True
                        self.__startedc = False
                        self.__state = State.START
            elif self.__state == State.INPUT:
                if i in ['\n', '\t', ' '] and not self.__startedc:
                    continue
                elif i == '"' and not self.__startedc:
                    if '"' in command[ind+1:]:
                        self.__consumer = True
                        self.__startedc = True
                        continue
                elif i == '"' and self.__accum['lastchar'] != '\\' and self.__consumer and self.__startedc:
                    self.__accum['lastflag'] = 2
                    self.__accum['lastfname'] = ''
                    self.__accum['flag'] = ''
                    self.__inputc = False
                    self.__flagc = True
                    self.__startedc = False
                    self.__state = State.START
                    continue
                elif i == '`' and not self.__codeblock:
                    dnext = command[ind+2:]
                    if command[ind-2:ind+1] == '```' and '```' in dnext and ind-2 > 0:
                        self.__codeblock = True
                        self.__accum['codelit'] = '```'
                    elif command[ind-1:ind+1] == '``' and [1 for c, cind in zip(dnext, range(len(dnext))) if c+((dnext+' ')[cind+1]) == '``' and (dnext+'  ')[cind+2] != '`' and dnext[cind-1] != '`' and cind-1 > 0]:
                        self.__codeblock = True
                        self.__accum['codelit'] = '``'
                    elif i == '`' and [1 for c, cind in zip(dnext, range(len(dnext))) if c == '`' and (dnext+' ')[cind+1] != '`' and dnext[cind-1] != '`' and cind-1 > 0]:
                        self.__codeblock = True
                        self.__accum['codelit'] = '`'
                elif i == '`' and self.__codeblock:
                    if self.__accum['codelit'] == '```' and command[ind:ind+3] == '```':
                        self.__codeblock = False
                        self.__accum['codelit'] = None
                    elif self.__accum['codelit'] == '``' and command[ind:ind+2] == '``' and command[ind+2] != '`':
                        self.__codeblock = False
                        self.__accum['codelit'] = None
                    elif self.__accum['codelit'] == '`' and command[ind+1] != '`':
                        self.__codeblock = False
                        self.__accum['codelit'] = None
                elif self.__startedc and not self.__consumer and i == '-':
                    self.__state = State.START
                    self.__inputc = True
                    self.__accum['inputc'] += i
                    self.__accum['lastchar'] = i
                    continue
                elif self.__startedc and not self.__consumer and i == ';' and self.__accum['lastchar'] != '\\':
                    self.__accum['lastflag'] = 2
                    self.__accum['lastfname'] = ''
                    self.__accum['flag'] = ''
                    self.__inputc = False
                    self.__flagc = True
                    self.__startedc = False
                    self.__state = State.START
                    continue
                self.__startedc = True
                self.data[self.__accum['lastfname']] += i
                self.__accum['lastchar'] = i
        return {d:v.strip() for d,v in self.data.items()}
