import sys
import re


iq=[]
rq=[]
eq=[]
wq=[]


latency=[0 for itr in range(10)]

unit_status=[[],[]]
branch_id=-1
list_of_instn=[]

reg_busy=[[],[]]

result=[[0 for itr in range(80)]for itr in range(9) ]


dest_reg=["S.D","SW"]

cid = 0
iteration=0
cacheflag=0
stall_id=0
dict_reg={}
max_iterations=1




def instn_parser():
      global branch_id,list_of_instn
      f = open(f_name1, mode = "r", encoding='utf-8-sig')
      l=f.read()

      l=l.split("\n")

      while l[-1]=='':
          l.pop()
      for i in range(len(l)):
            list_of_instn.append(l[i].strip().replace(',','').split())


      for i in range(len(list_of_instn)):
              unit=find_unit(list_of_instn[i][0])
              if list_of_instn[i][0]=='LI':
                  dict_reg[list_of_instn[i][1]]=int(list_of_instn[i][2])
              if unit=="":
                  list_of_instn[i].pop(0)
                  branch_id=i
                  break

      x=list_of_instn.pop()
      ll=list_of_instn[branch_id:]

      for i in range(max_iterations):
        list_of_instn+=ll
      list_of_instn+=[x]



unit_data=[["INTEGER","DATA"],[1,1],[1,1]]


def config_parser():

    f = open(f_name3,mode = "r", encoding='utf-8-sig')
    l = f.read()
    l = l.split("\n")
    data = []
    for i in range(len(l)):
        l[i] = l[i].strip()
        id=re.split(": |,",l[i])
        unit_data[0].append(id[0].upper())
        unit_data[1].append(int(id[1]))
        unit_data[2].append(int(id[2]))

    for i in range(len(unit_data[0])):
        unit_status[0].append(unit_data[0][i].upper())
        unit_status[1].append(unit_data[1][i])


def data_parser():
      f = open(f_name2, mode = "r", encoding='utf-8-sig')
      l = f.read()

      l=l.split("\n")
      data=[]
      for i in range(len(l)):
        l[i]=l[i].strip()
        data.append(binaryToDecimal(int(l[i])))



def binaryToDecimal(binary):

        dec = 0
        i=0
        n=0
        while (binary != 0):

            decs = binary % 10

            decimal = dec + decs * pow(2, i)
            binary = binary // 10
            i += 1

        return (dec)

cachecycle=cid
def fetch():

    global cid,hlt_flag,iteration,cachecycle

    if cid==-1:
        return -1

    unit=find_unit(list_of_instn[cid][0])

    if unit=="HLT" :
            cachecycle=branch_id
            return cid


    if len(iq)!=0:
        return -1

    if len(rq)!=0:
        unit1 = find_unit(list_of_instn[rq[0]][0])
        if unit1=="BNE":
            return -1
    iq.append(cid)
    return cid



def find_unit(val):


    add1 = ["ADD.D", "SUB.D"]
    mul1 = ["MUL.D"]
    div1 = ["DIV.D"]
    data1 = ["L.D", "S.D", "LW", "SW"]
    unit = ""
    int1=["DADD","DADDI","DSUB","DSUBI","AND","ANDI","OR","ORI","LI","LUI"]


    if val.upper() in int1:
        unit="INTEGER"
    elif val.upper() in add1:
        unit="FP ADDER"
    elif val.upper() in mul1:
        unit="FP MULTIPLIER"
    elif val.upper() in div1:
        unit="FP DIVIDER"
    elif val.upper() in data1:
        unit="DATA"
    elif val.upper() == "BNE":
        unit="BNE"
    elif val.upper() == "HLT":
        unit="HLT"
    return unit

def if_reg_free(r1,id):
    if r1 not in reg_busy[0]:
        return True
    if r1 in reg_busy[0] and id<reg_busy[1][reg_busy[0].index(r1)]:
        return True
    return False

hlt_flag=0
def hlt():
    global list_of_instn, hlt_flag,iteration
    if hlt_flag==0 and iteration==0:
        hlt_flag=1
        iteration=1

    return


def issue():
    flag=0
    if len(iq)==0:
        return -1
    id=iq[0]

    unit=find_unit(list_of_instn[id][0])

    if unit == "BNE":
        iq.pop(0)
        rq.append(id)
        return id
    if list_of_instn[id][0].upper() in dest_reg:
        dest = list_of_instn[id][2]
    else:
        dest=list_of_instn[id][1]
    if dest in reg_busy[0]:
        result[7][id]='YES'
        flag=1


    if unit_status[1][unit_status[0].index(unit)]>0:
        if flag==1:
            return -1
        unit_status[1][unit_status[0].index(unit)] -= 1
        iq.pop(0)
        rq.append(id)
        dest=""

        return id
    else:
        result[8][id]='YES'
        return -1


def read1():
    if len(rq)==0:
        return -1
    for id in rq:

        unit=find_unit(list_of_instn[id][0])
        r1=list_of_instn[id][1]
        r2=list_of_instn[id][2]
        r3=""
        if len(list_of_instn[id])==4:
            r3=list_of_instn[id][3]
        if if_reg_free(r1,id) and if_reg_free(r2,id) and if_reg_free(r3,id):
            if unit!="BNE":
                eq.append(id)
                if list_of_instn[id][0].upper() in dest_reg:
                    dest = list_of_instn[id][len(list_of_instn[id])-1]
                else:
                    dest = list_of_instn[id][1]
                reg_busy[0].append(dest)
                reg_busy[1].append(id)
            rq.pop(rq.index(id))
            return id
        else:
            result[6][id]='YES'
    return -1

dcache=[[],[]]

dirtybit=[[0,0],[0,0]]


def dcache2(id):

    global dcache_flag
    val= list_of_instn[id][2]
    val=(val.split('('))
    reg=val[1].strip(')')
    val=int(val[0])
    c1=dict_reg[reg]+val
    c2=c1+4
    ind1=int(c1/16)
    ind2=int(c2/16)
    lat=0

    if list_of_instn[id][0]=='L.D' or list_of_instn[id][0]=='S.D':
        lat=2
    elif list_of_instn[id][0]=='LW' or list_of_instn[id][0]=='SW':
        lat=1
    if ind1 not in dcache[ind1%2]:

        if len(dcache[ind1%2])<2:
            dcache[ind1%2].append(ind1)
        else:
            if dirtybit[ind1%2][0]=='D':
                lat+=12
            dirtybit[ind1 % 2][0]=0
            dcache[ind1%2].pop(0)
            dcache[ind1%2].append(ind1)
        dcache_flag=1
        lat=lat+12
        return lat


    if ind1 in dcache[ind1%2]:
        if list_of_instn[id][0]=='S.D' or list_of_instn[id][0]=='SW' :
            dirtybit[ind1%2][dcache[ind1%2].index(ind1)]='D'

        if ind1==dcache[ind1%2][0] and len(dcache[ind1%2])==2:
            dcache[ind1%2][0],dcache[ind1%2][1]=dcache[ind1%2][1],dcache[ind1%2][0]
            dirtybit[ind1 % 2][0], dirtybit[ind1 % 2][1] = dirtybit[ind1 % 2][1], dirtybit[ind1 % 2][0]

    if ind2 not in dcache[ind2 % 2]:

        if len(dcache[ind2 % 2]) < 2:
            dcache[ind2 % 2].append(ind2)
        else:
            if dirtybit[ind2%2][0]=='D':
                lat+=12
            dirtybit[ind2 % 2][0]=0
            dcache[ind2 % 2].pop(0)
            dcache[ind2 % 2].append(ind2)
        lat = lat + 12
        dcache_flag=1

    if ind2 in dcache[ind2%2]:

        if list_of_instn[id][0]=='S.D' or list_of_instn[id][0]=='SW' :
            dirtybit[ind2%2][dcache[ind2%2].index(ind2)]='D'

        if ind2==dcache[ind2%2][0] and len(dcache[ind2%2])==2:
            dcache[ind2%2][0],dcache[ind2%2][1]=dcache[ind2%2][1],dcache[ind2%2][0]
            dirtybit[ind2 % 2][0],dirtybit[ind2 % 2][1]=dirtybit[ind2 % 2][1],dirtybit[ind2 % 2][0]

    return lat



dcache_flag=0
icache_flag=0

def exe(cc):
    global dcache_flag ,latency
    if len(eq)==0:
        return -1
    for id in range(len(eq)):

        unit=find_unit(list_of_instn[eq[id]][0])
        if unit=="BNE":
            latency[id]=1
        elif unit=="DATA":

                 if dcache_flag==0:
                    latency[id]=dcache2(eq[id])+stall_id

        else:
            latency[id]= unit_data[2][unit_data[0].index(unit)]

        if result[3][eq[id]]+latency[id]<=cc:
            latency[id]=0
            if unit!="BNE":
                wq.append(eq[id])
            re=eq.pop(id)

            return re
    return -1

def writeback():
    if len(wq)==0:
        return -1
    id=wq[0]

    wq.pop(0)
    return id

def cachecheck():

    if icache[int(cachecycle/len(icache))%len(icache)]!=int(cachecycle/len(icache)):

        return len(icache)*3
    else:
        return 0

def simulate():
    global cid,cacheflag,stall_id,dcache_flag,cachecycle

    for clock_cycle in range(1,500):

        flag=writeback()

        if flag!=-1:
            result[5][flag]=(clock_cycle)

        exe_var=exe(clock_cycle)

        if exe_var!=-1:
            if list_of_instn[exe_var][0]=='DADDI':
                dict_reg[list_of_instn[exe_var][1]] += int(list_of_instn[exe_var][3])

            if dcache_flag!=0 and (list_of_instn[exe_var][0]=='L.D' or list_of_instn[exe_var][0]=='S.D'):
                dcache_flag=0
            result[4][exe_var]=(clock_cycle)

        read_var = read1()
        if read_var!=-1:
            result[3][read_var]=(clock_cycle)
            if find_unit(list_of_instn[read_var][0]) == "BNE":
                if stall_id>0:
                    stall_id-=1
                continue

        issue_var=issue()
        if issue_var!=-1:
            result[2][issue_var]=(clock_cycle)

        if cacheflag==0:
            cacheflag=cachecheck()
            stall_id=cacheflag

        if stall_id!=0:

            icache_flag=1
            stall_id-=1

            if flag != -1:
                unit = find_unit(list_of_instn[flag][0])
                if unit == "HLT" or unit == "BNE":
                    continue
                unit_status[1][unit_status[0].index(unit)] += 1
                dest = ""
                if list_of_instn[flag][0].upper() in dest_reg:
                    dest = list_of_instn[flag][len(list_of_instn[flag]) - 1]
                else:
                    dest = list_of_instn[flag][1]
                reg_busy[1].pop(reg_busy[0].index(dest))
                reg_busy[0].pop(reg_busy[0].index(dest))

            continue

        if cacheflag>0 and stall_id==0:

            cacheflag=0
            icache_flag=0
            icache[int(cachecycle/len(icache))%len(icache)]=int(cachecycle/len(icache))

        fetch_var=fetch()
        if fetch_var!=-1:
            result[0][fetch_var]=(" ".join(list_of_instn[fetch_var]))
            result[1][fetch_var]=(clock_cycle)
            cid+=1
            cachecycle+=1

        if flag!=-1:
            unit = find_unit(list_of_instn[flag][0])
            if unit=="HLT" or unit=="BNE":
                continue
            unit_status[1][unit_status[0].index(unit)] += 1
            dest = ""
            if list_of_instn[flag][0].upper() in dest_reg:
                dest = list_of_instn[flag][len(list_of_instn[flag]) - 1]
            else:
                dest = list_of_instn[flag][1]
            reg_busy[1].pop(reg_busy[0].index(dest))
            reg_busy[0].pop(reg_busy[0].index(dest))

        if cid==-1 and len(iq)==0 and len(rq)==0 and len(eq)==0:
            break

        if cid==len(list_of_instn):
            cid=-1


def func_cache():
    global unit_data, icache

    icache = [-1 for i in range(unit_data[1][unit_data[0].index('I-CACHE')])]


def check_hazard():
    for i in range (len(result)):

        if i > 5:
            for j in range(len(result[i])):

                result[i][j]='NO'


if __name__ == '__main__':

    if len(sys.argv) != 5:
        print("\nError!! \nCorrect format to run: main.py inst.txt data.txt config.txt result.txt")
        exit()

    f_name1 = sys.argv[1]
    f_name2 = sys.argv[2]
    f_name3 = sys.argv[3]
    f_name4 = sys.argv[4]

    if f_name1.find(".txt") == -1 or f_name2.find(".txt") == -1 or f_name3.find(".txt") == -1 or f_name4.find(
            ".txt") == -1:
        print("\nError!! \nPlease make sure that you are entering file names as arguments! \nCorrect format: file_name.txt ")
        exit()

    instn_parser()
    config_parser()
    data_parser()
    func_cache()
    check_hazard()
    simulate()

    f = open(f_name4, "w")

    f.write("Instn\tFetch\tIssue\tRead\tExecute\tWrite Back\t RAW\t WAW\tStruct Hazard\n")

    for i in range(len(result[0])):

        if (result[0][i] == '0' or result[0][i] == 0):
            continue
        print(" ")
        for j in range(len(result)):
            if j == 6:
                f.write(str("\t"))
            f.write(str(result[j][i]) + "\t")
        f.write('\n')
    f.close()