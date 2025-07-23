import os
import platform

class SystemModule:
    def get_system_info(self):
        """Obtiene información del sistema"""
        try:
            return {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        except Exception as e:
            print(f"Error obteniendo info del sistema: {e}")
            return {}

    def shutdown_pc(self):
        """Apaga el sistema"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /t 1")
            else:
                os.system("shutdown -h now")
            return True
        except Exception as e:
            print(f"Error apagando sistema: {e}")
            return False