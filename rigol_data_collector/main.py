import os
from typing import Callable
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import StringVar
from tkinter import ttk

from pyvisa import ResourceManager
import matplotlib.pyplot as plt
from pandas import read_csv

import util
from pathcheck_so import is_path_exists_or_creatable
from Rigol1000z import Rigol1000z
from Rigol1000z.constants import EWaveformMode


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.osc = None
        self.visa_name, self.visa_backend = "", ""

        # variables to store user input
        self.data_fpath = StringVar()
        self.data_fname = StringVar()
        self.scrshot_fpath = StringVar()
        self.scrshot_fname = StringVar()

        # variables to store status text
        self.scope_connected = StringVar()
        self.scope_connected.set("Scope disconnected.")  # default value
        self.data_save_time = StringVar()
        self.scrshot_save_time = StringVar()

        # callback to disconnect scope before window closes
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)

        # frame for scope connection buttons and status text
        scope_lf = ttk.LabelFrame(self, text="Scope Connection")
        scope_lf.grid(row=0, column=0, padx=20, pady=20, sticky=tk.EW)
        ttk.Button(scope_lf, text="Connect scope", command=self.connect_scope).grid(
            column=0, row=0, sticky=tk.EW
        )
        ttk.Button(
            scope_lf, text="Disconnect scope", command=self.disconnect_scope
        ).grid(column=0, row=1, sticky=tk.EW)
        # save status label so it can be manually updated
        self.scope_status_label = ttk.Label(scope_lf, textvariable=self.scope_connected)
        self.scope_status_label.grid(
            column=1, row=0, rowspan=2, sticky=tk.E, padx=20, pady=20
        )

        # frame for exporting data
        self.create_file_save_frame(
            1,
            0,
            "Save Data",
            "Save data",
            self.data_fpath,
            self.data_fname,
            self.data_save_time,
            self.browse_data_path,
            self.save_data,
        )

        # frame for plotting data previews
        plot_lf = ttk.LabelFrame(self, text="Plot Data")
        plot_lf.grid(row=2, column=0, padx=20, pady=20, sticky=tk.EW)
        # this doesn't work properly in a for loop and I don't feeling like troubleshooting it
        ttk.Button(
            plot_lf,
            text=f"Plot CH1 data",
            command=lambda: self.plot(1),
        ).grid(column=0, row=0, sticky=tk.EW)
        ttk.Button(
            plot_lf,
            text=f"Plot CH2 data",
            command=lambda: self.plot(2),
        ).grid(column=1, row=0, sticky=tk.EW)
        ttk.Button(
            plot_lf,
            text=f"Plot CH3 data",
            command=lambda: self.plot(3),
        ).grid(column=2, row=0, sticky=tk.EW)
        ttk.Button(
            plot_lf,
            text=f"Plot CH4 data",
            command=lambda: self.plot(4),
        ).grid(column=3, row=0, sticky=tk.EW)

        # frame for exporting screenshots
        self.create_file_save_frame(
            3,
            0,
            "Save Screenshots",
            "Save screenshot",
            self.scrshot_fpath,
            self.scrshot_fname,
            self.scrshot_save_time,
            self.browse_scrshot_path,
            self.save_scrshot,
        )

    def plot(self, channel: int) -> None:
        """
        Plots the data from the specified channel from the currently selected data file.
        Assumes the file is in the format created by this program (i.e. headers are Time, CH1-4)

        Args:
            channel (int): The channel number to plot (1-4).
        """
        # make sure the data file exists; tell the user if it doesn't
        full_path = util.add_extension_if_needed(
            os.path.join(self.data_fpath.get(), self.data_fname.get()), ".csv"
        )
        if not os.path.isfile(full_path):
            messagebox.showwarning(message="The specified data file doesn't exist!")
            return
        data = read_csv(full_path)  # read in the data
        # select the figure dedicated to the chosen channel and clear it
        plt.figure(channel, clear=True)
        # plot and label the data
        plt.plot(data["Time"], data[f"CH{channel}"])
        plt.title(f"{self.data_fname.get()}: CH{channel}")
        plt.xlabel("Time [s]")
        plt.ylabel(f"CH{channel} [V]")
        plt.show()

    def create_file_save_frame(
        self,
        row: int,
        column: int,
        frame_label: str,
        save_button_text: str,
        path_var: StringVar,
        name_var: StringVar,
        status_var: StringVar,
        browse_func: Callable,
        save_func: Callable,
    ):
        """
        Create a LabelFrame in the GUI containing widgets for inputting a file path
        and name, a button for saving a file, and text to display when a file was
        last saved.

        Args:
            row (int): Row of the parent element's grid for the frame to be placed.
            column (int): Column of the parent element's grid for the frame to be placed.
            frame_label (str): Title text for the LabelFrame.
            path_var (StringVar): tk StringVar to contain the selected file path.
            name_var (StringVar): tk StringVar to contain the selected file name.
            status_var (StringVar): tk StringVar to contain some status information
                about the last saved file.
            browse_func (Callable): Callback for browsing directories ('...' button)
                to select a file path.
            save_func (Callable): Callback for saving a file. (Save file button)
        """
        # LabelFrame to contain other widgets
        lf = ttk.LabelFrame(self, text=frame_label)
        lf.grid(row=row, column=column, padx=20, pady=20)

        # file path input label and text entry
        ttk.Label(lf, text="File path:").grid(column=0, row=0)
        ttk.Entry(lf, width=40, textvariable=path_var).grid(column=1, row=0)
        # button to browse directories
        ttk.Button(lf, text="...", command=browse_func).grid(column=2, row=0)

        # file name input label and text entry
        ttk.Label(lf, text="File name:").grid(column=0, row=1)
        ttk.Entry(lf, width=40, textvariable=name_var).grid(column=1, row=1)

        # save button and status text
        ttk.Button(lf, text=save_button_text, command=save_func).grid(column=1, row=2)
        ttk.Label(lf, textvariable=status_var).grid(column=2, row=2)

    def on_close(self) -> None:
        """
        Called when the window is closed to disconnect the scope before closing.
        """
        self.disconnect_scope()
        self.parent.destroy()

    def connect_scope(self) -> None:
        """
        Open the VISA resource to establish the communication channel.
        """
        self.scope_connected.set("Connecting to scope...")
        self.scope_status_label.update()
        if not self.check_scope_connected():
            if self.visa_name == "":
                visas = util.find_visas()
                try:
                    self.visa_name, self.visa_backend = visas[0]
                except IndexError:
                    self.visa_name, self.visa_backend = ("", "")
            try:
                self.visa_rsrc = ResourceManager(self.visa_backend).open_resource(
                    self.visa_name
                )
                self.osc = Rigol1000z(self.visa_rsrc)
            except:
                messagebox.showwarning(
                    message="Error connecting to scope. Check USB connection."
                )
        self.check_scope_connected()  # update scope connected text

    def disconnect_scope(self) -> None:
        """
        Close the VISA resource to terminate the communication channel.
        """
        if self.check_scope_connected():
            self.visa_rsrc.close()
            self.check_scope_connected()  # update scope connected text

    def check_scope_connected(self) -> bool:
        """
        Checks if a scope VISA resource is open.

        Returns:
            bool: Returns true if a scope is connected, false otherwise.
        """
        try:
            self.visa_rsrc.session
            self.scope_connected.set("Scope connected.")
            return True
        except:
            self.scope_connected.set("Scope disconnected.")
            return False

    def browse_data_path(self) -> None:
        """
        Calls select_path with proper arguments for data path selection.
        """
        self.select_path("Select data save location", self.data_fpath)

    def browse_scrshot_path(self) -> None:
        """
        Calls select_path with proper arguments for screenshot path selection.
        """
        self.select_path("Select screenshot save location", self.scrshot_fpath)

    def save_data(self) -> None:
        """
        Calls save_file with proper arguments for data saving.
        """
        try:
            self.save_file(
                ".csv",
                self.data_fpath,
                self.data_fname,
                self.data_save_time,
                self.osc.get_data,  # type:ignore
                leading_args=[EWaveformMode.Raw],
            )
        except:
            messagebox.showwarning(
                message="Couldn't save data! Is the scope connected?"
            )

    def save_scrshot(self) -> None:
        """
        Calls save_file with proper arguments for screenshot saving.
        """
        try:
            self.save_file(
                ".png",
                self.scrshot_fpath,
                self.scrshot_fname,
                self.scrshot_save_time,
                self.osc.get_screenshot,  # type:ignore
            )
        except:
            messagebox.showwarning(
                message="Couldn't save screenshot! Is the scope connected?"
            )

    def save_file(
        self,
        extension: str,
        path_var: StringVar,
        name_var: StringVar,
        status_var: StringVar,
        save_func: Callable,
        leading_args=[],
    ) -> None:
        """
        Saves a file after checking that the path is available and the scope is connected.

        Shows a warning dialog if no scope is connected or if the chosen path can't be used.
        Otherwise, it calls save_func and updates the provided status_var with the current time.

        Args:
            extension (str): File extension to use for the saved file.
            path_var (StringVar): tk StringVar containing path to save file to.
            name_var (StringVar): tk StringVar containing desired name of the file.
            status_var (StringVar): tk StringVar to write a status message to.
            save_func (Callable): Function to call in order to save the file.
                It is passed any arguments from leading_args followed by the file path.
            leading_args (list, optional): Arguments to precede the file path in save_func.
                Defaults to [].
        """
        if self.check_scope_connected():
            self.osc.stop()  # stop scope collection so it can be read  # type:ignore
            full_path = util.add_extension_if_needed(
                os.path.join(path_var.get(), name_var.get()), extension
            )
            # if the file exists already, confirm whether it should be overwritten
            if os.path.isfile(full_path) and not messagebox.askokcancel(
                message="A file already exists with the specified name and location. \
                Would you like to overwrite it?"
            ):
                return  # don't save the file if it isn't ok to overwrite
            if not is_path_exists_or_creatable(full_path):
                messagebox.showwarning(
                    message="Chosen file path is invalid or inaccessible."
                )
                return
            # save the file
            save_func(*leading_args, full_path)
            # update the status message with the name of the saved file and the current time
            status_var.set(
                f'{self.scrshot_fname.get()} saved at {datetime.now().strftime("%H:%M:%S")}'
            )
        else:
            messagebox.showwarning(message="Scope not connected!")

    def select_path(self, title: str, path_var: StringVar) -> None:
        """
        Opens a dialog to select a directory, and updates a StringVar with the path selected.
        If the path isn't write-accessible, a warning dialog appears and path_var is not
        updated. If no path is selected, path_var is not updated.

        Args:
            title (str): Window title of the dialog.
            path_var (StringVar): tk StringVar to be updated with the selected path.
        """
        path = filedialog.askdirectory(title=title, mustexist=True)
        if path == "":  # no path selected, do nothing
            return
        if is_path_exists_or_creatable(path):
            path_var.set(path)
        else:
            messagebox.showwarning(
                message="Chosen file path is invalid or inaccessible."
            )


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title("Rigol Data Collection")
    MainApplication(root).grid(row=0, column=0, sticky=tk.NSEW)
    root.mainloop()
