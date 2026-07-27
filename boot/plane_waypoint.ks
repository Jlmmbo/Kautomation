


// Set these to your desired values
set tgt_alt to 12500.
set pitch_fact to 0.0007.// how many degrees to pitch per meter of altitude difference.
set steering_damp to 0.1. // how slow to turn


//////////////////////////////////////////////////////////////////////////////////////////////////////////

function clamp{
    parameter mn.
    parameter mx.
    parameter val.

    return(max(min(val,mx),mn)).
}

function get_pitch{
    return clamp(-5,(tgt_alt-ship:altitude)*pitch_fact,10).
}

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
print "Takeoff".

lock steering to heading(90,20).

wait until ship:altitude > tgt_alt * 0.10.

set wpoint to allWaypoints()[0].
for wp in allWaypoints(){
    if wp:isselected{
        SET wpoint TO wp.
        BREAK.
    }
}


clearscreen.
print "Name: " + wpoint:name.
print "Heading: " + wpoint:geoposition:heading.
print "Distance: " + wpoint:geoposition:distance.
print "Target Altitude: " + tgt_alt.
set pitchPID to pidloop(pitch_fact, pitch_fact/10, pitch_fact/10, -5, 10).
set pitchPID:setpoint to tgt_alt.

lock steering to heading((wpoint:geoposition:heading * steering_damp + MOD(360 - latlng(90,0):Bearing, 360) * (1 - steering_damp)),
    pitchPID:update(time:seconds, ship:altitude)).

until wpoint:geoposition:distance < .1 {
    set t to wpoint:geoposition:distance / ship:airspeed.

    print "ETA to "+ wpoint:name + ": " + floor(t/3600) + "h " + floor(t/60) + "m " + floor(t) + "s".

}

print "Arrived at " + wpoint:name.