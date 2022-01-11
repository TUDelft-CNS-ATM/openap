from openap import prop, FuelFlow, Emission, WRAP

available_acs = prop.available_aircraft(use_synonym=True)

for actype in available_acs:
    # print(actype)
    aircraft = prop.aircraft(ac=actype, use_synonym=True)
    wrap = WRAP(ac=actype, use_synonym=True)
    fuelflow = FuelFlow(ac=actype, use_synonym=True)
    emission = Emission(ac=actype, use_synonym=True)


available_acs = prop.available_aircraft(use_synonym=False)

for actype in available_acs:
    # print(actype)
    aircraft = prop.aircraft(ac=actype, use_synonym=False)
    wrap = WRAP(ac=actype, use_synonym=True)
    fuelflow = FuelFlow(ac=actype, use_synonym=True)
    emission = Emission(ac=actype, use_synonym=True)
