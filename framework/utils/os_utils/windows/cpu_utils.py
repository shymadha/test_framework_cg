class CpuUtil:

    @staticmethod
    def get_core_count(platform_obj):
        output,error,exit_status = platform_obj.exec_cmd("wmic cpu get NumberOfCore")
        return output,error,exit_status


    @staticmethod
    def get_cpu_info(platform_obj):
        output,error,exit_status = platform_obj.exec_cmd("wmic cpu get name")
        return output,error,exit_status