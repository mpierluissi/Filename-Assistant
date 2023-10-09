#FILENAME ASSISTANT v4.0.0.2
#by Michael Pierluissi

############################################################################################################################################
#LIBRARY IMPORTS
from collections import defaultdict
import configparser
import csv
import os
import pyperclip
import re
import requests
import subprocess
import tkinter as tk
from tkinter.ttk import Combobox, Spinbox, Separator
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import END, Menu, messagebox, Spinbox

############################################################################################################################################
#DECLARE RELATIVE PATH
relpath = os.path.dirname(__file__)

#MASTER VARIABLES
ucsLabelColor = '#c62828'

ucsLabelText = 'Helvetica 10 bold'
catIDListboxText='Courier 14'
catIDLabelText = 'Helvetica 12 bold'
textBoxText = 'Helvetica 12'
noticeTextText = 'Helvetica 10 bold'

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
ucsURL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ_iljxJvLxjpbbaUTnnp_ij2S5iLl-U4lmS5dmiHfkcIWgI-LH7zDhl8iLWig-Q/pub?output=csv'

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
    catList.append(catIDData[x][2] + '                                ' + '   ' + catIDData[x][5] + '   ' + catIDData[x][4] + '   ' + '|')

#COMBOBOX LISTS
userListFile = relpath + '/data/userLists.cfg'

lists = configparser.ConfigParser(allow_no_value=True)
lists.read(userListFile)

############################################################################################################################################
#MASTER FUNCTIONS
def openUserLists():
    subprocess.call(['open', userListFile])

def openUCSDoc():
    subprocess.call(['open', relpath + 'data/UCS Filenaming Documentation.pdf'])

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
    inList = defaultdict(list)
    for i,item in enumerate(seq):
        inList[item].append(i)
    return ((key,locs) for key,locs in inList.items() if len(locs)>1)

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
        curWindowGeometry = str(self.geometry())
        posLoc = 0
        for item in curWindowGeometry:
            if item == '+':
                break
            posLoc += 1
        updateConfigVar('Window Settings', 'windowposition', '480x760' + curWindowGeometry[posLoc:])

        self.destroy()

    def runBatchRename(self):
        self.switchFrame(batchRenameWindow)

############################################################################################################################################
#CATEGORY ID
class categoryIDWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.resizable(False, False)
        master.title('Category ID')
        master.iconbitmap(relpath + '\data\icon.ico')

        rootFrame = tk.Frame(self)
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

        catIDBox = Combobox(rootFrame, values=catList)
        catIDBox.pack()

############################################################################################################################################
#BATCH RENAME
class batchRenameWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.resizable(False, False)
        master.title('Batch Rename')

        rootFrame = tk.Frame(self)
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
        inFileFrame = tk.Frame(rootFrame)
        inFileFrame.grid(row=0, column=0, pady=5, sticky='nw')

        inFileTextbox = tk.Text(inFileFrame, height=1, highlightthickness=0)
        inFileTextbox.pack(fill='x', pady=5)

        charCountLabel = tk.Label(inFileFrame, text='Characters: ')
        charCountLabel.pack(anchor='w', pady=(0, 5))

        inFileListbox = tk.Listbox(inFileFrame, selectmode='single', activestyle='none', height=40, font='Arial 10')
        inFileListbox.pack(fill='x')

        fileCountLabel = tk.Label(inFileFrame, text='Files:')
        fileCountLabel.pack(anchor='w')

        refillIndex = 0
        for item in inFilename:
            inFileListbox.insert(END, item + inExtension[refillIndex])
            refillIndex += 1
            fileCountLabel['text'] = 'Files: ' + str(len(inFilename))

        #OPTIONS
        optionsFrame = tk.Frame(rootFrame)
        optionsFrame.grid(padx=10, pady=5, row=0, column=1, rowspan=3, sticky='nw')
        Separator(optionsFrame, orient='vertical').pack(fill='y', side='left')

        #FIND & REPLACE
        findReplaceCheck = tk.IntVar()
        findReplaceCheck.set(configSettings['Batch Rename']['findandreplacecheck'])
        findReplaceCheckbox = tk.Checkbutton(optionsFrame, variable=findReplaceCheck, text='Find & Replace')
        findReplaceCheckbox.pack(anchor='w')

        findReplaceFrame = tk.Frame(optionsFrame)
        findReplaceFrame.pack(padx=20, pady=(0, 5), anchor='w')

        FRLabelFrame = tk.Frame(findReplaceFrame)
        FRLabelFrame.pack(side='left')
        tk.Label(FRLabelFrame, text='Find:').pack(pady=5, anchor='w')
        tk.Label(FRLabelFrame, text='Replace:').pack(anchor='w')

        FRTextFrame = tk.Frame(findReplaceFrame)
        FRTextFrame.pack(padx=(10, 0), side='right')
        findTextBox = tk.Text(FRTextFrame, height=1, width=29, highlightthickness=0)
        findTextBox.insert('1.0', configSettings['Batch Rename']['findInput'])
        replaceTextBox = tk.Text(FRTextFrame, height=1, width=29, highlightthickness=0)
        replaceTextBox.insert('1.0', configSettings['Batch Rename']['replaceInput'])
        
        findTextBox.pack(pady=5, anchor='e')
        replaceTextBox.pack(anchor='e')
        
        #CATEGORY ID
        Separator(optionsFrame, orient='horizontal').pack(fill='x')
        catIDCheck = tk.IntVar()
        catIDCheck.set(configSettings['Batch Rename']['catidcheck'])
        catIDCheckbox = tk.Checkbutton(optionsFrame, variable=catIDCheck, text='Category ID')
        catIDCheckbox.pack(anchor='w')
        
        catIDFrame = tk.Frame(optionsFrame)
        catIDFrame.pack(padx=20, pady=5, anchor='w')

        catIDTextbox = tk.Text(catIDFrame, width=20, height=1, highlightthickness=0, font=textBoxText)
        catIDTextbox.pack(pady=(0, 5), anchor='w', fill='x')
        catIDListbox = tk.Listbox(catIDFrame, width=35, height=5, selectmode='single', activestyle='none', font='Courier 14', exportselection=False)
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
        filenameCheckbox = tk.Checkbutton(optionsFrame, variable=filenameCheck, text='Clear & Replace Filename')
        filenameCheckbox.pack(anchor='w')

        filenameTextbox = tk.Text(optionsFrame, width=39, height=1, highlightthickness=0)
        filenameTextbox.pack(padx=20, pady=5, anchor='w')
        filenameTextbox.insert('1.0', configSettings['Batch Rename']['filenameinput'])

        #TRIM
        trimCheck = tk.IntVar()
        trimCheck.set(configSettings['Batch Rename']['trimcheck'])
        trimCheckbox = tk.Checkbutton(optionsFrame, variable=trimCheck, text='Trim Filename')
        trimCheckbox.pack(anchor='w')

        trimFrame = tk.Frame(optionsFrame)
        trimFrame.pack(padx=20, anchor='w')

        trimLabelFrame = tk.Frame(trimFrame)
        trimLabelFrame.pack(side='left')

        tk.Label(trimLabelFrame, text='From Beginning:').pack(pady=(0, 5), anchor='w')
        tk.Label(trimLabelFrame, text='From End:').pack(anchor='w')

        spinboxFrame = tk.Frame(trimFrame)
        spinboxFrame.pack(padx=(10, 0), side='right')

        fromInit = tk.IntVar()
        fromInit.set(configSettings['Batch Rename']['frominput'])

        fromWheel = Spinbox(spinboxFrame, from_=0, to=999, width=3, textvariable=fromInit)
        fromWheel.pack()

        toInit = tk.IntVar()
        toInit.set(configSettings['Batch Rename']['toinput'])

        toWheel = Spinbox(spinboxFrame, from_=0, to=999, width=3, textvariable=toInit)
        toWheel.pack()

        #CREATOR & SOURCE ID
        Separator(optionsFrame, orient='horizontal').pack(fill='x')
        creatorIDCheck = tk.IntVar()
        creatorIDCheck.set(configSettings['Batch Rename']['creatoridcheck'])
        creatorIDCheckbox = tk.Checkbutton(optionsFrame, variable=creatorIDCheck, text='Creator ID')
        creatorIDCheckbox.pack(anchor='w')

        creatorIDCombobox = Combobox(optionsFrame, values=creatorIDList, font=textBoxText, width=28, height=10)
        creatorIDCombobox.pack(padx=20, pady=5)
        creatorIDCombobox.insert(0, configSettings['Batch Rename']['creatoridinput'])

        sourceIDCheck = tk.IntVar()
        sourceIDCheck.set(configSettings['Batch Rename']['sourceidcheck'])
        sourceIDCheckbox = tk.Checkbutton(optionsFrame, variable=sourceIDCheck, text='Source ID')
        sourceIDCheckbox.pack(anchor='w')

        sourceIDCombobox = Combobox(optionsFrame, values=sourceIDList, font=textBoxText, width=28, height=10)
        sourceIDCombobox.pack(padx=20, pady=5)
        sourceIDCombobox.insert(0, configSettings['Batch Rename']['sourceidinput'])

        #USER & VENDOR CATEGORY
        Separator(optionsFrame, orient='horizontal').pack(fill='x')
        userCatCheck = tk.IntVar()
        userCatCheck.set(configSettings['Batch Rename']['usercatcheck'])
        userCatCheckbox = tk.Checkbutton(optionsFrame, variable=userCatCheck, text='User Category')
        userCatCheckbox.pack(anchor='w')

        userCatInput = configSettings['Batch Rename']['usercatinput']
        userCatCombobox = Combobox(optionsFrame, values=userCatList, font=textBoxText, width=28, height=10)
        userCatCombobox.insert(0, userCatInput)
        userCatCombobox.pack(padx=20, pady=5)
        userCatCombobox.insert(0, configSettings['Batch Rename']['usercatinput'])

        vendorCatCheck = tk.IntVar()
        vendorCatCheck.set(configSettings['Batch Rename']['vendorcatcheck'])
        vendorCatCheckbox = tk.Checkbutton(optionsFrame, variable=vendorCatCheck, text='Vendor Category')
        vendorCatCheckbox.pack(anchor='w')

        vendorCatInput = configSettings['Batch Rename']['vendorcatinput']
        vendorCatCombobox = Combobox(optionsFrame, values=vendorCatList, font=textBoxText, width=28, height=10)
        vendorCatCombobox.insert(0, vendorCatInput)
        vendorCatCombobox.pack(padx=20, pady=5)
        vendorCatCombobox.insert(0, configSettings['Batch Rename']['vendorcatinput'])

        #USER DATA & NUMBERING
        Separator(optionsFrame, orient='horizontal').pack(fill='x')
        userDataCheck = tk.IntVar()
        userDataCheck.set(configSettings['Batch Rename']['userdatacheck'])
        userDataCheckbox = tk.Checkbutton(optionsFrame, variable=userDataCheck, text='User Data')
        userDataCheckbox.pack(anchor='w')
        
        userDataTextbox = tk.Text(optionsFrame, width=39, height=1, highlightthickness=0)
        userDataTextbox.pack(padx=20, pady=5, anchor='w')
        userDataTextbox.insert('1.0', configSettings['Batch Rename']['userdatainput'])

        numberingCheck = tk.IntVar()
        numberingCheck.set(configSettings['Batch Rename']['numberingcheck'])
        numberingCheckbox = tk.Checkbutton(optionsFrame, variable=numberingCheck, text='Numbering')
        numberingCheckbox.pack(anchor='w')

        numberingFrame = tk.Frame(optionsFrame)
        numberingFrame.pack(padx=20, pady=5, anchor='w')

        tk.Label(numberingFrame, text='Start:').pack(anchor='w', side='left')
        numberingInit = tk.IntVar()
        numberingInit.set(configSettings['Batch Rename']['numberinginput'])

        numberingWheel = Spinbox(numberingFrame, from_=0, to=9999, width=4, textvariable=numberingInit)
        numberingWheel.pack(padx=10, anchor='w', side='right')

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame)
        buttonFrame.grid(row=1, column=0, sticky='sw', pady=5)

        tk.Button(buttonFrame, width=10, text='OK', command=OKPress).pack(side='left')

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

        rootFrame = tk.Frame(self)
        rootFrame.grid(padx=10, pady=10)

        #FUNCTIONS
        def updateListbox(list):
            for item in list:
                listbox.insert(END, item)

        def enterKey(event):
            OKPress()

        def OKPress():
            rewriteIndex = 0
            while rewriteIndex < len(newFilename):
                os.replace(inDirectory[rewriteIndex] + '/' + inFilename[rewriteIndex] + inExtension[rewriteIndex], inDirectory[rewriteIndex] + '/' + newFilename[rewriteIndex])
                rewriteIndex += 1
            
            clearBRCache()
            master.switchFrame(categoryIDWindow)

        def backPress():
            master.switchFrame(batchRenameWindow)

        def clearBRCache():
            global inDirectory
            global inFullFilename
            global inFilename
            global inExtension

            inDirectory = []
            inFullFilename = []
            inFilename = []
            inExtension = []

        #LABELS
        labelFrame = tk.Frame(rootFrame)
        labelFrame.grid(row=0, column=0, sticky='w')
        tk.Label(labelFrame, text='Confirm batch rename:').pack()

        #LISTBOX
        listboxFrame = tk.Frame(rootFrame)
        listboxFrame.grid(column=0, row=1, sticky='w')
        listbox = tk.Listbox(listboxFrame, width=50, height=30, selectmode='single', activestyle='none')
        listbox.pack(pady=10)
        updateListbox(newFilename)

        #BUTTONS
        buttonFrame = tk.Frame(rootFrame)
        buttonFrame.grid(row=2, column=0, sticky='w')
        tk.Label(buttonFrame, text='This action cannot be undone.', fg=ucsLabelColor).pack(side='top', anchor='w')
        tk.Button(buttonFrame, width=10, text='OK', command=OKPress).pack(side='left')
        tk.Button(buttonFrame, width=10, text='Back', command=backPress).pack(side='right')

        listbox.focus_set()

        master.bind('<Return>', enterKey)

############################################################################################################################################
#APP MAINLOOP()
if __name__ == '__main__':
    app = fnAsst()
    app.mainloop()