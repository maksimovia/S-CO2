import modules
from sqlite import open_db, close_db, read_block, write_stream, read_stream
import prop

##Реактор
Tin_hot = 540
Tout_hot = 400
P_hot = 0.155
fluid_hot = 'Pb'
cp_hot = 0.148
G_hot = 33835

##Входной поток
fluid = 'CO2'
P = 28
p_out = 8
x = 0.9

##Настройки цикла
root_tolerance = 10**-4 #
cycle_tolerance = 10**-5 #
h_steps = 20 #

##Холодный источник
fluid_cond = 'WATER'
Tcond = 32
Tfcond = 15
Pcond = 0.15

#Теплообменники и турб
dt_RHE = 10
dt_C = 5
dt_HTR = 5
dt_LTR = 5

KPD_T = 0.9
KPD_MC = 0.9
KPD_RC = 0.9


open_db()
write_stream('R-RHE',Tin_hot,P_hot,Tin_hot*cp_hot,0,0, G_hot,fluid_hot)
write_stream('HTR-RHE',Tout_hot-dt_RHE,P,prop.t_p(Tout_hot-dt_RHE,P,fluid)['H'],prop.t_p(Tout_hot-dt_RHE,P,fluid)['S'],prop.t_p(Tout_hot-dt_RHE,P, fluid)['Q'], 1000,fluid)

RHE = modules.RHE('R-RHE', 'RHE-R', 'HTR-RHE', 'RHE-T', Tout_hot, dt_RHE, root_tolerance, h_steps)
HTR = modules.HTR('T-HTR', 'HTR-LTR', 'MIX-HTR', 'HTR-RHE', dt_HTR, root_tolerance, h_steps)
LTR = modules.LTR('HTR-LTR', 'LTR-SPLIT', 'MC-LTR', 'LTR-MIX', dt_LTR, root_tolerance, h_steps)
MC = modules.MC('C-MC', 'MC-LTR', P, KPD_MC)
RC = modules.RC('SPLIT-RC', 'RC-MIX', P, KPD_RC)
T = modules.Turb('RHE-T', 'T-HTR', p_out, KPD_T)
C = modules.C('SPLIT-C', 'C-MC', 'IN-C', 'C-OUT', Tcond, dt_C, root_tolerance, h_steps)
MIX = modules.MIX('LTR-MIX', 'RC-MIX', 'MIX-HTR')
SPLIT = modules.SPLIT('LTR-SPLIT', 'SPLIT-C', 'SPLIT-RC', x)

for j in range(9999):
    RHE.calc()
    T.calc()
    if j == 0:
        write_stream('HTR-LTR',read_stream('T-HTR')['T'],read_stream('T-HTR')['P'],read_stream('T-HTR')['H'],read_stream('T-HTR')['S'],read_stream('T-HTR')['Q'],read_stream('T-HTR')['G'], read_stream('T-HTR')['X'])
        write_stream('LTR-SPLIT',read_stream('T-HTR')['T'],read_stream('T-HTR')['P'],read_stream('T-HTR')['H'],read_stream('T-HTR')['S'],read_stream('T-HTR')['Q'],read_stream('T-HTR')['G'], read_stream('T-HTR')['X'])
    else:
        HTR.calc()
        LTR.calc()
    SPLIT.calc()
    write_stream('IN-C',Tcond,Pcond,prop.t_p(Tfcond,Pcond, fluid_cond)['H'],prop.t_p(Tfcond,Pcond,fluid_cond)['S'],0, 1000,fluid_cond)
    C.calc()
    MC.calc()
    RC.calc()
    LTR.calc()
    MIX.calc()
    HTR.calc()
    balance = abs(read_block('RHE')["Q"] + read_block('MC')["Q"] + read_block('RC')["Q"] - read_block('T')["Q"] - read_block('C')["Q"]) / read_block('RHE')["Q"]
    print(balance)
    if balance < cycle_tolerance:
        break
KPD = (read_block('T')["Q"] - read_block('MC')["Q"] - read_block('RC')["Q"])/read_block('RHE')["Q"]
print('KPD:',KPD)
close_db()