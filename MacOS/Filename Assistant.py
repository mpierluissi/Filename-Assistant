# UCS FILENAME ASSISTANT v3.7.8.1
# by Michael Pierluissi

############################################################################################################################################
#LIBRARY IMPORTS
import os
import csv
import re
import pyperclip
import configparser
import requests
import subprocess
import tkinter as tk
from collections import defaultdict
from tkinter.ttk import Combobox, Progressbar, Spinbox, Separator
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import END, Menu, messagebox, Spinbox

############################################################################################################################################
#DECLARE RELATIVE PATH
relpath = os.path.dirname(__file__)

#MASTER VARIABLES
windowColor = '#222222'
textColor = '#cfcfcf'
ucsLabelColor = '#c62828'
widgetBgColor = '#3e3e3e'
textBoxBgColor = '#cfcfcf'

ucsLabelText = 'Helvetica 14 bold'
textBoxFont = 'Helvetica 14'
noticeTextFont = 'Helvetica 10 bold'

specialCharacters = '<>:"/\|?*'

catID = ''
inDirectory = []
inFullFilename = []
inFilename = []
inExtension = []
newFilename = []

BR_categoryID = ''
BR_vendorCategory = ''
BR_filename = ''
BR_creatorID = ''
BR_sourceID = ''
BR_userData = ''

#CONFIG FILE
configFile = relpath + '/data/config.cfg'
configSettings = configparser.ConfigParser()
configSettings.read(configFile)

#CATEGORY ID INIT
ucsURL = 'https://docs.google.com/spreadsheets/d/1lfYszp5TEjcqSUNgXd0ph9V3UDhXQFZFVtGkERH24u4/gviz/tq?tqx=out:csv&sheet=categorylist'

try:
    requests.get(ucsURL, relpath + '/data/UCSList.csv', timeout=0.250)
except requests.exceptions.Timeout:
    x = None

catIDCSV = relpath + '/data/UCSList.csv'

catIDFile = open(catIDCSV, encoding='utf8')
catIDReader = csv.reader(catIDFile)
catIDData = list(catIDReader)
del(catIDData[0])

catList = []
for x in list(range(0, len(catIDData))):
    catList.append(catIDData[x][0] + ' ' + catIDData[x][1] + '                                ' + '   ' + catIDData[x][5] + '   ' + catIDData[x][4] + '   ' + catIDData[x][2])

#COMBOBOX LISTS
userListFile = relpath + '/data/userLists.cfg'

lists = configparser.ConfigParser(allow_no_value=True)
lists.read(userListFile)

############################################################################################################################################
#MASTER FUNCTIONS
def openUserLists():
    subprocess.call(['open', userListFile])

def openUCSDoc():
    subprocess.call(['open', relpath + '/data/UCS Filenaming Documentation.pdf'])

def openFnAsstDoc():
    subprocess.call(['open', 'https://www.michaelpierluissi.com/filename-assistant.html'])

def updateConfigBool(variable, section, key, value):
    if variable != configSettings[section][key]:
        with open(configFile, 'w') as writer:
            configSettings.set(section, key, value)
            configSettings.write(writer)

def updateConfigVar(section, key, value):
    with open(configFile, 'w') as writer:
        configSettings.set(section, key, value)
        configSettings.write(writer)

def updateUserList(section, variable, userlist):
    if variable is not userlist:
        with open(userListFile, 'w') as writer:
            lists.set(section, variable)
            lists.write(writer)

def setCatID(input):
    global catID
    
    if input == '':
        catID = ''
    elif input == 'userCatSwitch':        
        catID = catID[:len(catID) - (len(userCat)+1)]
    else:    
        catID += input

def duplicateCheck(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() if len(locs)>1)

############################################################################################################################################
#ROOT FUNCTIONS
class fnAsst(TkinterDnD.Tk):
    #FUNCTIONS
    def __init__(self):
        TkinterDnD.Tk.__init__(self)
        self._frame = None
        self.switchFrame(categoryIDWindow)

    def switchFrame(self, frameClass):
        newFrame = frameClass(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = newFrame
        self._frame.pack()

    def onClose(self):
        updateConfigVar('Window Settings', 'windowPositionX', str(self.winfo_rootx()))
        updateConfigVar('Window Settings', 'windowPositionY', str(self.winfo_rooty()-20))

        self.destroy()

    def runBatchRename(self):
        self.switchFrame(batchRenameWindow)

############################################################################################################################################
#CATEGORY ID
class categoryIDWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        #
        master.resizable(False, False)
        master.geometry('%dx%d+%d+%d' % (440, 650, int(configSettings['Window Settings']['windowPositionX']), int(configSettings['Window Settings']['windowPositionY'])))
        master.title('Category ID')

        self.configure(background=windowColor)

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=10)

        #MENU BAR
        menubar = Menu(master)

        runMenu = Menu(menubar, tearoff=0)
        runMenu.add_command(label='Batch Rename', command=master.runBatchRename)
        menubar.add_cascade(label='Run', menu=runMenu)

        optionsMenu = Menu(menubar, tearoff=0)
        optionsMenu.add_command(label="Edit User Lists", command=openUserLists)
        optionsMenu.add_separator()
        optionsMenu.add_command(label="Exit", command=master.onClose)
        menubar.add_cascade(label="Options", menu=optionsMenu)

        helpMenu = Menu(menubar, tearoff=0)
        helpMenu.add_command(label="Filename Assistant", command=openFnAsstDoc)
        helpMenu.add_command(label="Universal Category System", command=openUCSDoc)
        menubar.add_cascade(label="Help", menu=helpMenu)

        master.config(menu=menubar)

        #FUNCTIONS
        def listboxUpdate(data):
            listbox.delete(0, END)

            for item in data:
                listbox.insert(END, item)

        def textCheck(e):
            typed = textbox.get('1.0', 'end-1c')

            if e.keysym == 'Up' or e.keysym == 'Down':
                return

            if typed == '':
                data = catList

            else:
                data = []
                for item in catList:
                    if typed.lower() in item.lower():
                        data.append(item)

            listboxUpdate(data)
            listbox.selection_clear(0, END)
            listbox.selection_set(0)
            descUpdate(listbox.selection_get())

        def descUpdate(event):
            for i in listbox.curselection():
                curData = listbox.get(i).split('   ')
                label1.configure(text=curData[-1])
                label2.configure(text=curData[-2].lstrip(' '))

        def upArrow(event):
            selection = listbox.curselection()
            selection = int(selection[0])
            if selection > 0:
                selection -= 1
                listbox.selection_clear(0, END)
                listbox.selection_set(selection)
                descUpdate(event)

        def downArrow(event):
            selection = listbox.curselection()
            selection = int(selection[0])
            if selection < listbox.size()-1:
                selection += 1
                listbox.selection_clear(0, END)
                listbox.selection_set(selection)
                descUpdate(event)

        def enterKey(event):
            OKPress()

        def OKPress():
            for i in listbox.curselection():
                updateConfigBool(vendorCatCheck.get(), 'Options', 'vendorCat', str(vendorCatCheck.get()))
                updateConfigBool(userCatCheck.get(), 'Options', 'userCat', str(userCatCheck.get()))

                curData = listbox.get(i).split('   ')

                setCatID(curData[-1])

                if userCatCheck.get() == 1:
                    master.switchFrame(userCategoryWindow)
                elif vendorCatCheck.get() == 1:
                    master.switchFrame(vendorCategoryWindow)
                else:
                    master.switchFrame(filenameWindow)

        #TEXTBOX
        textFrame = tk.Frame(rootFrame)
        textFrame.grid(row=0, column=0, rowspan=2, columnspan=2, pady=(10, 5), sticky='w')

        textbox = tk.Text(textFrame, width=30, height=1, insertbackground=textColor, background=widgetBgColor, highlightthickness=0, foreground=textColor, font=textBoxFont)
        textbox.pack()

        #OPTIONS
        checkboxFrame = tk.Frame(rootFrame)
        checkboxFrame.configure(background=windowColor)
        checkboxFrame.grid(row=0, column=0, sticky='e', pady=5)

        userCatCheck = tk.IntVar()
        userCatCheck.set(configSettings['Options']['userCat'])

        userCatCheckbox = tk.Checkbutton(checkboxFrame, variable=userCatCheck, text='User Category', bg=windowColor, fg=textColor)
        userCatCheckbox.pack(side='top', anchor='w')
        userCatCheckbox.var = userCatCheck

        vendorCatCheck = tk.IntVar()
        vendorCatCheck.set(configSettings['Options']['vendorCat'])

        vendorCatCheckbox = tk.Checkbutton(checkboxFrame, variable=vendorCatCheck, text='Vendor Category', bg=windowColor, fg=textColor)
        vendorCatCheckbox.pack(side='bottom', anchor='w')
        vendorCatCheckbox.var = vendorCatCheck

        #LISTBOX
        listboxFrame = tk.Frame(rootFrame)
        listboxFrame.grid(row=2, column=0, sticky='w', pady=5)

        listbox = tk.Listbox(listboxFrame, selectmode='single', activestyle='none', width=40, height=25, font='Courier 16', background=widgetBgColor, foreground=textColor)
        listboxScroll = tk.Scrollbar(listboxFrame, orient='vertical', command=listbox.yview)

        listbox.config(yscrollcommand=listboxScroll.set, xscrollcommand='')

        listbox.pack(side='left')
        listboxScroll.pack(side='right', fill='y')

        listboxUpdate(catList)
        listbox.selection_set(0)

        #DESCRIPTION LABELS
        descriptionFrame = tk.Frame(rootFrame, width=46, background='#000000')
        descriptionFrame.grid(row=3, column=0, sticky='news', pady=5)

        label1 = tk.Label(descriptionFrame, font=ucsLabelText, fg=textColor)
        label2 = tk.Label(descriptionFrame, height=3, font=(24), fg=textColor)

        label1.configure(background=widgetBgColor, anchor='w')
        label2.configure(background=widgetBgColor, justify='left', anchor='nw', wraplength=400)

        label1.pack(fill='x')
        label2.pack(fill='x')

        descUpdate(listbox.selection_get())

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame)
        buttonFrame.grid(row=4, column=0, sticky='w', pady=(5, 10))

        tk.Button(buttonFrame, width=10, text='OK', highlightbackground=windowColor, command=OKPress).pack()

        #BINDINGS
        textbox.bind('<KeyRelease>', textCheck)
        textbox.focus_set()

        listbox.bind('<<ListboxSelect>>', descUpdate)

        master.bind('<Up>', upArrow)
        master.bind('<Down>', downArrow)
        master.bind('<Return>', enterKey)
        master.protocol("WM_DELETE_WINDOW", master.onClose)

############################################################################################################################################
#USER CATEGORY
class userCategoryWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        
        master.resizable(False, False)
        master.title('User Category')
        master.geometry('675x75')

        self.configure(background=windowColor)

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=10)

        #FUNCTIONS
        userCatList = []
        for item in lists['User Category']:
            userCatList.append(item.upper())
        userCatList.sort()

        def enterKey(event):
            OKPress()

        def OKPress():
            global userCat
            userCat = combobox.get().upper()

            if userCat == '' or any(c in specialCharacters for c in userCat):
                messagebox.showerror('Notice', 'Source ID must not contain special characters.')
                master.switchFrame(userCategoryWindow)
                return

            updateUserList('User Category', userCat, userCatList)

            setCatID(('-' + userCat))

            if configSettings.getboolean('Options', 'vendorcat') == 1:
                master.switchFrame(vendorCategoryWindow)
            else:
                master.switchFrame(filenameWindow)

        def backPress():
            setCatID('')
            master.switchFrame(categoryIDWindow)
        
        #COMBOBOX
        comboboxFrame = tk.Frame(rootFrame)
        comboboxFrame.grid(row=0, column=0, pady=(10, 5), sticky='w')
        
        combobox = Combobox(comboboxFrame, values=userCatList, background=windowColor, width=40, height=10)
        combobox.pack(anchor='w')

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame, bg=windowColor)
        buttonFrame.grid(row=0, column=1, pady=(5, 0), sticky='w')

        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='OK', command=OKPress).pack(side='left', padx=10)
        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='Back', command=backPress).pack(side='right')

        #UCS LABEL
        labelFrame2 = tk.Frame(rootFrame)
        labelFrame2.grid(row=1, column=0, pady=5, sticky='w', columnspan=2)

        label = tk.Label(labelFrame2, text=catID, fg=textColor)
        label.configure(background=windowColor, anchor='w', font=ucsLabelText, fg=ucsLabelColor)
        label.pack(fill='x')

        #BINDINGS
        combobox.focus_set()

        master.unbind('<Up>')
        master.unbind('<Down>')
        master.bind('<Return>', enterKey)

############################################################################################################################################
#VENDOR CATEGORY
class vendorCategoryWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
    
        master.resizable(False, False)

        master.title('Vendor Category')

        self.configure(background=windowColor)

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=10)

        #FUNCTIONS
        vendorCatList = []
        for item in lists['Vendor Category']:
            vendorCatList.append(item.upper())
        vendorCatList.sort()

        def enterKey(event):
            OKPress()

        def OKPress():
            global vendorCat
            vendorCat = combobox.get()

            if vendorCat == '' or any(c in specialCharacters for c in vendorCat):
                messagebox.showerror('Notice', 'Source ID must not contain special characters.')
                master.switchFrame(vendorCategoryWindow)
                return

            updateUserList('Vendor Category', vendorCat, vendorCatList)

            master.switchFrame(filenameWindow)
        
        def backPress():
            if configSettings.getboolean('Options', 'usercat') == 1:
                setCatID('userCatSwitch')
                master.switchFrame(userCategoryWindow)
            else:
                setCatID('')
                master.switchFrame(categoryIDWindow)
        
        #COMBOBOX
        comboboxFrame = tk.Frame(rootFrame)
        comboboxFrame.grid(row=0, column=0, pady=(10, 5), sticky='w')
        
        combobox = Combobox(comboboxFrame, values=vendorCatList, background=windowColor, width=40, height=10)
        combobox.pack(anchor='w')

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame, bg=windowColor)
        buttonFrame.grid(row=0, column=1, pady=(5, 0), sticky='w')

        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='OK', command=OKPress).pack(side='left', padx=10)
        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='Back', command=backPress).pack(side='right')

        #UCS LABEL
        labelFrame2 = tk.Frame(rootFrame)
        labelFrame2.grid(row=1, column=0, pady=5, sticky='w', columnspan=2)

        label = tk.Label(labelFrame2, text=catID, background=windowColor, anchor='w', font=ucsLabelText, fg=ucsLabelColor)
        label.pack(fill='x')

        #BINDINGS
        combobox.focus_set()

        master.unbind('<Up>')
        master.unbind('<Down>')
        master.bind('<Return>', enterKey)

############################################################################################################################################
#FILENAME
class filenameWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        master.title('Filename')
        master.geometry('690x65')

        self.configure(background=windowColor)

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=10)

        #FUNCTIONS
        def enterKey(event):
            OKPress()

        def OKPress():
            updateConfigBool(titlecaseCheck.get(), 'Options', 'titlecase', str(titlecaseCheck.get()))

            global filename
            filename = textbox.get('1.0', END).strip()

            if filename == '' or any(c in specialCharacters for c in filename):
                messagebox.showerror('Notice', 'Filename must not be empty or contain special characters.')
                master.switchFrame(filenameWindow)
                return
            
            if titlecaseCheck.get() == 1:
                filename = filename.title()

            if configSettings.getboolean('Options', 'vendorcat') == 1:
                filename = vendorCat + '-' + filename

            master.switchFrame(creatorIDWindow)
        
        def backPress():
            if configSettings.getboolean('Options', 'vendorcat') == 1:
                master.switchFrame(vendorCategoryWindow)
            elif configSettings.getboolean('Options', 'usercat') == 1:
                setCatID('userCatSwitch')
                master.switchFrame(userCategoryWindow)
            else:
                setCatID('')
                master.switchFrame(categoryIDWindow)

        #TEXTBOX
        textFrame = tk.Frame(rootFrame)
        textFrame.grid(row=0, column=0, pady=(10, 5), sticky='w')

        textbox = tk.Text(textFrame, width=50, height=1, insertbackground=textColor, background=widgetBgColor, highlightthickness=0, font=textBoxFont)
        textbox.pack()

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame, bg=windowColor)
        buttonFrame.grid(row=0, column=1, pady=(5,0), sticky='w')

        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='OK', command=OKPress).pack(side='left', padx=10)
        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='Back', command=backPress).pack(side='right')

        #OPTIONS
        optionsFrame = tk.Frame(rootFrame)
        optionsFrame.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        titlecaseCheck = tk.IntVar()
        titlecaseCheck.set(configSettings['Options']['titlecase'])

        titlecaseCheckbox = tk.Checkbutton(optionsFrame, variable=titlecaseCheck, text='Title case', font=ucsLabelText, bg=windowColor, fg=textColor)
        titlecaseCheckbox.pack()
        titlecaseCheckbox.var = titlecaseCheck

        #UCS LABEL
        labelFrame = tk.Frame(rootFrame)
        labelFrame.grid(row=1, column=0, sticky='w', columnspan=2)

        label = tk.Label(labelFrame, background=windowColor, pady=5, anchor='w', font=ucsLabelText, fg=ucsLabelColor)
        label.pack(fill='x')

        if configSettings.getboolean('Options', 'vendorcat') == 1:
            label.configure(text=catID + '_' + vendorCat)
        else:
            label.configure(text=catID)

        #BINDINGS
        textbox.focus_set()

        master.unbind('<Up>')
        master.unbind('<Down>')
        master.bind('<Return>', enterKey)

############################################################################################################################################
#CREATOR ID
class creatorIDWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        master.title('Creator ID')
        master.geometry('680x105')

        self.configure(background=windowColor)

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=10)

        #FUNCTIONS
        creatorIDList = []
        for item in lists['Creator ID']:
            creatorIDList.append(item.upper())
        creatorIDList.sort()

        def enterKey(event):
            OKPress()

        def OKPress():
            global creatorID
            creatorID = combobox.get().upper()

            if any(c in specialCharacters for c in creatorID):
                messagebox.showerror('Notice', 'Creator ID must not contain special characters.')
                master.switchFrame(creatorIDWindow)
                return

            updateUserList('Creator ID', creatorID, creatorIDList)

            if creatorID == '':
                creatorID = 'NONE'

            master.switchFrame(sourceIDWindow)
        
        #COMBOBOX
        comboboxFrame = tk.Frame(rootFrame)
        comboboxFrame.grid(row=1, column=0, pady=(10, 5), sticky='w')

        combobox = Combobox(comboboxFrame, values=creatorIDList, background=windowColor, width=40, height=10)
        combobox.pack(anchor='w')

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame, bg=windowColor)
        buttonFrame.grid(row=1, column=1, pady=(5, 0), sticky='w')

        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='OK', command=OKPress).pack(side='left', padx=10)
        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='Back', command=lambda: master.switchFrame(filenameWindow)).pack(side='right')

        #INFO LABEL
        labelFrame1 = tk.Frame(rootFrame)
        labelFrame1.grid(row=0, column=0, sticky='w')
        
        label1 = tk.Label(labelFrame1, text='If none, leave blank.', fg=textColor)
        label1.configure(pady=5, background=windowColor, font=textBoxFont)
        label1.pack(fill='x')

        #UCS LABEL
        labelFrame2 = tk.Frame(rootFrame)
        labelFrame2.grid(row=2, column=0, pady=5, sticky='w', columnspan=2)

        label = tk.Label(labelFrame2, text=catID + '_' + filename)
        label.configure(background=windowColor, anchor='w', font=ucsLabelText, fg=ucsLabelColor)
        label.pack(fill='x')

        #BINDINGS
        combobox.focus_set()

        master.bind('<Return>', enterKey)

############################################################################################################################################
#SOURCE ID
class sourceIDWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('Source ID')

        self.configure(background=windowColor)

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=10)

        #FUNCTIONS
        sourceIDList = []
        for item in lists['Source ID']:
            sourceIDList.append(item.upper())
        sourceIDList.sort()

        def enterKey(event):
            OKPress()

        def OKPress():
            global sourceID
            sourceID = combobox.get().upper()

            if any(c in specialCharacters for c in sourceID):
                messagebox.showerror('Notice', 'Source ID must not contain special characters.')
                master.switchFrame(sourceIDWindow)
                return

            updateUserList('Source ID', sourceID, sourceIDList)

            if sourceID == '':
                sourceID = 'NONE'

            master.switchFrame(userDataWindow)
        
        #COMBOBOX
        comboboxFrame = tk.Frame(rootFrame)
        comboboxFrame.grid(row=1, column=0, pady=(10, 5), sticky='w')
        
        combobox = Combobox(comboboxFrame, values=sourceIDList, background=windowColor, width=40, height=10)
        combobox.pack(anchor='w')

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame, bg=windowColor)
        buttonFrame.grid(row=1, column=1, pady=(5, 0), sticky='w')

        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='OK', command=OKPress).pack(side='left', padx=10)
        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='Back', command=lambda: master.switchFrame(creatorIDWindow)).pack(side='right')

        #INFO LABEL
        labelFrame1 = tk.Frame(rootFrame)
        labelFrame1.grid(row=0, column=0, sticky='w')
        
        label1 = tk.Label(labelFrame1, text='If none, leave blank.')
        label1.configure(pady=5, background=windowColor, font=textBoxFont, fg=textColor)
        label1.pack(fill='x')

        #UCS LABEL
        labelFrame2 = tk.Frame(rootFrame)
        labelFrame2.grid(row=2, column=0, pady=5, sticky='w', columnspan=2)

        label = tk.Label(labelFrame2, text=catID + '_' + filename + '_' + creatorID)
        label.configure(background=windowColor, anchor='w', font=ucsLabelText, fg=ucsLabelColor)
        label.pack(fill='x')

        #BINDINGS
        combobox.focus_set()

        master.bind('<Return>', enterKey)

############################################################################################################################################
#USER DATA
class userDataWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        master.title('User Data')
        master.geometry('690x95')

        self.configure(background=windowColor)

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=10)

        #FUNCTIONS
        def enterKey(event):
            OKPress()

        def OKPress():
            global userData
            userData = textbox.get('1.0', END).strip()

            if configSettings.getboolean('Options', 'noconfirm') == 1:
                copyToClipboard()
                master.destroy()
            else:
                copyToClipboard()
                master.switchFrame(confirmationWindow)

        def copyToClipboard():
            if userData == '':
                pyperclip.copy(catID + '_' + filename + '_' + creatorID + '_' + sourceID)
            else:
                pyperclip.copy(catID + '_' + filename + '_' + creatorID + '_' + sourceID + '_' + userData)

        #TEXTBOX
        textFrame = tk.Frame(rootFrame)
        textFrame.grid(row=1, column=0, pady=(5, 5), sticky='w')

        textbox = tk.Text(textFrame, width=50, height=1, insertbackground=textColor, background=widgetBgColor, highlightthickness=0, font=textBoxFont)
        textbox.pack()

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame, bg=windowColor)
        buttonFrame.grid(row=1, column=1, sticky='w')

        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='OK', command=OKPress).pack(side='left', padx=10)
        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='Back', command=lambda: master.switchFrame(sourceIDWindow)).pack(side='right')

        #INFO LABEL
        labelFrame1 = tk.Frame(rootFrame)
        labelFrame1.grid(row=0, column=0, sticky='w')
        
        label1 = tk.Label(labelFrame1, text='If none, leave blank.')
        label1.configure(pady=5, background=windowColor, font=textBoxFont, fg=textColor)
        label1.pack(fill='x')

        #UCS LABEL
        labelFrame2 = tk.Frame(rootFrame)
        labelFrame2.grid(row=2, column=0, sticky='w', columnspan=2)

        label2 = tk.Label(labelFrame2, text=catID + '_' + filename + '_' + creatorID + '_' + sourceID)
        label2.configure(pady=10, background=windowColor, anchor='w', font=ucsLabelText, fg=ucsLabelColor)
        label2.pack(fill='x')

        #BINDINGS
        textbox.focus_set()

        master.bind('<Return>', enterKey)

############################################################################################################################################
#CONFIRMATION WINDOW
class confirmationWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        master.title('Filename Assistant')
        master.geometry('300x100')

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=(10, 50))

        self.configure(background=windowColor)

        #FUNCTIONS
        def OKPress():
            updateConfigBool(noConfirm.get(), 'Options', 'noconfirm', str(noConfirm.get()))
            master.quit()

        #LABELS
        labelFrame = tk.Frame(rootFrame, background=windowColor)
        labelFrame.grid(row=0, column=0, sticky='w', pady=10, padx=10)

        label1 = tk.Label(labelFrame, text=master.clipboard_get(), fg=ucsLabelColor)
        label2 = tk.Label(labelFrame, text='has been copied to the clipboard.', fg=textColor)

        label1.configure(background=windowColor, anchor='w', font=ucsLabelText)
        label2.configure(background=windowColor, anchor='w', font=ucsLabelText)

        label1.pack(fill='x', pady=(0, 5), side='top')
        label2.pack(fill='x', pady=(5, 0), side='bottom')

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame, bg=windowColor)
        buttonFrame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='OK', command=OKPress).pack(side='right', padx=10)       

        noConfirm = tk.IntVar()
        noConfirm.set(configSettings['Options']['noconfirm'])

        checkbox = tk.Checkbutton(buttonFrame, variable=noConfirm, text="Don't show this again.", bg=windowColor, fg=textColor)
        checkbox.pack(side='left')
        checkbox.var = noConfirm

############################################################################################################################################
#BATCH RENAME
class batchRenameWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.resizable(False, False)
        master.geometry('915x760')
        master.title('Batch Rename')

        self.configure(background=windowColor)

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=10, rowspan=1, columnspan=1)

        #FUNCTIONS
        creatorIDList = []
        for item in lists['Creator ID']:
            creatorIDList.append(item.upper())
        creatorIDList.sort()

        sourceIDList = []
        for item in lists['Source ID']:
            sourceIDList.append(item.upper())
        sourceIDList.sort()

        userCatList = []
        for item in lists['User Category']:
            userCatList.append(item.upper())
        userCatList.sort()

        vendorCatList = []
        for item in lists['Vendor Category']:
            vendorCatList.append(item.upper())
        vendorCatList.sort()

        def updateCharCountLabel(event):
            selFirst = inFileTextbox.index("sel.first")
            selLast = inFileTextbox.index("sel.last")

            charCount = inFileTextbox.count(selFirst, selLast, 'chars')[0]

            charCountLabel['text'] = 'Characters: ' + str(charCount)
        
        def updateInFileText(event):
            inFileSplit = os.path.splitext(inFileListbox.get(inFileListbox.curselection()))
            inFileTextbox.replace(1.0, END, inFileSplit[0])

        def addToInFileListbox(event):
            index = 0

            global inDirectory
            global inFullFilename
            global inFilename
            global inExtension

            files = inFileListbox.tk.splitlist(event.data)

            for item in files:
                inFileSplit = os.path.split(item)
                inExtSplit = os.path.splitext(inFileSplit[1])
                
                if inFileSplit[1] not in inFullFilename:
                    inDirectory.append(inFileSplit[0])
                    inFullFilename.append(inFileSplit[1])
                    inFilename.append(inExtSplit[0])
                    inExtension.append(inExtSplit[1])

                    inFileListbox.insert(END, inFileSplit[1])
                    index += 1
            
            fileCountLabel['text'] = 'Files: ' + str(len(inFilename))

        def catIDListboxUpdate(data):
            catIDListbox.delete(0, END)

            for item in data:
                catIDListbox.insert(END, item)

        def textCheck(e):
            typed = catIDTextbox.get('1.0', 'end-1c')

            if e.keysym == 'Up' or e.keysym == 'Down':
                return

            if typed == '':
                data = catList

            else:
                data = []
                for item in catList:
                    if typed.lower() in item.lower():
                        data.append(item)

            catIDListboxUpdate(data)
            catIDListbox.selection_clear(0, END)
            catIDListbox.selection_set(0)

        def upArrow(event):
            selection = catIDListbox.curselection()
            selection = int(selection[0])
            if selection > 0:
                selection -= 1
                catIDListbox.selection_clear(0, END)
                catIDListbox.selection_set(selection)

        def downArrow(event):
            selection = catIDListbox.curselection()
            selection = int(selection[0])
            if selection < catIDListbox.size()-1:
                selection += 1
                catIDListbox.selection_clear(0, END)
                catIDListbox.selection_set(selection)

        def enterKey(event):
            OKPress()

        def OKPress():
            global newFilename
            newFilename = []

            global BR_categoryID
            global BR_vendorCategory
            global BR_creatorID
            global BR_sourceID
            global BR_userData

            index = 0
            if len(inFilename) == 0:
                messagebox.showerror('Notice', 'No files to rename.')
                master.switchFrame(batchRenameWindow)
                return

            for filename in inFilename:
                newFilename.append(filename)

                if vendorCatCheck.get() == True:                       
                    BR_vendorCategory = vendorCatCombobox.get().upper() + '-'
                    newFilename[index] = BR_vendorCategory + newFilename[index]
                    updateUserList('Vendor Category', vendorCatCombobox.get().upper(), vendorCatList)
                    updateConfigVar('Batch Rename', 'vendorcatinput', vendorCatCombobox.get().upper())
                else:
                    updateConfigVar('Batch Rename', 'vendorcatinput', '')

                if filenameCheck.get() == True and vendorCatCheck.get() == True:
                    filename = filenameTextbox.get('1.0', END).strip()
                    newFilename[index] = BR_vendorCategory + filename
                    updateConfigVar('Batch Rename', 'vendorcatinput', vendorCatCombobox.get().upper())
                    updateConfigVar('Batch Rename', 'filenameinput', filenameTextbox.get('1.0', END).strip())
                else:
                    updateConfigVar('Batch Rename', 'vendorcatinput', '')
                    updateConfigVar('Batch Rename', 'filenameinput', '')

                if trimCheck.get() == True:
                    if fromWheel.get() == '' or fromWheel.get() == '0':
                        updateConfigVar('Batch Rename', 'frominput', '0')
                    else:
                        filename = filename[int(fromWheel.get()):]
                        newFilename[index] = filename
                        updateConfigVar('Batch Rename', 'frominput', fromWheel.get())

                    if toWheel.get() == '' or toWheel.get() == '0':
                        updateConfigVar('Batch Rename', 'toinput', '0')
                    else:
                        filename = filename[:0 - int(toWheel.get())]
                        newFilename[index] = filename
                        updateConfigVar('Batch Rename', 'toinput', toWheel.get())
                else:
                    fromInit.set('0')
                    updateConfigVar('Batch Rename', 'frominput', '0')
                    toInit.set('0')
                    updateConfigVar('Batch Rename', 'toinput', '0')

                if findReplaceCheck.get() == True:
                    filename = re.sub(findTextBox.get('1.0', END).strip('\n'), replaceTextBox.get('1.0', END).strip('\n'), filename, flags=re.IGNORECASE)
                    newFilename[index] = filename
                    updateConfigVar('Batch Rename', 'findinput', findTextBox.get('1.0', END).strip('\n'))
                    updateConfigVar('Batch Rename', 'replaceinput', replaceTextBox.get('1.0', END).strip('\n'))
                else:
                    updateConfigVar('Batch Rename', 'findinput', '')
                    updateConfigVar('Batch Rename', 'replaceinput', '')

                if findReplaceCheck.get() == True and vendorCatCheck.get() == True:
                    newFilename[index] = BR_vendorCategory + filename

                if filenameCheck.get() == True:
                    newFilename[index] = filenameTextbox.get('1.0', END).strip()
                    updateConfigVar('Batch Rename', 'filenameinput', filenameTextbox.get('1.0', END).strip())
                else:
                    updateConfigVar('Batch Rename', 'filenameinput', '')

                if catIDCheck.get() == True:
                    for i in catIDListbox.curselection():
                        curData = catIDListbox.get(i).split('   ')
                        BR_categoryID = (curData[-1])

                        if userCatCheck.get() == True:
                            newFilename[index] = BR_categoryID + '-' + userCatCombobox.get().upper() + '_' + newFilename[index]
                        else:
                            newFilename[index] = BR_categoryID + '_' + newFilename[index]
                    updateConfigVar('Batch Rename', 'catIDInput', BR_categoryID)
                else:
                    updateConfigVar('Batch Rename', 'catIDInput', '')
                
                if userCatCheck.get() == True and catIDCheck.get() == False:
                    newFilename[index] = userCatCombobox.get().upper() + '_' + newFilename[index]
                    updateUserList('User Category', userCatCombobox.get().upper(), userCatList)
                    updateConfigVar('Batch Rename', 'usercatinput', userCatCombobox.get().upper())
                else:
                    updateConfigVar('Batch Rename', 'usercatinput', '')

                if creatorIDCheck.get() == True:
                    newFilename[index] = newFilename[index] + '_' + creatorIDCombobox.get().upper()
                    updateUserList('Creator ID', creatorIDCombobox.get().upper(), creatorIDList)
                    updateConfigVar('Batch Rename', 'creatoridinput', creatorIDCombobox.get().upper())
                else:
                    updateConfigVar('Batch Rename', 'creatoridinput', '')
                
                if sourceIDCheck.get() == True:
                    newFilename[index] = newFilename[index] + '_' + sourceIDCombobox.get().upper()
                    updateUserList('Source ID', sourceIDCombobox.get().upper(), sourceIDList)
                    updateConfigVar('Batch Rename', 'sourceidinput', sourceIDCombobox.get().upper())
                else:
                    updateConfigVar('Batch Rename', 'sourceidinput', '')
                
                if userDataCheck.get() == True:
                    updateConfigVar('Batch Rename', 'userdatainput', userDataTextbox.get('1.0', END).strip())
                    BR_userData =  userDataTextbox.get('1.0', END).strip()
                
                    if numberingCheck.get() == True:
                        if len(inFilename) + int(numberingWheel.get()) > 10:
                            places = 2

                        if len(inFilename) + int(numberingWheel.get()) > 100:
                            places = 3

                        if len(inFilename) + int(numberingWheel.get()) > 1000:
                            places = 4

                        if len(inFilename) + int(numberingWheel.get()) < 10:
                            places = 1
                        
                        BR_userData = BR_userData + ' ' + str(index + int(numberingWheel.get())).zfill(places)

                    newFilename[index] = newFilename[index] + '_' + BR_userData
                else:
                    updateConfigVar('Batch Rename', 'userdatainput', '')
                
                if numberingCheck.get() == True and userDataCheck.get() == False:
                    updateConfigVar('Batch Rename', 'numberinginput', numberingWheel.get())
                    BR_userData = index + int(numberingWheel.get())

                    if len(inFilename) + int(numberingWheel.get()) > 10:
                        places = 2

                    if len(inFilename) + int(numberingWheel.get()) > 100:
                        places = 3

                    if len(inFilename) + int(numberingWheel.get()) > 1000:
                        places = 4

                    if len(inFilename) + int(numberingWheel.get()) < 10:
                        places = 1

                    BR_userData = str(BR_userData).zfill(places)
                    newFilename[index] = newFilename[index] + '_' + BR_userData
                else:
                    updateConfigVar('Batch Rename', 'numberinginput', '')

                index += 1
            
            #DUPLICATE CHECK
            for original in newFilename:
                for duplicate in duplicateCheck(newFilename):
                    dupNumber = 0
                    dupIndexFound = duplicate[1]
                    for number in dupIndexFound:
                        if userDataCheck.get() == True:
                            newFilename[number] = newFilename[number] + ' ' + str(dupNumber)
                            dupNumber += 1
                        else:
                            newFilename[number] = newFilename[number] + '_' + str(dupNumber)
                            dupNumber += 1
                        
            #COMPILE FINAL
            finalIndex = 0
            for finalItem in newFilename:
                newFilename[finalIndex] = finalItem + inExtension[finalIndex]
                finalIndex += 1

            if fromWheel.get() == '' or fromWheel.get() == '0':
                updateConfigVar('Batch Rename', 'frominput', '0')
            else:
                updateConfigVar('Batch Rename', 'frominput', fromWheel.get())

            if toWheel.get() == '' or toWheel.get() == '0':
                updateConfigVar('Batch Rename', 'toinput', '0')
            else:
                updateConfigVar('Batch Rename', 'toinput', toWheel.get())

            updateConfigBool(catIDCheck.get(), 'Batch Rename', 'catidcheck', str(catIDCheck.get()))
            updateConfigBool(filenameCheck.get(), 'Batch Rename', 'filenamecheck', str(filenameCheck.get()))
            updateConfigBool(findReplaceCheck.get(), 'Batch Rename', 'findandreplacecheck', str(findReplaceCheck.get()))
            updateConfigBool(trimCheck.get(), 'Batch Rename', 'trimcheck', str(trimCheck.get()))
            updateConfigBool(creatorIDCheck.get(), 'Batch Rename', 'creatoridcheck', str(creatorIDCheck.get()))
            updateConfigBool(sourceIDCheck.get(), 'Batch Rename', 'sourceidcheck', str(sourceIDCheck.get()))
            updateConfigBool(vendorCatCheck.get(), 'Batch Rename', 'vendorcatcheck', str(vendorCatCheck.get()))
            updateConfigBool(userCatCheck.get(), 'Batch Rename', 'usercatcheck', str(userCatCheck.get()))
            updateConfigBool(userDataCheck.get(), 'Batch Rename', 'userdatacheck', str(userDataCheck.get()))
            updateConfigBool(numberingCheck.get(), 'Batch Rename', 'numberingcheck', str(numberingCheck.get()))

            master.switchFrame(batchConfirmationWindow)
        
        #IN FILES
        inFileFrame = tk.Frame(rootFrame, background=windowColor)
        inFileFrame.grid(row=0, column=0, pady=5, sticky='nw')

        inFileTextbox = tk.Text(inFileFrame, height=1, insertbackground=textColor, background=widgetBgColor, highlightthickness=0, foreground=textColor)
        inFileTextbox.pack(fill='x', pady=5)

        charCountLabel = tk.Label(inFileFrame, text='Characters: ', bg=windowColor, fg=textColor)
        charCountLabel.pack(anchor='w', pady=(0, 5))

        inFileListbox = tk.Listbox(inFileFrame, selectmode='single', activestyle='none', height=40, font='Arial', background=widgetBgColor, foreground=textColor)
        inFileListbox.pack(fill='x')

        fileCountLabel = tk.Label(inFileFrame, text='Files:', background=windowColor, foreground=textColor)
        fileCountLabel.pack(anchor='w')

        refillIndex = 0
        for item in inFilename:
            inFileListbox.insert(END, item + inExtension[refillIndex])
            refillIndex += 1
            fileCountLabel['text'] = 'Files: ' + str(len(inFilename))

        #OPTIONS
        optionsFrame = tk.Frame(rootFrame, background=windowColor)
        optionsFrame.grid(padx=10, pady=5, row=0, column=1, rowspan=2, sticky='nw')
        Separator(optionsFrame, orient='vertical').pack(fill='y', side='left')

        #FIND & REPLACE
        findReplaceCheck = tk.IntVar()
        findReplaceCheck.set(configSettings['Batch Rename']['findandreplacecheck'])
        findReplaceCheckbox = tk.Checkbutton(optionsFrame, variable=findReplaceCheck, text='Find & Replace', bg=windowColor, fg=textColor, selectcolor=windowColor)
        findReplaceCheckbox.pack(anchor='w')

        findReplaceFrame = tk.Frame(optionsFrame, background=windowColor)
        findReplaceFrame.pack(padx=20, pady=(0, 5), anchor='w')

        FRLabelFrame = tk.Frame(findReplaceFrame, background=windowColor)
        FRLabelFrame.pack(side='left')
        tk.Label(FRLabelFrame, text='Find:', bg=windowColor, fg=textColor).pack(pady=5, anchor='w')
        tk.Label(FRLabelFrame, text='Replace:', bg=windowColor, fg=textColor).pack(anchor='w')

        FRTextFrame = tk.Frame(findReplaceFrame, background=windowColor)
        FRTextFrame.pack(padx=(10, 0), side='right')
        findTextBox = tk.Text(FRTextFrame, height=1, width=29, insertbackground=textColor, background=widgetBgColor, highlightthickness=0, foreground=textColor)
        findTextBox.insert('1.0', configSettings['Batch Rename']['findInput'])
        replaceTextBox = tk.Text(FRTextFrame, height=1, width=29, insertbackground=textColor, background=widgetBgColor, highlightthickness=0, foreground=textColor)
        replaceTextBox.insert('1.0', configSettings['Batch Rename']['replaceInput'])
        
        findTextBox.pack(pady=5, anchor='e')
        replaceTextBox.pack(anchor='e')
        
        #CATEGORY ID
        Separator(optionsFrame, orient='horizontal').pack(fill='x')
        catIDCheck = tk.IntVar()
        catIDCheck.set(configSettings['Batch Rename']['catidcheck'])
        catIDCheckbox = tk.Checkbutton(optionsFrame, variable=catIDCheck, text='Category ID', bg=windowColor, fg=textColor, selectcolor=windowColor)
        catIDCheckbox.pack(anchor='w')
        
        catIDFrame = tk.Frame(optionsFrame, background=windowColor)
        catIDFrame.pack(padx=20, pady=5, anchor='w')

        catIDTextbox = tk.Text(catIDFrame, width=20, height=1, insertbackground=textColor, background=widgetBgColor, highlightthickness=0, foreground=textColor, font=textBoxFont)
        catIDTextbox.pack(pady=(0, 5), anchor='w', fill='x')
        catIDListbox = tk.Listbox(catIDFrame, width=35, height=5, selectmode='single', activestyle='none', font='Courier 14', background=widgetBgColor, foreground=textColor)
        listboxScroll = tk.Scrollbar(catIDFrame, orient='vertical', command=catIDListbox.yview)

        catIDListbox.config(yscrollcommand=listboxScroll.set, xscrollcommand='')

        catIDListbox.pack(side='left', anchor='w')
        listboxScroll.pack(side='right', fill='y')
        
        catIDListboxUpdate(catList)
        catIDListbox.selection_set(0)

        if configSettings['Batch Rename']['catidinput'] != '':
            for item in configSettings['Batch Rename']['catidinput']:
                catIDTextbox.insert(END, item)
                data = []
                for item in catList:
                    if configSettings['Batch Rename']['catidinput'].lower() in item.lower():
                        data.append(item)

                catIDListboxUpdate(data)
                catIDListbox.selection_set(0)

        #FILENAME
        Separator(optionsFrame, orient='horizontal').pack(fill='x')
        filenameCheck = tk.IntVar()
        filenameCheck.set(configSettings['Batch Rename']['filenamecheck'])
        filenameCheckbox = tk.Checkbutton(optionsFrame, variable=filenameCheck, text='Clear & Replace Filename', bg=windowColor, fg=textColor, selectcolor=windowColor)
        filenameCheckbox.pack(anchor='w')

        filenameTextbox = tk.Text(optionsFrame, width=39, height=1, insertbackground=textColor, background=widgetBgColor, highlightthickness=0, foreground=textColor)
        filenameTextbox.pack(padx=20, pady=5, anchor='w')
        filenameTextbox.insert('1.0', configSettings['Batch Rename']['filenameinput'])

        #TRIM
        trimCheck = tk.IntVar()
        trimCheck.set(configSettings['Batch Rename']['trimcheck'])
        trimCheckbox = tk.Checkbutton(optionsFrame, variable=trimCheck, text='Trim Filename', bg=windowColor, fg=textColor, selectcolor=windowColor)
        trimCheckbox.pack(anchor='w')

        trimFrame = tk.Frame(optionsFrame, background=windowColor)
        trimFrame.pack(padx=20, anchor='w')

        trimLabelFrame = tk.Frame(trimFrame, background=windowColor)
        trimLabelFrame.pack(side='left')

        tk.Label(trimLabelFrame, text='From Beginning:', bg=windowColor, fg=textColor).pack(pady=(0, 5), anchor='w')
        tk.Label(trimLabelFrame, text='From End:', bg=windowColor, fg=textColor).pack(anchor='w')

        spinboxFrame = tk.Frame(trimFrame, background=windowColor)
        spinboxFrame.pack(padx=(10, 0), side='right')

        fromInit = tk.IntVar()
        fromInit.set(configSettings['Batch Rename']['frominput'])

        fromWheel = Spinbox(spinboxFrame, from_=0, to=999, width=3, textvariable=fromInit, background=widgetBgColor, highlightbackground=windowColor, foreground=textColor)
        fromWheel.pack()

        toInit = tk.IntVar()
        toInit.set(configSettings['Batch Rename']['toinput'])

        toWheel = Spinbox(spinboxFrame, from_=0, to=999, width=3, textvariable=toInit, background=widgetBgColor, highlightbackground=windowColor, foreground=textColor)
        toWheel.pack()

        #CREATOR & SOURCE ID
        Separator(optionsFrame, orient='horizontal').pack(fill='x')
        creatorIDCheck = tk.IntVar()
        creatorIDCheck.set(configSettings['Batch Rename']['creatoridcheck'])
        creatorIDCheckbox = tk.Checkbutton(optionsFrame, variable=creatorIDCheck, text='Creator ID', bg=windowColor, fg=textColor, selectcolor=windowColor)
        creatorIDCheckbox.pack(anchor='w')

        creatorIDCombobox = Combobox(optionsFrame, values=creatorIDList, background=windowColor, width=28, height=10)
        creatorIDCombobox.pack(padx=20, pady=5)
        creatorIDCombobox.insert(0, configSettings['Batch Rename']['creatoridinput'])

        sourceIDCheck = tk.IntVar()
        sourceIDCheck.set(configSettings['Batch Rename']['sourceidcheck'])
        sourceIDCheckbox = tk.Checkbutton(optionsFrame, variable=sourceIDCheck, text='Source ID', bg=windowColor, fg=textColor, selectcolor=windowColor)
        sourceIDCheckbox.pack(anchor='w')

        sourceIDCombobox = Combobox(optionsFrame, values=sourceIDList, background=windowColor, width=28, height=10)
        sourceIDCombobox.pack(padx=20, pady=5)
        sourceIDCombobox.insert(0, configSettings['Batch Rename']['sourceidinput'])

        #USER & VENDOR CATEGORY
        Separator(optionsFrame, orient='horizontal').pack(fill='x')
        userCatCheck = tk.IntVar()
        userCatCheck.set(configSettings['Batch Rename']['usercatcheck'])
        userCatCheckbox = tk.Checkbutton(optionsFrame, variable=userCatCheck, text='User Category', bg=windowColor, fg=textColor, selectcolor=windowColor)
        userCatCheckbox.pack(anchor='w')

        userCatInput = configSettings['Batch Rename']['usercatinput']
        userCatCombobox = Combobox(optionsFrame, values=userCatList, background=windowColor, width=28, height=10)
        userCatCombobox.insert(0, userCatInput)
        userCatCombobox.pack(padx=20, pady=5)
        userCatCombobox.insert(0, configSettings['Batch Rename']['usercatinput'])

        vendorCatCheck = tk.IntVar()
        vendorCatCheck.set(configSettings['Batch Rename']['vendorcatcheck'])
        vendorCatCheckbox = tk.Checkbutton(optionsFrame, variable=vendorCatCheck, text='Vendor Category', bg=windowColor, fg=textColor, selectcolor=windowColor)
        vendorCatCheckbox.pack(anchor='w')

        vendorCatInput = configSettings['Batch Rename']['vendorcatinput']
        vendorCatCombobox = Combobox(optionsFrame, values=vendorCatList, background=windowColor, width=28, height=10)
        vendorCatCombobox.insert(0, vendorCatInput)
        vendorCatCombobox.pack(padx=20, pady=5)
        vendorCatCombobox.insert(0, configSettings['Batch Rename']['vendorcatinput'])

        #USER DATA & NUMBERING
        Separator(optionsFrame, orient='horizontal').pack(fill='x')
        userDataCheck = tk.IntVar()
        userDataCheck.set(configSettings['Batch Rename']['userdatacheck'])
        userDataCheckbox = tk.Checkbutton(optionsFrame, variable=userDataCheck, text='User Data', bg=windowColor, fg=textColor, selectcolor=windowColor)
        userDataCheckbox.pack(anchor='w')
        
        userDataTextbox = tk.Text(optionsFrame, width=39, height=1, insertbackground=textColor, background=widgetBgColor, highlightthickness=0, foreground=textColor)
        userDataTextbox.pack(padx=20, pady=5, anchor='w')
        userDataTextbox.insert('1.0', configSettings['Batch Rename']['userdatainput'])

        numberingCheck = tk.IntVar()
        numberingCheck.set(configSettings['Batch Rename']['numberingcheck'])
        numberingCheckbox = tk.Checkbutton(optionsFrame, variable=numberingCheck, text='Numbering', bg=windowColor, fg=textColor, selectcolor=windowColor)
        numberingCheckbox.pack(anchor='w')

        numberingFrame = tk.Frame(optionsFrame, background=windowColor)
        numberingFrame.pack(padx=20, pady=5, anchor='w')

        tk.Label(numberingFrame, text='Start:', bg=windowColor, fg=textColor).pack(anchor='w', side='left')
        numberingInit = tk.IntVar()
        numberingInit.set(configSettings['Batch Rename']['numberinginput'])

        numberingWheel = Spinbox(numberingFrame, from_=0, to=9999, width=4, textvariable=numberingInit, background=widgetBgColor, highlightbackground=windowColor, foreground=textColor)
        numberingWheel.pack(padx=10, anchor='w', side='right')

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame)
        buttonFrame.grid(row=1, column=0, sticky='sw', pady=5)

        tk.Button(buttonFrame, width=10, text='OK', background=widgetBgColor, highlightbackground=windowColor, command=OKPress).pack(side='left')

        #BINDINGS
        catIDTextbox.bind('<KeyRelease>', textCheck)
        catIDTextbox.bind('<Up>', upArrow)
        catIDTextbox.bind('<Down>', downArrow)

        inFileTextbox.bind('<<Selection>>', updateCharCountLabel)
        inFileListbox.bind('<<ListboxSelect>>', updateInFileText)

        inFileListbox.drop_target_register(DND_FILES)
        inFileListbox.dnd_bind('<<Drop>>', addToInFileListbox)

        master.bind('<Return>', enterKey)

############################################################################################################################################
#BATCH CONFIRMATION WINDOW
class batchConfirmationWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.title('Batch Rename')

        rootFrame = tk.Frame(self, bg=windowColor)
        rootFrame.grid(padx=10, pady=10)

        self.configure(background=windowColor)

        #FUNCTIONS
        def updateListbox(list):
            for item in list:
                listbox.insert(END, item)

        def enterKey(event):
            OKPress()

        def OKPress():
            rewriteProgressWindow = tk.Tk()
            rewriteProgressWindow.title('Rewriting...')
            rewriteProgressbar = Progressbar(rewriteProgressWindow, length=280, mode='determinate')
            rewriteProgressbar.pack()

            rewriteIndex = 0
            while rewriteIndex < len(newFilename):
                os.replace(inDirectory[rewriteIndex] + '/' + inFilename[rewriteIndex] + inExtension[rewriteIndex], inDirectory[rewriteIndex] + '/' + newFilename[rewriteIndex])
                rewriteIndex += 1
                rewriteProgressbar['value'] += 100/len(newFilename)
            master.quit()

        def backPress():
            master.switchFrame(batchRenameWindow)

        #LABELS
        labelFrame = tk.Frame(rootFrame, background=windowColor)
        labelFrame.grid(row=0, column=0, sticky='w')
        tk.Label(labelFrame, text='Confirm batch rename:', bg=windowColor, fg=textColor).pack()

        #LISTBOX
        listboxFrame = tk.Frame(rootFrame, background=windowColor)
        listboxFrame.grid(column=0, row=1, sticky='w')
        listbox = tk.Listbox(listboxFrame, width=50, height=30, selectmode='single', activestyle='none', background=widgetBgColor, foreground=textColor)
        listbox.pack(pady=10)
        updateListbox(newFilename)

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame, background=windowColor)
        buttonFrame.grid(row=2, column=0, sticky='w')
        tk.Label(buttonFrame, text='This action cannot be undone.', bg=windowColor, fg=ucsLabelColor).pack(side='top', anchor='w')
        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='OK', command=OKPress).pack(side='left')
        tk.Button(buttonFrame, highlightbackground=windowColor, width=10, text='Back', command=backPress).pack(side='right')

        listbox.focus_set()

        master.bind('<Return>', enterKey)

############################################################################################################################################
#APP MAINLOOP()
if __name__ == '__main__':
    app = fnAsst()
    app.mainloop()