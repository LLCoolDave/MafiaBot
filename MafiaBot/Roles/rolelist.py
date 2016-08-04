from .Goon import Goon
from .Civilian import Civilian
from .Prostitute import Prostitute
from .Medic import Medic
from .Cop import Cop
from .RoleCop import RoleCop
from .Jailer import Jailer
from .Vigilante import Vigilante
from .Tracker import Tracker
from .Watcher import Watcher
from .Sleepwalker import Sleepwalker
from .Oracle import Oracle
from .CorruptBureaucrat import CorruptBureaucrat
from .Bulletproof import Bulletproof
from .Gunsmith import Gunsmith
from .Armorsmith import Armorsmith
from .Alien import Alien
from .Nurse import Nurse
from .Santa import Santa
from .Fabricator import Fabricator
from .Inventor import Inventor
from .Traitor import Traitor
from .ParityCop import ParityCop

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
         'alien': Alien,
         'nurse': Nurse,
         'santa': Santa,
         'fabricator': Fabricator,
         'inventor': Inventor,
         'traitor': Traitor,
         'paritycop': ParityCop, 'parity cop': ParityCop}
