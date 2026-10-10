"""Draw a source-derived results summary using Matplotlib; no generated artwork."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=Path('/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010')
fig,axes=plt.subplots(1,3,figsize=(13.4,5.0),facecolor='white')
fig.suptitle('TCAS: controlled stage allocation and bounded texturing evidence',fontsize=18,y=.96)
matched=json.loads((EVIDENCE/'MATCHED300_STATISTICS.json').read_text())
order=['Fixed Low','Early-high','Middle-high','Fixed Applied Mean','Late-high','Fixed High'];labels=['Low','Early','C3 / Middle','Mean','Late','High']
ax=axes[0];ax.barh(labels,[matched['means'][c]['fg_psnr'] for c in order],color=['#7d98ac','#7d98ac','#cd8b60','#7d98ac','#278a85','#3979a8']);ax.set_xlim(10.5,13.0);ax.set_xlabel('FG-PSNR (dB, higher is better)');ax.set_title('300 paired objects\nMiddle is not universally best',fontsize=12)
for ax,key,title,primary in [(axes[1],'BAKE','10-object bake pilot','Late − Mean FG-LPIPS'),(axes[2],'MVADAPTER','50-object native MV-Adapter','Middle − Mean FG-PSNR')]:
 d=json.loads((EVIDENCE/(key+'_STATISTICS.json')).read_text())['primary'];mean=d['mean_difference'];lo,hi=d['ci95'];ax.axvline(0,color='#adb6bd',lw=1);ax.errorbar(mean,0,xerr=[[mean-lo],[hi-mean]],fmt='o',color='#278a85' if key=='BAKE' else '#3979a8',capsize=5);ax.set_ylim(-1,1);ax.set_yticks([]);ax.set_title(title+'\n'+primary,fontsize=12);ax.set_xlabel('Paired mean and 95% object-bootstrap CI');ax.text(.5,.25,f'{mean:+.5f}\n[{lo:+.5f}, {hi:+.5f}]',ha='center',transform=ax.transAxes,fontsize=11)
axes[1].text(.5,.06,'Small late-high benefit; C3 counter-results retained',ha='center',transform=axes[1].transAxes,fontsize=9)
axes[2].text(.5,.06,'Primary does not separate; interface-specific result',ha='center',transform=axes[2].transAxes,fontsize=9)
for ax in axes:
 for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
fig.text(.5,.03,'Existing scheduling primitive • Unlit bake pilot • No universal C3 optimum or PBR-fidelity claim',ha='center',fontsize=11,color='#536574')
fig.tight_layout(rect=(0,.09,1,.88));fig.savefig(ROOT/'Graphical_Abstract_1008_DRAFT.pdf');(ROOT/'Author_Review').mkdir(exist_ok=True);fig.savefig(ROOT/'Author_Review/Graphical_Abstract_1008_DRAFT_preview.png',dpi=160)
