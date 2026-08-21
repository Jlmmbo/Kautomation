"""
This is a script that will Launch a spaceplane from the SPH, and log telemetry data to a CSV file.

Requires kRPC to be running in KSP, and a save names [SAVE_NAME] to be loaded, with a spaceplane named [CRAFT_NAME].
Also requires the kRPC python library to be installed in the python environment:
pip install krpc
"""

import krpc
import csv
import time
import os
import sys


# ============================================================
# CONFIGURATION
# ============================================================

SAVE_NAME = "START"
CRAFT_NAME = "Test_Plane"

OUTPUT_DIR = "telemetry"

LOG_RATE = 5.0
SAMPLE_INTERVAL = 1.0 / LOG_RATE

# Log for this long (seconds) instead of detecting landing -
# takeoff bounces ("hops") would otherwise fake a landing and stop logging.
MAX_DURATION = 600.0

# Stop when the ship has been firmly grounded this long after taking off
# (crashes / crashed landings)
GROUNDED_STOP_TIME = 3.0


# ============================================================
# CONNECT
# ============================================================

print("Connecting to KSP...")

try:
    conn = krpc.connect(
        name="Autopilot Experiment",
        address="127.0.0.1",
        rpc_port=50000,
        stream_port=50001
    )
except Exception as e:
    print("Could not connect to kRPC.")
    print(e)
    sys.exit(1)

sc = conn.space_center
if sc is None:
    print("Could not connect to Space Center.")
    conn.close()
    sys.exit(1)

print("Connected.")


# ============================================================
# LOAD CLEAN SAVE
# ============================================================

print()
print("Loading clean save:", SAVE_NAME)

try:
    sc.load(SAVE_NAME)
    print("Save loaded.")
except Exception as e:
    print("Could not load save.")
    print(e)
    conn.close()
    sys.exit(1)


# Give KSP some time to finish changing scenes.
time.sleep(10)


# ============================================================
# CREATE WAYPOINT
# ============================================================

print()
print("Creating waypoint for KOS...")

try:
    kerbin = sc.bodies["Kerbin"]
    wp_mgr = sc.waypoint_manager
    waypoint = wp_mgr.add_waypoint(
        -0.1, -74.5, kerbin, "KOS Target"
    )
    waypoint.mean_altitude = 1500
    print("Waypoint created: KOS Target")
    print("  Lat:", waypoint.latitude)
    print("  Lon:", waypoint.longitude)
    print("  Alt:", waypoint.mean_altitude)
except Exception as e:
    print("Could not create waypoint.")
    print(e)
    print("The KOS script will try to find an existing waypoint.")


# ============================================================
# LAUNCH
# ============================================================

print()
print("Launching:", CRAFT_NAME)

try:
    sc.launch_vessel_from_sph(CRAFT_NAME)
except Exception as e:
    print("Could not launch vessel.")
    print(e)
    conn.close()
    sys.exit(1)


# ============================================================
# WAIT FOR VESSEL
# ============================================================

print("Waiting for vessel...")

vessel = None

for _ in range(200):

    try:
        vessel = sc.active_vessel

        if vessel is not None:
            break

    except Exception:
        pass

    time.sleep(0.1)


if vessel is None:

    print("Vessel did not appear.")

    conn.close()
    sys.exit(1)


print("Vessel:", vessel.name)


# ============================================================
# CREATE FLIGHT STREAMS
# ============================================================

flight = vessel.flight()

print("Creating telemetry streams...")


def make_stream(obj, attribute):

    stream = conn.add_stream(
        getattr,
        obj,
        attribute
    )

    stream.rate = LOG_RATE

    return stream


# ------------------------------------------------------------
# Flight
# ------------------------------------------------------------

altitude = make_stream(flight, "mean_altitude")
surface_altitude = make_stream(flight, "surface_altitude")
terrain_altitude = make_stream(flight, "bedrock_altitude")

speed = make_stream(flight, "speed")
vertical_speed = make_stream(flight, "vertical_speed")
horizontal_speed = make_stream(flight, "horizontal_speed")

true_air_speed = make_stream(flight, "true_air_speed")
equivalent_airspeed = make_stream(flight, "equivalent_air_speed")
#orbital_speed = make_stream(flight, "orbital_speed")
#orbital speed is not an actual attribute of the flight object.

pitch = make_stream(flight, "pitch")
heading = make_stream(flight, "heading")
roll = make_stream(flight, "roll")

mach = make_stream(flight, "mach")
angle_of_attack = make_stream(flight, "angle_of_attack")
sideslip_angle = make_stream(flight, "sideslip_angle")
g_force = make_stream(flight, "g_force")

latitude = make_stream(flight, "latitude")
longitude = make_stream(flight, "longitude")

atmosphere_density = make_stream(flight, "atmosphere_density")

static_pressure = make_stream(flight, "static_pressure")

dynamic_pressure = make_stream(flight, "dynamic_pressure")

#temperature = make_stream(flight, "temperature")
#temerature is not an actual attribute of the flight object.


#apoapsis = make_stream(flight, "apoapsis_altitude")

#periapsis = make_stream( flight, "periapsis_altitude")

#time_to_apoapsis = make_stream(flight, "time_to_apoapsis")

#time_to_periapsis = make_stream(flight, "time_to_periapsis")


# ------------------------------------------------------------
# Vessel
# ------------------------------------------------------------

mass = make_stream(vessel, "mass")
dry_mass = make_stream(vessel, "dry_mass")

thrust = make_stream(vessel, "thrust")
available_thrust = make_stream(vessel, "available_thrust")

max_thrust = make_stream(vessel, "max_thrust")

specific_impulse = make_stream(vessel, "specific_impulse")


# ------------------------------------------------------------
# Controls
# ------------------------------------------------------------

control = vessel.control

throttle = make_stream(control, "throttle")
pitch_input = make_stream(control, "pitch")
yaw_input = make_stream(control, "yaw")
roll_input = make_stream(control, "roll")

forward_input = make_stream(
    control,
    "forward"
)

right_input = make_stream(
    control,
    "right"
)

up_input = make_stream(
    control,
    "up"
)


# ------------------------------------------------------------
# Position / velocity
# ------------------------------------------------------------

body = vessel.orbit.body

position = conn.add_stream(
    vessel.position,
    body.reference_frame
)

velocity = conn.add_stream(
    vessel.velocity,
    body.reference_frame
)

angular_velocity = conn.add_stream(
    vessel.angular_velocity,
    vessel.surface_reference_frame
)

position.rate = LOG_RATE
velocity.rate = LOG_RATE
angular_velocity.rate = LOG_RATE


# ============================================================
# CSV
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

timestamp = time.strftime(
    "%Y%m%d_%H%M%S"
)

output_file = os.path.join(
    OUTPUT_DIR,
    f"flight_{timestamp}.csv"
)

print()
print("Logging at", LOG_RATE, "Hz")
print("Output:", output_file)
print()


headers = [

    "time",

    # Position
    "altitude",
    "surface_altitude",
    "terrain_altitude",
    "latitude",
    "longitude",

    # Velocity
    "speed",
    "vertical_speed",
    "horizontal_speed",
    "true_air_speed",
    "equivalent_air_speed",
    #"orbital_speed",

    # Rotation
    "pitch",
    "heading",
    "roll",

    # Rotation rates
    "pitch_rate",
    "heading_rate",
    "roll_rate",

    # Angular velocity
    "angular_velocity_x",
    "angular_velocity_y",
    "angular_velocity_z",

    # Aerodynamics
    "mach",
    "angle_of_attack",
    "sideslip_angle",
    "g_force",

    # Atmosphere
    "atmosphere_density",
    "static_pressure",
    "dynamic_pressure",
    #"temperature",

    # Orbit
    #"apoapsis",
    #"periapsis",
    #"time_to_apoapsis",
    #"time_to_periapsis",

    # Vessel
    "mass",
    "dry_mass",
    "thrust",
    "available_thrust",
    "max_thrust",
    "specific_impulse",

    # Controls
    "throttle",
    "pitch_input",
    "yaw_input",
    "roll_input",
    "forward_input",
    "right_input",
    "up_input",

    # Position vector
    "position_x",
    "position_y",
    "position_z",

    # Velocity vector
    "velocity_x",
    "velocity_y",
    "velocity_z",

    # Flight result
    "flight_status"
]


# ============================================================
# ANGLE DIFFERENCE
# ============================================================

def angle_difference(a, b):

    difference = a - b

    while difference > 180:
        difference -= 360

    while difference < -180:
        difference += 360

    return difference


# ============================================================
# LOGGING
# ============================================================

start_time = time.time()

previous_time = None

previous_pitch = None
previous_heading = None
previous_roll = None

flight_status = "flying"
has_flown = False
grounded_time = 0.0
last_situation = None
last_grounded_print = 0.0


print("Flight started.")


try:

    with open(
        output_file,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(headers)

        while True:

            loop_start = time.time()

            # ------------------------------------------------
            # Check whether vessel still exists
            # ------------------------------------------------

            try:

                vessel.name

                # The active vessel changing means the craft broke apart
                # (crashed) and the debris is now the active vessel.
                if sc.active_vessel != vessel:
                    raise Exception("active vessel changed")

            except Exception:

                flight_status = "destroyed"

                print()
                print("Vessel destroyed / no longer exists.")

                break


            # ------------------------------------------------
            # Time
            # ------------------------------------------------

            current_time = (
                time.time() - start_time
            )


            # ------------------------------------------------
            # Attitude
            # ------------------------------------------------

            current_pitch = pitch()
            current_heading = heading()
            current_roll = roll()


            # ------------------------------------------------
            # Rotation rates
            # ------------------------------------------------

            if previous_time is None:

                pitch_rate = 0.0
                heading_rate = 0.0
                roll_rate = 0.0

            else:

                dt = current_time - previous_time

                if dt > 0:

                    pitch_rate = (
                        angle_difference(
                            current_pitch,
                            previous_pitch
                        ) / dt
                    )

                    heading_rate = (
                        angle_difference(
                            current_heading,
                            previous_heading
                        ) / dt
                    )

                    roll_rate = (
                        angle_difference(
                            current_roll,
                            previous_roll
                        ) / dt
                    )

                else:

                    pitch_rate = 0.0
                    heading_rate = 0.0
                    roll_rate = 0.0


            previous_pitch = current_pitch
            previous_heading = current_heading
            previous_roll = current_roll

            previous_time = current_time


            # ------------------------------------------------
            # Vectors
            # ------------------------------------------------

            try:

                px, py, pz = position()

            except Exception:

                px = py = pz = 0.0


            try:

                vx, vy, vz = velocity()

            except Exception:

                vx = vy = vz = 0.0


            try:

                avx, avy, avz = angular_velocity()

            except Exception:

                avx = avy = avz = 0.0


            # ------------------------------------------------
            # Determine flight status
            # ------------------------------------------------

            # Stop on a crash: the ship must stay grounded for a while.
            # A takeoff "hop" only touches the runway briefly, so a
            # sustained-ground window won't falsely trigger.
            # Debris flickers between landed/flying while breaking apart,
            # so the grounded timer decays instead of hard-resetting.

            try:

                situation = vessel.situation

                situation_name = str(
                    situation
                ).lower()

            except Exception:

                # Reading the situation failing means the vessel is gone
                flight_status = "destroyed"
                print()
                print("Vessel destroyed / situation unavailable.")
                break

            if situation_name != last_situation:
                print(
                    "[{:.1f}s] situation: {}".format(
                        current_time, situation_name
                    )
                )
                last_situation = situation_name

            if (
                "destroyed" in situation_name
            ):

                flight_status = "destroyed"

                print()
                print("Flight ended:", flight_status)

                break

            if (
                "landed" in situation_name
                or "splashed" in situation_name
            ):

                if has_flown:

                    if previous_time is not None:
                        grounded_time += (
                            current_time - previous_time
                        )

                    if current_time - last_grounded_print > 0.5:
                        print(
                            "[{:.1f}s] grounded {:.1f}s / {:.1f}s"
                            .format(
                                current_time, grounded_time,
                                GROUNDED_STOP_TIME
                            )
                        )
                        last_grounded_print = current_time

                    if grounded_time >= GROUNDED_STOP_TIME:

                        flight_status = "landed"

                        print()
                        print("Flight ended:", flight_status)

                        break

                else:

                    grounded_time = 0.0

            elif (
                "flying" in situation_name
                or "orbit" in situation_name
                or "escap" in situation_name
            ):

                has_flown = True
                grounded_time *= 0.25

            else:

                # prelaunch and anything else on the ground: not a flight yet
                grounded_time = 0.0


            # ------------------------------------------------
            # Write row
            # ------------------------------------------------

            writer.writerow([

                current_time,

                # Position
                altitude(),
                surface_altitude(),
                terrain_altitude(),
                latitude(),
                longitude(),

                # Velocity
                speed(),
                vertical_speed(),
                horizontal_speed(),
                true_air_speed(),
                equivalent_airspeed(),
                #orbital_speed(),

                # Rotation
                current_pitch,
                current_heading,
                current_roll,

                # Rotation rates
                pitch_rate,
                heading_rate,
                roll_rate,

                # Angular velocity
                avx,
                avy,
                avz,

                # Aerodynamics
                mach(),
                angle_of_attack(),
                sideslip_angle(),
                g_force(),

                # Atmosphere
                atmosphere_density(),
                static_pressure(),
                dynamic_pressure(),
                #temperature(),

                # Orbit
                #apoapsis(),
                #periapsis(),
                #time_to_apoapsis(),
                #time_to_periapsis(),

                # Vessel
                mass(),
                dry_mass(),
                thrust(),
                available_thrust(),
                max_thrust(),
                specific_impulse(),

                # Controls
                throttle(),
                pitch_input(),
                yaw_input(),
                roll_input(),
                forward_input(),
                right_input(),
                up_input(),

                # Position vector
                px,
                py,
                pz,

                # Velocity vector
                vx,
                vy,
                vz,

                # Status
                flight_status
            ])


            file.flush()


            # ------------------------------------------------
            # Stop after the time limit
            # (landing is not used as a stop condition - a takeoff
            #  bounce would otherwise fake a landing)
            # ------------------------------------------------

            if current_time >= MAX_DURATION:

                flight_status = "duration_limit"

                print()
                print("Flight ended:", flight_status)

                break


            # ------------------------------------------------
            # Maintain 5 Hz
            # ------------------------------------------------

            elapsed = time.time() - loop_start

            remaining = (
                SAMPLE_INTERVAL - elapsed
            )

            if remaining > 0:

                time.sleep(remaining)


except KeyboardInterrupt:

    flight_status = "manually_stopped"

    print()
    print("Logging manually stopped.")


except Exception as e:

    flight_status = "error"

    print()
    print("Telemetry error:")
    print(e)


finally:

    try:
        conn.close()
    except Exception:
        pass


print()
print("========================================")
print("Experiment finished")
print("Status:", flight_status)
print("Telemetry:", output_file)
print("========================================")