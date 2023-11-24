# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 17:47:34 2023

@author: Chrumo
"""

import os
import originpro as op
import sys

template_path = (r'C:\Users\piotr\Documents\VS_Code\spectrographer\TimeDecay.otpu')

def origin_fit_decay(wavelength, unit, title, csv_path, fun='ExpDecay1', irf_end = 0.0):

    def origin_shutdown_exception_hook(exctype, value, traceback):
        '''Ensures Origin gets shut down if an uncaught exception'''
        op.exit()
        print('OriginPro instance terminated successfuly')
        sys.__excepthook__(exctype, value, traceback)
    if op and op.oext:
        sys.excepthook = origin_shutdown_exception_hook
        op.set_show(False)

    wks = op.new_sheet('w')
    
    wks.from_file(csv_path)
    wks.cols_axis('xny')
    wks.set_label(0, 'Time / {}'.format(unit))
    wks.set_label(2, 'Normalized intensity at {} nm'.format(wavelength))
    
    model = op.NLFit(fun)
    model.set_data(wks, 0, 2)
    model.fit()
    fit_report_wks, fit_curve_wks = model.report()
    
    fit_report = op.find_sheet('w', fit_report_wks)
    fit_curve = op.find_sheet('w', fit_curve_wks)
    
    irf_end = 2.0
    
    graph = op.new_graph(template = template_path)
    graph_layer = graph[0]
    plot = graph_layer.add_plot(wks, 2, 0, type = 's')
    plot.set_cmd('-k 2')
    plot.symbol_size = 3.0
    graph_layer.rescale()
    graph_layer.xlim = (irf_end, graph_layer.xlim[1], (graph_layer.xlim[1] - irf_end)/5)
    graph_layer.ylim = (0.0, 1.0, 0.2)
    fit_plot = graph_layer.add_plot(fit_curve, 1, 0)
    fit_plot.set_cmd('-c 2', '-w 10')


    
    outdir = os.path.split(csv_path)[0]
    graph_out_path = os.path.join(outdir, '{}_at_{}.png'.format(title, wavelength))
    graph.save_fig(graph_out_path)
    
    fit_dataframe = fit_report.report_table("Parameters")
    print('\n')
    print(csv_path)
    print(fit_dataframe)
    print('t1 = {} +- {}'.format(fit_dataframe.loc[3]['Value'], fit_dataframe.loc[3]['Standard Error']))
    if fun != 'ExpDecay1' and fun!= 'ExpDec1':
        print('t2 = {} +- {}'.format(fit_dataframe.loc[5]['Value'], fit_dataframe.loc[5]['Standard Error']))

    report_out_path = os.path.join(outdir, '{}_at_{}_fit_report.txt'.format(title, wavelength))
    lifetimes_out_path = os.path.join(outdir, '{}_at_{}_lifetimes.txt'.format(title, wavelength))
    
    fit_dataframe.to_csv(report_out_path, sep='\t')
    
    with open(lifetimes_out_path, 'w') as f:
        f.write('{} {}'.format(fit_dataframe.loc[3]['Value'], fit_dataframe.loc[3]['Standard Error']))
        f.write('\n')
        if fun != 'ExpDecay1' and fun!= 'ExpDec1':
            f.write('{} {}'.format(fit_dataframe.loc[5]['Value'], fit_dataframe.loc[5]['Standard Error']))
    cwd = os.path.split(csv_path)[0]
    op.save(os.path.join(cwd, 'oproject.opju'))
    op.exit()
    return

if __name__ == '__main__':
    origin_fit_decay(wavelength = '558',
                     unit = 'ns',
                     title = 'p1k1',
                     fun = 'ExpDecay2',
                     csv_path = 'C:\\Users\\piotr\\Desktop\\revised_Rh\\Photoluminescence\\_data\\22_07_22_Rh1_100K\\out\\TimeResolved_IRF_557.csv')