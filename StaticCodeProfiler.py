#input: code directory that contains c/c++/java source code
#output: static code profile: classification of statements based on their operators and the data types of the variables

import os, fnmatch, sys, string, xml.dom.minidom

def Arithmetic(expr, xmldoc):
    itemlist = xmldoc.getElementsByTagName(expr)
    # the number of arithmetic
    acount = 0
    for s in itemlist:
        str2 = s.toxml()
        if "</name>*" in str2 or "</call>*" in str2 or "*<name>" in str2 or "*<call>" in str2:
           acount = acount +1
        elif "</name>/" in str2 or "</call>/" in str2 or "/<name>" in str2 or "/<call>" in str2:
            acount = acount +1
        elif "</name>-" in str2 or "</call>-" in str2 or "-<name>" in str2 or "-<call>" in str2:
            acount = acount +1
        elif "</name>+" in str2 or "</call>+" in str2 or "+<name>" in str2 or "+<call>" in str2:
            acount = acount +1
        elif "</name>%" in str2 or "</call>%" in str2 or "%<name>" in str2 or "%<call>" in str2:
            acount = acount +1
    return acount


def Condition(xmldoc):
    itemlist = xmldoc.getElementsByTagName('condition')
    totalc = 0
    for s in itemlist:
        str2 = s.toxml()
        if "<expr>1</expr>" not in str2 and "<expr>0</expr>" not in str2:            
            totalc = totalc+1 
    return totalc

def Loop(xmldoc):
    itemlist = xmldoc.getElementsByTagName('while')
    total = 0
    for s in itemlist:
        str2 = s.toxml()
        total = total+1
            
    itemlist = xmldoc.getElementsByTagName('for')
    for s in itemlist:
        str2 = s.toxml()
        total = total+1
        
    return total

def OtherContols(xmldoc):
    itemlist = xmldoc.getElementsByTagName('continue')
    total = 0
    for s in itemlist:
        str2 = s.toxml()
        total = total+1
            
    itemlist = xmldoc.getElementsByTagName('break')
    for s in itemlist:
        str2 = s.toxml()
        total = total+1

    itemlist = xmldoc.getElementsByTagName('goto')
    for s in itemlist:
        str2 = s.toxml()
        total = total+1

    itemlist = xmldoc.getElementsByTagName('return')
    for s in itemlist:
        str2 = s.toxml()
        total = total+1
        
    return total

def Calls(xmldoc):

    itemlist = xmldoc.getElementsByTagName('call')
    total = 0
    for s in itemlist:
        str2 = s.toxml()
        total = total+1

    return total

#todo
def ProfileLOC(srcdir):
    return

def ComputeFuncList(xmldoc):
    funclist = []
    itemlist = xmldoc.getElementsByTagName('function')
    for s in itemlist:
       try:
           xmldoc2 = xml.dom.minidom.parseString(s.toxml())
       except:
           if "</type> <name>" in s.toxml():
               begin = s.toxml().index("</type> <name>")+14
               end = s.toxml().index("</name><parameter_list>")
               name = s.toxml()[begin:end]
               funclist.append(name)
           continue
       itemlist2 = xmldoc2.getElementsByTagName('name')
       counter = 0
       for i in itemlist2:
           if counter == 1:
               name = i.toxml()[6:len(i.toxml())-7]
               funclist.append(name)
           counter = counter + 1
    return funclist

mapping = []
def GetNameType(string, label):    
    temp = string
    llabel = "<"+label+">"
    rlabel = "</"+label+">"
    begin = temp.find(llabel)
    if begin == -1:
        return ""
    end = temp.find(rlabel)
    end = end + 7
    s = temp[begin:end]
    mapping.append(s)
    temp = temp[end:len(temp) - end +1]
    if s != "":
        s = GetNameType(temp, 'decl')
        mapping.append(s)
    return s

def pair(xmlstr, funcname):

    typename = ""
    name = ""
    begin = xmlstr.find("<type><name>")
    if begin == -1:
        begin = xmlstr.find("<type> <name>")
        if begin != -1:
            begin = begin + 13
    else:
        begin = begin + 12
        
    end = xmlstr.find("</name>")
    
    if begin != -1 and end != -1:
        typename = xmlstr[begin:end]

    namebegin = xmlstr.find("</type> <name>")
    offset = 14
    if namebegin == -1:
        namebegin = xmlstr.find("</type><name>")
        offset = 13
    if namebegin != -1:
        namebegin = namebegin + offset
    left = xmlstr[namebegin:]
    nameend = left.find("</name>")
    if nameend != -1:
        name = left[:nameend]
        name = funcname +": "+name
        
    if typename != "" and name != "":
        #print typename
        #print name
        #print "--------------"
        return (typename, name)

    return ()

def TestStmtType(string, funcname, table):

    t = ""
    doc =  xml.dom.minidom.parseString(string)
    slist = doc.getElementsByTagName('name')
    namelist = []
    for s in slist:
        namelist.append(s.toxml()[6:len(s.toxml())- 7])
    
    for (typename, name) in table:
            i = name.find(':')
            if i != -1 and name[0:i] == funcname:
                for n in namelist:
                    if n == name [i+2:]:
                        if "int" in typename or "long" in typename or "char" in typename or "Boolean" in typename or "short" in typename or "byte" in typename:
                            if t == "":
                                t = "scalar"
                        elif typename == "double" or typename == "float" or typename == "long double":
                            if t == "" or t == "scalar":
                                t=typename
                            else:
                                t+=":"+typename
                        elif typename == "list" or typename == "array" or typename == "stack" or typename == "queue":
                            if t == "" or t == "scalar":
                                t = "container"
                            else:
                                t+= ":container"
                        else:
                            # user defined name
                            if t == "" or t == "scalar":
                                t = "user"
                            else:
                                t+= ":user"
                           #print typename
    #print t
    return t

def StmtTypeBasedOnDataType(xmldoc, table, funclist):
    
    itemlist = xmldoc.getElementsByTagName('function')
    count = 0
    stotal = 0
    ftotal = 0
    ctotal = 0
    dtotal = 0
    utotal = 0
    
    for item in itemlist:
        funcname = funclist[count]
        try: 
            sxmldoc = xml.dom.minidom.parseString(item.toxml())
        except:
            #print len(itemlist)
            # find all the condition, expr_stmt, decl_stmt via string matching
            source = item.toxml()
            temp = source
            ilist = []
            while len(temp) > 0:
                cbegin = temp.find("<condition>")
                cend = temp.find("</condition>")
                if cbegin == -1 or cend == -1:
                    break
                cend += 12
                ilist.append(temp[cbegin:cend])
                temp = temp[cend:]

            temp = source
            while len(temp) > 0:
                cbegin = temp.find("<expr_stmt>")
                cend = temp.find("</expr_stmt>")
                if cbegin == -1 or cend == -1:
                    break
                cend += 12
                ilist.append(temp[cbegin:cend])
                temp = temp[cend:]

            temp = source
            while len(temp) > 0:
                cbegin = temp.find("<decl_stmt>")
                cend = temp.find("</decl_stmt>")
                if cbegin == -1 or cend == -1:
                    break
                cend += 12
                ilist.append(temp[cbegin:cend])
                temp = temp[cend:]

            for i in ilist:
                t = TestStmtType(i, funcname, table)
                if "scalar" in t:
                    stotal = stotal + 1
                if "float" in t:
                    ftotal = ftotal + 1
                if "container" in t:
                    ctotal = ctotal + 1
                if "user" in t:
                    utotal = utotal + 1
                if "double" in t:
                    dtotal = dtotal + 1
                

        sitemlist = sxmldoc.getElementsByTagName('condition')
        sitemlist2 = xmldoc.getElementsByTagName('expr_stmt')
        sitemlist3 = xmldoc.getElementsByTagName('decl_stmt')

        for s in sitemlist2:
            sitemlist.append(s)

        for s2 in sitemlist3:
            sitemlist.append(s2)
        
        for sitem in sitemlist:
            stritem = sitem.toxml()
            t = TestStmtType(stritem, funcname, table)
            if "scalar" in t:
                stotal = stotal + 1
            if "float" in t:
                ftotal = ftotal + 1
            if "double" in t:
                dtotal = dtotal + 1
            if "container" in t:
                ctotal = ctotal + 1
            if "user" in t:
                utotal = utotal + 1
                
        count = count + 1
                    
    return (stotal, ftotal, dtotal, ctotal, utotal)
    
#todo handle global variables
#funcname: varname, type
def BuildASimpleSymbolTable(xmldoc, funclist):
    table = []
    itemlist = xmldoc.getElementsByTagName('function')
    current = 0
    for s in itemlist:
        funcname = funclist[current]
        #print s.toxml()
        current = current + 1
        #print funcname
        try:
           xmldoc2 = xml.dom.minidom.parseString(s.toxml())
        except:
            GetNameType(s.toxml(), 'decl')
            for m in mapping:
                p = pair(m, funcname)
                if p != ():
                    table.append(p)
            continue
        itemlist2 = xmldoc2.getElementsByTagName('decl')
        for i in itemlist2:
            p = pair(i.toxml(), funcname)
            if p != ():
                table.append(p)
    return table

#output statement classification regarding computation
def ProfileComputation(arithmetic, cond, loop, othercontrols, calls):
    print "\nStatement classification based on computation"
    print str(arithmetic)+" - the number of arithmetic"
    print str(cond)+" - the number of conditions (including loop conditions)"
    print str(loop)+" - the number of loops"
    print str(othercontrols)+ " - the number of goto, break, continue, return"
    print str(calls)+ " - the number of calls"
   
    return

#output statement classification regarding datatype
def ProfileDataType(profile):
    print "\nStatement classification based on data types"
    print str(profile[0]) + " - the number of statements with only scalar (int, long, char, Boolean, short) data type"
    print str(profile[1]) + " - the number of statements with float point - single precision"
    print str(profile[2]) + " - the number of statements with double"
    print str(profile[3]) + " - the number of statements with containers (stack, array, list, queue)"
    print str(profile[4]) + " - the number of statements with user defined data types"
    return 

def GetFiles(srcdir):
    
    filelist = []
    files = os.walk(srcdir)
    
    for paths, dirs, fname in files:         
        for filename in fname:
            d = srcdir+"\\"+filename
         
            if os.path.exists(d):           
                if filename[len(filename)-3:len(filename)] == "cpp" or filename[len(filename)-1:len(filename)] == "c" or filename[len(filename)-4:len(filename)] == ".java" or filename[len(filename)-3:len(filename)] == "cxx":
                    if (srcdir, filename) not in filelist:
                        filelist.append((srcdir, filename))
        
        if str(paths) != str(srcdir):
            
            ftemp = GetFiles(paths)
            for (d, f) in ftemp:
                if (d, f) not in filelist:
                    filelist.append((d, f))
                              
    return filelist    
    

def StaticCodeProfiling(srcdir):

 
    filelist = GetFiles(srcdir)        
                   
    for (d, f) in filelist:
           
        srcml = ".\src2srcml\src2srcml.exe " + d+"\\"+ f  + " -o " +f+".xml"   
        os.system(srcml)
        print "\n####################################"
        print "\n Profiling: " + f
        xmldoc = xml.dom.minidom.parse(f+".xml")
        #all arithmetics
        totala = Arithmetic('expr', xmldoc)
        #arithmetics in indices computation
        indexa = Arithmetic('index', xmldoc)
        a = totala - indexa

        #all conditions (including loop conditions)
        c = Condition(xmldoc)

        #all while/for loops
        l = Loop(xmldoc)

        #other controls: goto, break, continue, return
        otherc = OtherContols(xmldoc)

        #calls
        calls = Calls(xmldoc)

        #TODO: profileLOC

        ProfileComputation(a, c, l, otherc, calls)
        funclist = ComputeFuncList(xmldoc)
       
        table = BuildASimpleSymbolTable(xmldoc, funclist)

        #scalar: integer, boolean, char;  float point: double, single; containers: list, queue, stack,  other user defined data structure
        profile = StmtTypeBasedOnDataType(xmldoc, table, funclist)

        ProfileDataType(profile)   
    
StaticCodeProfiling(sys.argv[1])



    
