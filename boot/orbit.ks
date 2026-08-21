

// Set these to your desired values
set AP to 60. //seconds to apoapsis for adjusting apoapsis
set PE to 35. //seconds to apoapsis for adjusting periapsis
set ap_alt to 70000.
set pe_alt to 70000.
set t_aggression to .1. //how aggressive to stick to the target Ap/Pe ETA
set turn_heading to 90. // direction to turn to after launch (0 is north, 90 is east, 180 is south, -90 is west)


//////////////////////////////////////////////////////////////////////////////////////////////////////////

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
when ship:stagedeltav(ship:stagenum):current = 0 then{
    stage.
    return true.
}

SAS ON.

until ship:airspeed > 200 {
    wait .1.
}

print "Initiating turn".
sas off.
lock steering to heading(turn_heading,70).

until ship:obt:eta:apoapsis > 35 {
    wait .5.
}
print "Heading prograde until apoapsis above " + ap_alt/1000 + "km".
unlock steering.
sas on.
wait .2.
set sasmode to "PROGRADE".


until ship:apoapsis > ap_alt {// set apoapsis
    if ship:obt:eta:apoapsis < AP-1 {
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
    if ship:obt:eta:apoapsis < PE-1 {
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

deletepath("boot/orbit.ks").