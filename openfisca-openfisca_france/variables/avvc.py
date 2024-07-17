from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable
from openfisca_core.indexed_enums import Enum
from ressources import *

from entities import Household


class code_organisme(Variable):
    value_type = int
    definition_period = MONTH


class nombre_enfant_charge(Variable):
    value_type = int
    entity = Household
    definition_period = MONTH


class montant_smic_35h(Variable):
    value_type = float
#    entity = Household
    definition_period = MONTH

    def formula(household, period, parameters):
        code_orga = ('code_organisme', period)
        mayotte = household(parameters(period).smic_net_35h_mayotte)
        print(mayotte)
        met = household(parameters(period).smic_net_35h_met_dom)
        if code_orga >= 970:
            return mayotte
        else :
            return met


class TypeAide(Enum):
    pret = 'prêt'
    aide = "aide non remoursable - subvention"


class type_aide(Variable):
    value_type = Enum
    possible_values = TypeAide
    entity = Household
    definition_period = MONTH

    def formula(person, household, period):
        nb_enfant_charge = nombre_enfant_charge
        total_des_ressources = person("total_ressources_foyer", period)
        smic_35h = household("montant_smic_35h", period)
        type_aide = household("TypeAide")
        print(smic_35h)
        
        match (nb_enfant_charge, total_des_ressources, smic_35h):
            case (0, total_des_ressources) if total_des_ressources > (1.5 * smic_35h):
                return type_aide.pret
            case (1, total_des_ressources) if total_des_ressources > (2.25 * smic_35h):
                return type_aide.pret
            case (2, total_des_ressources) if total_des_ressources > (2.7 * smic_35h):
                return type_aide.pret
            case (nb_enfant_charge, total_des_ressources) if nb_enfant_charge >= 3 and total_des_ressources > (3.3 * smic_35h):
                return type_aide.pret
            case _:
                return type_aide.aide


class montant_avvc_majore(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH

    def formula(period, parameters):
        code_orga = code_organisme
        nb_enfant_charge = nombre_enfant_charge
        montant_base_rsa = parameters(period).montant_forfaitaire_RSA_mayotte if code_orga >= 970 else parameters(period).montant_forfaitaire_RSA_met_dom
        
        match(nb_enfant_charge):
            case 0:
                return montant_base_rsa
            case 1:
                return montant_base_rsa * 1.5
            case 2:
                return montant_base_rsa * 1.8
            case 3:
                return montant_base_rsa * 2.2
            case _:
                return montant_base_rsa * (2.2 + ((nb_enfant_charge - 3) * 0.4))


class taux_minoration_avvc(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH

    def fomrula():
        total_des_ressources = total_ressources_foyer
        mont_smic_35h = montant_smic_35h
        match(total_des_ressources):
            case total_des_ressources if mont_smic_35h * 0.5 <= total_des_ressources < mont_smic_35h:
                return 0.2
            case total_des_ressources if mont_smic_35h <= total_des_ressources < mont_smic_35h * 1.5:
                return 0.4
            case total_des_ressources if mont_smic_35h * 1.5 <= total_des_ressources:
                return 0.6
            case _: 0


class montant_avvc(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH

    def formula():
        montant_avvc_maj = montant_avvc_majore
        taux_minoration = taux_minoration_avvc

        return (montant_avvc_maj * (1 - taux_minoration))
