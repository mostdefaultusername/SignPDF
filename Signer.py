from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
from pathlib import Path
from pdf2image import convert_from_path
import os

canvas_size = 768
document_type = (("document file", "*.jpg *.jpeg *.pdf"),
                 ("pdf files", "*.pdf"), ("image files", "*.jpg *.jpeg"))
sign_type = (("stamp file","*.png"),)

class DocCanv(Canvas):
	#Document
	DocumentList=None
	DocumentImage = None
	DocResize = 1
	DocImgLink = None

	#Signature
	SignImage = None
	SignResize = DocResize
	SignImgLink = None
	SignObj = None


	def DocFile(self, use_in_func=False):
		if use_in_func is False:
			doc_path = filedialog.askopenfilename(filetypes=document_type)
			if (Path(doc_path).suffix).lower() == '.pdf':
				try:
					#try to use poppler from pyinstaller bundle temp directory
					self.DocumentList=convert_from_path(doc_path, poppler_path = os.path.join(sys._MEIPASS, "poppler") )
				except:
					#reserve for poppler
					self.DocumentList=convert_from_path(doc_path, poppler_path = "poppler" )
				self.DocumentImage=self.DocumentList[0]
			else:
				self.DocumentImage = Image.open(doc_path)
		(width, height) = self.DocumentImage.size
		self.DocResize = canvas_size / max(height, width)
		self.DocImgLink=ImageTk.PhotoImage(
           self.DocumentImage.resize((int(width * self.DocResize), int(height * self.DocResize)), Image.ANTIALIAS))
		self.create_image(0, 0, image=self.DocImgLink, anchor=NW)

	def SignFile(self):
		if self.SignImage is not None:
			self.MergeFile()
		sign_path = filedialog.askopenfilename(filetypes = sign_type)
		self.SignImage = Image.open(sign_path)
		(width, height) = self.SignImage.size
		self.SignResize=self.DocResize
		self.SignImgLink=ImageTk.PhotoImage(
           self.SignImage.resize((int(width * self.SignResize), int(height * self.SignResize)), Image.ANTIALIAS))
		self.SignObj = self.create_image(0, 0, image=self.SignImgLink, anchor=NW)

	def MoveSign(self, event):
		self.coords(self.SignObj, event.x, event.y)

	def ResizeSign(self, event):
		if event.delta > 0:
			self.SignResize = self.SignResize + 0.1
		else:
			self.SignResize = self.SignResize - 0.1

		(width, height) = self.SignImage.size
		self.SignImage.resize((int(width * self.SignResize), int(height * self.SignResize)), Image.ANTIALIAS)
		self.SignImgLink=ImageTk.PhotoImage(
           self.SignImage.resize((int(width * self.SignResize), int(height * self.SignResize)), Image.ANTIALIAS) )
		x, y = self.coords(self.SignObj)
		self.SignObj = self.create_image(x, y, image=self.SignImgLink, anchor=NW)

	def MergeFile(self):
		sign_coords =self.coords(self.SignObj)
		sign_coords = [(int)(x / self.DocResize) for x in sign_coords]
		(width, height) = self.SignImage.size
		width=int((width * self.SignResize)/self.DocResize)
		height=int((height * self.SignResize) / self.DocResize)
		ResizedSign=self.SignImage.resize((width,height), Image.ANTIALIAS)
		self.DocumentImage.paste(ResizedSign, box=sign_coords , mask=ResizedSign.convert('RGBA'))
		self.DocFile(True)


	def SaveFile(self,f_type="jpg"):
		self.MergeFile()
		SavePath=filedialog.asksaveasfilename()
		if (SavePath.split('.'))[-1]!=f_type:
    			SavePath=(SavePath.split('.'))[0]+'.'+f_type
		self.DocumentImage.save(SavePath)





root = Tk()
root.title("Documents signer")
DocCan = DocCanv(root, width=canvas_size, height=canvas_size)
DocCan.pack(side='right', fill=BOTH, expand=1)
MenuFrame = Frame(root, width=120, bg='gray22')
MenuFrame.pack(side='right', fill=Y)

OpenDocBtn = Button(MenuFrame, text='Open Document',command=DocCan.DocFile)
OpenDocBtn.pack(fill=X, padx=5,pady=3)
OpenDocBtn = Button(MenuFrame, text='Open sign',command=DocCan.SignFile)
OpenDocBtn.pack(fill=X, padx=5,pady=3)
OpenDocBtn = Button(MenuFrame, text='Save as pdf',command = lambda arg1=DocCan, arg2='pdf': DocCanv.SaveFile(arg1,arg2))
OpenDocBtn.pack(fill=X, padx=5,pady=3)
OpenDocBtn = Button(MenuFrame, text='Save as jpg',command = lambda arg1=DocCan, arg2='jpg': DocCanv.SaveFile(arg1,arg2))
OpenDocBtn.pack(fill=X, padx=5,pady=3)

DocCan.bind("<B1-Motion>", DocCan.MoveSign)
DocCan.bind("<MouseWheel>", DocCan.ResizeSign)


root.mainloop()
