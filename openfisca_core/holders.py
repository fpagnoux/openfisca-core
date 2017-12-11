# -*- coding: utf-8 -*-


from __future__ import division
import warnings
import os
import shutil

import numpy as np

from commons import empty_clone
import periods
from periods import MONTH, YEAR, ETERNITY
from columns import make_column_from_variable
import logging
import psutil

log = logging.getLogger(__name__)


WHITE_LIST = set(['indemnite_residence', 'aspa', 'al_nb_personnes_a_charge', 'revenu_assimile_pension', 'date_arret_de_travail', 'tns_auto_entrepreneur_benefice', 'enfant_a_charge', 'indemnites_stage', 'salaire_net_hors_revenus_exceptionnels', 'div', 'assiette_cotisations_sociales', 'nbR', 'rsa_forfait_logement', 'glo', 'hsup', 'tns_benefice_exploitant_agricole', 'prestation_compensatoire', 'aide_logement_montant', 'rsa_indemnites_journalieres_activite', 'pensions_invalidite', 'plafond_securite_sociale', 'f2ee', 'rev_cap_bar', 'tns_micro_entreprise_benefice', 'aide_logement_assiette_abattement_chomage', 'autonomie_financiere', 'est_enfant_dans_famille', 'residence_dom', 'pensions_alimentaires_versees_individu', 'revenu_assimile_salaire_apres_abattements', 'aspa_eligibilite', 'ass', 'asi', 'tns_autres_revenus', 'paje_clca', 'f3vt', 'f3vm', 'f3vc', 'f3ve', 'salaire_de_base', 'f3vl', 'f3vg', 'aah', 'gains_exceptionnels', 'retraite_titre_onereux', 'f2tr', 'f2ts', 'rev_coll', 'traitement_indiciaire_brut', 'indemnites_volontariat', 'af_nbenf', 'al_couple', 'f2fu', 'ppa_rsa_derniers_revenus_tns_annuels_connus', 'rfr', 'primes_fonction_publique', 'paje_colca', 'allocation_securisation_professionnelle', 'cf_non_majore_avant_cumul', 'rpns', 'rsa_forfait_asf', 'etr', 'asi_eligibilite', 'chomage_net', 'f2ch', 'rsa_indemnites_journalieres_hors_activite', 'tns_micro_entreprise_chiffre_affaires', 'revenus_stage_formation_pro', 'prime_forfaitaire_mensuelle_reprise_activite', 'avf', 'tns_autres_revenus_chiffre_affaires', 'en_couple', 'dedommagement_victime_amiante', 'statut_occupation_logement', 'prestations_familiales_base_ressources', 'paje_base', 'rsa_nb_enfants', 'div_ms', 'af_base', 'retraite_nette', 'cf', 'residence_mayotte', 'rsa_base_ressources_patrimoine_individu', 'rev_microsocial', 'rsa_majore_eligibilite', 'indemnites_journalieres', 'salaire_net', 'cotisation_sociale_mode_recouvrement', 'salaire_imposable', 'revenu_activite', 'date_naissance', 'indemnites_chomage_partiel', 'af', 'bourse_recherche', 'etudiant', 'categorie_salarie', 'f2dh', 'f2da', 'f2dc', 'pensions_alimentaires_percues', 'age', 'tns_auto_entrepreneur_type_activite'])


BLACK_LIST = set(['nombre_enfants_majeurs_celibataires_sans_enfant', 'forfait_jours_remuneres_volume', 'pensions', 'af_coeff_garde_alternee', 'af_allocation_forfaitaire_taux_modulation', 'f7wr', 'residence_guyane', 'af_nbenf_fonc', 'revenus_du_travail', 'assiette_proflib', 'isf_tot', 'f5kt', 'aides_logement_primo_accedant_plafond_mensualite', 'af_complement_degressif', 'f6fl', 'f6fb', 'f6fa', 'f6fd', 'f6fe', 'aides_logement', 'cncn_adef', 'cotsoc_bar', 'doment', 'f3sa', 'locmeu', 'f6ps', 'dfppce', 'f2ab', 'f2aa', 'f2an', 'f2am', 'f2al', 'macc_pvce', 'cf_dom_enfant_eligible', 'f7gn', 'f7gh', 'f2ar', 'f2aq', 'grosses_reparations', 'f7ge', 'f7gf', 'f7gg', 'f7ga', 'f7gb', 'f7gc', 'preetu', 'tns_avec_employe', 'nbN', 'valeur_locative_immo_non_loue', 'aide_logement_base_ressources_eval_forfaitaire', 'alnp_defs', 'csg_fon', 'b2mv', 'isf_reduc_pac', 'b1ab', 'b1ac', 'prelsoc_fon', 'csg_deduc', 'b2mx', 'aide_logement_abattement_depart_retraite', 'f7ec', 'paje_cmg', 'daepad', 'af_eligibilite_dom', 'revenus_du_capital', 'isf_imm_non_bati', 'mbic_pvct', 'ppa_ressources_hors_activite_individu', 'isf_droits_sociaux', 'valeur_locative_terrains_non_loue', 'ape', 'csg_pv_mo', 'deficit_ante', 'invfor', 'mbnc_mvlt', 'aeeh', 'ppa_eligibilite', 'saldom2', 'prelsoc_pv_immo', 'f7nz', 'caseH', 'aacc_gits', 'agirc_gmp_assiette', 'heures_duree_collective_entreprise', 'minimum_vieillesse', 'f7ed', 'ir_ss_qf', 'residence_reunion', 'cd_sofipe', 'f5sq', 'cf_majore_avant_cumul', 'cehr', 'f5rr', 'aah_base', 'ir_brut', 'decote_isf', 'exoneration_cotisations_salarie_stagiaire', 'csg', 'ecpess', 'aides_logement_primo_accedant_loyer_minimal', 'plus_values', 'f5qp', 'aacc_defs', 'autent', 'f7uo', 'f7um', 'f7uc', 'teicaa', 'nrag_ajag', 'aide_logement_participation_personnelle', 'f7us', 'f5qq', 'travailleur_non_salarie', 'patnat', 'rev_cat', 'cd_deddiv', 'macc_mvlt', 'heures_remunerees_volume', 'frag_pvce', 'f5jt', 'f6fc', 'mncn_pvce', 'revenu_activite_salariee', 'isf_actions_sal', 'macc_mvct', 'aefa', 'mbnc_pvct', 'af_age_aine', 'aide_logement_neutralisation_rsa', 'epargne_non_remuneree', 'af_allocation_forfaitaire_complement_degressif', 'mbnc_pvce', 'f7cd', 'f7ce', 'stage_gratification', 'residence_guadeloupe', 'nombre_jours_calendaires', 'f1tw', 'f1tv', 'f7uk', 'f1tx', 'garext', 'b2nc', 'b2na', 'b2nf', 'revimpres', 'b2ne', 'avantage_en_nature', 'abic_impm', 'f6hj', 'f6hk', 'f6hl', 'rsa_condition_nationalite', 'mncn_mvct', 'indemnite_fin_contrat_due', 'f5mt', 'nouvelle_bonification_indiciaire', 'f6gh', 'abic_pvce', 'isf_inv_pme', 'charges_deduc', 'impots_directs', 'aide_logement_loyer_seuil_suppression', 'revenu_activite_non_salariee', 'mbic_mvct', 'mohist', 'abnc_pvce', 'iai', 'cotsyn', 'f4bf', 'gar_dom', 'f3vj', 'cf_dom_enfant_trop_jeune', 'asf_elig', 'aide_logement_R0', 'mbic_mvlt', 'decote', 'creimp', 'isf_avant_reduction', 'aeeh_niveau_handicap', 'f4bl', 'f7fh', 'cncn_pvce', 'f7ff', 'f3va', 'indemnites_compensatrices_conges_payes', 'titre_restaurant_volume', 'isf_imm_bati', 'cd_doment', 'f8uy', 'f7gz', 'f7gi', 'contrat_de_travail', 'ci_garext', 'aacc_pvce', 'cbnc_assc', 'prise_en_charge_employeur_prevoyance_complementaire', 'iaidrdi', 'rsa_activite', 'f2bg', 'paje_clca_taux_partiel', 'mbnc_mvct', 'crds_fon', 'aah_eligible', 'f5it', 'prelsoc_pv_mo', 'aide_logement_taux_loyer', 'f6dd', 'apje_avant_cumul', 'csg_deduc_patrimoine', 'f7fn', 'drbail', 'spfcpi', 'duflot', 'ass_mat', 'interets_epargne_sur_livrets', 'defacc', 'reductions', 'nbnc_pvce', 'enceinte', 'scelli', 'f7fg', 'ass_base_ressources', 'revenu_disponible', 'prestations_familiales', 'nbic_apch', 'domlog', 'als_etudiant', 'invlst', 'adhcga', 'f5rq', 'af_majoration_enfant', 'f5rw', 'isf_iai', 'nbic_pvce', 'cd1', 'cd2', 'participation_frais', 'ppa_base_ressources', 'ass_base_ressources_individu', 'f5ro', 'f5rn', 'residence_martinique', 'complementaire_sante_employeur', 'assiette_cotisations_sociales_prive', 'pvtaimpres', 'nacc_meup', 'asf_elig_enfant', 'b2mt', 'aides_logement_primo_accedant', 'f5lt', 'prlire', 'f4tq', 'contribution_exceptionnelle_solidarite', 'rfr_cd', 'reduction_impot_exceptionnelle', 'revenu_assimile_salaire', 'ircantec_salarie', 'rfr_rvcm', 'boursier', 'avantage_en_nature_valeur_forfaitaire', 'crds', 'prestations_sociales', 'assloy', 'rsa_revenu_activite', 'tot_impot', 'f5qn', 'f5qo', 'f6rs', 'f5qg', 'pensions_alimentaires_percues_decl', 'f7eb', 'f7ea', 'f7ef', 'f7eg', 'tns_autres_revenus_type_activite', 'caseL', 'contrat_de_travail_fin', 'saldom', 'pensions_alimentaires_versees', 'ppa_montant_forfaitaire_familial_non_majore', 'cappme', 'f7wl', 'f7wm', 'f7wn', 'sofica', 'f7wj', 'b1cf', 'b1cd', 'b1ce', 'b1cb', 'b1cl', 'f7wp', 'isf_org_int_gen', 'casa', 'asi_aspa_base_ressources_individu', 'f5gb', 'f5gc', 'f5ga', 'f5gf', 'f5gg', 'f5gd', 'f5ge', 'f5gj', 'f5gh', 'f5gi', 'assiette_cotisations_sociales_public', 'rev_cat_rpns', 'donapd', 'f5ht', 'prevoyance_obligatoire_cadre', 'f6eu', 'cont_rev_loc', 'apje', 'ppa_montant_forfaitaire_familial_majore', 'abattement_salaires_pensions', 'cf_majore_plafond', 'ppa_bonification', 'salarie_regime_alsace_moselle', 'b4rs', 'inthab', 'ass_base_ressources_conjoint', 'crds_pv_immo', 'abic_defm', 'nacc_pvce', 'cotsoc_lib', 'prelsoc_cap', 'arrco_tranche_a_taux_salarie', 'aah_base_ressources', 'aide_logement_loyer_seuil_degressivite', 'deficit_rcm', 'contrat_de_travail_duree', 'f7td', 'aide_logement_taux_famille', 'defrag', 'rev_cat_tspr', 'aspa_couple', 'f6ev', 'titre_restaurant_valeur_unitaire', 'rnc', 'remuneration_apprenti', 'psa', 'f5qf', 'assiette_vente', 'cf_ressources_individu', 'ppa_ressources_hors_activite', 'defmeu', 'api', 'ass_precondition_remplie', 'cotisations_salariales', 'crds_pv_mo', 'als_non_etudiant', 'defncn', 'cf_montant', 'ppa_eligibilite_etudiants', 'revetproduits', 'mbic_pvce', 'taux_effectif', 'quaenv', 'revenus_capital', 'aide_logement_base_ressources_defaut', 'ppa_base_ressources_prestations_familiales', 'f5rp', 'isf_apres_plaf', 'crds_mini', 'paje_clca_taux_plein', 'paje_naissance', 'partiel2', 'reintegration_titre_restaurant_employeur', 'csg_pv_immo', 'f7ac', 'empl_dir', 'rpns_mvlt', 'f7vo', 'ppa', 'cf_enfant_eligible', 'ppe', 'aidper', 'stage_gratification_taux', 'taxe_habitation', 'b1bc', 'b1be', 'f6de', 'b1bh', 'b1bk', 'nbic_mvct', 'exonere_taxe_habitation', 'arag_pvce', 'minima_sociaux', 'b2gh', 'prevoyance_obligatoire_cadre_taux_employeur', 'ape_avant_cumul', 'exoneration_cotisations_salariales_apprenti', 'rsa_eligibilite', 'af_eligibilite_base', 'creaen', 'aides_logement_primo_accedant_k', 'complementaire_sante_salarie', 'prcomp', 'paje_base_enfant_eligible_apres_reforme_2014', 'contrat_de_travail_debut', 'direpa', 'credits_impot', 'repsoc', 'intagr', 'f6cb', 'nrag_pvce', 'aide_logement_montant_brut_avant_degressivite', 'f7wo', 'opt_colca', 'aide_logement_abattement_chomage_indemnise', 'rsceha', 'titre_restaurant_taux_employeur', 'assiette_service', 'ppa_fictive', 'indu_plaf_abat_pen', 'deffor', 'pveximpres', 'mncn_mvlt', 'f6ss', 'rsa_non_calculable', 'ass_eligibilite_individu', 'pensions_alimentaires_deduites', 'rsa_base_ressources_prestations_familiales', 'resimm'])


class DatedHolder(object):
    """
        A wrapper of the value of a variable for a given period (and possibly a given set of extra parameters).
    """
    holder = None
    period = None
    extra_params = None

    def __init__(self, holder, period, value, extra_params = None):
        self.holder = holder
        self.period = period
        self.extra_params = extra_params
        self.value = value

    @property
    def array(self):
        return self.value

    @array.setter
    def array(self, array):
        raise ValueError('Impossible to modify DatedHolder.array. Please use Holder.put_in_cache.')

    @property
    def variable(self):
        return self.holder.variable

    @property
    def entity(self):
        return self.holder.entity

    def to_value_json(self, use_label = False):
        column = make_column_from_variable(self.holder.variable)
        transform_dated_value_to_json = column.transform_dated_value_to_json
        return [
            transform_dated_value_to_json(cell, use_label = use_label)
            for cell in self.array.tolist()
            ]


class Holder(object):
    """
        A holder keeps tracks of a variable values after they have been calculated, or set as an input.
    """
    _array = None  # Only used when variable.definition_period == ETERNITY
    _array_by_period = None  # Only used when variable.definition_period != ETERNITY
    variable = None
    entity = None
    formula = None
    formula_output_period_by_requested_period = None

    def __init__(self, simulation = None, variable = None, entity = None):
        assert variable is not None
        assert self.variable is None
        if simulation is not None:
            warnings.warn(
                u"The Holder(simulation, variable) constructor has been deprecated. "
                u"Please use Holder(entity = entity, variable = variable) instead.",
                Warning
                )
            self.simulation = simulation
            self.entity = simulation.get_entity(variable.entity)
        else:
            self.entity = entity
            self.simulation = entity.simulation
        self.variable = variable
        self.buffer = {}
        self.memory_storage = InMemoryStorage(is_eternal = self.variable.definition_period == ETERNITY)
        self.disk_storage = None  # By default, do not activate on-disk storage

    # Sould probably be deprecated
    @property
    def array(self):
        return get_array(self.simulation.perio)

    @array.setter
    def array(self, array):
        if self.variable.definition_period != ETERNITY:
            return self.put_in_cache(array, self.simulation.period)
        self._array = array

    def calculate(self, period, **parameters):
        dated_holder = self.compute(period = period, **parameters)
        return dated_holder.array

    def calculate_output(self, period):
        return self.formula.calculate_output(period)

    def clone(self, entity):
        """Copy the holder just enough to be able to run a new simulation without modifying the original simulation."""
        new = empty_clone(self)
        new_dict = new.__dict__

        for key, value in self.__dict__.iteritems():
            if key in ('_array_by_period',):
                if value is not None:
                    # There is no need to copy the arrays, because the formulas don't modify them.
                    new_dict[key] = value.copy()
            elif key not in ('entity', 'formula', 'simulation'):
                new_dict[key] = value

        new_dict['entity'] = entity
        new_dict['simulation'] = entity.simulation
        # Caution: formula must be cloned after the entity has been set into new.
        formula = self.formula
        if formula is not None:
            new_dict['formula'] = formula.clone(new)

        return new

    def compute(self, period, **parameters):
        """
            Compute the variable's value for the ``period`` and return a dated holder containing the value.
        """

        if self.simulation.trace:
            self.simulation.tracer.record_calculation_start(self.variable.name, period, **parameters)
        variable = self.variable

        # Check that the requested period matches definition_period
        if variable.definition_period != ETERNITY:
            if variable.definition_period == MONTH and period.unit != periods.MONTH:
                raise ValueError(u'Unable to compute variable {0} for period {1} : {0} must be computed for a whole month. You can use the ADD option to sum {0} over the requested period, or change the requested period to "period.first_month".'.format(
                    variable.name,
                    period
                    ).encode('utf-8'))
            if variable.definition_period == YEAR and period.unit != periods.YEAR:
                raise ValueError(u'Unable to compute variable {0} for period {1} : {0} must be computed for a whole year. You can use the DIVIDE option to get an estimate of {0} by dividing the yearly value by 12, or change the requested period to "period.this_year".'.format(
                    variable.name,
                    period
                    ).encode('utf-8'))
            if period.size != 1:
                raise ValueError(u'Unable to compute variable {0} for period {1} : {0} must be computed for a whole {2}. You can use the ADD option to sum {0} over the requested period.'.format(
                    variable.name,
                    period,
                    'month' if variable.definition_period == MONTH else 'year').encode('utf-8'))

        extra_params = parameters.get('extra_params')

        # First look for a value already cached
        holder_or_dated_holder = self.get_from_cache(period, extra_params)
        if holder_or_dated_holder.array is not None:
            if self.simulation.trace:
                self.simulation.tracer.record_calculation_end(self.variable.name, period, holder_or_dated_holder.array, **parameters)
            return holder_or_dated_holder
        assert self._array is None  # self._array should always be None when dated_holder.array is None.

        # Request a computation
        dated_holder = self.formula.compute(period = period, **parameters)
        if self.variable.name in BLACK_LIST:
            formula_dated_holder = dated_holder
        else:
            formula_dated_holder = self.put_in_cache(dated_holder.array, period, extra_params)
        if self.simulation.trace:
            self.simulation.tracer.record_calculation_end(self.variable.name, period, dated_holder.array, **parameters)
        return formula_dated_holder

    def compute_add(self, period, **parameters):
        # Check that the requested period matches definition_period
        if self.variable.definition_period == YEAR and period.unit == periods.MONTH:
            raise ValueError(u'Unable to compute variable {0} for period {1} : {0} can only be computed for year-long periods. You can use the DIVIDE option to get an estimate of {0} by dividing the yearly value by 12, or change the requested period to "period.this_year".'.format(
                self.variable.name,
                period,
                ).encode('utf-8'))

        if self.variable.definition_period == MONTH:
            variable_definition_period = periods.MONTH
        elif self.variable.definition_period == YEAR:
            variable_definition_period = periods.YEAR
        else:
            raise ValueError(u'Unable to sum constant variable {} over period {} : only variables defined monthly or yearly can be summed over time.'.format(
                self.variable.name,
                period).encode('utf-8'))

        after_instant = period.start.offset(period.size, period.unit)
        sub_period = period.start.period(variable_definition_period)
        array = None
        while sub_period.start < after_instant:
            dated_holder = self.compute(period = sub_period, **parameters)
            if array is None:
                array = dated_holder.array.copy()
            else:
                array += dated_holder.array
            sub_period = sub_period.offset(1)

        return DatedHolder(self, period, array, parameters.get('extra_params'))

    def compute_divide(self, period, **parameters):
        # Check that the requested period matches definition_period
        if self.variable.definition_period != YEAR:
            raise ValueError(u'Unable to divide the value of {} over time (on period {}) : only variables defined yearly can be divided over time.'.format(
                self.variable.name,
                period).encode('utf-8'))

        if period.size != 1:
            raise ValueError("DIVIDE option can only be used for a one-year or a one-month requested period")

        if period.unit == periods.MONTH:
            computation_period = period.this_year
            dated_holder = self.compute(period = computation_period, **parameters)
            array = dated_holder.array / 12.
            return DatedHolder(self, period, array, parameters.get('extra_params'))
        elif period.unit == periods.YEAR:
            return self.compute(period, **parameters)

        raise ValueError(u'Unable to divide the value of {} to match the period {}.'.format(
            self.variable.name,
            period).encode('utf-8'))

    def delete_arrays(self, period = None):
        """
            If ``period`` is ``None``, remove all known values of the variable.

            If ``period`` is not ``None``, only remove all values for any period included in period (e.g. if period is "2017", values for "2017-01", "2017-07", etc. would be removed)

        """

        self.memory_storage.delete(period)
        if self.disk_storage:
            self.disk_storage.delete(period)

    def get_array(self, period, extra_params = None):
        """
        Get the value of the variable for the given period (and possibly a list of extra parameters).

        If the value is not known, return ``None``.
        """
        value = self.memory_storage.get(period, extra_params)
        if value is not None:
            return value
        if self.disk_storage:
            return self.disk_storage.get(period, extra_params)

    def graph(self, edges, get_input_variables_and_parameters, nodes, visited):
        variable = self.variable
        if self in visited:
            return
        visited.add(self)
        nodes.append(dict(
            id = variable.name,
            group = self.entity.key,
            label = variable.name,
            title = variable.label,
            ))
        formula = self.formula
        if formula is None:
            return
        formula.graph_parameters(edges, get_input_variables_and_parameters, nodes, visited)

    def get_memory_usage(self):
        """
            Gets data about the virtual memory usage of the holder.

            :returns: Memory usage data
            :rtype: dict

            Exemple:

            >>> holder.get_memory_usage()
            >>> {
            >>>    'nb_arrays': 12,  # The holder contains the variable values for 12 different periods
            >>>    'nb_cells_by_array': 100, # There are 100 entities (e.g. persons) in our simulation
            >>>    'cell_size': 8,  # Each value takes 8B of memory
            >>>    'dtype': dtype('float64')  # Each value is a float 64
            >>>    'total_nb_bytes': 10400  # The holder uses 10.4kB of virtual memory
            >>>    }
        """

        usage = dict(
            nb_cells_by_array = self.entity.count,
            dtype = self.variable.dtype,
            )

        usage.update(self.memory_storage.get_memory_usage())

        if self.simulation.trace:
            usage_stats = self.simulation.tracer.usage_stats[self.variable.name]
            try:
                usage_stats['nb_requests'] / float(usage['nb_arrays'])
            except:
                from nose.tools import set_trace; set_trace(); import ipdb; ipdb.set_trace()

            usage.update(dict(
                nb_requests = usage_stats['nb_requests'],
                nb_requests_by_array = usage_stats['nb_requests'] / float(usage['nb_arrays'])
                ))

        return usage

    def get_known_periods(self):
        """
        Get the list of periods the variable value is known for.
        """
        return self.memory_storage.get_known_periods() + (
            self.disk_storage.get_known_periods() if self.disk_storage else [])

    @property
    def real_formula(self):
        formula = self.formula
        if formula is None:
            return None
        return formula.real_formula

    def set_input(self, period, array):
        if period.unit == ETERNITY and self.variable.definition_period != ETERNITY:
            error_message = os.linesep.join([
                u'Unable to set a value for variable {0} for ETERNITY.',
                u'{0} is only defined for {1}s. Please adapt your input.',
                ]).format(
                    self.variable.name,
                    self.variable.definition_period
                ).encode('utf-8')
            raise PeriodMismatchError(
                self.variable.name,
                period,
                self.variable.definition_period,
                error_message
                )

        self.formula.set_input(period, array)

    def put_in_cache(self, value, period, extra_params = None):
        simulation = self.simulation

        if value.dtype != self.variable.dtype:
            try:
                value = value.astype(self.variable.dtype)
            except ValueError:
                raise ValueError(
                    u'Unable to set value "{}" for variable "{}", as the variable dtype "{}" does not match the value dtype "{}".'
                    .format(value, self.variable.name, self.variable.dtype, value.dtype)
                    .encode('utf-8'))


        if self.variable.definition_period != ETERNITY:
            if period is None:
                raise ValueError('A period must be specified to put values in cache, except for variables with ETERNITY as as period_definition.')
            if ((self.variable.definition_period == MONTH and period.unit != periods.MONTH) or
               (self.variable.definition_period == YEAR and period.unit != periods.YEAR)):
                error_message = os.linesep.join([
                    u'Unable to set a value for variable {0} for {1}-long period {2}.',
                    u'{0} is only defined for {3}s. Please adapt your input.',
                    u'If you are the maintainer of {0}, you can consider adding it a set_input attribute to enable automatic period casting.'
                    ]).format(
                        self.variable.name,
                        period.unit,
                        period,
                        self.variable.definition_period
                    ).encode('utf-8')

                raise PeriodMismatchError(
                    self.variable.name,
                    period,
                    self.variable.definition_period,
                    error_message
                    )

        if (simulation.opt_out_cache and
                simulation.tax_benefit_system.cache_blacklist and
                self.variable.name in simulation.tax_benefit_system.cache_blacklist):
            return DatedHolder(self, period, value, extra_params)

        if (
            self.simulation.max_memory_occupation is not None and
            self.variable.name not in WHITE_LIST and
            psutil.virtual_memory().percent >= self.simulation.max_memory_occupation
            ):
            if self.disk_storage is None:
                storage_dir = os.path.join(self.simulation.data_storage_dir, self.variable.name)
                os.makedirs(storage_dir)
                self.disk_storage = OnDiskStorage(
                    storage_dir, is_eternal = self.variable.definition_period == ETERNITY)

            self.disk_storage.put(value, period, extra_params)
        else:
            self.memory_storage.put(value, period, extra_params)

        return DatedHolder(self, period, value, extra_params)

    def get_from_cache(self, period, extra_params = None):
        if self.variable.is_neutralized:
            return DatedHolder(self, period, value = self.default_array())

        value = self.get_array(period, extra_params)
        return DatedHolder(self, period, value, extra_params)

    def get_extra_param_names(self, period):
        function = self.formula.find_function(period)

        return function.__func__.func_code.co_varnames[3:]

    def to_value_json(self, use_label = False):
        column = make_column_from_variable(self.variable)
        transform_dated_value_to_json = column.transform_dated_value_to_json

        def extra_params_to_json_key(extra_params, period):
            return '{' + ', '.join(
                ['{}: {}'.format(name, value)
                    for name, value in zip(self.get_extra_param_names(period), extra_params)]
                ) + '}'

        if self.variable.definition_period == ETERNITY:
            array = self._array
            if array is None:
                return None
            return [
                transform_dated_value_to_json(cell, use_label = use_label)
                for cell in array.tolist()
                ]
        value_json = {}
        for period, array_or_dict in self.memory_storage._arrays.iteritems():
            if type(array_or_dict) == dict:
                value_json[str(period)] = values_dict = {}
                for extra_params, array in array_or_dict.iteritems():
                    extra_params_key = extra_params_to_json_key(extra_params, period)
                    values_dict[str(extra_params_key)] = [
                        transform_dated_value_to_json(cell, use_label = use_label)
                        for cell in array.tolist()
                        ]
            else:
                value_json[str(period)] = [
                    transform_dated_value_to_json(cell, use_label = use_label)
                    for cell in array_or_dict.tolist()
                    ]
        if self.disk_storage:
            for period, file_or_dict in self.disk_storage._files.iteritems():
                if type(file_or_dict) == dict:
                    value_json[str(period)] = values_dict = {}
                    for extra_params, file in file_or_dict.iteritems():
                        extra_params_key = extra_params_to_json_key(extra_params, period)
                        values_dict[str(extra_params_key)] = [
                            transform_dated_value_to_json(cell, use_label = use_label)
                            for cell in np.load(file).tolist()
                            ]
                else:
                    value_json[str(period)] = [
                        transform_dated_value_to_json(cell, use_label = use_label)
                        for cell in np.load(file_or_dict).tolist()
                        ]
        return value_json

    def default_array(self):
        array_size = self.entity.count
        array = np.empty(array_size, dtype = self.variable.dtype)
        array.fill(self.variable.default_value)
        return array


class PeriodMismatchError(ValueError):
    def __init__(self, variable_name, period, definition_period, message):
        self.variable_name = variable_name
        self.period = period
        self.definition_period = definition_period
        ValueError.__init__(self, message)


class OnDiskStorage(object):

    def __init__(self, storage_dir, is_eternal = False):
        self._files = {}
        self.is_eternal = is_eternal
        self.storage_dir = storage_dir

    def get(self, period, extra_params = None):
        if self.is_eternal:
            period = periods.period(ETERNITY)
        period = periods.period(period)

        values = self._files.get(period)
        if values is None:
            return None
        if extra_params:
            if values.get(tuple(extra_params)) is None:
                return None
            return np.load(values.get(tuple(extra_params)))
        if isinstance(values, dict):
            return np.load(values.values()[0])
        return np.load(values)

    def put(self, value, period, extra_params = None):
        if self.is_eternal:
            period = periods.period(ETERNITY)
        period = periods.period(period)

        filename = str(period)
        if extra_params:
            filename = '{}_{}'.format(
                filename, '_'.join([str(param) for param in extra_params]))
        path = os.path.join(self.storage_dir, filename) + '.npy'
        np.save(path, value)
        if extra_params is None:
            self._files[period] = path
        else:
            if self._files.get(period) is None:
                self._files[period] = {}
            self._files[period][tuple(extra_params)] = path

    def delete(self, period = None):
        if period is None:
            self._files = {}
            return

        if self.is_eternal:
            period = periods.period(ETERNITY)
        period = periods.period(period)

        if period is not None:
            self._files = {
                period_item: value
                for period_item, value in self._files.iteritems()
                if not period.contains(period_item)
                }

    def get_known_periods(self):
        return self._files.keys()

    def __del__(self):
        shutil.rmtree(self.storage_dir)  # Remove the holder temporary files
        # If the simulation temporary directory is empty, remove it
        parent_dir = os.path.abspath(os.path.join(self.storage_dir, os.pardir))
        if not os.listdir(parent_dir):
            shutil.rmtree(parent_dir)

class InMemoryStorage(object):

    def __init__(self, is_eternal = False):
        self._arrays = {}
        self.is_eternal = is_eternal

    def get(self, period, extra_params = None):
        if self.is_eternal:
            period = periods.period(ETERNITY)
        period = periods.period(period)

        values = self._arrays.get(period)
        if values is None:
            return None
        if extra_params:
            return values.get(tuple(extra_params))
        if isinstance(values, dict):
            return values.values()[0]
        return values

    def put(self, value, period, extra_params = None):
        if self.is_eternal:
            period = periods.period(ETERNITY)
        period = periods.period(period)

        if extra_params is None:
            self._arrays[period] = value
        else:
            if self._arrays.get(period) is None:
                self._arrays[period] = {}
            self._arrays[period][tuple(extra_params)] = value

    def delete(self, period = None):
        if period is None:
            self._arrays = {}
            return

        if self.is_eternal:
            period = periods.period(ETERNITY)
        period = periods.period(period)

        self._arrays = {
            period_item: value
            for period_item, value in self._arrays.iteritems()
            if not period.contains(period_item)
            }

    def get_known_periods(self):
        return self._arrays.keys()

    def get_memory_usage(self):
        if not self._arrays:
            return dict(
                nb_arrays = 0,
                total_nb_bytes = 0,
                cell_size = np.nan,
                )

        nb_arrays = sum([
            len(array_or_dict) if isinstance(array_or_dict, dict) else 1
            for array_or_dict in self._arrays.itervalues()
            ])

        array = self._arrays.values()[0]
        if isinstance(array, dict):
            array = array.values()[0]
        return dict(
            nb_arrays = nb_arrays,
            total_nb_bytes = array.nbytes * nb_arrays,
            cell_size = array.itemsize,
            )
