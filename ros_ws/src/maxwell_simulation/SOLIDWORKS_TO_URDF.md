# This is the documentation for the SOLIDWORKS_TO_URDF package.

This guide is being made from the Maxwell rover on a simplified model put together for this purpose (sole part of having the simplified model is to reduce the file size for easier sharing). The same steps can be applied to the full Maxwell rover model.

## Prerequisites
1. Have SolidWorks installed on your machine.
2. Get Setup with the model (I had to do this through the teams PDM system, but you may have the files directly).
3. Make sure that your Solidworks has the movement inside of solidworks that is desired in the simulation,

## Setting up the Solidworks URDF Exporter:
1. Go to the github here and and download the .exe
https://github.com/ros/solidworks_urdf_exporter/releases
- I had solidworks 2024, and I downloaded the 2021 version of the exporter, and it worked fine.

2. After running the .exe try to find it in a path like this as you probably need to add it to solidworks manually like I did:
- I had mine at this path, but here are some other options:
* C:\Program Files\SolidWorks Corp\SolidWorks\URDFExporter
* C:\Program Files\SolidWorks Corp\SolidWorks\addins\SW2URDF

3. Then at this path make sure you can find this file `SW2URDF.dll`

4. Manually Register the Add-in
We will use a Windows tool (RegAsm.exe) to force SolidWorks to recognize the file.
- Open Command Prompt as Administrator:

- Click your Start Menu and type cmd.

- You will see "Command Prompt". Right-click it and select "Run as administrator".

- Run the Registration Command:

- This add-in is a .NET program, so we need to use the .NET registration tool.

- Copy this entire command and paste it into your black command prompt window:
    C:\Windows\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe /codebase "FULL_PATH_TO_YOUR_DLL_FILE"

    **Before you press Enter: Replace the FULL_PATH_TO_YOUR_DLL_FILE part (including the quotes) with the full path you found in Step 1.**

Example: If your file was at C:\Program Files\SW2URDF\SW2URDF.dll, your final command will look like this:
`C:\Windows\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe /codebase "C:\Program Files\SW2URDF\SW2URDF.dll"`

* Press Enter. You should see a message like "Types registered successfully."

Then when you go into SolidWorks you should see the extension near the bottom of the tools tab



## Steps to Export URDF from SolidWorks

Important thing to note. There may be wayyy too much detail currently in our robot design, so their may need to be a new sort of robot model made to mock our robot, but not have the same detail as it currently does.


### Setting up Links and Joints: 
Watch this video starting at 12:30
https://www.youtube.com/watch?v=et6CEGqmudQ
