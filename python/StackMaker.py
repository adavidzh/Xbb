import ROOT 
import sys,os
from HistoMaker import orderandadd
from BetterConfigParser import BetterConfigParser
import TdrStyles
from Ratio import getRatio

class StackMaker:
    def __init__(self, config, var,region,SignalRegion):
        plotConfig = BetterConfigParser()
        plotConfig.read('vhbbPlotDef.ini')
        section='Plot:%s'%region
        self.var = var
        self.normalize = eval(config.get(section,'Normalize'))
        self.log = eval(config.get(section,'log'))
        if plotConfig.has_option('plotDef:%s'%var,'log') and not self.log:
            self.log = eval(plotConfig.get('plotDef:%s'%var,'log'))
        self.blind = eval(config.get(section,'blind'))
        if self.blind: blindopt='blind'
        else: blindopt = 'noblind'
        self.setup=config.get('Plot_general','setup')
        if self.log:
            self.setup=config.get('Plot_general','setupLog')
        self.setup=self.setup.split(',')
        if not SignalRegion: self.setup.remove('ZH')
        self.rebin = 1
        if config.has_option(section,'rebin'):
            self.rebin = eval(config.get(section,'rebin'))
        if config.has_option(section,'nBins'):
            self.nBins = int(eval(config.get(section,'nBins'))/self.rebin)
        else:
            self.nBins = int(eval(plotConfig.get('plotDef:%s'%var,'nBins'))/self.rebin)
        print self.nBins
        if config.has_option(section,'min'):
            self.xMin = eval(config.get(section,'min'))
        else:
            self.xMin = eval(plotConfig.get('plotDef:%s'%var,'min'))
        if config.has_option(section,'max'):
            self.xMax = eval(config.get(section,'max'))
        else:
            self.xMax = eval(plotConfig.get('plotDef:%s'%var,'max'))
        self.name = plotConfig.get('plotDef:%s'%var,'relPath')
        self.mass = config.get(section,'Signal')
        data = config.get(section,'Datas')
        if '<mass>' in self.name:
            self.name = self.name.replace('<mass>',self.mass)
            print self.name
        if config.has_option(section, 'Datacut'):
            datacut=config.get(section, 'Datacut')
        else:
            datacut = region
        self.colorDict=eval(config.get('Plot_general','colorDict'))
        self.typLegendDict=eval(config.get('Plot_general','typLegendDict'))
        self.anaTag = config.get("Analysis","tag")
        self.xAxis = plotConfig.get('plotDef:%s'%var,'xAxis')
        self.options = [self.name,'',self.xAxis,self.nBins,self.xMin,self.xMax,'%s_%s.pdf'%(region,var),region,datacut,self.mass,data,blindopt]
        self.config = config
        self.datas = None
        self.datatyps = None
        self.overlay = None
        self.lumi = None
        self.histos = None
        self.typs = None
        self.AddErrors = None
        print self.setup

    def myText(self,txt="CMS Preliminary",ndcX=0,ndcY=0,size=0.8):
        ROOT.gPad.Update()
        text = ROOT.TLatex()
        text.SetNDC()
        text.SetTextColor(ROOT.kBlack)
        text.SetTextSize(text.GetTextSize()*size)
        text.DrawLatex(ndcX,ndcY,txt)
        return text


    def doPlot(self):
        TdrStyles.tdrStyle()
        self.histos, self.typs = orderandadd(self.histos,self.typs,self.setup)
    
        c = ROOT.TCanvas(self.var,'', 600, 600)
        c.SetFillStyle(4000)
        c.SetFrameFillStyle(1000)
        c.SetFrameFillColor(0)

        oben = ROOT.TPad('oben','oben',0,0.3 ,1.0,1.0)
        oben.SetBottomMargin(0)
        oben.SetFillStyle(4000)
        oben.SetFrameFillStyle(1000)
        oben.SetFrameFillColor(0)
        unten = ROOT.TPad('unten','unten',0,0.0,1.0,0.3)
        unten.SetTopMargin(0.)
        unten.SetBottomMargin(0.35)
        unten.SetFillStyle(4000)
        unten.SetFrameFillStyle(1000)
        unten.SetFrameFillColor(0)

        oben.Draw()
        unten.Draw()

        oben.cd()
        allStack = ROOT.THStack(self.var,'')     
        l = ROOT.TLegend(0.63, 0.60,0.92,0.92)
        l.SetLineWidth(2)
        l.SetBorderSize(0)
        l.SetFillColor(0)
        l.SetFillStyle(4000)
        l.SetTextFont(62)
        l.SetTextSize(0.035)
        MC_integral=0
        MC_entries=0

        for histo in self.histos:
            MC_integral+=histo.Integral()
        print "\033[1;32m\n\tMC integral = %s\033[1;m"%MC_integral

        #ORDER AND ADD TOGETHER
        #print typs
        #print setup


        if not 'DYc' in self.typs: self.typLegendDict.update({'DYlight':self.typLegendDict['DYlc']})
        print self.typLegendDict

        k=len(self.histos)
    
        for j in range(0,k):
            #print histos[j].GetBinContent(1)
            i=k-j-1
            self.histos[i].SetFillColor(int(self.colorDict[self.typs[i]]))
            self.histos[i].SetLineColor(1)
            allStack.Add(self.histos[i])

        d1 = ROOT.TH1F('noData','noData',self.nBins,self.xMin,self.xMax)
        datatitle='Data'
        addFlag = ''
        if 'Zee' in self.datanames and 'Zmm' in self.datanames:
	        addFlag = 'Z(l^{-}l^{+})H(b#bar{b})'
        elif 'Zee' in self.datanames:
	        addFlag = 'Z(e^{-}e^{+})H(b#bar{b})'
        elif 'Zmm' in self.datanames:
	        addFlag = 'Z(#mu^{-}#mu^{+})H(b#bar{b})'
        for i in range(0,len(self.datas)):
            d1.Add(self.datas[i],1)
        print "\033[1;32m\n\tDATA integral = %s\033[1;m"%d1.Integral()
        flow = d1.GetEntries()-d1.Integral()
        if flow > 0:
            print "\033[1;31m\tU/O flow: %s\033[1;m"%flow

        self.overlay.SetLineColor(2)
        self.overlay.SetLineWidth(2)
        self.overlay.SetFillColor(0)
        self.overlay.SetFillStyle(4000)
        self.overlay.SetNameTitle('Overlay','Overlay')

        l.AddEntry(d1,datatitle,'P')
        for j in range(0,k):
            l.AddEntry(self.histos[j],self.typLegendDict[self.typs[j]],'F')
        l.AddEntry(self.overlay,self.typLegendDict['Overlay'],'L')
    
        if self.normalize:
            if MC_integral != 0:	stackscale=d1.Integral()/MC_integral
            self.overlay.Scale(stackscale)
            stackhists=allStack.GetHists()
            for blabla in stackhists:
        	    if MC_integral != 0: blabla.Scale(stackscale)
    
        allMC=allStack.GetStack().Last().Clone()

        allStack.SetTitle()
        allStack.Draw("hist")
        allStack.GetXaxis().SetTitle('')
        yTitle = 'Entries'
        if not '/' in yTitle:
            yAppend = '%s' %(allStack.GetXaxis().GetBinWidth(1)) 
            yTitle = '%s / %s' %(yTitle, yAppend)
        allStack.GetYaxis().SetTitle(yTitle)
        allStack.GetXaxis().SetRangeUser(self.xMin,self.xMax)
        allStack.GetYaxis().SetRangeUser(0,20000)
        theErrorGraph = ROOT.TGraphErrors(allMC)
        theErrorGraph.SetFillColor(ROOT.kGray+3)
        theErrorGraph.SetFillStyle(3013)
        theErrorGraph.Draw('SAME2')
        l.AddEntry(theErrorGraph,"MC uncert. (stat.)","fl")
        Ymax = max(allStack.GetMaximum(),d1.GetMaximum())*1.7
        if self.log:
            allStack.SetMinimum(0.05)
            Ymax = Ymax*ROOT.TMath.Power(10,1.6*(ROOT.TMath.Log(1.6*(Ymax/0.1))/ROOT.TMath.Log(10)))*(0.6*0.1)
            ROOT.gPad.SetLogy()
        allStack.SetMaximum(Ymax)
        c.Update()
        ROOT.gPad.SetTicks(1,1)
        #allStack.Draw("hist")
        l.SetFillColor(0)
        l.SetBorderSize(0)

        self.overlay.Draw('hist,same')
        d1.Draw("E,same")
        l.Draw()

        tPrel = self.myText("CMS Preliminary",0.17,0.88,1.04)
        tLumi = self.myText("#sqrt{s} =  %s, L = %s fb^{-1}"%(self.anaTag,(float(self.lumi)/1000.)),0.17,0.83)
        tAddFlag = self.myText(addFlag,0.17,0.78)

        unten.cd()
        ROOT.gPad.SetTicks(1,1)

        l2 = ROOT.TLegend(0.5, 0.82,0.92,0.95)
        l2.SetLineWidth(2)
        l2.SetBorderSize(0)
        l2.SetFillColor(0)
        l2.SetFillStyle(4000)
        l2.SetTextFont(62)
        #l2.SetTextSize(0.035)
        l2.SetNColumns(2)

        ratio, error = getRatio(d1,allMC,self.xMin,self.xMax)
        ksScore = d1.KolmogorovTest( allMC )
        chiScore = d1.Chi2Test( allMC , "UWCHI2/NDF")
        print ksScore
        print chiScore
        ratio.SetStats(0)
        ratio.GetXaxis().SetTitle(self.xAxis)
        ratioError = ROOT.TGraphErrors(error)
        ratioError.SetFillColor(ROOT.kGray+3)
        ratioError.SetFillStyle(3013)
        ratio.Draw("E1")



        if not self.AddErrors == None:
            self.AddErrors.SetFillColor(5)
            self.AddErrors.SetFillStyle(1001)
            self.AddErrors.Draw('SAME2')

            l2.AddEntry(self.AddErrors,"MC uncert. (stat. + syst.)","f")

        l2.AddEntry(ratioError,"MC uncert. (stat.)","f")

        l2.Draw()

        ratioError.Draw('SAME2')
        ratio.Draw("E1SAME")
        ratio.SetTitle("")
        m_one_line = ROOT.TLine(self.xMin,1,self.xMax,1)
        m_one_line.SetLineStyle(ROOT.kDashed)
        m_one_line.Draw("Same")

        if not self.blind:
            tKsChi = self.myText("#chi_{#nu}^{2} = %.3f K_{s} = %.3f"%(chiScore,ksScore),0.17,0.9,1.5)
        t0 = ROOT.TText()
        t0.SetTextSize(ROOT.gStyle.GetLabelSize()*2.4)
        t0.SetTextFont(ROOT.gStyle.GetLabelFont())
        if not self.log:
    	    t0.DrawTextNDC(0.1059,0.96, "0")

        name = '%s/%s' %(self.config.get('Directories','plotpath'),self.options[6])
        c.Print(name)
