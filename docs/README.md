# Network Visualizer

Network Visualizer is a open-source tool that allows everyone - not just security professionals - to visualize their computers network connections. Additional methods are in development to mitigate malicious activity from unwanted network connections. Network Visualizer compliments existing security methods and will grow in sophistication over time. <br><br><br>

<p align="center">
  <img src="gifs/Network-Visualizer.gif" alt="animated" />
</p>
<br>

<br>

# Donate

Network Visualizer is 100% funded through donations — which is none so far at the time of this writing. 🙃 <br> 

Your donation would facilitate the development of open source tools to serve you. Send me an email (TinkeringEngr at protonmail.com) with a screenshot of your donation; I would like to attribute those who are supporting the work. Thank you!
<br>

Venmo<br>
https://account.venmo.com/u/TinkeringEngr

BTC Wallet<br>
bc1qy5ejsgsslgag32ddzjww3mrkwsr9v5avx9swz2

ADA Wallet<br>
addr1q9vhvts97guem5njwqwlwnhd5lajacqdegqn93nhayz78zjewchqtu3enhf8yuqa7a8wmflm9msqmjspxtr806g9uw9q8vz0xn

XRP Wallet<br>
rwgWYtUfVRL92aTquMiXqeUBqTfYxmhcSc

If your crypto of choice isn't listed, please let me know.

<br><br>

# Download (64-bit)

Run with administrator privileges -- future changes will be forthcoming regarding elevated privileges.

## Linux

[Network-Visualizer-Linux.zip](https://downloads.sourceforge.net/project/network-visualizer/Network-Visualizer-Linux.zip?ts=gAAAAABjLmlLIfIPNXxGNgQ1jQ1SWPJB4bjfyIXvqFXXrH7CBvp6No2yc38H1wNgqYn2RL-QlToP15fEPvlIj-GFo-XXAWBUKg%3D%3D&r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fnetwork-visualizer%2Ffiles%2FNetwork-Visualizer-Linux.zip%2Fdownload)

## Windows

[Network-Visualizer-Windows.zip](https://downloads.sourceforge.net/project/network-visualizer/Network-Visualizer-Windows.zip?ts=gAAAAABjLnSsw9T2IhLWJBSkgb_2oRuw_n49g8SQgj-BPaq0-3MYdUKnmIXXnP_56pazmVNtvzzv_XeTzdMmHmDjgsCFBRv9ZQ%3D%3D&r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fnetwork-visualizer%2Ffiles%2FNetwork-Visualizer-Windows.zip%2Fdownload)

## MacOS

[Network-Visualizer-Mac.dmg](https://downloads.sourceforge.net/project/network-visualizer/Network-Visualizer-Mac.dmg?ts=gAAAAABjLl-NFofsI-_9d0wx6Xb2N-3-FxRAf3a9fBRJitxoa9lPPUt-aRws6INdRWuOpaawU2xaiQJU_Mp9fffrKJms5HF-nA%3D%3D&r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fnetwork-visualizer%2Ffiles%2FNetwork-Visualizer-Mac.dmg%2Fdownload)

<br><br>
If there is a problem, search [github issues](https://github.com/TinkeringEngr/Network-Visualizer/issues) for the resolution and if not, please submit a github issue with as much detail as possible to replicate/diagnose the issue. 
<br><br><br>


# Running Source Code From Terminal
<br>

1.  `Install Python3` <br>
     <br>I use Python version 3.9.6 — your results may vary. <br><br>


## Linux & MacOS
<br>

2.  `git clone https://github.com/TinkeringEngr/Network-Visualizer.git` <br>
3.  `pip install -r requirements.txt` <br><br>

If the computer gods have smiled upon you, run the program with administrator privileges <br> `sudo python network_visualizer.py` <br>

If there is a problem, search [github issues](https://github.com/TinkeringEngr/Network-Visualizer/issues) for the resolution and if not, please submit a github issue with as much detail as possible to replicate/diagnose the issue. <br><br>

## Windows
<br>

Be sure Microsoft Visual C++ 14.0 or higher is installed and Python is linked to it (i.e. add Python and Python/Scripts to the PATH variable) <br><br>

2.  `git clone https://github.com/TinkeringEngr/Network-Visualizer.git` <br>
3.   Delete pcapy-ng from the requirements.txt file <br>
4.  `pip install -r requirements.txt` <br>
5.  Download [Npcap SDK 1.12](https://npcap.com/dist/npcap-sdk-1.12.zip)
6.  Install pcapy-ng with the Npcap SDK files linked explicitly.  Like the following example:<br><br> `pip install pcapy-ng --global-option=build_ext --global-option="-LC:\PATH\TO\npcap-sdk-1.12\Lib\x64" --global-option="-IC:\PATH\TO\npcap-sdk-1.12\Include\pcap"` <br><br>

If the computer gods have smiled upon you, run the program with administrator privileges<br> `python network_visualizer.py` <br><br>

If there is a problem, search [github issues](https://github.com/TinkeringEngr/Network-Visualizer/issues) for the resolution and if not, please submit a github issue with as much detail as possible to replicate/diagnose the issue. 
