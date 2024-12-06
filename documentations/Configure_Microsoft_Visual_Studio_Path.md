# Configure Microsoft Visual Studio Path

Here, we show how you can easily change the Microsoft Visual Studio Path so that Windows uses the correct version you want.
    
## Step 1: Locate System Environment Variables
Open up your environment variables. You can search "env" in the search tab, it should look something like this.
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151625223-18027e0a-1bb4-48f6-aacf-1afb5dd4fdcf.png" width="250">
</p>
Then open it. Then click "Environment Variables"
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151625750-dc5fc2ec-ef62-4f06-a87e-78c61f4dfc01.png" width="400">
</p>
Then it should open up a window like this
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151625921-57d87224-720e-44ab-9480-32e9a8b6f424.png" width="600">
</p>

## Step 2: Change System Paths
Scroll down and find `Path`, double click to open
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151627109-59345099-d736-44ac-b38c-37d61cb9e624.png" width="600">
</p>
You should see a pop up window like this
<p align="center">
   <img src="https://github.com/user-attachments/assets/2d51351d-d334-4218-809d-fbdb34317466" width="600">
</p>
Scroll down and see if your desired Microsoft Visual Studio path is inside here. For example, I saw my Microsoft Visual Studio Path has been added to `Path`
<p align="center">
   <img src="https://github.com/user-attachments/assets/1b8c8581-987e-4a6e-bacb-438ed2dbee80" width="600">
</p>

If there is no Microsoft Visual Studio path listed OR the listed path is not your desired version, try doing so:
<p align="center">
   <img src="https://github.com/user-attachments/assets/635d309d-7f84-4e3d-8896-7954d126129b" width="600">
</p>

Press ok and you may now close all the windows for environment variables & system properties.

## Step 3: Restart your computer (Optional)

⚠️ Note: We are not sure if this is a must, but we always restart. We just recommend doing so.

## Step 4: Check if succeed
Now please run `python setup.py develop` to setup OpenPCDet again. You should be able to resolve the error `unsupported Microsoft Visual Studio version! Only the versions between 2017 and 2022 (inclusive) are supported! The nvcc flag '-allow-unsupported-compiler' can be used to override this version check; however, using an unsupported host compiler may cause compilation failure or incorrect run time execution. Use at your own risk.`
