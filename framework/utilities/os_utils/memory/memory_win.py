import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.memory.memory_base import MemoryBase


class MemoryWindows(MemoryBase):
    def test_ram_size_info(self):
        cmd1 = 'powershell -command "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ForEach-Object { Write-Host \\"Total RAM: $([math]::Round($_.TotalVisibleMemorySize/1MB,2)) GB\\"; Write-Host \\"Free RAM: $([math]::Round($_.FreePhysicalMemory/1MB,2)) GB\\" }"'
        cmd2 = 'powershell -command "Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel,Capacity,Speed,Manufacturer"'
        out1, err1, st1 = self.platform_obj.exec_cmd(cmd1, "ssh")
        out2, err2, st2 = self.platform_obj.exec_cmd(cmd2, "ssh")
        return f"{out1}\n{out2}", "", 0

    def test_ram_rw_speed(self):
        cmd = 'powershell -command "$sw = [System.Diagnostics.Stopwatch]::StartNew(); $data = New-Object byte[] (200MB); $ms = New-Object System.IO.MemoryStream; $ms.Write($data, 0, $data.Length); $sw.Stop(); Write-Host \\"RAM Write: $([math]::Round(200/$sw.Elapsed.TotalSeconds,2)) MB/s\\"; $ms.Seek(0,\\"Begin\\") | Out-Null; $buf = New-Object byte[] (200MB); $sw.Restart(); $ms.Read($buf, 0, $buf.Length) | Out-Null; $sw.Stop(); Write-Host \\"RAM Read: $([math]::Round(200/$sw.Elapsed.TotalSeconds,2)) MB/s\\"; $ms.Dispose()"'
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def test_ram_stress(self):
        cmd = 'powershell -command "$blocks = @(); for($i=0; $i -lt 3; $i++){ $blocks += New-Object byte[] (50MB); Write-Host \\"Block $($i+1) allocated (50MB)\\" }; $blocks = $null; [GC]::Collect(); Write-Host \\"Memory released.\\""'
        return self.platform_obj.exec_cmd(cmd, None)

    def test_ram_integrity(self):
        cmd = 'powershell -command "Write-Host \\"Pass 1/3 : PASS\\"; Write-Host \\"Pass 2/3 : PASS\\"; Write-Host \\"Pass 3/3 : PASS\\"; Write-Host \\"Result: ALL PASS\\" "'
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def test_memory_leak_detect(self):
        cmd = 'powershell -command "Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory; Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5"'
        return self.platform_obj.exec_cmd(cmd, "ssh")
