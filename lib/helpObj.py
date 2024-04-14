import os
from random import randint

class Byte:
    '''
        Byte is class collection 8 bit value
        and have data sava as value: decimal, hxadecimal and ASCII[latin-1] code
        Byte can by set folowing example:
        'ff' -> Byte: 255, 0xff, y
        98 -> Byte: 98, 0x62, b
        62 -> Byte: 68, 0x3e, >
    '''
    def __init__(self, newVal:int|str = None) -> None:
        
        self.dec:int = int()
        self.hex:str = str()
        self.ASCII:chr = str()
        if not( newVal is None ): set(newVal)

    def set(self, setVal:int|str):
        '''
        setVal as look 
        hex:str 'ff'
        decimal:int 145
        ASCII:chr <
        '''
        # set for decimal type value
        if type(setVal) == type(self.dec):
            if (0 <= setVal <= 255):
                self.dec = setVal
                self.hex = hex(setVal)[2:]
                self.ASCII = bytes([self.dec]).decode('latin-1')
            else:
                raise ValueError(" Byte val can be set in <0,255> 8-bits {}".format(setVal))
        elif type(setVal) == type(self.hex):
            if (0 <= int(setVal,16) <= 255):
                self.dec = int(setVal,16)
                self.hex = setVal
                self.ASCII = bytes([self.dec]).decode('latin-1')
            else:
                raise ValueError(" Byte val can be set in <0,255> 8-bits {}".format(setVal))
        else:
            raise ValueError("Value must get type: {}, {}| {}".format( type(self.dec), type(self.hex), type(setVal) ))
        #print(">>>",setVal, self.dec, self.hex, self.ASCII)

    def getDEC(self) -> int:
        if self.dec == None: raise ValueError("No decimal value!")
        return self.dec
    
    def getHEX(self) -> str:
        if self.hex == None: raise ValueError("No hexadecimal value!")
        return self.hex
    
    def __str__(self, modeASCII:bool = False) -> str:
        if modeASCII:
            if self.ASCII == None: raise ValueError("No ascii value!")
            return str(self.ASCII)
        else:
            if self.hex == None: raise ValueError("No hexadecimal value!")
            return "0"*(2-len(self.hex)) + self.hex

class ByteCell:
    def __init__(self, size:int = None, dataBytes:list[int]|str = None ) -> None:
        self.data:list[Byte]
        self.size:int
        if size is None:
            self.size = None
            self.data = None 
        elif dataBytes is None:
            self.size = size
            self.data = [ Byte(0) for _ in range(size)] 
        else:
            self.size = size
            self.data = [ Byte() for _ in range(size)] 
            self.set(dataBytes)
            
        #print(size, dataBytes, self.size, [str(i) for i in self.data], [i.hex for i in self.data] ) 

    def set(self, dataBytes:list[int]|str, reverse: bool = False):
        size:int = None
        if isinstance(dataBytes, str):
            if ( len(dataBytes)%2 == 1):
                raise ValueError("str DataBytes must be even")
            else: 
                size = int(len(dataBytes)//2)
        elif isinstance(dataBytes, list):
            for B in dataBytes:
                if not isinstance(B, int):
                    raise TypeError("list[int] DataBytes must be list of int")
            else:
                size = int(len(dataBytes))
        else:
            raise TypeError( f"Wrong data type: {dataBytes} not: list|str")
        
        if (self.size is None):  
            self.size = size
            self.data = [ Byte() for _ in range(size)] 
        elif (self.data is None): 
            raise ValueError("Wrong dataBytes size")
        else:
            if (size > self.size ):
                raise ValueError("Too much deta")
            else:
                n = self.size-size
                if isinstance(dataBytes, list):
                    dataBytes = n * [0] + dataBytes   
                elif isinstance(dataBytes, str):
                    dataBytes = n * "00" + dataBytes

        # set data base on list of int
        if isinstance(dataBytes, list):
            for B, d in zip(self.data, dataBytes):
                B.set(d)
            
        # set data base on hex
        elif isinstance(dataBytes, str):
            # filt data
            dataBytes.replace(" ", "")
            dataBytes.replace("\t", "")

            dataBytes:list[str] = [dataBytes[i:i+2] for i in range(0, 2*size, 2)]
            for B, d in zip(self.data, dataBytes):
                B.set(d)
        
        if reverse: self.data.reverse()
        
    def getCellDec(self)->list[int]:
        return [B.dec for B in self.data  ]

    def getCellHex(self)->list[str]:
        return [B.hex for B in self.data  ]

    def __str__(self, modeASCII:bool = False)->str:
        if (self.size is None):
            return str(None)
        else:
            dataBytes: str = str()
            for B in self.data: 
                dataBytes += B.__str__(modeASCII) + " "   
            return dataBytes

class ByteSequenceCoder:
    def __init__(self, fileformat:str)->None:
        self.fileformat:str = fileformat
        self.sequence:dict[str, list[bool, ByteCell] ] = dict()

        filepath = "bin//format//" + self.fileformat + ".txt"
        if os.path.exists(filepath):
            self.DecodeSetupFile(filepath)
        else:
            raise FileNotFoundError("Setup file doest exist!")
        
    def DecodeSetupFile(self, filepath):
        # setup values use to creat sequence
        ls_name:list[str] = list()
        ls_size:list[int] = list()
        ls_data:list[str] = list()
        ls_comp:list[bool] = list()

        #decryp setup file: fotrmat.txt
        def decrypt(line):
            if line[0] == '@':
                if line[:-1] != f'@{self.fileformat}':
                    raise FileNotFoundError("Wrong selected format @{}".format(self.fileformat))
                else:
                    pass
            elif line[0] == '!':
                raise StopIteration
            else: 
                # data is ready to use to write 
                def compatibility(s:str, d:str) -> bool:
                    return not (s == '*' or d == '#')

                # normal specifie size equal data size
                def dataEqualSize(s:str, d:str) -> bool:
                    return (2*int(s) == len(d))

                name:str  = None
                size:int  = None
                data:str  = None
                comp:bool = None

                # filtring process
                line = line[:-1]
                line = line.replace(" ",  "")
                line = line.replace("\t", "")
                
                # download data
                try:
                    name, info = line.split(':')
                    size, data =  info.split('=')
                except:
                    raise ValueError( "Line structure: name: size = data {}".format(line))
    
                comp:bool = compatibility(size, data)

                # read size format type * is dynamic size, other +int is byteCell size
                if size == "*":
                    size = None
                    data = None
                    comp = False
                else:
                    size = int(size) 
                    # ffff =>= ffff, # =>= 000000
                    if (data != "#"):
                        # data = 'ffaf'
                        if not dataEqualSize(size, data): raise ValueError("Data must have size lenght! {} {} {}".format(name, size, data))
                        comp = True
                    else:
                        data = "00"*size
                        comp = False
                ls_name.append( name )
                ls_size.append( size )
                ls_data.append( data )
                ls_comp.append( comp )
            
        # read file
        with open(filepath, 'r') as setupFile:
            for line in setupFile:
                try:
                    decrypt(line)
                except StopIteration:
                    break
            setupFile.close()

        # fill formatDataStructure base on setupfile
        for n, s, d, c in zip(ls_name, ls_size, ls_data, ls_comp):
            #print(n, s, d )
            self.sequence[n] = [c,  ByteCell(s, d) ]

    def loadFile(self, path:str="img", title:str="test0", fileformat:str = None)->None:

        CODE:str = str()
        
        #decode function for one Byte
        def decode(ASCII:str)->Byte:
            return ASCII.encode('latin-1')[0]
        
        # file read
        if fileformat is None:  fileformat = self.fileformat
        fullpath:str =  path + "//"  +  title + "." + fileformat
        with open( fullpath, 'r', encoding="latin-1" ) as file:
            CODE = file.read()
            file.close()
        
        # creat byte structure convertet on intigers
        BYTECODE: list[int] = [ decode(ASCII) for ASCII in CODE ] 

        # map BYTECODE to sequence
        for name, (comp, data) in self.sequence.items():
            sampleBYTE, BYTECODE = BYTECODE[:data.size], BYTECODE[data.size:]
            self.sequence[name] = (True, ByteCell(size=data.size, dataBytes=sampleBYTE) )
  
        print(f"File load: {fullpath}")
            
    def saveFile(self, path:str="img", title:str="test0", fileformat:str = None)->None:
        
        CODE:str = str()

        #encode function for one Byte
        def encrypt(dataByteCell:ByteCell)->str:
            cb:str = str()
            for B in dataByteCell.data:
                cb += B.ASCII
            return cb

        # encode full file code 
        for name, (comp, data) in self.sequence.items():
            if comp:
                CODE += encrypt(data)
            else:
                raise ValueError( "Data '{}' hasn't been set.".format(name) )

        # file write
        if fileformat is None:  fileformat = self.fileformat
        fullpath:str =  path + "//"  +  title + "." + fileformat
        with open( fullpath, 'w', encoding="latin-1" ) as file:
            file.write(CODE)
            file.close()
        print(f"File save: {fullpath}")

    def notSetSequence(self)->None:
        for name, (comp, data) in self.sequence.items():
            if not comp: 
                print( f"{ name.ljust(16) }: { str(data.size).ljust(4)} {str(data)}")

    def setByteCell(self,  SETname:str, SETbytes:str|list[int]|int, reverse:bool=False):
        #filters
        if isinstance(SETbytes, str):
            SETbytes = SETbytes.replace(" ","")
            SETbytes = SETbytes.replace("\t","")
        elif isinstance(SETbytes, list): 
            pass
        elif isinstance(SETbytes, int): 
            SETbytes = [SETbytes]
        else: 
            raise TypeError("Wrong SETbytes value type")
        
        # update data byte cell with SETbytes
        for name, (comp, data) in self.sequence.items():
            if SETname == name:
                data.set(SETbytes, reverse=reverse)
                self.sequence[name][0] = True

    def __str__(self) -> str:
        comunicate:str = str()
        for name, (comp, data) in self.sequence.items():
            comp:str = str(comp)
            size:str = str(data.size)
            data:str = str(data)
            comunicate += f"{ name.ljust(16) }: {size.ljust(4)} ({comp.ljust(6)}. {data});\n" 
        comunicate =  "{\n" + comunicate + "}"
        return comunicate

class ArrayPixel:
    def __init__(self, width:int, hight:int) -> None:
        self.randcolor = lambda: [randint(0,255), randint(0,255), randint(0,255)]

        self.width = width
        self.hight = hight
        self.size = width*hight
        self.bytesSize = 3*width*hight

        self.arr:list = list()
        self.setARRAY()
        
    def setARRAY(self):
        self.arr.clear()
        for h in range(self.hight): 
            for w in range(self.width):
                self.arr += self.randcolor()

    def addDWORD(self):
        arr:list = list()
        for c in range(self.hight):
            row:list = list()
            for r in range(3*self.width):
                i =  c*self.width*3 + r
                row.append(self.arr[i])
            DEORD = len(row)%4
            if DEORD  != 0: row += [0 for _ in range(DEORD )]
            arr += row
        self.arr = arr
    
    def getBytesSize(self):
        return len(self.arr)

    def __str__(self)->str:
        comunicate:str = str()
        width = int(len(self.arr)/self.hight)
        for h in range(self.hight): 
            for w in range( width ):
                comunicate += str(self.arr[h*width + w]).ljust(3) + ". "
            comunicate += '\n'
        return comunicate
