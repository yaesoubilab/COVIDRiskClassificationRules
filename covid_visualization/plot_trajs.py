import apacepy.analysis.trajectories as A

import covid_model.data as D
import definitions as Def
from covid_model.data import *
from covid_model.settings import COVIDSettings
from definitions import AgeGroups, Variants, FEASIBILITY_PERIOD, ROOT_DIR

A.FEASIBLE_REGION_COLOR_CODE = 'pink'
A.Y_LABEL_COORD_X = -0.15
A.SUBPLOT_W_SPACE = 0.0


def plot(prev_multiplier=52, incd_multiplier=1, obs_incd_multiplier=1,
         n_random_trajs_to_display=None, save_plots_dir=None,
         plot_the_size_of_compartments=False):
    """
    :param prev_multiplier: (int) to multiply the simulation time to convert it to year, week, or day.
    :param incd_multiplier: (int) to multiply the simulation period to covert it to year, week, or day.
    :param obs_incd_multiplier: (int) to multiply the observation period to conver it to year, week, or day.
    :param n_random_trajs_to_display: (int) number of trajectories to display
    :param save_plots_dir: (string) directory to save
    :param plot_the_size_of_compartments: (bool) if plot the size of all compartments
    """

    print('Making plots ...')
    if save_plots_dir is None:
        save_plots_dir = ROOT_DIR + '/outputs/figures'

    directory = ROOT_DIR + '/outputs/trajectories'
    sim_outcomes = A.SimOutcomeTrajectories(csv_directory=directory)

    # defaults
    SIM_DURATION = Def.SIM_DURATION*52
    A.X_RANGE = (0, SIM_DURATION)     # x-axis range
    A.X_TICKS = (0, 52/2)      # x-axis ticks (min at 0 with interval of 5)
    A.X_LABEL = 'Weeks since March 1, 2020'     # x-axis label

    pd = Def.ProfileDefiner(
        n_age_groups=len(AgeGroups), n_variants=len(Variants), n_vacc_status=2)

    # -----------------------------------------------------------------
    # ------ plot information for the validation plot (by age) --------
    # -----------------------------------------------------------------
    if plot_the_size_of_compartments:
        for a in range(pd.nAgeGroups):

            str_a = pd.strAge[a]
            S = A.TrajPlotInfo(outcome_name='In: Susceptible-'+str_a, title='Susceptible',
                               # y_range=(0, 55000),
                               x_multiplier=prev_multiplier)
            V = A.TrajPlotInfo(outcome_name='In: Vaccinated-'+str_a, title='Vaccinated',
                               # y_range=(0, 55000),
                               x_multiplier=prev_multiplier)

            Es = []
            Is = []
            Hs = []
            Rs = []
            Ds = []
            for v in range(pd.nVariants):
                for vs in range(pd.nVaccStatus):
                    str_a_p = pd.strAgeProfile[a][v][vs]
                    str_p = pd.strProfile[v][vs]
                    Es.append(A.TrajPlotInfo(outcome_name='In: Exposed-'+str_a_p, title='Exposed\n'+str_p,
                                             # y_range=(0, 22000),
                                             x_multiplier=prev_multiplier))
                    Is.append(A.TrajPlotInfo(outcome_name='In: Infectious-'+str_a_p, title='Infectious\n'+str_p,
                                             # y_range=(0, 17000),
                                             x_multiplier=prev_multiplier))
                    Hs.append(A.TrajPlotInfo(outcome_name='In: Hospitalized-'+str_a_p, title='Hospitalized\n'+str_p,
                                             # y_range=(0, 5000),
                                             x_multiplier=prev_multiplier))
                    Rs.append(A.TrajPlotInfo(outcome_name='In: Recovered-'+str_a_p, title='Recovered\n'+str_p,
                                             # y_range=(0, 105000),
                                             x_multiplier=prev_multiplier))
                    Ds.append(A.TrajPlotInfo(outcome_name='Total to: Death-'+str_a_p, title='Cumulative death\n'+str_p,
                                             # y_range=(0, 500),
                                             x_multiplier=prev_multiplier))

            list_plot_info = []
            for v in range(pd.nVariants):
                for vs in range(pd.nVaccStatus):
                    p = pd.get_profile_index(variant=v, vacc_status=vs)
                    list_plot_info.extend([Es[p], Is[p], Hs[p], Rs[p], Ds[p]])
            list_plot_info += [S, V]

            # validation
            filename_validation = ROOT_DIR+'/outputs/figures/{}.png'.format(str_a)
            sim_outcomes.plot_multi_panel(n_rows=pd.nProfiles+1, n_cols=5,
                                          list_plot_info=list_plot_info,
                                          n_random_trajs_to_display=n_random_trajs_to_display,
                                          file_name=filename_validation,
                                          figure_size=(2*(pd.nVariants+1), 2*5))

    # -----------------------------------------------------
    # ------ plot information for the summary plot --------
    # -----------------------------------------------------
    obs_inc_rate = A.TrajPlotInfo(
        outcome_name='Obs: Incidence rate',
        title='Incidence rate\n(per 100,000 population)',
        y_range=(0, 25000), y_multiplier=100000, x_multiplier=obs_incd_multiplier)
    obs_hosp_occ_rate = A.TrajPlotInfo(
        outcome_name='Hospital occupancy rate',
        title='Rate of hospital occupancy\n(per 100,000 population)',
        y_range=(0, 150), y_multiplier=100000, x_multiplier=prev_multiplier,
        calibration_info=A.CalibrationTargetPlotInfo(
            feasible_range_info=A.FeasibleRangeInfo(
                x_range=[0, FEASIBILITY_PERIOD*52],
                y_range=[MIN_HOSP_OCC_RATE, MAX_HOSP_OCC_RATE]))
    )
    obs_hosp_rate = A.TrajPlotInfo(
        outcome_name='Obs: New hospitalization rate',
        title='Rate of new hospitalizations\n(per 100,000 population)',
        y_range=(0, 150), y_multiplier=100000, x_multiplier=incd_multiplier,
        calibration_info=A.CalibrationTargetPlotInfo(
            feasible_range_info=A.FeasibleRangeInfo(
                x_range=[0, FEASIBILITY_PERIOD*52],
                y_range=[MIN_HOSP_RATE_OVERALL, MAX_HOSP_RATE_OVERALL])))
    obs_cum_hosp_rate = A.TrajPlotInfo(
        outcome_name='Obs: Cumulative hospitalization rate',
        title='Cumulative hospitalizations\n(per 100,000 population)',
        y_range=(0, 1000*3), y_multiplier=100000, x_multiplier=prev_multiplier,
        calibration_info=A.CalibrationTargetPlotInfo(
            rows_of_data=CUM_HOSP_RATE_OVERALL
        ))
    obs_prev_immune_from_inf = A.TrajPlotInfo(
        outcome_name='Obs: Prevalence with immunity from infection',
        title='Prevalence of population with\nimmunity from infection (%)',
        y_range=(0, 100), y_multiplier=100, x_multiplier=prev_multiplier,
        calibration_info=A.CalibrationTargetPlotInfo(
            rows_of_data=PREV_IMMUNE_FROM_INF,
            feasible_range_info=A.FeasibleRangeInfo(
                x_range=[0, FEASIBILITY_PERIOD * 52],
                y_range=[0, MAX_PREV_IMMUNE_FROM_INF])))
    obs_cum_vacc_rate = A.TrajPlotInfo(
        outcome_name='Obs: Cumulative vaccination rate',
        title='Prevalence of vaccinated\nindividuals (%)',
        y_range=(0, 100), y_multiplier=100, x_multiplier=prev_multiplier,
        calibration_info=A.CalibrationTargetPlotInfo(
            rows_of_data=D.VACCINE_COVERAGE_OVER_TIME,
            if_connect_obss=True))
    obs_incd_delta = A.TrajPlotInfo(
        outcome_name='Obs: % of incidence due to Delta',
        title='Incidence associated with\n'
              'the delta variant (%)',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier,
        calibration_info=A.CalibrationTargetPlotInfo(
            rows_of_data=D.PERC_INF_WITH_NOVEL,
            if_connect_obss=False))
    obs_incd_novel = A.TrajPlotInfo(
        outcome_name='Obs: % of incidence due to Novel',
        title='Incidence associated\nwith a novel variant (%)',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier)

    # summary
    # sim_outcomes.plot_multi_panel(n_rows=2, n_cols=2,
    #                               list_plot_info=[obs_hosp_rate, obs_cum_hosp_rate,
    #                                               obs_hosp_occ_rate, obs_cum_vacc_rate],
    #                               file_name=save_plots_dir+'/summary3.png',
    #                               n_random_trajs_to_display=n_random_trajs_to_display,
    #                               show_subplot_labels=True,
    #                               figure_size=(2.3*2, 2.4*2)
    #                               )
    sim_outcomes.plot_multi_panel(n_rows=3, n_cols=3,
                                  list_plot_info=[obs_hosp_occ_rate, obs_hosp_rate, obs_prev_immune_from_inf,
                                                  obs_cum_hosp_rate, obs_cum_vacc_rate, obs_incd_delta,
                                                  obs_incd_novel],
                                  file_name=save_plots_dir+'/summary.png',
                                  n_random_trajs_to_display=n_random_trajs_to_display,
                                  show_subplot_labels=True,
                                  figure_size=(2.3*3, 2.4*3)
                                  )

    sim_outcomes.plot_multi_panel(n_rows=1, n_cols=2,
                                  list_plot_info=[obs_cum_hosp_rate, obs_cum_vacc_rate, obs_incd_delta],
                                  file_name=save_plots_dir+'/summary_r21.png',
                                  n_random_trajs_to_display=n_random_trajs_to_display,
                                  show_subplot_labels=True,
                                  figure_size=(1.8*2, 1.8)
                                  )

    # -----------------------------------------------------
    # ------ plot information for the novel variant plot --------
    # -----------------------------------------------------

    obs_incd_delta = A.TrajPlotInfo(
        outcome_name='Obs: % of incidence due to Delta',
        title='Incidence associated\nwith Delta variant (%)',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier,
        calibration_info=A.CalibrationTargetPlotInfo(
            rows_of_data=D.PERC_INF_WITH_NOVEL,
            if_connect_obss=False))
    obs_new_hosp_delta = A.TrajPlotInfo(
        outcome_name='Obs: % of new hospitalizations due to Delta',
        title='New hospitalizations associated\nwith Delta variant (%)',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier)
    obs_incd_delta_vacc = A.TrajPlotInfo(
        outcome_name='Obs: % of incidence due to Delta-Vacc',
        title='% incidence that are\nvaccinated and due to Delta variant',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier)
    obs_new_hosp_delta_vacc = A.TrajPlotInfo(
        outcome_name='Obs: % of new hospitalizations due to Delta-Vacc',
        title='% new hospitalizations that are\nvaccinated and due to Delta variant',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier)

    obs_incd_novel = A.TrajPlotInfo(
        outcome_name='Obs: % of incidence due to Novel',
        title='Incidence associated\nwith a novel variant (%)',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier)
    obs_new_hosp_novel = A.TrajPlotInfo(
        outcome_name='Obs: % of new hospitalizations due to Novel',
        title='New hospitalizations associated\nwith a novel variant (%)',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier)
    obs_incd_novel_vacc = A.TrajPlotInfo(
        outcome_name='Obs: % of incidence due to Novel-Vacc',
        title='% incidence that are\nvaccinated and due to a novel variant',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier)
    obs_new_hosp_novel_vacc = A.TrajPlotInfo(
        outcome_name='Obs: % of new hospitalizations due to Novel-Vacc',
        title='% new hospitalizations that are\n vaccinated and due to a novel variant',
        y_range=(0, 100), y_multiplier=100,
        x_multiplier=obs_incd_multiplier)

    sim_outcomes.plot_multi_panel(n_rows=4, n_cols=2,
                                  list_plot_info=[obs_incd_delta, obs_incd_novel,
                                                  obs_new_hosp_delta, obs_new_hosp_novel,
                                                  obs_incd_delta_vacc, obs_incd_novel_vacc,
                                                  obs_new_hosp_delta_vacc, obs_new_hosp_novel_vacc],
                                  file_name=save_plots_dir+'/novel_variant.png',
                                  n_random_trajs_to_display=n_random_trajs_to_display,
                                  show_subplot_labels=True,
                                  figure_size=(2.3*2, 2.4*4)
                                  )

    # -----------------------------------------------------
    # ------ plot information for calibration figure
    # -----------------------------------------------------
    hosp_rate_by_age = []
    cum_hosp_rate_by_age = []
    age_dist_cum_hosp = []
    cum_vaccine_rate_by_age = []

    for a in range(pd.nAgeGroups):
        str_a = pd.strAge[a]

        hosp_rate_by_age.append(A.TrajPlotInfo(
            outcome_name='New hospitalization rate-{}'.format(str_a),
            title=str_a, y_label='New hospitalization rate\n(per 100,000 population)' if a == 0 else None,
            y_range=(0, 1000), y_multiplier=100000, x_multiplier=incd_multiplier,
            # calibration_info=A.CalibrationTargetPlotInfo(
            #     feasible_range_info=A.FeasibleRangeInfo(
            #         x_range=[0, CALIB_PERIOD * 52], y_range=[0, MAX_HOSP_RATE_BY_AGE[a]]))
        ))

        cum_hosp_rate_by_age.append(A.TrajPlotInfo(
            outcome_name='Cumulative hospitalization rate-{}'.format(str_a),
            title=str_a, y_label='Cumulative hospitalization rate\n(per 100,000 population)' if a == 0 else None,
            y_range=(0, 5000), y_multiplier=100000, x_multiplier=prev_multiplier,
            calibration_info=A.CalibrationTargetPlotInfo(rows_of_data=D.CUM_HOSP_RATE_BY_AGE[a])))

        age_dist_cum_hosp.append(A.TrajPlotInfo(
            outcome_name='Cumulative hospitalizations-{} (%)'.format(str_a),
            title=str_a, y_label='Age-distribution of\ncumulative hospitalizations (%)' if a == 0 else None,
            y_range=(0, 100), y_multiplier=100, x_multiplier=prev_multiplier,
            calibration_info=A.CalibrationTargetPlotInfo(rows_of_data=D.HOSP_AGE_DIST[a])))

        cum_vaccine_rate_by_age.append(A.TrajPlotInfo(
            outcome_name='Cumulative vaccination rate-{}'.format(str_a),
            title=str_a, y_label='Cumulative vaccination rate (%)' if a == 0 else None,
            y_range=(0, 100), y_multiplier=100, x_multiplier=prev_multiplier,
            calibration_info=A.CalibrationTargetPlotInfo(rows_of_data=VACCINE_COVERAGE_BY_AGE[a],
                                                         if_connect_obss=True)
        ))

    filename_validation = save_plots_dir+'/calibration.png'
    list_plot_info = hosp_rate_by_age
    list_plot_info.extend(cum_hosp_rate_by_age)
    list_plot_info.extend(age_dist_cum_hosp)
    list_plot_info.extend(cum_vaccine_rate_by_age)
    A.Y_LABEL_COORD_X = -0.35
    sim_outcomes.plot_multi_panel(n_rows=4, n_cols=len(AgeGroups),
                                  list_plot_info=list_plot_info,
                                  n_random_trajs_to_display=n_random_trajs_to_display,
                                  file_name=filename_validation,
                                  figure_size=(11, 6.5))

    # --------------------------------------------------------------------
    # ------ plot information for the incidence figure  --------
    # --------------------------------------------------------------------
    incd_rate_by_age = []
    age_dist_cum_incd = []
    cum_death_rate_by_age = []
    age_dist_cum_death = []

    for a in range(pd.nAgeGroups):

        str_a = pd.strAge[a]

        incd_rate_by_age.append(A.TrajPlotInfo(
            outcome_name='Incidence rate-{}'.format(str_a),
            title=str_a, y_label='Incidence rate\n(per 100,000 population) ' if a == 0 else None,
            y_range=(0, 20000), y_multiplier=100000, x_multiplier=incd_multiplier))
        age_dist_cum_incd.append(A.TrajPlotInfo(
            outcome_name='Cumulative incidence-{} (%)'.format(str_a),
            title=str_a, y_label='Age-distribution of\ncumulative incident (%)' if a == 0 else None,
            y_range=(0, 100), y_multiplier=100, x_multiplier=prev_multiplier))
        cum_death_rate_by_age.append(A.TrajPlotInfo(
            outcome_name='Cumulative death rate-{}'.format(str_a),
            title=str_a, y_label='Cumulative deaths rate\n(per 100,000 population)' if a == 0 else None,
            y_range=(0, 1000), y_multiplier=100000, x_multiplier=prev_multiplier))

        age_dist_cum_death.append(A.TrajPlotInfo(
            outcome_name='Cumulative death-{} (%)'.format(str_a),
            title=str_a, y_label='Age-distribution of\n cumulative deaths (%)' if a == 0 else None,
            y_range=(0, 100), y_multiplier=100, x_multiplier=prev_multiplier))

    filename_validation = save_plots_dir+'/incidence.png'
    list_plot_info = incd_rate_by_age
    list_plot_info.extend(age_dist_cum_incd)
    #list_plot_info.extend(age_dist_cum_death)
    A.Y_LABEL_COORD_X = -0.25
    sim_outcomes.plot_multi_panel(n_rows=2, n_cols=len(AgeGroups),
                                  list_plot_info=list_plot_info,
                                  n_random_trajs_to_display=n_random_trajs_to_display,
                                  file_name=filename_validation,
                                  figure_size=(15, 4))


if __name__ == "__main__":

    # get model settings
    sets = COVIDSettings()

    plot(prev_multiplier=52,  # to show weeks on the x-axis of prevalence data
         incd_multiplier=sets.simulationOutputPeriod * 52,  # to show weeks on the x-axis of incidence data
         obs_incd_multiplier=sets.observationPeriod * 52,
         n_random_trajs_to_display=100,
         plot_the_size_of_compartments=sets.ifCollectTrajsOfCompartments)

