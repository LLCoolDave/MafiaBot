from .Gun import Gun
from .FakeGun import FakeGun
from .BulletproofVest import BulletproofVest
from .FakeVest import FakeVest
from .Syringe import Syringe
from .FakeSyringe import FakeSyringe
from .BackgroundCheck import BackgroundCheck
from .FakeBackgroundCheck import FakeBackgroundCheck
from .FakeBread import FakeBread
from .Probe import Probe

Items = {'gun': Gun,
         'fakegun': FakeGun, 'fake gun': FakeGun,
         'bulletproofvest': BulletproofVest, 'bulletproof vest': BulletproofVest, 'vest': BulletproofVest, 'bulletproof': BulletproofVest,
         'fakebulletproofvest': FakeVest, 'fake bulletproof vest': FakeVest, 'fakevest': FakeVest, 'fake vest': FakeVest, 'fakebulletproof': FakeVest, 'fake bulletproof': FakeVest,
         'syringe': Syringe,
         'fakesyringe': FakeSyringe, 'fake syringe': FakeSyringe,
         'backgroundcheck': BackgroundCheck, 'background check': BackgroundCheck, 'check': BackgroundCheck,
         'fakebackgroundcheck': FakeBackgroundCheck, 'fake background check': FakeBackgroundCheck, 'fakecheck': FakeBackgroundCheck, 'fake check': FakeBackgroundCheck,
         'fakebread': FakeBread, 'fake bread': FakeBread,
         'probe': Probe}
