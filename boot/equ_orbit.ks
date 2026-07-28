

// Set these to your desired values
set AP to 60. //seconds to apoapsis for adjusting apoapsis
set PE to 35. //seconds to apoapsis for adjusting periapsis
set ap_alt to 70000.
set pe_alt to 70000.
set t_aggression to .1. //how aggressive to stick to the target Ap/Pe ETA


//////////////////////////////////////////////////////////////////////////////////////////////////////////


//import necessary libs
copypath("0:/lib_fuel.ks", "1:/lib_fuel.ks").
run "lib_fuel.ks".

wait until ship:unpacked.

clearscreen.

set mythrottle to 0.
lock throttle to mythrottle.

print "Countdown".

from {local countdown is 10.} until countdown = 0 step {set countdown to countdown - 1.} do {
    print countdown.
    wait 1.
}
stage.
set mythrottle to 1.
print "Liftoff".

SAS ON.

until ship:airspeed > 200 {
    checkfuel().
    wait .1.
}

print "Initiating turn".
sas off.
lock steering to heading(90,70).

until ship:obt:eta:apoapsis > 35 {
    checkfuel().
    wait .5.
}
print "Heading prograde until apoapsis above " + ap_alt/1000 + "km".
unlock steering.
sas on.
wait .2.
set sasmode to "PROGRADE".


until ship:apoapsis > ap_alt {// set apoapsis
    checkfuel().
    if ship:obt:eta:apoapsis < AP-1 {
        checkfuel().
        if mythrottle<1{
            set mythrottle to (AP-ship:obt:eta:apoapsis)*t_aggression.
        }
        if mythrottle>1{
            set mythrottle to 1.
        }
        wait .001.
    }
    if ship:obt:eta:apoapsis > AP+1 {
        set mythrottle to 0.
    }
}
print "Apoapsis is above " + ap_alt/1000 + "km".
print "Waiting until ETA to Apoapsis is " + PE + "s before
heading prograde until periapsis is " + pe_alt/1000 + "km".
unlock steering.
sas on.
wait .1.
set sasmode to "PROGRADE".

until ship:periapsis > pe_alt {// set periapsis
    checkfuel().
    if ship:obt:eta:apoapsis < PE-1 {
        checkfuel().
        if mythrottle<1{
            set mythrottle to (PE-ship:obt:eta:apoapsis)*t_aggression.
        }
        if mythrottle>1{
            set mythrottle to 1.
        }
        wait .001.
    }
    if ship:obt:eta:apoapsis > PE+1 {
        set mythrottle to 0.
    }
}
print "Pe is above 70km".

deletepath("boot/equ_orbit.ks").