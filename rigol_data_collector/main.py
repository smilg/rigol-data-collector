import os
import tkinter as tk
from tkinter import filedialog
from tkinter import StringVar
from tkinter import ttk

from pyvisa import ResourceManager
from pyvisa.errors import InvalidSession

import util
from Rigol1000z import Rigol1000z
from Rigol1000z.constants import EWaveformMode

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        # self.parent.columnconfigure(0, weight=1)
        # self.parent.rowconfigure(0, weight=1)
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)
        
        self.parent = parent
        self.visa_name = None
        self.visa_backend = None
        self.visa_rsrc = None
        self.osc = None
        
        self.data_fpath = StringVar()
        self.data_fname = StringVar()
        self.scrshot_fpath = StringVar()
        self.scrshot_fname = StringVar()
        self.scope_connected = StringVar()
        self.scope_connected.set('Scope disconnected.')

        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)
        
        scope_lf = ttk.LabelFrame(self, text='Scope Connection')
        scope_lf.grid(row=0, column=0, padx=20, pady=20, sticky=tk.EW)
        ttk.Button(scope_lf, text='Connect scope', command=self.connect_scope).grid(column=0, row=0, sticky=tk.EW)
        ttk.Button(scope_lf, text='Disconnect scope', command=self.disconnect_scope).grid(column=0, row=1, sticky=tk.EW)
        ttk.Label(scope_lf, textvariable=self.scope_connected).grid(column=1, row=0, rowspan=2, sticky=tk.E, padx=20, pady=20)
        
        data_lf = ttk.LabelFrame(self, text='Save Data')
        data_lf.grid(column=0, row=1, padx=20, pady=20)
        
        scrshot_lf = ttk.LabelFrame(self, text='Save Screenshots')
        scrshot_lf.grid(column=0, row=2, columnspan=2, padx=20, pady=20)
        
        data_path_label = ttk.Label(data_lf, text='File path:')
        data_path_entry = ttk.Entry(data_lf, width=40, textvariable=self.data_fpath)
        data_path_choose_button = ttk.Button(data_lf, text='...', command=self.browse_data_path)
        data_fname_label = ttk.Label(data_lf, text='File name:')
        data_fname_entry = ttk.Entry(data_lf, width=40, textvariable=self.data_fname)
        data_save_btn = ttk.Button(data_lf, text='Save data', command=self.save_data)
        
        data_path_label.grid(column=0, row=0)
        data_path_entry.grid(column=1, row=0)
        data_path_choose_button.grid(column=2, row=0)
        data_fname_label.grid(column=0, row=1)
        data_fname_entry.grid(column=1, row=1)
        data_save_btn.grid(column=1, row=2)
        
        scrshot_path_label = ttk.Label(scrshot_lf, text='File path:')
        scrshot_path_entry = ttk.Entry(scrshot_lf, width=40, textvariable=self.scrshot_fpath)
        scrshot_path_choose_button = ttk.Button(scrshot_lf, text='...', command=self.browse_scrshot_path)
        scrshot_fname_label = ttk.Label(scrshot_lf, text='File name:')
        scrshot_fname_entry = ttk.Entry(scrshot_lf, width=40, textvariable=self.scrshot_fname)
        scrshot_save_btn = ttk.Button(scrshot_lf, text='Save screenshot', command=self.save_scrshot)
        
        scrshot_path_label.grid(column=0, row=0)
        scrshot_path_entry.grid(column=1, row=0)
        scrshot_path_choose_button.grid(column=2, row=0)
        scrshot_fname_label.grid(column=0, row=1)
        scrshot_fname_entry.grid(column=1, row=1)
        scrshot_save_btn.grid(column=1, row=2)
    
    def on_close(self):
        try:
            print("Checking if scope is connected...")
            self.visa_rsrc.session
            print("Disconnecting scope...")
            disconnect_scope()
        except:
            print("Scope already disconnected.")
        self.parent.destroy()
    
    def init_visas(self):
        visas = util.find_visas()
        try:
            self.visa_name, self.visa_backend = visas[0]
        except IndexError:
            tk.messagebox.showwarning(message="Couldn't find scope! Check USB connection.")
    
    def connect_scope(self):
        """Open the VISA resource to establish the communication channel."""
        if not self.check_scope_connected():
            if self.visa_name is None:
                self.init_visas()
            try:
                self.visa_rsrc = ResourceManager(self.visa_backend).open_resource(
                    self.visa_name
                )
                self.osc = Rigol1000z(self.visa_rsrc)
            except:
                tk.messagebox.showwarning(message="Error connecting to scope.")
        self.check_scope_connected()    # update scope connected text
    
    def disconnect_scope(self):
        """Close the VISA resource to terminate the communication channel."""
        if self.check_scope_connected():
            self.visa_rsrc.close()
            self.check_scope_connected()    # update scope connected text
        
    def check_scope_connected(self):
        try:
            self.visa_rsrc.session
            self.scope_connected.set("Scope connected.")
            return True
        except:
            self.scope_connected.set("Scope disconnected.")
            return False

    def browse_data_path(self):
        self.select_path('Select data save location', self.data_fpath)
        
    def browse_scrshot_path(self):
        self.select_path('Select screenshot save location', self.screenshot_fpath)
    
    def save_data(self):
        try:
            self.check_file_name(self.data_fpath, self.data_fname)
        except ValueError:
            return
        if self.check_scope_connected():
            self.osc.stop()
            full_path = os.path.join(self.data_fpath.get(), self.data_fname.get())
            if not full_path.endswith('.csv'):
                full_path = full_path + '.csv'
            self.osc.get_data(EWaveformMode.Raw, full_path)
        else:
            tk.messagebox.showwarning(message='Scope not connected!')
    
    def save_scrshot(self):
        try:
            self.check_file_name(self.data_fpath, self.data_fname)
        except ValueError:
            return
        if self.check_scope_connected():
            self.osc.stop()
            full_path = os.path.join(self.scrshot_fpath.get(), self.scrshot_fname.get())
            if not full_path.endswith('.png'):
                full_path = full_path + '.png'
            self.osc.get_screenshot(full_path)
        else:
            tk.messagebox.showwarning(message='Scope not connected!')

    def select_path(self, title: str, path_var: StringVar):
        path = filedialog.askdirectory(title=title, mustexist=True)
        if path == '':  # no path selected, do nothing
            return
        if os.access(path, os.W_OK):
            path_var.set(path)
        else:
            tk.messagebox.showwarning(message="Can't write to selected file path!")
    
    def check_file_name(self, path_var: StringVar, name_var: StringVar):
        if name_var.get() == '':
            tk.messagebox.showwarning(message='Choose a name for the file.')
            raise ValueError("Empty file name")
        full_name = os.path.join(path_var.get(), name_var.get())
        try:
            util.is_valid_folder_name(full_name)
        except ValueError as error:
            tk.messagebox.showwarning(message=error.message)
            raise ValueError("Invalid file or path name")
            
            
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title('Rigol Data Collection')
    MainApplication(root).grid(row=0, column=0, sticky=tk.NSEW)
    root.mainloop()
