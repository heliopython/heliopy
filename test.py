from sunpy.net import Fido
import heliopy.net
import heliopy.net.attrs as a
from heliopy.net.mms import MMSClient

query = a.Time('2018-11-01', '2018-11-01 01:00:00') & a.Source('MMS') & a.Version('2.0.3')
res = Fido.search(query)
print(res)
Fido.fetch(res)
