set AP to 60.
set PE to 35.
//set ap_alt to 13143021.
//set pe_alt to 12976722.
set ap_alt to 70000.
set pe_alt to 70000.
set t_aggression to .1.


//////////////////////////////////////////////////////////////////////////////////////////////////////////


//import necessary libs
copypath("0:/lib_fuel.ks", "1:/lib_fuel.ks").
run "lib_fuel.ks".


wait until ship:unpacked.

clearscreen.

set mythrottle to 1.
lock throttle to mythrottle.

print "Countdown".

from {local countdown is 5.} until countdown = 0 step {set countdown to countdown - 1.} do {
    print countdown.
    wait 1.
}
stage.
print "Liftoff".

SAS ON.
set sasmode to "stability".

until ship:altitude > 1000 {
    checkfuel().
    wait .1.
}

print "Initiating turn".
sas off.
lock steering to heading(345,70).

until ship:altitude > 5000 {
    checkfuel().
    wait .1.
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