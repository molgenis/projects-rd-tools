
from rdtools.utils import print2
from rdtools.molgenis import Molgenis


db = Molgenis('https://david.gcc.rug.nl/api/')
db.login('admin', 'unit-CASTAWAY-unholy-bangle')

print2('Hello world')