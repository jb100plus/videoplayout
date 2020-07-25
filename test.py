from PunktumFiles import PunktumFiles


pf = PunktumFiles()

print(pf.getFilesNeeded())
print(pf.relativeTage)

pf.deleteOldFiles()

