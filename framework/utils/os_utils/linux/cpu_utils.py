class CpuUtil:

    @staticmethod
    def get_core_count(platform_obj):
        output,error,exit_staus = platform_obj.exec_cmd("nproc","ssh")
        return output,error,exit_staus
      
    @staticmethod
    def get_cpu_info(platform_obj):
        output,error,exit_staus = platform_obj.exec_cmd("lscpu","ssh")
        return output,error,exit_staus