#-*- coding:utf-8 -*-
from tooltip import *
import json
import tkinter.font as tkFont
from tkinter.filedialog import askdirectory,askopenfilename
from  tkinter  import ttk
import tkinter
import copy
import argparse
import webbrowser
class Annotation(object):

    def __init__(self, arg):
        self.annotations = []
        self.annotations_stack = []
        self.stack_point = 0
        self.idx_anno = {}
        self.desc_zh = json.load(open('ZH-desciption.json', 'r'))
        self.desc_en = json.load(open('EN-desciption.json', 'r'))
        self.candidates = json.load(open('candidates.json','r'))
        self.entity2path = json.load(open('entity2path_simple.json', 'r'))
        self.fp = json.load(open('fp_simple.json','r'))
        self.hightype = json.load(open('100type.json','r'))
        self.path = None
        self.dataset = []
        self.width = 100
        self.height = 20
        self.arg = arg
        self.reset_flag = 0
        self.direct = 'X'
        self.mainUI()

    def open_wiki(self,event):
        title = self.dataset[self.idx]['entity']
        webbrowser.open('https://en.wikipedia.org/wiki/%s'%title, new=0, autoraise=True)

    def translate(self, event):
        print('translation!')
        widget = event.widget
        text = widget.selection_get()
        for s in self.annotations:
            text = text.replace('['+s[3]+']','')
        print(translate(text, 'EN', 'zh-CN'))

    def mainUI(self):
        root = Tk()

        label_h = self.label_h = 20
        text_h = self.text_h = self.arg.heightY

        menubar = Menu(root)
        menubar.add_command(label="Open", command=lambda :self.selectPath(menubar))
        menubar.add_command(label="Typing", command=lambda :self.type_select(menubar))
        menubar.add_command(label="Export", command=lambda :self.export_annotations(menubar))
        menubar.add_command(label="Reset", command=lambda: self.reset(menubar))
        menubar.add_command(label="Link", command=lambda: self.linking(menubar))

        root.config(menu=menubar)

        self.h = h = root.winfo_screenheight()
        self.w = w = root.winfo_screenwidth()
        self.wgap = 20
        self.hgap = (h-label_h-text_h-50)/12-self.height

        root.geometry('%dx%d'%(w,h))

        root.bind('<o>',self.selectPath)
        root.bind('<e>', self.export_annotations)

        self.vertical_shift = 0
        self.horizon_shift = 0

        root.bind('<w>', self.shift)
        root.bind('<s>', self.shift)
        root.bind('<a>', self.shift)
        root.bind('<d>', self.shift)
        root.bind('<W>', self.shift)
        root.bind('<S>', self.shift)
        root.bind('<A>', self.shift)
        root.bind('<D>', self.shift)
        root.bind('<c>', self.change_direction)

        t1 = Frame(root)
        #t1.pack(pady=20,side=RIGHT,fill=BOTH)
        t2 = Frame(root)
        t2.pack(side=LEFT,fill=BOTH,expand=True)
        ft = tkFont.Font(family='Times New Roman', size=15, weight=tkFont.BOLD)
        Button(t1, text="open", command=self.selectPath).pack(side=TOP, padx=10, pady=50, anchor=NW)

        self.button = Button(t1, text='typing', command=self.type_select)
        #self.button.pack(padx=10, pady=0, side=TOP,anchor=NW)

        self.export_button = Button(t1, text='export', command=self.export_annotations)

        self.entityLabel = Label(t1, text='Entity selected')
        #self.entityLabel.pack(side=TOP, anchor=NW,padx=10)
        self.lb = Listbox(t1)
        #self.lb.pack(side=TOP, fill=Y,padx=10,expand=True)

        self.lb.bind('<Double-Button-1>', self.delete_annotation)
        self.lb.bind('<Control-a>', self.entity_bg)
        self.lb.bind('<Control-b>', self.return_pos)
        self.lbset = []

        if self.direct=='Y':
            self.f1=Frame(t2)
            self.f1.place(x=0,y=0,width=w-20,height=label_h)
            self.f2=Frame(t2)
            self.f2.place(x=0,y=label_h,width=w-20,height=text_h)
            self.f3=Frame(t2)
            self.f3.place(x=0,y=text_h+label_h,width=w-20,height=h-text_h-label_h)
            self.f4 = Frame(t2)
            self.f4.place(x=self.w/2,y=text_h+label_h+10,width=w/2-40,height=100)
            self.docName = StringVar()
            self.docLabel = Label(self.f1,textvariable = self.docName)
            #self.docLabel.pack(side=TOP)
            self.docLabel.pack(fill=X,expand=True)
            #self.text = scrolledtext.ScrolledText(t2, width=1920, height=1080, wrap =WORD)
            self.text = Text(self.f2,font=ft)
            self.text.config(state=DISABLED)
            self.add_scrollbar(self.f2, self.text, 'Y')
            self.text.bind('<t>', self.type_select)
            self.text.bind('<b>', self.open_wiki)
            self.text.bind('<f>', self.translate)
            self.text.bind('<z>', self.text_undo)
            self.text.bind('<y>', self.text_redo)
            #self.text.pack(side=TOP,fill=X,expand=True)
            self.text.pack(side=TOP,fill=X)
            self.type_select_win = Frame(self.f3)
            self.type_select_win.pack(side=TOP,fill=BOTH,expand=True)#place(x=0,y=0,width=w,height=h/4*3,anchor=NW)
        else:
            self.f1=Frame(t2)
            self.f1.place(x=0,y=0,width=w/2,height=label_h)
            self.f2=Frame(t2)
            self.f2.place(x=0,y=label_h,width=w/2,height=self.arg.heightX-label_h)
            self.f3=Frame(t2)
            self.f3.place(x=w/2,y=0,width=w/2,height=h)
            self.f4 = Frame(t2)
            self.f4.place(x=0,y=self.arg.heightX,width=w/2-40,height=100)
            self.docName = StringVar()
            self.docLabel = Label(self.f1,textvariable = self.docName)
            #self.docLabel.pack(side=TOP)
            self.docLabel.pack(fill=X,expand=True)
            #self.text = scrolledtext.ScrolledText(t2, width=1920, height=1080, wrap =WORD)
            self.text = Text(self.f2,font=ft)
            self.text.config(state=DISABLED)
            self.add_scrollbar(self.f2, self.text, 'Y')
            self.text.bind('<t>', self.type_select)
            self.text.bind('<b>', self.open_wiki)
            self.text.bind('<f>', self.translate)
            self.text.bind('<z>', self.text_undo)
            self.text.bind('<y>', self.text_redo)
            #self.text.pack(side=TOP,fill=X,expand=True)
            self.text.pack(side=TOP,fill=X)
            self.type_select_win = Frame(self.f3)
            self.type_select_win.pack(side=TOP,fill=BOTH,expand=True)#place(x=0,y=0,width=w,height=h/4*3,anchor=NW)


        root.mainloop()

    def change_direction(self, event):
        if self.direct == 'X':
            self.direct = 'Y'
        elif self.direct == 'Y':
            self.direct = 'X'

        if self.direct=='X':
            self.f1.place(x=0, y=0, width=self.w / 2, height=self.label_h)
            self.f2.place(x=0, y=self.label_h, width=self.w / 2, height=self.arg.heightX - self.label_h)

            self.f4.place(x=0, y=self.arg.heightX, width=self.w / 2-40, height=100)
            self.f3.place(x=self.w / 2, y=0, width=self.w / 2, height=self.h)
            #self.f4.place(x=0, y=self.h / 2, width=self.w / 2, height=self.h / 2)
            cvs_width = self.w / 2
            cvs_height = self.h
        else:
            self.f1.place(x=0, y=0, width=self.w - 20, height=self.label_h)
            self.f2.place(x=0, y=self.label_h, width=self.w - 20, height=self.text_h)
            self.f4.place(x=self.w / 2, y=self.text_h + self.label_h + 10, width=self.w / 2-40, height=100)
            self.f3.place(x=0, y=self.text_h + self.label_h, width=self.w - 20, height=self.h - self.text_h - self.label_h)
            cvs_width = self.w
            cvs_height = self.h - self.label_h - self.text_h  # self.type_select_win.winfo_screenmmheight()

        if self.max_height > cvs_height:
            self.unseen_height = self.max_height - cvs_height
        else:
            self.unseen_height = 0

        if self.max_width > cvs_width:
            self.unseen_width = self.max_width - cvs_width
        else:
            self.unseen_width = 0
        self.cvs['scrollregion'] = (0, 0, cvs_width + self.unseen_width, cvs_height + self.unseen_height)
            #self.f4.destroy()
    def find_idx(self):
        try:
            s_text = self.text.selection_get()
            line_no, end = self.text.index(INSERT).split('.')
            end = int(end) - 1
            line_no = int(line_no) - 1
            begin = end - len(s_text) + 1
        except TclError as e:
            line_no, end = self.text.index(INSERT).split('.')
            end = int(end) - 1
            line_no = int(line_no) - 1
            begin = end
        begin, end, idx = self.find_annotation_index(begin, end, line_no)
        return idx

    def linking(self, event):
        self.lk_w = Tk()
        self.lk_w.geometry('500x400')
        # self.lk_text = Entry(self.lk_w)
        # self.lk_text.pack(side=TOP)
        # self.lk_button = Button(self.lk_w,text='click',command = self.linking_process)
        # self.lk_button.pack(side=TOP)
        self.lk_lb = Listbox(self.lk_w)
        self.lk_lb.pack(side=TOP,fill=X)
        idx = self.find_idx()
        self.idx = idx
        for c in self.candidates[self.dataset[self.idx]['surface_name'].lower()]:
            self.lk_lb.insert(END, c)
        self.lk_lb.bind('<Button-1>', self.linking_process)
        self.lk_lb.bind('<b>', self.open_wiki)
        self.lk_w.mainloop()

    def linking_process(self, event):
        try:
            index = int(self.lk_lb.curselection()[0])
        except TclError:
            pass
        value = self.lk_lb.get(index)
        self.dataset[self.idx]['entity'] = value
        self.type_select()
        return


    # def linking_process(self):
    #     idx = self.find_idx()
    #     self.dataset[idx]['entity'] = self.lk_text.get()
    #     for c in self.candidates[self.dataset[idx]['surface_name'].lower()]:
    #         print(c)
    #     self.lk_w.destroy()

    def reset(self, event):

        self.annotations_ = copy.deepcopy(self.annotations)
        self.annotations_stack_ = copy.deepcopy(self.annotations_stack)
        self.idx_anno_ = copy.deepcopy(self.idx_anno)
        self.stack_point_ = self.stack_point
        for i in range(len(self.dataset)):
            self.idx_anno[i] = 'root'
        self.stack_bound_ = self.stack_bound
        for i in range(len(self.dataset)):
            self.remove_annotation(self.dataset[i]['line_no'],i)
        self.annotations = []
        self.annotations_stack = []
        self.stack_point = 0
        self.stack_bound = 0
        self.reset_flag = 1

    def text_undo(self,event):
        if self.reset_flag == 1:
            self.stack_bound = self.stack_bound_
            self.annotations_stack = copy.deepcopy(self.annotations_stack_)
            self.stack_point = self.stack_point_
            self.idx_anno = copy.deepcopy(self.idx_anno_)
            for annotation in self.annotations_:
                idx,node,line_no = annotation[-3],annotation[-2],annotation[-1]
                self.insert_annotation(line_no, idx, node)
            self.reset_flag = 0
            return
        self.stack_point -= 1
        if self.stack_point<self.stack_bound-1:
            self.stack_point = self.stack_bound-1
        else:
            idx = self.annotations_stack[self.stack_point+1][0]
            line_no = self.annotations_stack[self.stack_point+1][2]
            node = 'root'
            i = self.stack_point
            print(self.annotations_stack)
            while True:
                if i<0:
                    break
                if self.annotations_stack[i][0] == idx:
                    node = self.annotations_stack[i][1]
                    break
                i = i - 1
                if i < 0:
                    break
            self.remove_annotation(line_no, idx)
            print(node)
            self.insert_annotation(line_no, idx, node)

    def text_redo(self,event):
        print('redo')
        self.stack_point += 1
        if self.stack_point>len(self.annotations_stack)-1:
            self.stack_point = len(self.annotations_stack)-1
        else:
            idx = self.annotations_stack[self.stack_point][0]
            node = self.annotations_stack[self.stack_point][1]
            line_no = self.annotations_stack[self.stack_point][2]
            self.remove_annotation(line_no,idx)
            self.insert_annotation(line_no, idx, node)

    def shift(self,event):
        if event.char == 'a':
            self.horizon_shift -= 1
        if event.char == 'd':
            self.horizon_shift += 1
        if event.char == 'w':
            self.vertical_shift -= 1
        if event.char == 's':
            self.vertical_shift += 1
        if event.char == 'A':
            self.horizon_shift = -100
        if event.char == 'D':
            self.horizon_shift = 100
        if event.char == 'W':
            self.vertical_shift = -100
        if event.char == 'S':
            self.vertical_shift = 100
        #print(self.vertical_shift,self.horizon_shift)

        hp = 50
        vp = 50

        if self.horizon_shift <0:
            self.horizon_shift = 0
        if self.horizon_shift>int((self.unseen_width+hp-1)/hp):
            self.horizon_shift = int((self.unseen_width+hp-1)/hp)

        if self.vertical_shift <0:
            self.vertical_shift = 0
        if self.vertical_shift>int((self.unseen_height+vp-1)/vp):
            self.vertical_shift = int((self.unseen_height+vp-1)/vp)

        shift_v = self.vertical_shift*vp
        shift_h = self.horizon_shift*hp
        self.cvs.delete(ALL)
        self.draw_tree('root', 0, shift_v, shift_h)

    def export_annotations(self,event):
        try:
            with open(self.path,'w',encoding='utf-8') as f:
                for content in self.content:
                    f.write(content)
                f.write('%%TYPE_ANNOTATIONS%%\n')
                idxmap={}
                for annotation in self.annotations:
                    idx = annotation[2]
                    typing = annotation[3]
                    idxmap[idx] = typing
                for i,data in enumerate(self.dataset):
                    if i in idxmap:
                        f.write(str(data['start']) + '\t' + str(data['end']) + '\t' + data['entity'] + '\t' + idxmap[i] + '\n')
                    else:
                        f.write(str(data['start']) + '\t' + str(data['end']) + '\t' + data['entity'] + '\n')
            tkinter.messagebox.showinfo('提示', '导出成功')
        except Exception as e:
            print(e)
            tkinter.messagebox.showinfo('提示', '导出失败')

    def delete_annotation(self,event):
        try:
            index = int(self.lb.curselection()[0])
        except TclError:
            pass
        self.text.tag_delete('tag3')
        value = self.lb.get(index)
        self.lb.delete(index)
        idx=index
        del self.lbset[index]
        cur_annotation = self.annotations[idx]
        cur_annotation_len = cur_annotation[1]-cur_annotation[0]+1
        line_no = cur_annotation[-1]
        self.change_annotation_offset(cur_annotation[2], cur_annotation_len, line_no, -1)

        entity_len = int(self.dataset[cur_annotation[2]]['end'] - self.dataset[cur_annotation[2]]['start'] + 1)
        self.text.tag_add('tag', '%d.%d'%(line_no+1, cur_annotation[0]-1-entity_len+1), '%d.%d'%(line_no+1, cur_annotation[0]))
        self.text.config(state=NORMAL)
        self.text.delete('%d.%d'%(line_no+1, cur_annotation[0]),'%d.%d'%(line_no+1, cur_annotation[1]+1))
        self.text.config(state=DISABLED)
        del self.annotations[idx]
        return

    def entity_bg(self, event):
        try:
            index = int(self.lb.curselection()[0])
        except TclError:
            pass
        annotation = self.annotations[index]
        entity_len = self.dataset[annotation[2]]['end']-self.dataset[annotation[2]]['start']+1
        end = annotation[0]-1
        line_no = annotation[-1]
        begin = end - entity_len + 1

        self.scan_line = int(self.text.index(INSERT).split('.')[0])
        self.text.tag_delete('tag3')
        self.text.see('%d.1'%(line_no+1))
        self.text.tag_add('tag3', '%d.%d'%(line_no+1,begin), '%d.%d'%(line_no+1, end+1))
        self.text.tag_config('tag3', background='gray')

    def return_pos(self, event):
        try:
            index = int(self.lb.curselection()[0])
        except TclError:
            pass
        annotation = self.annotations[index]
        entity_len = self.dataset[annotation[2]]['end']-self.dataset[annotation[2]]['start']+1
        end = annotation[0]-1
        line_no = annotation[-1]
        begin = end - entity_len + 1

        if self.scan_line>0:
            self.text.see('%d.1' % (self.scan_line))
        self.text.tag_delete('tag3')

    def change_annotation_offset(self, idx, l, line_no, direction):
        for annotation in self.annotations:
            if annotation[2] > idx and annotation[-1]==line_no:
                annotation[0]=annotation[0]+l*direction
                annotation[1]=annotation[1]+l*direction

    def find_annotation_index(self, begin, end, line_no):
        maxIntersect = -1
        idx = -1
        ori_begin = begin
        ori_end = end
        for i in range(len(self.annotations)):
            if not self.annotations[i][-1] == line_no:
                continue
            if begin>self.annotations[i][1]:
                ori_begin = ori_begin - (self.annotations[i][1]-self.annotations[i][0]+1)
                ori_end = ori_end - (self.annotations[i][1] - self.annotations[i][0] + 1)
        ori_begin = ori_begin + self.accumulate_char_num[line_no-1]
        ori_end = ori_end + self.accumulate_char_num[line_no-1]
        for i in range(len(self.dataset)):
            # if (dataset[i][0]==begin and dataset[i][1]==end):
            #     type_path = entity2path[dataset[i][2]]
            #     break
            if min(ori_end,self.dataset[i]['end'])-max(ori_begin,self.dataset[i]['start'])>maxIntersect:
                maxIntersect = min(ori_end,self.dataset[i]['end'])-max(ori_begin,self.dataset[i]['start'])
                idx = i
        begin = begin-ori_begin+self.dataset[idx]['start']
        end = end - ori_end+self.dataset[idx]['end']
        return begin, end, idx

    def search_annotation(self, idx):
        for i, annotation in enumerate(self.annotations):
            if idx == annotation[2]:
                return i
        return -1

    def remove_annotation(self,line_no,idx):
        pos = self.search_annotation(idx)
        if pos >= 0:
            self.change_annotation_offset(idx, self.annotations[pos][1] - self.annotations[pos][0] + 1, line_no, -1)
            self.text.config(state=NORMAL)
            self.text.delete('%d.%d' % (line_no + 1, self.annotations[pos][0]),
                             '%d.%d' % (line_no + 1, self.annotations[pos][1] + 1))
            self.text.config(state=DISABLED)
            del self.annotations[pos]

    def insert_annotation(self, line_no, idx, node):
        if node == 'root':
            self.idx_anno[idx] = node
            return

        acc_len = 0
        for i in range(len(self.dataset)):
            if self.dataset[i]['line_no'] == line_no:
                if i == idx:
                    end = self.dataset[i]['end']-self.accumulate_char_num[line_no-1]+acc_len
                else:
                    if self.idx_anno[i] == 'root':
                        pass
                    else:
                        acc_len += len(self.idx_anno[i])+2

        self.text.config(state=NORMAL)
        self.text.insert('%d.%d' % (line_no + 1, end + 1), '[' + node + ']')
        self.text.config(state=DISABLED)
        self.change_annotation_offset(idx, len(node) + 2, line_no, 1)
        self.annotations.append([end + 1, end + 2 + len(node), idx, node, line_no])

        self.idx_anno[idx] = node
        self.text.tag_add('tag1', '%d.%d' % (line_no + 1, end + 1), '%d.%d' % (line_no + 1, end + 1 + len(node) + 2))
        self.text.tag_config('tag1', foreground='blue')


    def confirm(self,event,node):
        #a = tk.messagebox.askokcancel('提示', '要选择这个类别吗?')
        a = True
        if a==True:
            try:
                s_text = self.text.selection_get()
                line_no, end = self.text.index(INSERT).split('.')
                end = int(end)-1
                line_no = int(line_no)-1
                begin = end-len(s_text)+1
            except TclError as e:
                line_no, end = self.text.index(INSERT).split('.')
                end = int(end)-1
                line_no = int(line_no) - 1
                begin = end

            begin, end, idx = self.find_annotation_index(begin,end,line_no)

            if self.reset_flag == 1:
                self.annotations_stack = []
                self.stack_point = 0
                self.stack_bound = 0
                self.reset_flag = 0

            del self.annotations_stack[self.stack_point + 1:]
            self.annotations_stack.append([idx, node, line_no])
            self.stack_point = len(self.annotations_stack) - 1

            self.remove_annotation(line_no,idx)
            self.insert_annotation(line_no, idx, node)
            #pos = self.search_annotation(idx)
            # if pos>=0:
            #     self.change_annotation_offset(idx, self.annotations[pos][1]-self.annotations[pos][0]+1, line_no, -1)
            #     self.text.config(state=NORMAL)
            #     self.text.delete('%d.%d'%(line_no+1, self.annotations[pos][0]),'%d.%d'%(line_no+1,self.annotations[pos][1]+1))
            #     self.text.config(state=DISABLED)
            #     del self.annotations[pos]
            #     self.lb.delete(pos)
            #     del self.lbset[pos]
            # if node=='root':
            #     self.type_select_win.destroy()
            #     return
            # self.text.config(state=NORMAL)
            # self.text.insert('%d.%d'%(line_no+1, end+1),'['+node+']')
            # self.text.config(state=DISABLED)
            # self.change_annotation_offset(idx, len(node) + 2, line_no, 1)

            #self.annotations.append([end+1, end+2+len(node), idx, node, line_no])
            # del self.annotations_stack[self.stack_point+1:]
            # self.annotations_stack.append([idx,node,line_no])
            # self.stack_point = len(self.annotations_stack)-1

            # self.text.tag_add('tag1', '%d.%d' % (line_no+1,end+1), '%d.%d' % (line_no+1, end + 1+len(node)+2))
            # self.text.tag_config('tag1', foreground='blue')
            self.type_select_win.destroy()
            # _,_,idx = self.find_annotation_index(begin,end,line_no)
            # self.lb.insert(END,self.dataset[idx][2])
            # self.lbset.append(idx)

    def filternum(self,name):
        i = 0
        for s in name:
            if ord(s)>=48 and ord(s)<=57:
                break
            i = i + 1
        return name[:i]

    def find(self, node, l, order, xx, yy):
        if not l in self.y2x:
            self.y2x[l] = -1
        if not node in self.son_:
            if xx > self.y2x[l]:
                self.y2x[l] = xx
                self.posx[node] = xx
                self.posy[node] = yy
                return 1
            else:
                if order == 0:
                    return 0
                else:
                    while (xx <= self.y2x[l]):
                        xx = xx + (self.width + self.wgap)
                    self.posx[node] = xx
                    self.posy[node] = yy
                    return 1
        else:
            if order == 0:
                if xx <= self.y2x[l]:
                    return 0
            else:
                while (xx <= self.y2x[l]):
                    xx = xx + (self.width + self.wgap)
            while True:
                flag = 1
                for i, s in enumerate(self.son_[node]):
                    if not self.find(s, l + 1, i, xx + i * (self.width + self.wgap), yy + (self.height + self.hgap)):
                        flag = 0
                        break
                if flag:
                    break
                else:
                    if order == 0:
                        return 0
                    else:
                        xx = xx + (self.width + self.wgap)
            self.y2x[l] = xx
            self.posx[node] = xx
            self.posy[node] = yy
            return 1

    def show_desc(self, event):
        self.desc_text.config(state=NORMAL)
        self.desc_text.delete('1.0', END)
        self.desc_text.insert('1.0',self.button2node[event.widget])
        self.desc_text.config(state=DISABLED)
        return

    def draw_tree(self, node, l, shift_v = 0, shift_h = 0):
        if self.init_flag==0:
            if not node in self.btn:
                if node in self.hightype:
                    self.btn[node] = Button(self.cvs, text=self.filternum(node), font=('微软雅黑', 8,tkFont.BOLD))
                else:
                    self.btn[node] = Button(self.cvs, text=self.filternum(node), font=('微软雅黑', 8))
                self.btn[node].bind('<Button-3>', self.show_desc)
                self.btn[node].bind('<Button-1>', lambda x: self.confirm(x, node))
        self.btn[node].place(x=self.posx[node]-int(shift_h), y=self.posy[node]-int(shift_v), width=self.width, height=self.height)
        if not node in self.desc_en:
            self.button2node[self.btn[node]] = ''
        else:
            if not self.desc_en[node]:
                self.button2node[self.btn[node]] = ''
            else:
                self.button2node[self.btn[node]] = node+':'+self.desc_en[node]+'\n'+ node+':'+self.desc_zh[node]
                #createToolTip(self.btn[node], self.desc[node])
        if self.unseen_height == -1:
            if self.posy[node]+self.height>self.max_height:
                self.max_height=self.posy[node]+self.height
        if self.unseen_width == -1:
            if self.posx[node]+self.width>self.max_width:
                self.max_width=self.posx[node]+self.width
        if not node in self.son:
            return
        for leaf in self.son[node]:
            self.cvs.create_line(self.posx[node] + self.width / 2-int(shift_h), self.posy[node] + self.height-int(shift_v),
                                 self.posx[leaf] + self.width / 2-int(shift_h), self.posy[leaf]-int(shift_v), arrow='last')
            self.draw_tree(leaf, l + 1,shift_v,shift_h)
        return

    def build_tree(self):
        # for path in self.type_path:
        #     node = 'root'
        #     for t in path[1:].split('/'):
        #         if not node in self.son:
        #             self.son[node] = []
        #         if not t in self.son[node]:
        #             self.son[node].append(t)
        #         node = t

        for path in self.type_path:
            node = 'root'
            for i, t in enumerate(path[1:].split('/')):
                self.nodes.append(t)
                if not node in self.son:
                    self.son[node] = []
                if not t in self.son[node]:
                    self.son[node].append(t)
                    if not t in self.ff:
                        self.ff[t] = [node]
                    else:
                        self.ff[t].append(node)
                    if not t in self.ru:
                        self.ru[t] = 1
                    else:
                        self.ru[t] = self.ru[t] + 1
                node = t

    def tp(self):
        while True:
            flag = 0
            for node in self.nodes:
                if self.ru[node] == 0:
                    flag = 1
                    self.ru[node] = -1
                    if not node in self.son:
                        continue
                    for s in self.son[node]:
                        self.ru[s] = self.ru[s] - 1
                        if not s in self.deep:
                            self.deep[s] = 0
                        if self.deep[node] + 1 > self.deep[s]:
                            self.deep[s] = self.deep[node] + 1
                            self.father[s] = node
            if flag == 0:
                break

    def shift_cal(self,event):
        cur_be, cur_end = self.vertical_bar.get()[0], self.vertical_bar.get()[1]
        len = cur_end - cur_be
        left = 1 - len
        shift_v = self.vertical_bar.get()[0] / left * self.unseen_height
        self.cvs.delete(ALL)
        self.draw_tree('root', 0, shift_v)
        return

    def add_scrollbar(self, t, widget, d='X'):
        if d=='X':
            hbar = Scrollbar(t, orient=HORIZONTAL)
            hbar.pack(side=BOTTOM, fill=X)
            hbar.config(command=widget.xview)
            widget.config(xscrollcommand=hbar.set)
            return hbar
        if d=='Y':
            vbar = Scrollbar(t, orient=VERTICAL)
            vbar.pack(side=RIGHT, fill=Y)
            vbar.config(command=widget.yview)
            widget.config(yscrollcommand=vbar.set)
            return vbar
        if d=='XY':
            hbar = Scrollbar(t, orient=HORIZONTAL)
            hbar.pack(side=BOTTOM, fill=X)
            hbar.config(command=widget.xview)
            vbar = Scrollbar(t, orient=VERTICAL)
            vbar.pack(side=RIGHT, fill=Y)
            vbar.config(command=widget.yview)
            widget.config(xscrollcommand=hbar.set,yscrollcommand=vbar.set)
            return hbar,vbar

    def type_select(self,event=None):
        self.type_select_win.destroy()
        self.type_select_win = Frame(self.f3)
        self.type_select_win.pack(side=TOP,fill=BOTH,expand=True)
        try:
            s_text = self.text.selection_get()
            line_no,end = self.text.index(INSERT).split('.')
            end = int(end) - 1
            line_no = int(line_no) - 1
            begin = end - len(s_text) + 1
        except TclError as e:
            line_no,end = self.text.index(INSERT).split('.')
            end = int(end) - 1
            line_no = int(line_no) - 1
            begin = end
        _,_,idx = self.find_annotation_index(begin, end,line_no)

        self.idx = idx

        if idx == -1:
            self.type_path = None
        else:
            self.type_path = self.entity2path[self.dataset[idx]['entity']]
        #self.type_select_win = Tk()
        screen_width=self.type_select_win.winfo_screenwidth()
        screen_height=self.type_select_win.winfo_screenheight()

        if self.direct=='Y':
            cvs_width = self.w
            cvs_height = self.h - self.label_h-self.text_h#self.type_select_win.winfo_screenmmheight()
        else:
            cvs_width = self.w / 2
            cvs_height = self.h
        #self.type_select_win.geometry('%dx%d'%(screen_width,screen_height))
        self.cvs = Canvas(self.type_select_win, width=cvs_width, height=cvs_height)
        self.cvs.pack(side=RIGHT,expand=True,fill=BOTH)

        #self.vertical_bar = self.add_scrollbar(self.type_select_win, self.cvs, 'Y')
        #self.vertical_bar.bind('<B1-Motion>', self.shift_cal)


        self.son = dict()
        self.father = {}
        self.ff = {}
        self.ru = {}
        self.ru['root'] = 0
        self.btn={}
        self.deep = {}
        self.deep['root'] = 1
        self.nodes = ['root']
        self.build_tree()
        self.nodes = list(set(self.nodes))
        self.tp()
        self.son_ = copy.deepcopy(self.son)
        for fnode in self.son_:
            for ss in self.son_[fnode]:
                if not self.father[ss] == fnode:
                    self.son_[fnode].remove(ss)
        self.levelnum = dict()
        self.y2x = {}
        self.posx = {}
        self.posy = {}
        self.find('root', 0, 0, 20, 20)
        self.button2node={}

        self.max_height = 0
        self.unseen_height = -1
        self.max_width = 0
        self.unseen_width = -1
        self.init_flag = 0
        print('draw_init!')
        self.draw_tree('root', 0)



        self.desc_text = Text(self.f4)
        self.descLabel1 = Label(self.f4, text='Type description')
        self.descLabel1.place(x=0, y=0)
        self.desc_text.place(x=0,y=20, height=88, width=self.w/4-20)
            #self.f4.place(x=0, y=self.h / 2, width=self.w / 2, height=self.h / 2)
            #self.descLabel1.place(x=0, y=self.h-100)
            #self.desc_text.place(x=0,y=self.h-88, height=88, width=screen_width/4)

        self.desc_text.bind('<f>', self.translate)
        self.desc_text.config(state=DISABLED)


        self.descLabel2 = Label(self.f4, text='Entity description')
        self.entity_text = Text(self.f4)
        self.descLabel2.place(x=self.w/4-20, y=0)
        self.entity_text.place(x=self.w/4-20, y=20, height=88, width=self.w/4-20)

        self.entity_text.bind('<f>', self.translate)

        self.entity_text.insert(END,self.fp[self.dataset[self.idx]['entity']][1])
        self.entity_text.config(state=DISABLED)

        self.init_flag == 1
        self.max_height += 100
        self.max_width += 100
        if self.max_height > cvs_height:
            self.unseen_height = self.max_height - cvs_height
        else:
            self.unseen_height = 0

        if self.max_width > cvs_width:
            self.unseen_width = self.max_width - cvs_width
        else:
            self.unseen_width = 0
        self.cvs['scrollregion']=(0,0,cvs_width+self.unseen_width, cvs_height+self.unseen_height)
        #self.type_select_win.mainloop()

    @staticmethod
    def find_line_no(end, accumulate_char_num):
        line_no = 9999
        for i in accumulate_char_num:
            if accumulate_char_num[i]>=end and i<line_no:
                line_no = i
        return line_no

    def selectPath(self,event):
        self.pre_path = self.path
        self.path = askopenfilename()
        if not self.path:
            self.path = self.pre_path
            return
        self.docName.set(self.path)
        self.annotations=[]
        self.lbset=[]
        self.dataset=[]
        self.scan_line = -1
        self.lb.delete(0,END)
        accumulate_char_num={}
        accumulate_char_num[-1]=0
        self.content=[]
        self.annotations_stack = []
        with open(self.path, 'r', encoding='utf-8') as f:
            self.text.config(state=NORMAL)
            self.text.delete(index1=1.0, index2=END)
            self.text.config(state=DISABLED)
            for i, content in enumerate(f):
                if content == '%%TYPE_ANNOTATIONS%%\n':
                    break
                self.content.append(content)
                accumulate_char_num[i] = accumulate_char_num[i-1] + len(content)
                self.text.config(state=NORMAL)
                self.text.insert(END, content)
                self.text.config(state=DISABLED)
            annotation_done = []
            for i, line in enumerate(f):
                self.idx_anno[i] = 'root'
                if len(line[0:-1].split('\t')) == 3:
                    be, end, entity = line[0:-1].split('\t')
                    line_no = self.find_line_no(int(end)+1, accumulate_char_num)
                    surface_name = ''.join(self.content)[int(be):int(end)+1]
                    self.dataset.append({'start':int(be),'end':int(end),'entity':entity,'line_no':line_no, 'surface_name':surface_name})
                    self.text.tag_add('tag', '%d.%d' % (line_no+1,int(be)-accumulate_char_num[line_no-1]),
                                      '%d.%d' % (line_no+1,int(end)+1-accumulate_char_num[line_no-1]))
                    self.text.tag_config('tag', foreground='red')

                if len(line[0:-1].split('\t')) ==4:
                    be, end, entity,_ = line[0:-1].split('\t')
                    line_no = self.find_line_no(int(end) + 1, accumulate_char_num)
                    surface_name = ''.join(self.content)[int(be):int(end) + 1]
                    self.dataset.append({'start':int(be),'end':int(end),'entity':entity,'line_no':line_no,'surface_name':surface_name})
                    self.text.tag_add('tag', '%d.%d' % (line_no + 1, int(be)-accumulate_char_num[line_no-1]),
                                      '%d.%d' % (line_no + 1, int(end) + 1-accumulate_char_num[line_no-1]))
                    self.text.tag_config('tag', foreground='red')
                    data = line[0:-1].split('\t')
                    data.append(i)
                    data.append(line_no)
                    annotation_done.append(data)
            acc_len = {}
            for annotation in annotation_done:
                end = int(annotation[1])
                entity = annotation[2]
                node = annotation[3]
                idx = annotation[4]
                line_no = annotation[5]
                self.annotations_stack.append([idx,node,line_no])
                if not line_no in acc_len:
                    acc_len[line_no] = 0
                end = end - accumulate_char_num[line_no-1]
                self.annotations.append([end+1+acc_len[line_no],end+1+acc_len[line_no]+len(node)+1,idx,node,line_no])
                self.idx_anno[idx] = node
                self.text.config(state=NORMAL)
                self.text.insert('%d.%d'%(line_no+1,end+1+acc_len[line_no]),'['+node+']')
                self.text.config(state=DISABLED)
                self.text.tag_add('tag1','%d.%d'%(line_no+1,end+1+acc_len[line_no]), '%d.%d'%(line_no+1,end+1+acc_len[line_no]+len(node)+1))
                self.text.tag_config('tag1', foreground='blue')
                self.lb.insert(END, entity)
                self.lbset.append(idx)
                acc_len[line_no] = acc_len[line_no] + len(node) + 2
        self.stack_point = len(self.annotations_stack)-1
        self.stack_bound = self.stack_point
        self.accumulate_char_num = accumulate_char_num

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--heightX', type=int,default=550)
    parser.add_argument('--heightY', type=int, default=200)
    args = parser.parse_args()
    Annotation(args)

