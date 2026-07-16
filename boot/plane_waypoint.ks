


// Set these to your desired values
set tgt_alt to 12500.
set pitch_fact to 0.0007.// how many degrees to pitch per meter of altitude difference.


//////////////////////////////////////////////////////////////////////////////////////////////////////////

function get_heading{
    parameter wp is waypoint.

    //set theta to arctan((wp:geoposition:lat - ship:latitude) / (wp:geoposition:lng - ship:longitude))/constant:pi/2*360+90.
    return wp:geoposition:heading.

    //return theta.
}

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

wait until ship:altitude > tgt_alt * 0.90.

set wpoint to allWaypoints()[0].
for wp in allWaypoints(){
    if wp:isselected{
        SET wpoint TO wp.
        BREAK.
    }
}


set w_point_dist to sqrt((ship:latitude - wpoint:geoposition:lat)^2 + (ship:longitude - wpoint:geoposition:lng)^2).

clearscreen.
print "Name: " + wpoint:name.
print "Heading: " + get_heading(wpoint).
print "Distance: " + w_point_dist.
print "Target Altitude: " + tgt_alt.

lock steering to heading(get_heading(wpoint),get_pitch()).

until w_point_dist < .1 {
    set w_point_dist to sqrt((ship:latitude - wpoint:geoposition:lat)^2 + (ship:longitude - wpoint:geoposition:lng)^2).

    set t to w_point_dist / ship:airspeed.

    print "ETA to "+ wpoint:name + ": " + floor(t/3600) + "h " + floor(t/60) + "m " + floor(t) + "s".
}

print "Arrived at " + wpoint:name.