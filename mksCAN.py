import can
import time

class Motor:
    def __init__(self, name, bus, version, can_id, mode='serial-vfoc', set_default=True, *args, **kwargs):
        self.name = name
        self.bus = bus
        self.version = self.set_version(version)
        self.can_id = self.set_can_id(can_id)
        self.mode = self.set_mode(mode)
        self.end_limit = False

        if set_default:
            self.set_defaults()
            
    def set_defaults(self):
        if 'vfoc' not in self.mode:
            self.set_holding_current(0.5)

        if 'pulse' in self.mode:
            self.set_motor_direction(0)

        self.set_microstepping(16)
        self.set_en_level('low')
        self.set_screen_auto_turnoff(0)
        self.set_locked_rotor_protection(0)
        self.set_mplyer(1)
        self.set_can_rate(500000)
        self.set_can_rsp(1)
        self.set_zero_mode('disable')
        self.set_zero_speed(2)
        self.set_zero_direction(0)
        self.set_home_trigger_high(0)
        self.set_home_direction(0)
        self.use_home_limit_switch(1)
        self.use_endstop_limit(0)

    def add_crc(data: list) -> list:
        crc = sum(data)
        crc = 0xFF & crc
        return data.append(crc)

    def calibrate(self):
        data = [self.can_id, 0x80, 00]
        msg = can.Message(dlc=len(data), data=self.add_crc(data))
        bus.send(msg)
        return True

    def set_version(self, version: str):
        VERSIONS = {
            '42D': [1600, 3000, 800],
            '57D': [3200, 5200, 400],
            '28D': [600,  3000, 200],
            '35D': [800,  3000, 200],
        }

        if version.lower() not in map(str.lower, VERSIONS.keys()):
            raise ValueError(f'The only MKS Servo versions supported are {", ".join(VERSIONS)}')

        self.version = version
        self.ma = VERSIONS[version][0]
        self.max_ma = VERSIONS[version][1]
        self.home_ma = VERSIONS[version][2]
        
        return version

    def set_can_id(self, can_id) -> None:
        if 0x00 < can_id < 0x800: 
            if self.can_id:
                can.Message(data=[self.can_id, ])
            self.can_id = can_id
        else:
            raise ValueError('The CAN ID must be between 0 and 2047 or 0x800.')

    def set_mode(self, mode):
        MODES = [
            'pulse-open',
            'pulse-close',
            'pulse-vfoc',
            'serial-open',
            'serial-close',
            'serial-vfoc',
        ]

        if mode not in MODES:
            raise ValueError(f'The only supported modes are {", ".join(MODES)}')

        if 'open' in mode:
            self.max_rpm = 400
        if 'close' in mode:
            self.max_rpm = 1500
        if 'vfoc' in mode:
            self.max_rpm = 3000

        return mode
            

    def read_params(self, mode='addition'):
        MODES = [
            'addition',
            'carry',
        ]
        if mode not in MODES:
            raise ValueError(f'The only allowed modes are {", ".join(MODES)}')

        pass

    def set_working_current(self, ma):
        if ma > self.max_ma:
            raise ValueError(f'The MKS Servo{self.version} can only have a maximum working current of {self.max_ma} mA.')
        
        self.ma = ma

    def set_holding_current(self, hold_ma):
        if 'vfoc' in self.mode:
            raise TypeError(f'Cannot set holding current for {self.mode} mode.')
        
        self.hold_ma = hold_ma

    def set_microstepping(self, mstep):
        if 0 > mstep > 256:
            raise ValueError('Microstepping is only allowed between 1-256 subdivisions.')
        
        self.mstep = mstep

    def set_en_level(self, en_level):
        EN_LEVELS = [
            'high', 'low', 'hold'
        ]

        if en_level not in EN_LEVELS:
            raise ValueError(f'The only EN levels supported are {", ".join(EN_LEVELS)}.')
        
        self.set_en_level = en_level


    # for pulse interface
    def set_motor_direction(self, dir: bool):
        ''' 
        If True: CCW

        '''

        if "pulse" not in self.mode:
            raise ValueError("Cannot set motor direction for other modes except pulse.")
            
        self.motor_direction = dir

    def set_screen_auto_turnoff(self, auto: bool):
        self.screen_auto_turnoff = auto

    def is_oled_auto_turnoff(self):
        return self.screen_auto_turnoff

    def set_locked_rotor_protection(self, protect: bool):
        self.locked_rotor_protection = protect

    def is_locked_rotor_protection(self):
        return self.locked_rotor_protection

    def set_mplyer(self, mplyer: bool):
        self.mplyer = mplyer

    def is_mplyer_enabled(self):
        return self.mplyer

    def set_can_rate(self, can_rate):
        CAN_RATES = [
            125e3, 250e3, 500e3, 1e6
        ]

        if can_rate not in CAN_RATES:
            raise ValueError(f'The only CAN rates supported are {", ".join(CAN_RATES)}.')

    def set_can_id(self, can_id):
        if 0x00 < can_id < 0x800: 
            self.can_id = can_id
        else:
            raise ValueError('The CAN ID must be between 0 and 2047.')

    def set_can_rsp(self, can_rsp: bool):
        self.can_rsp = can_rsp

    def is_can_rsp_enabled(self):
        return self.can_rsp

    def set_zero_mode(self, mode):
        MODES = [
            'disable', 'direction', 'near'
        ]

        if mode not in MODES:
            raise ValueError(f'The mode only supported are {", ".join(MODES)}.')
        
        self.zero_mode = mode

    def set_zero_at_boot(self, set: bool):
        if self.zero_mode == 'disable':
            raise PermissionError('Cannot set zero position if zero mode is disabled.')
        self.zero_at_boot = set

    def set_zero_speed(self, speed: int):
        if speed in range(0, 5):
            self.zero_speed = speed
            return
        
        raise ValueError('Speed must be set between 0-4.')

    def set_zero_direction(self, dir: bool):
        self.zero_direction = dir

    def set_home_trigger_high(self, trigger: bool):
        self.home_trigger = trigger
        pass

    def is_home_trigger_high(self):
        return self.home_trigger

    def set_home_direction(self, dir: bool):
        
        self.home_direction = dir

    def use_home_limit_switch(self, use_limit_switch: bool):
        self.home_limit_switch = use_limit_switch

    def is_home_limit_switch_enabled(self):
        return self.home_limit_switch

    def set_home_current(self, ma):
        if not self.is_home_limit_switch_enabled():
            raise PermissionError('Cannot adjust home current if no home limit switch is used.')
        self.home_ma = ma

    def go_home(self):
        pass

    def use_endstop_limit(self, end_limit: bool):
        if not self.end_limit:
            self.go_home()
        self.end_limit = end_limit

    def is_end_limit_enabled(self):
        return self.end_limit

    def restore(self):
        self.calibrate()
        pass

    def show_params(self):
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                print(attr, ":", getattr(self, attr))


    # Commands

    def turn(self, amount, direction, velocity, acceleration, type='absolute'):
        data = bytearray([self.can_id, ])
        msg = can.Message()