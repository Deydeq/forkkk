# -*- coding: utf-8 -*-

import wx
from wx import grid as wxgrid
import exceldata

'''
mzh
2015-4-28
'''

ID_BTN_IMPORT = wx.NewId()
ID_BTN_EXPORT = wx.NewId()

class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.error_msg = ''
        # self.data = exceldata.get_data()
        self.initUI()

    def initUI(self):
        panel = wx.Panel(self)

        main_box = wx.BoxSizer(wx.VERTICAL)

        '''button'''
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_import = wx.Button(panel, label=u'导入', size=(80, 35), id=ID_BTN_IMPORT)
        self.btn_import.Bind(wx.EVT_BUTTON, self.on_button_clicked)
        btn_box.Add(self.btn_import, 1)
        self.btn_export = wx.Button(panel, label=u'导出', size=(80, 35), id=ID_BTN_EXPORT)
        self.btn_export.Bind(wx.EVT_BUTTON, self.on_button_clicked)
        btn_box.Add(self.btn_export, 1, wx.LEFT, 10)
        # proportion is very import
        main_box.Add(btn_box, proportion=0, flag=wx.BOTTOM|wx.LEFT, border=10)

        main_box.Add((-1, 10))

        '''create notebook, add a scroll panel'''
        self.notebook = wx.Notebook(panel, style=wx.NB_LEFT)

        self.sales_page = wx.ScrolledWindow(self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL | wx.VSCROLL)
        self.sales_grid = wxgrid.Grid(self.sales_page)
        self.sales_grid.SetSize((1300, 500))
        self.notebook.AddPage(self.sales_page, u"销售统计", select=True)

        self.payment_page = wx.ScrolledWindow(self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL | wx.VSCROLL)
        self.payment_grid = wxgrid.Grid(self.payment_page)
        self.payment_grid.SetSize((1300, 500))
        self.notebook.AddPage(self.payment_page, u"中收")
        main_box.Add(self.notebook, proportion=1, flag=wx.EXPAND)

        panel.SetSizer(main_box)

        self.Center()
        self.Show()

    def on_button_clicked(self, e):
        eid = e.GetId()
        if eid == ID_BTN_IMPORT:
            print 'do import'
            self.import_data()
        elif eid == ID_BTN_EXPORT:
            print 'do export'

    '''导入数据'''
    def import_data(self):
        import_dlg = wx.FileDialog(self, 'Open Excel Doc', '', '', 'Excel files |*.xls*', wx.FD_OPEN)
        if import_dlg.ShowModal() == wx.ID_OK:
            file_path = import_dlg.GetPath()
            self.data = exceldata.get_data(file_path)
            if self.data is not None:
                self.put_data_in_grid(self.sales_grid, self.data.get('sales'), self.data.get('sales_column'))
                self.put_data_in_grid(self.payment_grid, self.data.get('payment'), self.data.get('payment_column'))

    def put_data_in_grid(self, target_grid=None, grid_data=None, col_name_list=None):
        if grid_data is None or col_name_list is None:
            self.error_msg += 'oh, there is no data in your specified file'
            return
        col_count = len(col_name_list)
        row_count = len(grid_data)

        target_grid.CreateGrid(row_count, col_count)
        '''设置列名'''
        for i in xrange(col_count):
            target_grid.SetColLabelValue(i, col_name_list[i])

        '''填充表体'''
        row_index = 0
        for row_dict in grid_data.values():
            for i in xrange(col_count):
                cell_value = row_dict.get(col_name_list[i])
                '''因为grid只接收String和Unicode，所以对其他类型进行转换'''
                if type(cell_value) is not unicode:
                    cell_value = str(cell_value)
                target_grid.SetCellValue(row_index, i, cell_value)
            row_index += 1

if __name__ == '__main__':
    app = wx.App()
    mw = MainWindow(None, title='Statistics', size=(1350, 600), style=wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.CAPTION | wx.SYSTEM_MENU)
    app.MainLoop()