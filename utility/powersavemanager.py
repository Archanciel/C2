import subprocess
import re

class PowerSaveManager:
    def getPowerSaveModeNormalUID(self):
        powerSaveModeLst = str(subprocess.check_output('powercfg /L')).split('\\r\\n')
        powerSaveModeNormal = [x for x in powerSaveModeLst if 'normal' in x]
        return re.match(r".* (.*-.*-.*-.*-.* ) .*", powerSaveModeNormal[0]).group(1)

    def deactivatePowerSaveOptions(self):
        subprocess.call("powercfg /change standby-timeout-ac 0")
        subprocess.call("powercfg /change standby-timeout-dc 0")
        subprocess.call("powercfg /change hibernate-timeout-ac 0")
        subprocess.call("powercfg /change hibernate-timeout-dc 0")

    def reactivateNormalPowerSaveMode(self):
        subprocess.call("powercfg /change standby-timeout-ac 10")
        subprocess.call("powercfg /change standby-timeout-dc 5")
        subprocess.call("powercfg /change hibernate-timeout-ac 10")
        subprocess.call("powercfg /change hibernate-timeout-dc 5")

p = PowerSaveManager()
p.deactivatePowerSaveOptions()
p.reactivateNormalPowerSaveMode()
