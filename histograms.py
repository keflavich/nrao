import numpy as np
from astropy import table
from astropy.table import Table
from astropy import units as u
import pylab as pl

pl.rc('font', size=16)


table1 = Table.read('/Users/adam/work/w51/alma/mcclellan/cmcclellan-summer-2018/cat/45-93-226GHz_photometered_adjustedRADEC.dat', format='ascii')
table2 = Table.read('/Users/adam/work/w51/alma/mcclellan/cmcclellan-summer-2018/cat/w51IRS2_photometered.dat', format='ascii')

tbl = table.vstack([table1, table2])

ok1 = table1['rejected'] == 0
ok2 = table2['rejected'] == 0

flux_1mm = np.concatenate([(table2['226.4GHz_Circle_peak']-table2['45.0GHz_Circle_peak']).data[ok2],
                           (table1['226.1GHz_Circle_peak']-table1['45.0GHz_Circle_peak']).data[ok1]])
flux_3mm = np.concatenate([(table2['93.0GHz_Circle_peak']-table2['45.0GHz_Circle_peak']).data[ok2],
                           (table1['93.0GHz_Circle_peak']-table1['45.0GHz_Circle_peak']).data[ok1]])

pl.clf()
ax1 = pl.subplot(2,1,1)
ax1.semilogx()
ax1.hist(flux_1mm*1e3, bins=np.logspace(-1,2,20), histtype='stepfilled', edgecolor='k', facecolor=(0.3, 0, 0, 0.25))
#ax1.set_xlabel("S$_{1 mm}$")
ax2 = pl.subplot(2,1,2)
ax2.semilogx()
ax2.hist(flux_3mm*1e3, bins=np.logspace(-1,2,20), histtype='stepfilled', edgecolor='k', facecolor=(0.3, 0, 0, 0.25))
#ax2.set_xlabel("S$_{3 mm}$")

pl.savefig('/Users/adam/work/w51/alma/mcclellan/cmcclellan-summer-2018/figures/flux_histograms.png')


# loose estimate of completeness
rms_1mm = np.concatenate([table2['226.4GHz_Annulus_rms'].data[ok2],
                          table1['226.1GHz_Annulus_rms'].data[ok1]])
completeness_1mm = np.nanmean(rms_1mm) * 3
rms_3mm = np.concatenate([table2['93.0GHz_Annulus_rms'].data[ok2],
                           table1['93.0GHz_Annulus_rms'].data[ok1]])
completeness_3mm = np.nanmean(rms_3mm) * 3

ax1.vlines(completeness_1mm*1e3, 0, 25, linestyle='--', color='k', linewidth=2)
ax2.vlines(completeness_3mm*1e3, 0, 25, linestyle='--', color='k', linewidth=2)

# now compare to a simple IMF...
import dust_emissivity
import imf
masses = np.logspace(-2, 2, 1000)*u.M_sun
probabilities = imf.Kroupa()(masses)
core_efficiency = 1/3.

beta = 1.5

model_fluxes_1mm_20K = dust_emissivity.dust.snuofmass(226*u.GHz, masses/core_efficiency,
                                                      distance=5.4*u.kpc,
                                                      beta=beta,
                                                      temperature=20*u.K)
model_fluxes_3mm_20K = dust_emissivity.dust.snuofmass(93*u.GHz, masses/core_efficiency,
                                                      distance=5.4*u.kpc,
                                                      beta=beta,
                                                      temperature=20*u.K)

model_fluxes_1mm_100K = dust_emissivity.dust.snuofmass(226*u.GHz, masses/core_efficiency,
                                                       distance=5.4*u.kpc,
                                                       beta=beta,
                                                       temperature=100*u.K)
model_fluxes_3mm_100K = dust_emissivity.dust.snuofmass(93*u.GHz, masses/core_efficiency,
                                                       distance=5.4*u.kpc,
                                                       beta=beta,
                                                       temperature=100*u.K)


ax1.plot(model_fluxes_1mm_20K*1e3, probabilities / probabilities.max() * 500, linewidth=3, alpha=0.85)
ax1.plot(model_fluxes_1mm_100K*1e3, probabilities / probabilities.max() * 25, linewidth=3, alpha=0.85)
ax1.set_ylim(0, 20)
ax1.set_xlim(5e-1, 1e2)

ax2.plot(model_fluxes_3mm_20K*1e3, probabilities / probabilities.max() * 500, linewidth=3, alpha=0.85, label='20 K')
ax2.plot(model_fluxes_3mm_100K*1e3, probabilities / probabilities.max() * 25, linewidth=3, alpha=0.85, label='100 K')
ax2.set_ylim(0, 15)
ax2.set_xlim(5e-1, 1e2)
pl.legend(loc='best')

ax1.text(0.5, 0.85, "1 mm", horizontalalignment='center', transform=ax1.transAxes)
ax2.text(0.5, 0.85, "3 mm", horizontalalignment='center', transform=ax2.transAxes)
ax1.text(0.22, -0.17, "mJy", horizontalalignment='center', transform=ax1.transAxes)
ax2.text(0.22, -0.17, "mJy", horizontalalignment='center', transform=ax2.transAxes)

from matplotlib.ticker import ScalarFormatter
ax1.xaxis.set_major_formatter(ScalarFormatter())
ax2.xaxis.set_major_formatter(ScalarFormatter())

pl.subplots_adjust(hspace=0.3)

pl.savefig('/Users/adam/work/w51/alma/mcclellan/cmcclellan-summer-2018/figures/flux_histograms_with_imf_models.png', bbox_inches='tight')
pl.savefig('/Users/adam/work/w51/alma/mcclellan/cmcclellan-summer-2018/figures/flux_histograms_with_imf_models.pdf', bbox_inches='tight')
