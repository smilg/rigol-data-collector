# rigol-data-collector

This is a Python (3.11) app used to collect data from Rigol DS1000Z series oscilloscopes. Most of the code for interacting with the scope is from [AlexZettler](https://github.com/AlexZettler/Rigol1000z/tree/master) on GitHub. I made a few changes to their code to make it work. I also used some code from [amosborne](https://github.com/amosborne/rigol-ds1000z/tree/main) for visa stuff.

I don't guarantee that this program will work at all for anyone else, but I don't see why it shouldn't. If you find problems, feel free to submit a PR, but note that I don't plan on actively maintaining this.

## preparing for use

To use this project, first clone the repository and enter the root directory of the cloned repo.

This project was only tested with Python 3.11. It may work with other versions of Python 3, but YMMV. You may need to install the NI-VISA driver to communicate with the scope, but try it without first. [You can find it here](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html). If you have [Poetry](https://python-poetry.org/), run `poetry install --only main` to get the required dependencies. If you don't have Poetry, you can run `pip install -r requirements.txt` to install the dependencies.

If you're on Linux, you may need to reload udev rules after installing the VISA library (pyvisa-py, ni-visa, or similar). You can do this by logging out and back in or restarting your computer (see [issue #1](https://github.com/smilg/rigol-data-collector/issues/1#issue-2180666499)). Depending on your distro, there may be ways to do this without relogging or restarting.

## using

To run the app, run the script `./rigol_data_collector/main.py`. If you're using Poetry, you can do this with `poetry run python ./rigol_data_collector/main.py`. Otherwise, run the file in whatever way is appropriate based on how you installed the dependencies.

When opened, you should see something like the window shown below:

![Screenshot of the project's GUI](ui.png)

Connect the USB cable to the oscilloscope, then click on "Connect scope". The scope is disconnected automatically when closing the window.

To save data, add the path to the directory where the data should be saved to the text box labelled "File path". You can press the button next to that text box to select a directory using a GUI.

Input the desired name of the data file in the box labelled "File name". The program will automatically add the .csv extension if you don't. To save data to the selected location, click "Save data". After you've saved data, you can preview it using the plot buttons. These will plot data from the file indicated by the text entries (in the "Save Data" section). Note that if you change the headers of the selected csv, the plot buttons won't work.

Saving a screenshot of the oscilloscope works almost identically. Screenshots are saved as `.png` files. (The scope and library support other formats, but I left it as the default.)

If you need to communicate with the scope from a different program, you can release the VISA resource by clicking "Disconnect scope". It can be reconnected using the "Connect scope" button.

## problems?

If you try to run the script and get the error "`No module called tkinter`" or similar, you need to install tkinter. Installing it through pip will not work. If you're on Windows, you need to re-run the Python installer and make sure the box "tcl/tk and IDLE" is checked in the Optional Features screen. If you're on Linux, you can use your package manager (e.g. for Ubuntu, `sudo apt-get install python3-tk`). If you're on MacOS, you can install it with brew: `brew install python-tk`.
