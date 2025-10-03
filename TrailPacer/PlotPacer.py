import itertools as it
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import pandas as pd
import streamlit as st
import json
import os
class PacingPlotter():

    def __init__(self, year, event, course_name,course, is_elite=False,offline=True,drop_ckpt=None, loadconfig=True,reduction=0.95,show_peloton=True):
        self.event = event
        self.course = course
        self.course_name =course_name 
        self.year = year
        self.offline = offline
        self.is_elite=is_elite
        self.reduction=reduction
        self.show_peloton=show_peloton
        self.root_data = os.path.join(f"data/TrailPacer/", event,course or "")
        #self.root_data = os.path.join("/data/TrailPacer", event or "")
        self.output_pth = f"data/TrailPacer/{event}/{course}/"
        self.color_cofinishers = u'#48d1cc'
        self.color_hlines = u'#5b5f97'
        self._idx_runner = ['bib', 'name', 'sex',]
        self.drop_ckpt = [] if drop_ckpt is None else drop_ckpt
        self.race_query = {'year': year, 'event': event, 'course': course}
        
        #TODO : remplacer par la lecture des fichiers dans temp_data.
        self.df_ref_pacing = self.load_ref_pacing(**self.race_query)
        self.df_times = self.load_times(**self.race_query)
        self.df_gpx = self.load_altitude_profile(year, course)
        self.df_checkpoints = self._get_df_checkpoints()
        self.finish=self.df_times.columns[-1]
        self.mapping_bib = self.df_times.reset_index('bib')['bib'].droplevel('sex')
        #self.df_ranks = self.load_ranks(**self.race_query)
        self.max_altitude = self.df_gpx.altitude.max()
        self.ymin = 0.93
        self._idx_runner = ['bib','name','status','category','sex','country']
       
    # def load_ranks(self, year, event, course):

    #     pth = f"{self.output_pth}/ranks/{course}_{year}.csv"
    #     return pd.read_csv(pth, index_col=self._idx_runner)
    

    def load_ref_pacing(self, year, event, course):
        pth = f"{self.output_pth}/ref_pacing/ref_{year}.csv"
        df = pd.read_csv(pth, index_col='checkpoint') 
        df= df.sort_values(by="dist_total")
        return df
       
    def load_altitude_profile(self, year, course):
        pth = f"{self.output_pth}/profile/profile_{year}.csv"
        df = pd.read_csv(pth)

        # convertir en km
        df["dist_total"] = df["distance_cum"] / 1000

        # supprimer la colonne
        df = df.drop(columns=["distance_cum"])

        return df 
        
    def load_times(self, year, event, course):

        pth = f"{self.output_pth}/times/times_{year}.csv"
        df=pd.read_csv(pth, index_col=self._idx_runner)
        df=df.drop(columns=['status','category','country'])
        df = df.apply(lambda col: pd.to_datetime(col, errors='coerce').dt.tz_localize(None))
        start_col = df.iloc[:, 0]
        # Soustraire l'heure de départ à toutes les colonnes
        df = df.apply(lambda col: col - start_col)
        return df.apply(pd.to_timedelta, errors="coerce")
        
    
        
    def hstring_to_hours(self,t):
        if t==0 :
            return 0
        if pd.isna(t):
            return None
        h, m = t.split('h')
        return int(h) + int(m)/60
    def _get_df_checkpoints(self):
        
        checkpoints = (self.df_ref_pacing['dist_total']
                       .drop(self.drop_ckpt, errors='ignore')
                       .reset_index())
        
        df = (self.df_gpx
              .merge(checkpoints,
                     on='dist_total',
                     how='outer')
              .sort_values('dist_total')
              .assign(altitude=lambda x: x.altitude.ffill())
              .dropna(subset=['checkpoint'])
              .set_index('checkpoint'))

        return df
        
    def get_df_splits(self, bibs, df_abs, names):
        if len(names) == 1:
            split_ref,col_split_ref= (round(df_abs['ref_pacing']*self.reduction), 'ref_pacing')
            df = (df_abs
                .apply(lambda x: x - (split_ref))
                .drop(columns=[col_split_ref])
                .apply(lambda x: x.apply(lambda x: self.printable_hms(x, print_0=False)))
                )
        else :
            col=names[0]
            split_ref,col_split_ref= df_abs[col], col
            df = (df_abs
                    .apply(lambda x:  (split_ref)-x)
                    .drop(columns=[col_split_ref])
                    .apply(lambda x: x.apply(lambda x: self.printable_hms(x, print_0=False)))
                    )

        return df, col_split_ref
        
    def get_ref_pacing_(self, temps_cible):
        self.df_ref_pacing['ref_pacing'] = (self.df_ref_pacing['temps_ref_norm']
                                            .mul(temps_cible)
                                            .cumsum())
        return self.df_ref_pacing[['ref_pacing', 'dist_total']]
    
    
    def get_ref_pacing(self, temps_cible):
        df = self.df_ref_pacing.copy()
        col=f'temps_cumule_med_{temps_cible}'
        if 'temps_ref_norm' in df.columns:
            # temps normalisé déjà disponible
            df['ref_pacing'] = df['temps_ref_norm'].mul(temps_cible).cumsum()

        elif col in df.columns and 'dist_secteur' in df.columns:
            # convertir vitesse en temps pour chaque secteur
            df['ref_pacing'] = df[col].apply(self.hstring_to_hours)

        else:
            raise ValueError("Impossible de calculer ref_pacing: ni 'temps_ref_norm' ni 'vitesse_ref_norm' disponibles")
        
        return df[['ref_pacing', 'dist_total']]


    def get_runners_pacing(self, year, event, course, bibs, temps_cible):
        msk = self.df_times.index.get_level_values("bib").isin(bibs)

        # garder l'ordre des bibs avant de droplevel
        df_times_bibs = (
            self.df_times.loc[pd.Index(bibs, name="bib")]
            .droplevel(["sex", "bib"])
        )

        self.df_times_bibs = df_times_bibs
        names = df_times_bibs.index
        runner_pacings = (self.df_times_bibs
                         .T
                        / pd.Timedelta(hours=1))
        
        temps_cible = (runner_pacings.loc[self.finish].mean()
                       if temps_cible is None
                       else temps_cible)
        
        
        ref_pacing = self.get_ref_pacing(temps_cible=(temps_cible))
        df = runner_pacings.join(ref_pacing)
        return df, temps_cible, names
    

    @staticmethod
    def printable_hours(hr, print_0=True):
        if pd.isna(hr):
            return ""

        sign = "-" if hr < 0 else ""
        hr = abs(hr)

        HH = int(hr)
        MM = int(round((hr - HH) * 60))

        # Ajustement si arrondi à 60 minutes
        if MM == 60:
            HH += 1
            MM = 0

        if MM == 0 and (not print_0):
            return f"{sign}{HH}h"
        if HH == 0:
            return f"{sign}{MM}'"
        return f"{sign}{HH}h{MM:02d}"
    

    @staticmethod
    def printable_hms(hr, print_0=True):
        if pd.isna(hr):
            return ""
        
        sign = "-" if hr < 0 else "+"
        hr = abs(hr)
        
        HH = int(hr)
        MM = int((hr - HH) * 60)
        SS = int(round(((hr - HH) * 60 - MM) * 60))
        
        # Ajustement si arrondi à 60 secondes
        if SS == 60:
            MM += 1
            SS = 0
        if MM == 60:
            HH += 1
            MM = 0
        
        # if not print_0 and HH == 0 and MM == 0:
        #     return f"{sign}{SS}s"
        
        return f"{sign}{HH:02d}:{MM:02d}:{SS:02d}"

    @staticmethod
    def format_hr_to_time(x):
        x = int(x*60)
        return f'{x//60}h{x%60:02d}'

    def _get_pacings(self, bibs, temps_cible):
        df, finish_time, names = self.get_runners_pacing(**self.race_query,
                                                         bibs=bibs,
                                                         temps_cible=temps_cible)
        
        self.df_cofinishers = self._get_cofinishers_pacings(bibs, finish_time)

        df = df.join(self.df_cofinishers)
        

        first_idx = df.index[0]
        if df.loc[first_idx].isna().any():
            df.loc[first_idx] = df.loc[first_idx].fillna(0)

        df = (df
              .set_index('dist_total', append=True)
              .sort_values('dist_total'))
        #self.df = df
        reference_pacing = df.ref_pacing
        df_plotted_relative_pacings = (df
                                       .apply(lambda x: x.div(reference_pacing))
                                       .mul(finish_time)
                                         )
        return (df_plotted_relative_pacings,
                df.droplevel('dist_total'),
                finish_time,
                names)
        
    def _get_cofinishers_pacings(self, bibs, finish_time):
        
        df = self.df_times.apply(pd.to_timedelta, errors="coerce")
        df = df.div(pd.Timedelta(hours=1))

        finish_times = df[self.finish]
        
        msk = (finish_times - finish_time).div(finish_time).abs() < 0.05

        df_cofinishers = (df
                          .drop(bibs, level='bib')
                          .loc[msk]
                          .droplevel([0,2])
                          .T)
        return df_cofinishers
        
        
    @staticmethod
    def _get_plotted_elevation(elevation, yr_spread, yr_min, height_scale=1/2.5):
        plotted_elevation = (elevation
                             .div(elevation.max())
                             .mul(yr_spread*height_scale)
                             .add(yr_min))
        return plotted_elevation
     
    def _draw_altitude_profile(self, ax, yr_spread, yr_min):
        plotted_elevation = self._get_plotted_elevation(self.df_gpx.altitude,
                                                        yr_spread,
                                                        yr_min)
            
        ax.fill_between(self.df_gpx['dist_total'],
                         y1=0,
                         y2=plotted_elevation,
                         color='darkgray',
                         alpha=1)
        
        ax.plot(self.df_gpx['dist_total'],
                  plotted_elevation,
                  color='k')
        return ax
    
    def _draw_hlines(self, ax, yr_finish, yr_min, yr_max):
        
        gap = 1 if (yr_max - yr_min) < 6 else 2
        #TODO : select which hlines we show.
        hlines = np.arange(int(yr_min)+2, int(yr_max), gap)

        line_kwargs = dict(linestyle='--',
                            color=self.color_hlines,)
        
        kwargs = dict(
                      textcoords='offset points',
                      color=self.color_hlines,
                      weight='bold',
                      fontsize=10)
        
        ax.axhline(y=yr_finish,
                    alpha=0.8,
                    linewidth=2,
                    
                    **line_kwargs,
                label='Plan de course TrailPacer')
                
        ax.annotate(xy=(0, yr_finish),
                    text=self.printable_hours(yr_finish),
                    xytext=(5, 5),
                    **kwargs)
        for y in hlines:
            if abs(y-yr_finish)>gap/2:
                ax.axhline(y=y,
                           alpha=0.5,
                           linewidth=1,
                           
                           **line_kwargs)
                
                ax.annotate(xy=(0, y),
                            text=self.printable_hours(y),
                            xytext=(5, 5),
                            **kwargs)
        return ax 
    
    def _draw_uniform_background(self, ax, yr_min, yr_max, xmax):
        ax.fill_between([0, xmax],
                         y1=yr_max,
                         y2=yr_min,
                         color=self.color_cofinishers, 
                         alpha=0.1)
        return ax
    
    def _draw_splits(self, ax, df_relative, df_splits, splits_reference, names, yr_spread, yr_min, yr_max,y_finish):
        
        plotted_elevation = self._get_plotted_elevation(self.df_checkpoints.altitude,
                                                        yr_spread,
                                                        yr_min)
        self.df_checkpoints['plotted_elevation'] = plotted_elevation
        
     
        col_splits = df_splits.columns[0]
        for i, (ckpt, row) in enumerate(self.df_checkpoints.iterrows()):

            if i==0:
                ax.annotate(xy=(row['dist_total'], yr_max),
                        text= ckpt + " " ,
                        verticalalignment='top', 
                        horizontalalignment='left',
                        rotation=45,
                        color='k',)
                continue
            y_ref = df_relative.loc[ckpt, splits_reference]  if splits_reference!="ref_pacing" else y_finish
            y_splits = df_relative.loc[ckpt, col_splits]

            #y_finish = df_relative.loc[ckpt, 'ref_pacing']

            ax.annotate(xy=(row['dist_total'], yr_max),
                        text=ckpt+ " " ,
                        verticalalignment='top', 
                        horizontalalignment='center',
                        rotation=45,
                        color='k',)

            if not self.is_elite : 
                ax.vlines(x=row['dist_total'],
                        linestyle='--',
                        color='tab:gray',
                        #ymin=y_ref,
                        ymax=y_splits,
                        ymin=y_ref,
                        alpha=0.5)
                                
                value = df_splits.loc[ckpt, col_splits]
                # Couleur conditionnelle
                if len(names) > 1:
                    facecolor = "green" if value.startswith("-")  else "red"
                else:
                    facecolor = self.color_hlines

                ax.annotate(
                    xy=(row['dist_total'], y_ref),
                    text=value,
                    verticalalignment='center', 
                    horizontalalignment='center',
                    rotation=90,
                    fontsize=8,
                    color="w",
                    zorder=6,
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        edgecolor='none',
                        linewidth=0.8,
                        facecolor=facecolor
                    ),
                    #label='Ecarts'
                )
            
        return ax
    
    
    @staticmethod
    def is_color_dark(color):
        rgb = mcolors.to_rgb(color)  
        luminance = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        return luminance < 0.5
    
    def _draw_runner_pacing(self, ax, df, names, df_ranks=None):
        df = df.reset_index('dist_total')
        df_pace = (df
                   .loc[df.dist_total>=0] 
                   #.join(df_ranks, how='left')
                   )
        for name in names:
            color = next(self.color_cycle)
            ax.plot(df_pace['dist_total'],
                    df_pace[name],
                    color=color,
                    linewidth=2,
                    label=name,
                    )
        
            for ckpt, row in df_pace.iterrows():
                if ckpt in self.drop_ckpt:
                    continue
                annot_color = "white" if self.is_color_dark(color) else 'k'
                ax.annotate(xy=(row['dist_total'], row[name]),
                            text="",
                            xytext=(0,0),
                            ha='center',
                            textcoords='offset points',
                            fontsize=10,
                            weight='bold',
                            color=annot_color,
                            
                            bbox=dict(boxstyle="round,pad=0.3",
                                      edgecolor='none',
                                      linewidth=0.8,
                                      facecolor=color))
        return ax
    
    def _draw_copacing(self, ax, df, names):
        
        df_pace = (df
                   .loc[df.index.get_level_values('dist_total')>=0]
                   .reset_index('dist_total')
                   .drop(columns=[*names, 'ref_pacing']))
        
        enough_notnas = df_pace.isna().mean(1) < 0.3
        
        df_pace = (df_pace
                   .loc[enough_notnas]
                   .set_index('dist_total', append=True))
        
        alpha= 0.5
        q = 0.2
        q1 = df_pace.quantile(q, axis=1)
        q3 = df_pace.quantile(1-q, axis=1)
        
        ax.fill_between(df_pace.index.get_level_values('dist_total'),
                 q1,q3,
                 color=self.color_cofinishers,
                 alpha=alpha,
                 )
        
        return ax
    
    # def _get_ranks(self, bibs):
    #     msk = self.df_ranks.index.get_level_values('bib').isin(bibs)
    #     df = self.df_ranks.loc[msk].droplevel(['bib', 'sex']).T.add_suffix('_rank')
    #     return df
    
    def _draw_legend(self, axr, temps_cible):
        self._init_color_cycle()
        handles, labels = axr.get_legend_handles_labels()

        kwargs_box = dict(width=1,
                          height=1,
                          boxstyle="round,pad=0.3",)


        if self.show_peloton : 
            patch_peloton = mpatches.Patch(color=self.color_cofinishers,
                                        label=f'Peloton {self.printable_hours(temps_cible)}')
        
            handles.append(patch_peloton) 
 
        if not self.is_elite and  self.show_peloton :
            patch_splits = mpatches.FancyBboxPatch((0, 0),
                                            color=self.color_hlines,
                                            label='Écart cumulé',
                                            **kwargs_box)
            handles.append(patch_splits)
        
        if not self.show_peloton:
            patch_splits_green = mpatches.FancyBboxPatch((0, 0),
                                            color='green',
                                            label='En avance ',
                                            **kwargs_box)
            handles.append(patch_splits_green)
            patch_splits_red = mpatches.FancyBboxPatch((0, 0),
                                            color='red',
                                            label='En retard',
                                            **kwargs_box)
            handles.append(patch_splits_red)
        




        axr.legend(handles=handles,
                   loc='lower left',
                   ncol=4)
        
        return axr
    

        
    def _format_axes(self, axr, axl, yr_min, yr_max, xmax, names):
        axr.set_ylim(yr_min, yr_max)
        axl.set_ylim(axr.get_ylim())
        axl.set_yticks([])
        axl.xaxis.set_major_formatter(
            FuncFormatter(lambda y, _: f'{int(y)}km')
            )
        axr.yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: self.printable_hours(y, print_0=False))
            )

        axl.set_xlim(0, xmax)
        axl.set_title(f'{" x ".join(names)} - {self.course_name} - {self.year}', fontsize=20)
        axr.set_ylabel('Plan de course (heures)', fontsize=13)
        axr.tick_params(labelsize=13)
        axl.tick_params(axis='x', labelsize=13)
        return axr, axl
    
    
    def _plot(self, bibs, temps_cible=None):
        """
        TODO : Comparer le ref prédit et le ref réel.
        """

        df_relative, df_absolute, temps_cible, names = self._get_pacings(bibs,
                                                                         temps_cible)

        #df_runners_rank = self._get_ranks(bibs)
        #TODO : integrate split ref into df_splits.
        df_splits, splits_reference = self.get_df_splits(bibs, df_absolute, names)
        yr_finish = round(temps_cible*self.reduction)
        x_max = df_relative.index.get_level_values('dist_total').max()

        yr_min  = df_relative[names].min().min()*0.9
        yr_max = df_relative[names].max().max()*1.05
        yr_spread = int(yr_max - yr_min)
        
        fig, axl = plt.subplots(figsize=(17,7))
        axr = axl.twinx()
         
        axr = self._draw_splits(axr, df_relative, df_splits, splits_reference, names, yr_spread, yr_min, yr_max,yr_finish)
        axr = self._draw_altitude_profile(axr, yr_spread, yr_min)
        if self.show_peloton:
            axr = self._draw_copacing(axr, df_relative, names)
        axr = self._draw_runner_pacing(axr, df_relative, names)
        axr = self._draw_uniform_background(axr, yr_min, yr_max, x_max, )
        axr = self._draw_hlines(axr, yr_finish, yr_min, yr_max)
        
        axr, axl = self._format_axes(axr, axl, yr_min, yr_max, x_max, names)
        axr = self._draw_legend(axr, temps_cible)
        
        
        return fig, df_relative
    
    def _init_color_cycle(self):
        self.color_cycle = it.cycle({u'#ff6b6c',
                                   u'#ffc145',
                                   })
        
    def plot(self, bib, temps_cible=None):
        self._init_color_cycle()
        if not isinstance(bib, list):
            return self.plot([bib], temps_cible)
        bibs = [i if isinstance(i, int) else self.mapping_bibloc[i] for i in bib]

        return self._plot(bibs, temps_cible)
    



