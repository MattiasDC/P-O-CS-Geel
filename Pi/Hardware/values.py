# -------------------------------- Core
delimiter = "#"                # Delimiter for the console lines
maximum_height = 200           # Maximum height of the zeppelin in cm

ground_height = 10             # Base height to hover over the ground (used to initialise the goal height and land)
extention = ".jpg"              # Extentions for the images

# -------------------------------- PID
pid_interval = 0.3

pid_error = 2.3                 # 1.95;0.12;3.2/ 3      -> Origineel
pid_integral = 1.2              # 2.3 1.2 5             -> goede
pid_derivative = 5              # 4 0.38 6
                                # 3.5 0.45 6            -> laatste test
pid_boundary = 100              # TODO nog te testen

# ------------------------------- Software PWM
software_frequency = 1.0               # Frequency of the duty cycle
#software_percentage_correction = (100 - minimal_cycle) / 10.0    # PWM percentual correction
power_ratio = 0.17                  # The ratio of the motor in backward/forward direction, used for calibrating
                                    # the turning

# ------------------------------- PWM Motor
frequency = 50                 # Frequency of the duty cycle
PWM_pin = 18                   # PWM pin
minimal_cycle = 15             # The minimal PWM the motor need to start spinning (13, 15 for safety)
percentage_correction = (100 - minimal_cycle) / 10.0    # PWM percentual correction

# ------------------------------- DistanceSensor
trig_duration = 0.0001         # Trigger duration
inttimeout = 2100              # Timeout on echo signal (NOT in ms)
v_snd = 340.29                 # Speed of sound in m/s
samples = 20                   # The number of samples taken to determine the height (mean)
interval = 0.5                 # Interval  of the amount of samples that are taken

echo_gpio = 22                 # = 15 on the pi
trig_gpio = 27                 # = 13 on the pi

# ------------------------------- Camera
cam_height = 500            # The camera resolution
cam_width = 666

# ------------------------------- Network
port = 10000                   # The port used in the connection

# ------------------------------- Server
host = '192.168.1.9'             #The ip-adress of the server
exchange = 'server'            #Name of the exchange used in the protocol
team = 'geel'                  #Name of the controlled zeppelin