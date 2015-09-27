from Goon import Goon
from Civilian import Civilian
from Prostitute import Prostitute
from Medic import Medic
from Cop import Cop
from RoleCop import RoleCop
from Jailer import Jailer
from Vigilante import Vigilante

Roles = {'goon': Goon,
         'civilian': Civilian, 'vt': Civilian, 'townie': Civilian,
         'prostitute': Prostitute, 'drunk': Prostitute, 'roleblocker': Prostitute, 'roleblock': Prostitute,
         'medic': Medic, 'doctor': Medic,
         'cop': Cop,
         'rolecop': RoleCop, 'role cop': RoleCop,
         'jailer': Jailer,
         'vigilante': Vigilante, 'vig': Vigilante}
