from Goon import Goon
from Civilian import Civilian
from Prostitute import Prostitute
from Medic import Medic
from Cop import Cop
from RoleCop import RoleCop
from Jailer import Jailer
from Vigilante import Vigilante
from Tracker import Tracker
from Watcher import Watcher
from Sleepwalker import Sleepwalker
from Oracle import Oracle
from CorruptBureaucrat import CorruptBureaucrat
from Bulletproof import Bulletproof
from Gunsmith import Gunsmith
from Armorsmith import Armorsmith
from Alien import Alien

Roles = {'goon': Goon,
         'civilian': Civilian, 'vt': Civilian, 'townie': Civilian,
         'prostitute': Prostitute, 'drunk': Prostitute, 'roleblocker': Prostitute, 'roleblock': Prostitute,
         'medic': Medic, 'doctor': Medic,
         'cop': Cop,
         'rolecop': RoleCop, 'role cop': RoleCop,
         'jailer': Jailer,
         'vigilante': Vigilante, 'vig': Vigilante,
         'tracker': Tracker,
         'watcher': Watcher,
         'sleepwalker': Sleepwalker,
         'oracle': Oracle,
         'corruptbureaucrat': CorruptBureaucrat, 'corrupt bureaucrat': CorruptBureaucrat, 'bureaucrat': CorruptBureaucrat,
         'bulletproof': Bulletproof,
         'gun smith': Gunsmith, 'gunsmith': Gunsmith,
         'armor smith': Armorsmith, 'armorsmith': Armorsmith,
         'alien': Alien}
