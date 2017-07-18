#	title		: LS-DYNA queue submittor
#	author		: Esther Liu
#	revision	: 170413 1st draft
#                         170420 add output path
#                         170509 add default selection of listbox
#                         170511 add "os.chdir"
#                                change to queue submittrt
#	Acknowledgement	: Milo Chen for coding help

import tkinter as tk
import subprocess
import os
from tkinter.filedialog import askopenfilename
from tkinter import *
from tkinter import messagebox

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.label_text = StringVar()
        self.label_text.set("")
        self.label_dir = StringVar()
        self.label_dir.set("")
        self.v1 = IntVar()
        self.v2 = StringVar()
        self.memory = StringVar()
        self.memory = "200"
        self.flag_run = IntVar()
        self.flag_run = 0
        self.ncpu = StringVar()
        self.ncpu = "0"
        self.pack()
        self.create_widgets()

    def create_widgets(self):

        frame1 = Frame(self)
        frame1.grid(row = 1, column = 1)
        frame2 = Frame(self)
        frame2.grid(row = 2, column = 1)
        frame3 = Frame(self)
        frame3.grid(row = 2, column = 2)
        frame4 = Frame(self)
        frame4.grid(row = 3, column = 1)
        frame5 = Frame(self)
        frame5.grid(row = 4, column = 1)
        frame6 = Frame(self)
        frame6.grid(row = 5, column = 1)

	# get input deck path
        self.lbl_openfile = tk.Label(frame1, text="choose input deck")
        self.openfile = tk.Button(frame1, text="file", command=self.openfilediag)
        self.lbl_openfile.grid(row = 1, column = 1)
        self.openfile.grid(row = 1, column = 2)

        # push job button
        self.pushjob =  tk.Button(frame3, text="Push job", command = self.pushjob)
        self.pushjob.grid(row = 1, column = 2)

	# run button
        self.printfile = tk.Button(frame3, text="RUN", command = self.run)
        self.printfile.grid(row = 2, column = 2)

	# show input deck path
        self.showfilename = tk.Label(frame1,text = "")
        self.showfilename.grid(row = 3, column = 1)

	# quit the job submitter
        self.quit = tk.Button(frame3, text="QUIT JS", fg="red",command=root.destroy)
        self.quit.grid(row = 3, column = 2)

        # stop the process
        #self.quit = tk.Button(frame3, text="STOP dyna", fg="blue",command=self.kill)
        #self.quit.grid(row = 3, column = 2)

        self.lbl_memory = tk.Label(frame5, text = "memory size")
        self.m1 = tk.Radiobutton(frame5, text="200MB", variable = self.v2, value = 200)
        self.m2 = tk.Radiobutton(frame5, text="400MB", variable = self.v2, value = 400)
        self.m3 = tk.Radiobutton(frame5, text="600MB", variable = self.v2, value = 600)
        self.m4 = tk.Radiobutton(frame5, text="1,000MB", variable = self.v2, value = 1000)
        self.lbl_memory.grid(row = 1, column = 2)
        self.m1.grid(row = 2, column = 2)
        self.m2.grid(row = 3, column = 2)
        self.m3.grid(row = 4, column = 2)
        self.m4.grid(row = 5, column = 2)


	# list box for the number of CPU
        self.lbl_listbox1 = tk.Label(frame2, text="CPU number")
        self.listbox1 = Listbox(frame2, height = 5, width = 5)
        self.lbl_listbox1.grid(row = 1, column = 1)
        self.listbox1.grid(row = 2, column = 1)
        for item in ["1","2","4","6","8"]:
            self.listbox1.insert(END,item)

	# SMP or MPP
        self.lbl_SMPMPP = tk.Label(frame5, text="SMP or MPP")
        self.smp = tk.Radiobutton(frame5, text="SMP", variable = self.v1, value = 1)
        self.mpp = tk.Radiobutton(frame5, text="MPP", variable = self.v1, value = 2)
        self.lbl_SMPMPP.grid(row = 1, column = 1)
        self.smp.grid(row = 2, column = 1)
        self.mpp.grid(row = 3, column = 1)

        # set default selection for the listbox
        self.listbox1.select_set(0) #This only sets focus on the first item.
        self.listbox1.event_generate("<<ListboxSelect>>")

        self.listbox2 = Listbox(frame6, height = 5, width = 20)
        self.listbox2.grid(row = 1, column = 1)
        self.listbox3 = Listbox(frame6, height = 5, width = 100)
        self.listbox3.grid(row = 1, column = 2)


    def pushjob(self):

        idx = 1


        # show IndexError
        try:
            self.index = int(self.listbox1.curselection()[0])
        except IndexError:
            messagebox.showinfo("","Please speficy CPU number")
        else:
            self.selection = self.listbox1.curselection()
            self.ncpu = self.listbox1.get(self.selection[0])

        if self.ncpu == "0":
            messagebox.showinfo("","Please specify CPU number")
        else:
            idx = 0

        self.memory = self.v2.get()


        if self.label_text.get():
            fn = self.label_text.get()
            if self.v1.get() == 1: #SMP
                cmd ="nohup /opt/LSTC/exe/ls-dyna_smp_d_r910_x64_redhat56_ifort131 NCPU="+self.ncpu+" I="+fn+" MEMORY="+self.memory+"m &"
                #print(cmd)
                #os.chdir(self.dir)
                #subprocess.call(cmd, shell = True)
                self.listbox2.insert(END,self.dir)
                self.listbox3.insert(END,cmd)
                self.flag_run = 1
            elif self.v1.get() == 2: #MPP
                cmd ="nohup /opt/ibm/platform_mpi/bin/mpirun -np "+self.ncpu+" /opt/LSTC/exe/ls-dyna_mpp_d_r9_1_113698_x64_redhat54_ifort131_avx2_platformmpi"+" I="+fn+" MEMORY="+self.memory+"m &"
                #print(cmd)
                #os.chdir(self.dir)
                #subprocess.call(cmd, shell = True)
                self.listbox2.insert(END,self.dir)
                self.listbox3.insert(END,cmd)
                self.flag_run = 1
            else:
                messagebox.showinfo("","Please choose SMP or MPP")
        else:
            messagebox.showinfo("","Please choose a input deck")


    def openfilediag(self):
        filename=askopenfilename()
        if filename:
            self.label_text.set(filename)
            #self.showfilename.config(text=filename)
            self.dir = os.path.split(filename)[0]
            self.label_dir.set(self.dir)

    #def kill(self):
    #    if self.flag_run == 1:
    #        cmd = self.dir+"/kill_by_pid"
    #        subprocess.call(cmd,shell = True)
    #        self.flag_run = 0

    def run(self):
        input = open("input.sh", "w")

        nn = self.listbox2.size()
        i = 0
        while i < nn:
            tmp = "cd "+self.listbox2.get(0)
            input.write(tmp)
            input.write("\n")
            tmp = self.listbox3.get(0)
            input.write(tmp)
            input.write("\n")
            i = i + 1

        input.close()

        tmp = "chmod 0731 ./input.sh"
        #subprocess.call(tmp, shell = True)


root = tk.Tk()
root.title("Job submitter")
app = Application(master=root)
app.mainloop()
