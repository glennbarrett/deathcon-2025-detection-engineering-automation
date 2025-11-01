# Workshop Lab Guide

## Initial Setup

1. Create a Windows 10 VM in Microsoft Azure. You can use a new Azure account to get trial credits or use a pre-existing Azure account. I recommend the ```Standard_D4s_v3 size``` and if you are not on a trial you should only need to pay for a couple of dollars a day of usage while you work on the workshop. You will need to be able to connect remotely, and by default the Azure VM setup will expose RDP and assign a public IP for you to do this. Feel free to use any other remote connectivity option you are comfortable with.
2. Download Git from https://git-scm.com/install/windows and install it on your Windows VM using the defaults.
3. Download Python from https://www.python.org/downloads/ and install it on your Windows VM. I recommend selecting to add python.exe to your PATH on install for this lab environment.
4. Open a command line and run ```pip install notebook ipykernel``` to ensure that you will be able to run Jupyter notebooks later in the workshop.
5. Download VS Code from https://code.visualstudio.com/ and install it on your Windows VM using the defaults. If you are already comfortable with git and python, you can install any text editor of your choice instead here. The workshop does not technically do anything that only VS Code can do.
6. Download Sysmon from https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon and install it on your Windows 10 VM using the default settings.
7. Download Splunk Enterprise from https://www.splunk.com/en_us/download/splunk-enterprise.html and install using the default settings on your Windows VM. You will need to create a Splunk account if you don’t have one already, but the download and usage is free.
8. Create an Ubuntu server VM in Azure. This can be a very small size VM, since we will only use it to host a lightweight web app with nginx. I recommend keeping the default of using certificate based authentication with SSH when you are setting up the VM.
9. Connect to the Ubuntu VM and run ```sudo apt install nginx npm nodejs``` followed by ```sudo ufw allow ‘Nginx HTTP’```
10. Install Angular on the Ubuntu VM by running ```sudo npm install -g @angular/cli```
11. Go ahead and shut down and stop this Ubuntu VM. You will not need it until the last section of the workshop.
12. Follow along from the beginning of the workshop YouTube video to set up some Splunk settings we will need inside your installed platform.

> IMPORTANT: The video will walk you through modifying the C:\Program Files\Splunk\etc\app\search\local\inputs.conf file. Here is the entry you will add:


```
[WinEventLog://Microsoft-Windows-Sysmon/Operational]
checkpointInterval = 5
current_only = 0
disabled = 0
index = winevent
start_from = oldest
```

## Main Sections
For the most part, you should be able to follow along with the workshop video, but I will include notes and links to code here for each section as necessary.



### Section 1 – Design and Creation of Custom Detections

In this section, you will run a command on the server, and then find that command in your Sysmon logs in Splunk. After that, you will set up a custom alert in Splunk to look for that command on a recurring basis.

> Note: I use index=main in this section of the video, but just make sure to use the index that you used when you set up your windows logging data feed earlier.


### Section 2 – Intro to MITRE ATT&CK

In this section, you will visit the MITRE ATT&CK webpage at https://attack.mitre.org/ and familiarize yourself with the Enterprise matrix and technique details.


### Section 3 – Detections-as-code Workflow

In this section, you will familiarize yourself with git by cloning a public repo from Github. I used https://github.com/glennbarrett/sigma but you can use any repo you want. We won’t be using the repo you download here; it is just to try out cloning and some git commands.

After the git intro, you will get logged into Azure DevOps at https://dev.azure.com/. This is a free service for up to 5 users, so you just need a Microsoft account to use it. If this is your first time accessing Azure DevOps, it may ask you to set up an organization. The name you use for this must be globally unique and will be used in your URL for the rest of this course, and the rest of the time you use Azure DevOps with that Microsoft account in general.

Once you have an organization, you will follow along with the video to set up a project and a repo in Azure DevOps, followed by setting up a repo-based wiki.


### Section 4 – Automating Detection Deployment

In this section, you will dive deeper into setting up Splunk alerts. This will include using the Splunk API to create alerts from python scripts. This will use the Splunk Python SDK that is on Github at https://github.com/splunk/splunk-sdk-python. You will not need to download this directly from Github, since the workshop video will show you to run ```pip install splunk-sdk``` to install it on your VM.

> IMPORTANT: At this time, please also run ```pip install beautifulsoup4 mistune```

In the workshop code repository, there is a Section-4 folder that has the Jupyter notebook ```testing.ipynb``` that is shown in the workshop video. You can open this notebook in VS Code to follow along. The other notebooks ```create_saved_search.ipynb``` and ```create_from_wiki.ipynb``` are also included for this section, in addition to the test custom detection markdown wiki file ```Generic-Ping-Command-Detection.md```

The python script for the final part of the section is also included as ```create_saved_search.py```


### Section 5 – Automating Detection Validation

In this section, you will learn to create and execute atomic test cases for your detections in an automated way.

> IMPORTANT: The video guide for this section refers to using powershell remoting to a separate target VM. For simplicity (and some cost savings if you aren’t on an Azure trial), in the workshop you can just run the commands locally on your Splunk workstation. I have included an amended version of the ```detection_test.py``` script from the video that simply omits the ComputerName call and runs the commands locally. In a real production environment, you will probably prefer the remote version so that you can set up a dedicated test case execution system on your network.

Follow along with the video to understand the validation test case creation and execution process. There are two other files in the Section-5 folder in the workshop code repo. They are:

```extract_test_case.py``` – Python script to extract test cases and execute them.

```Generic-Ping-Command-Detection.md``` – Same file from Section 4, includes test case.


### Section 6 – Tying Automations Together with a CI/CD Pipeline

In this section, you will learn to roll the automations we’ve built into a pipeline that runs from your git repository, so that the alert creation and validation execution are performed automatically when changes to the repository are detected.

You will follow along with the workshop video to install an agent on your Windows VM that will allow the pipeline to execute its commands on the VM directly.

The Section-6 folder in the workshop code repository includes the ```azure-pipelines.yml``` file which holds the configuration for the pipeline in this section. You can create this yourself by following along with the video, but I wanted to make sure you have a final version to use or at least compare against. The folder also includes ```process_updates.py``` which effectively combines all the python automations we have created so far into a single script to use in the pipeline.

I have also included the success and failure test cases from the video as ```test-failure-case.md``` and ```test-success-case.md```


### Section 7 – Track Detection Coverage with MITRE ATT&CK

Go ahead and spin up the Ubuntu VM that you set up in Azure that is running nginx. You will need it for this section.

You will start this section by reviewing and familiarizing yourself with the official hosted version of the MITRE ATT&CK Navigator app at https://mitre-attack.github.io/attack-navigator/.

The application code is hosted on GitHub at https://github.com/mitre-attack/attack-navigator You will need to clone or download this repository to your Ubuntu VM.

> IMPORTANT: Before proceeding with this section in the videos, please setup the Navigator web app to run on your Ubuntu VM by following these steps:

1. Delete files in ```/var/www/html``` on your Ubuntu VM.
2. Run ```ng build``` from within the nav-app directory where you downloaded the Navigator repo to your Ubuntu VM.
3. After the build completes, copy the files from ```nav-app/dist/``` to ```/var/www/html``` on your Ubuntu VM.
4. From your Windows VM where you are running Splunk, navigate to the IP of your Ubuntu VM in the web browser, and confirm that the ATT&CK Navigator loads properly.
5. In your Ubuntu VM, copy the ```layer.json``` file from the Section-7 directory of the workshop code repo into ```/var/www/html/assets```
6. In the ```config.json``` file in ```/var/www/html/assets/``` change the ```default_layers``` section to have ```assets/layer.json``` in the urls list. This is shown in the workshop video if you want to confirm syntax.

The other code file that is included in the Section-7 directory of the workshop repo is ```attack.py``` which handles the parsing of the detection wiki files and updating of the Navigator layer files in the pipeline. There are also several copies of detection markdown files with different techniques listed included so that they can be used to simulate realistic population of the layer scoring.

From here, please proceed with the workshop videos from the section to follow along with the rest of the configuration, including setting up an SSH service connection from the pipeline to your Ubuntu VM. In the Section-7 directory of the workshop code repo, I have also included an updated version of the ```azure-pipelines.yml``` file. In this file, you may need to change the name of your SSH endpoint based on how you configure your service connection.


### Questions/Issues

If you run into any snags or have any questions or just want to discuss the topics or use cases further, please reach out in the discord channel for the workshop.
