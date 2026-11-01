# G1-TV3-01 – Analysis Environment

## 1. General Information

- **Project:** API Hashing Lab
- **Task ID:** G1-TV3-01
- **Member:** TV3
- **Role:** Dynamic Analysis & Memory Evidence
- **Phase:** 1 – Environment Setup and Initial Collection
- **Test Date:** 2026-10-31
- **Status:** Initial tool testing completed; evidence packaging pending

## 2. Virtual Machine Environment

| Component | Configuration |
|---|---|
| Hypervisor | VMware Workstation Pro 25H2 |
| Guest OS | Windows 11 x64 |
| Windows Build | 26100 (observed from PowerShell version) |
| RAM | 8 GB |
| CPU | 2 virtual processors |
| Virtual Disk | 80 GB |
| VMware Tools | Installed |
| Snapshot | Created (name to be confirmed) |
| Network Adapter | NAT during installation; isolation status to be confirmed |

The virtual machine is used to perform controlled runtime analysis. Network connectivity will be disabled before executing project samples.

## 3. Analysis Tools

### 3.1. Process Monitor (Procmon)

- **Developer:** Microsoft Sysinternals
- **Version:** To be updated
- **Purpose:** Collect file-system, Registry, process and thread activity.

**Test information:**

- Process: `powershell.exe`
- PID: `5400`
- Operation: `WriteFile`
- Result: `SUCCESS`
- Target: `C:\APIHashingLab\samples\test.txt`
- Offset: `0`
- Length: `11 bytes`
- Timestamp: `2026-10-31 08:23:30`

**Observed result:** Successfully captured a file-write operation performed by PowerShell.

**Limitation:** Procmon does not directly provide a complete trace of dynamic API resolution or API return addresses.

### 3.2. Process Explorer

- **Developer:** Microsoft Sysinternals
- **Version:** To be updated
- **Purpose:** Inspect running processes, process hierarchy and loaded modules.

**Test information:**

- Process: `powershell.exe`
- PID: `5400`
- Parent PID: `9028`
- Observed module: `kernel32.dll`
- Module path: `C:\Windows\System32\kernel32.dll`
- Module version: `10.0.26100.9444`
- Load address: `0x00007FFFF4080000`
- Architecture: x64

**Observed result:** Successfully inspected process information and the base address of a loaded DLL.

**Limitation:** Loaded-module information does not establish whether a particular API has been called.

### 3.3. x64dbg

- **Tool:** x64dbg
- **Version:** To be updated
- **Architecture:** x64
- **Purpose:** Debug process execution and inspect registers, memory and loaded modules.

**Test information:**

- Debugging session title: `qmodule-2.0-0.dll`
- Observed PID: `1320`
- Main thread ID: `6296`
- Observed module: `ntdll.dll`
- RIP: `0x00007FFFF554223A`
- Status: `Paused – System breakpoint reached`

**Observed result:**
- Opened a debugging session.
- Inspected CPU instructions and registers.
- Viewed the Memory Map.
- Observed a system breakpoint.

**Limitation:** API-resolution arguments, return addresses and subsequent API execution have not yet been collected for the project's B1/B2/P1 samples.

## 4. Preliminary Collection Results

| Observation | Status |
|---|---|
| Process information | Observed |
| Process ID and parent PID | Observed |
| Loaded DLL information | Observed |
| Module base address | Observed |
| File-system WriteFile event | Observed |
| Debugger breakpoint | Observed |
| Memory Map | Observed |
| API resolution trace | Not yet tested |
| Resolved API execution | Not yet tested |

## 5. Evidence Status

Screenshots of the preliminary tests are currently stored outside the repository and will be added later.

Planned evidence directory:

`evidence/G1/TV3/G1-TV3-01/`

Expected evidence:
- VMware configuration and snapshot screenshots
- Procmon WriteFile event screenshot
- Process Explorer process/module screenshots
- x64dbg CPU and Memory Map screenshots
- Native collector logs, when exported

No evidence files are claimed to be committed at this stage.

## 6. Next Steps

- Confirm the installed tool versions.
- Export and organize collector logs.
- Add screenshots and original logs to the evidence directory.
- Test collection procedures using B1 and B2.
- Document collector coverage and missing telemetry.

## 7. Conclusion

The initial Windows 11 analysis environment has been prepared, and Process Monitor, Process Explorer and x64dbg have been tested.

Preliminary process, module, file-system and debugger observations were obtained. Further collection is required to capture dynamic API resolution and establish links between resolved addresses and subsequent API calls.
