from __future__ import print_function
from threading import Thread
import bottle, sys, math
from bottle import static_file
from pyosc import Server, Client
from googletrans import Translator
import eng_to_ipa as ipa
from InaturalistSearch import InatThread
from PixabaySearch import PixaThread

END = '\033[0m'
WHITE = '\033[0;37;48m'
TRANS = '\033[96m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
BW = '\033[30m\033[47m'
        
class TransThread(Thread):
    def __init__(self, textinput, dest='en', osc_client=None, lang='fr'):
        Thread.__init__(self)
        self.textinput = textinput
        self.dest = dest
        self.osc_client = osc_client
        self.lang = lang
        
    def run(self):
        try:
            self.translation = str(Translator().translate(self.textinput, dest=self.dest)).split("text=",1)[1].split(", pronunciation=")[0]
        except:
            self.translation = "ERROR"
        
        if self.translation == "ERROR" or self.lang == 'en':
            self.phonetic = str(ipa.convert(self.textinput))
            self.sotos_ochando = ''.join(c for c in self.textinput if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ')
        else:
            self.phonetic = str(ipa.convert(self.translation))
            self.sotos_ochando = ''.join(c for c in self.translation if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ')
            
        print(TRANS + "translation -|" + self.translation + "|-")
        print(TRANS + "phonetic    -|" + self.phonetic + "|-")
        print(TRANS + "soto_ochando-|" + self.sotos_ochando + "|-")
        self.osc_client.send('/litho/translation',self.translation.upper())
        self.osc_client.send('/litho/phonetic',self.phonetic.upper())
        self.osc_client.send('/litho/universal',self.sotos_ochando)



class Lithosys:
    global is_restart_needed

    def __init__(self, osc_server_port=45001, osc_client_host='127.0.0.1', osc_client_port=45000, http_server_port=8080, lang = 'fr', dest = 'en', mode='all', size='medium_url', maxwords=10):
        self.osc_client = Client(osc_client_host, osc_client_port)
        self.osc_server = Server('0.0.0.0', osc_server_port, self.callback)
        
        self.http_server_port = http_server_port
        self.silent = True
        self.is_restart_needed = True
        
        self.http_server = bottle.Bottle()

        self.silent = False
        self.lang = lang
        self.dest = dest
        self.count = 0
        self.phonetic = ''
        self.translation = ''
        self.sotos_ochando = ''
        self.sentence = False
        self.splLen = 0
        self.splLenPrev = 0
        self.splFloor = 0
        self.splModulo = 0
        self.splFloorPrev = 0
        self.splModuloPrev = 0
        self.mode = mode
        self.size=size
        
        self.maxwords = maxwords
        
        print(END + WHITE)
        print(BW + '*** Please open chrome at http://127.0.0.1:%d ***' % self.http_server_port)
        print(END + WHITE)

        self.http_server.get('/', callback=self.index)
        self.http_server.post('/getconfig', callback=self.config)
        self.http_server.post('/result', callback=self.result)
        self.http_server.get('/need_restart', callback=self.need_restart)
        self.http_server.run(host='localhost', port=self.http_server_port, quiet=True)

    def callback(self, address, *args):
        # print('OSC message = "%s"' % message)
        if address == '/record':
            self.silent = False
        elif address == '/pause':
            self.silent = True
        elif address == '/restart':
            self.is_restart_needed = True
            self.silent = False
        elif address == '/search':
            if len(args) >= 1 :
                print (END + WHITE + "searching "+BW+" "+str(args[0])+" "+END+"")
                self.search(str(args[0]))
        elif address == '/translate':
            if len(args) >= 1 :
                print (END + WHITE + "translating "+BW+" "+str(args[0])+" "+END+"")
                self.translate(str(args[0]))
        elif address == '/mode':
            if len(args) >= 1 :
                self.mode = str(args[0])
                print (END + WHITE + "-mode "+self.mode)
        elif address == '/size':
            if len(args) >= 1 :
                self.size = str(args[0])
                print (END + WHITE + "-size "+self.size)
        elif address == '/exit':
            self.osc_server.stop()
            self.http_server.close()
            sys.exit(0)
        else:
            print("callback : "+str(address))
            for x in range(0,len(args)):
                print("     " + str(args[x]))

    def result(self):
        result = {'transcript': bottle.request.forms.getunicode('transcript'),
                'confidence': float(bottle.request.forms.get('confidence', 0)),
                'sentence': int(bottle.request.forms.sentence)}
        #mess = ("   " + result['transcript'] + "   ").encode('utf-8').strip('<eos>')
        mess = result['transcript']
        
        if self.silent == True:
            if result['sentence'] == 1:
                print("(pause)phras_ " + mess)
            else:
                print("(pause)mots _ " + mess)
            return {'silent':True}
        
        self.sentence  = result['sentence'] == 1
        #print("SENTENCE : "+str(self.sentence))
        spl = mess.split(" ")
        self.splLenPrev = self.splLen
        self.splLen = len(spl)
        
        
        self.splFloor = math.floor(self.splLen / self.maxwords)
        self.splModulo = self.splLen % self.maxwords
        
        #print("MODULO "+str(self.splModulo)+" / "+str(self.splFloor)+" / "+str(self.splLen))
        
        if self.splModulo == self.splModuloPrev and self.splFloor == self.splFloorPrev and self.sentence == False:
            return {'silent':True}
        
        if self.splFloorPrev < self.splFloor :
            start = self.splFloorPrev*self.maxwords
            end = start + self.splModuloPrev + 1
            #print("SPLITTED    _ "+str(start)+" - "+str(end))
            spl = spl[start:end]
            mess = ''.join(str(e)+" " for e in spl)
            print(END + WHITE + "splitted    -|" + mess + "|-")
            if mess :
                #self.osc_client.send('/litho/words', mess.upper())
                self.translate(mess)
                self.sentence = True
        elif self.sentence :
            start = self.splFloor*self.maxwords
            end = start + self.splModulo + 1
            #print("SENTENCE    _ "+str(start)+" - "+str(end))
            spl = spl[start:end]
            mess = ''.join(str(e)+" " for e in spl)
            print(END + WHITE + "phrase      -|" + mess + "|-")
            if mess :
                self.osc_client.send('/litho/universal_direct', ''.join(c for c in mess.upper() if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '))
                self.osc_client.send('/litho/words', mess.upper())
                self.translate(mess)
        else:
            start = self.splFloor*self.maxwords
            end = start + self.splModulo + 1
            #print("WORDS       _ "+str(start)+" - "+str(end))
            spl = spl[start:end]
            mess = ''.join(str(e)+" " for e in spl)
            print(END + WHITE + "mots        -|" + mess + "|-")
            if mess :
                self.osc_client.send('/litho/universal_direct', ''.join(c for c in mess.upper() if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '))
                self.osc_client.send('/litho/words', mess.upper())
            
        self.splFloorPrev = self.splFloor
        self.splModuloPrev = self.splModulo

        return {'silent':False, 'message':mess, 'sentence':self.sentence, 'translation':self.translation, 'phonetic':self.phonetic, 'universal':self.sotos_ochando}

    def search(self, message):
        message = message.strip('\'')
        message = message.replace(",", " ")
        message = message.replace('à', "a")
        message = message.replace("â", "a")
        message = message.replace("é", "e")
        message = message.replace("è", "e")
        message = message.replace("ê", "e")
        message = message.replace("ë", "e")
        message = message.replace("î", "i")
        message = message.replace("ï", "i")
        message = message.replace("ô", "o")
        message = message.replace("ö", "o")
        message = message.replace("ù", "u")
        message = message.replace("ü", "u")
        message = message.replace("ç", "c")
        message = message.replace(")", " ")
        message = message.replace(", ", " ")
        message = message.replace("… ", " ")
        message = message.replace('\xe2\x80\x99', "'")
        
        thd1 = InatThread(message, self.osc_client, self.mode, self.size)
        thd1.start();
        thd2 = PixaThread(message, self.osc_client, self.mode)
        thd2.start();


    def translate(self, message):
        # THREAD TRANSLATE
        thd = TransThread(message, self.dest, self.osc_client);
        thd.start();
        
    def need_restart(self):
        if self.is_restart_needed:
            self.is_restart_needed = False
            return 'yes'
        return 'no'
   
    def index(self):
        return static_file('index.html',root='')
    
    def config(self):
        return {'lang':self.lang, 'dest':self.dest, 'ip':self.osc_client.getIp(), 'max':self.maxwords}


if __name__ == '__main__':    
    if len(sys.argv) == 1:
        Lithosys();
    elif len(sys.argv) == 2:
        Lithosys(maxwords=int(sys.argv[1]))
    elif len(sys.argv) == 3:
        Lithosys(lang = sys.argv[1], dest = sys.argv[2]);
    elif len(sys.argv) == 4:
        Lithosys(lang = sys.argv[1], dest = sys.argv[2], maxwords=int(sys.argv[3]));
    elif len(sys.argv) == 5:
        Lithosys(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif len(sys.argv) == 7:
        Lithosys(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6])
    else:
        print('usage: %s <osc-server-port> <osc-client-host> <osc-client-port> <http-server-port> <lang-in> <lang-out>')
