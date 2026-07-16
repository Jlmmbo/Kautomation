# Kautomation

Kautomation contains kOS scripts for Kerbal Space Program automation, focused on automated ascent and orbit insertion.

## Files

- `equ_orbit.ks`
  Get into a (roughly) equatorial orbit of kerbin at a set apoapsis and periapsis (approximate).
- `pol_obt.ks`
  `equ_obt.ks`, except for a polar orbit.
- `plane_waypoint.ks`
  Get to the waypoint that is selected on the map, or the first one in the list if none is selected.

## Usage

1. Place the lib_ scripts in `dir/to/KSP/install/Ships/Script/` and the scripts you want to use in `dir/to/KSP/install/Ships/Script/boot`.
2. In the VAB/SPH, click on the KOS menu-> reread boot folder -> click on the KOS cpu -> scroll through the bootfiles to the selected script -> launch
3. Sit back and watch

## Notes

- Adjust flight parameters inside the script files to fit different rockets.
