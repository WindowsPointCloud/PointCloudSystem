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
Then it should open up a winodw like this
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151625921-57d87224-720e-44ab-9480-32e9a8b6f424.png" width="600">
</p>

## Step 2: Change System Variables
Double check on `CUDA_PATH` and this window should pop up
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151626793-e6ea1837-4547-44a7-b39c-7a63f078354d.png" width="600">
</p>
Then enter the target version of your CUDA there. In my case it's changing 11.6 to 11.3
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151626887-c7c239a2-3f06-4705-a242-511df611c16c.png" width="600">
</p>

Press ok and proceed next step.

## Step 3: Change System Paths
Scroll down and find `Path`, double click to open
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151627109-59345099-d736-44ac-b38c-37d61cb9e624.png" width="600">
</p>
You should see your current version on the very top. You going have to move your desired version to the very top
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151627505-f7fb27ba-86ef-415d-9f1c-cb666364ab45.png" width="600">
</p>
So it should look like this after moving
<p align="center">
   <img src="https://user-images.githubusercontent.com/29135514/151627544-0ec9dcce-6b13-4d34-b627-b530fd42aad2.png" width="600">
</p>
Press ok and you may now close all the windows for environment variables & system properties.

## Step 4: Restart your computer

⚠️ Note: The original tutorial did not mention this step, but we find that generally restarting the computer is necessary, especially if you have multiple CUDA versions!

## Step 5: Check if succeed
**Close** the last command prompt, and **open a new one**. Enter the following command:
```
nvcc --version
```
![image](https://user-images.githubusercontent.com/29135514/151627878-c6dddbab-adf6-4e79-b5cf-3dfb462b1e1d.png)

If it outputs your desired version, then you have succeed in swapping CUDA version.

## Acknowledgement

We want to thank [this repo](https://github.com/bycloudai/SwapCudaVersionWindows) for teaching how to swap CUDA Toolkit Versions on Windows with ease. The tutorial is so good, that we directly copy it to here. Thanks again for the contribution by the user `byCloudAI`.
