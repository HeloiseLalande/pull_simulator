
import json
import random
from pathlib import Path


def load_gacha_config(json_path: str) -> dict:
    """Charge la configuration du système de gacha depuis le fichier JSON."""
    with open(json_path, 'r') as f:
        return json.load(f)


def determine_rarity(pity_five_star: int, pity_four_star: int, config: dict) -> str:
    """
    Détermine la rareté d'un pull basée sur les pity counters.
    
    Args:
        pity_five_star: Nombre de pulls depuis le dernier 5*
        pity_four_star: Nombre de pulls depuis le dernier 4*
        config: Configuration du gacha
        
    Returns:
        'five_star', 'four_star', ou 'three_star'
    """
    # Vérifier pity 4*
    if pity_four_star >= config['pity_system']['four_star_pity']:
        return 'four_star'
    
    # Vérifier pity 5* (soft pity entre 75 et 90)
    if pity_five_star >= config['pity_system']['five_star_pity']:
        return 'five_star'
    
    # Augmenter probabilité en soft pity (75-90)
    if pity_five_star >= config['pity_system']['five_star_soft_pity_start']:
        # Interpolation linéaire de 0.6% à 100%
        range_pulls = config['pity_system']['five_star_pity'] - config['pity_system']['five_star_soft_pity_start']
        progress = (pity_five_star - config['pity_system']['five_star_soft_pity_start']) / range_pulls
        soft_pity_prob = config['pull_probabilities']['five_star'] + (1.0 - config['pull_probabilities']['five_star']) * progress
        
        if random.random() < soft_pity_prob:
            return 'five_star'
    else:
        # Probabilité normale de 5*
        if random.random() < config['pull_probabilities']['five_star']:
            return 'five_star'
    
    # Probabilité de 4*
    if random.random() < config['pull_probabilities']['four_star']:
        return 'four_star'
    
    return 'three_star'


def determine_five_star_character(guaranteed: bool, config: dict) -> tuple[str, bool]:
    """
    Détermine si le personnage 5* obtenu est désiré ou non.
    
    Args:
        guaranteed: Si le personnage désiré est garanti
        config: Configuration du gacha
        
    Returns:
        Tuple (desired/undesired, new_guaranteed_status)
    """
    if guaranteed:
        return ('desired', False)
    
    if random.random() < config['banner_mechanics']['limited_character']['desired_chance']:
        return ('desired', False)
    else:
        return ('undesired', True)  # Le prochain est garanti


def determine_four_star_type(config: dict) -> str:
    """
    Détermine si le 4* est un personnage ou une arme.
    
    Returns:
        'character' ou 'weapon'
    """
    if random.random() < 0.5:
        return 'character'
    return 'weapon'


def simulate_pulls(num_pulls: int, config: dict, banner_type: str = 'character', use_starlight: bool = False, initial_pity_five_star: int = 0, five_star_guaranteed: bool = False) -> dict:
    """
    Simule un nombre donné de pulls sur une bannière.
    
    Args:
        num_pulls: Nombre de pulls à simuler
        config: Configuration du gacha
        banner_type: Type de bannière ('character' ou 'weapon')
        use_starlight: Si True, consomme les starlight obtenus (20 par pull) pour faire des nouveaux pulls
        initial_pity_five_star: Nombre de pulls déjà effectués en pity 5* (0-90)
        five_star_guaranteed: Si le prochain 5* est garanti (True/False)
        
    Returns:
        Dictionnaire avec les résultats
    """
    results = {
        'five_star_desired': 0, 'five_star_undesired': 0, 'four_star': 0,
        'four_star_characters': 0, 'four_star_weapons': 0,
        'three_star': 0, 'total_starlight': 0, 'total_pulls': 0,
        'bonus_pulls_from_starlight': 0, 'guarantee_active': False,
        'initial_pity_five_star': initial_pity_five_star,
        'initial_guarantee': five_star_guaranteed
    }
    
    pity_five_star = initial_pity_five_star
    pity_four_star = 0
    five_star_guaranteed_status = five_star_guaranteed
    current_starlight = 0
    total_iterations = 0
    max_iterations = 100000  # Limite de sécurité pour éviter les boucles infinies
    
    while num_pulls > 0 and total_iterations < max_iterations:
        total_iterations += 1
        pity_five_star += 1
        pity_four_star += 1
        num_pulls -= 1
        results['total_pulls'] += 1
        
        # Déterminer la rareté
        rarity = determine_rarity(pity_five_star, pity_four_star, config)
        
        if rarity == 'five_star':
            character_type, five_star_guaranteed_status = determine_five_star_character(
                five_star_guaranteed_status, config
            )
            
            if character_type == 'desired':
                results['five_star_desired'] += 1
            else:
                results['five_star_undesired'] += 1
            
            current_starlight += 25  # Exemple: 25 starlight par 5*
            pity_five_star = 0
            pity_four_star = 0
        
        elif rarity == 'four_star':
            results['four_star'] += 1
            four_star_type = determine_four_star_type(config)
            
            if four_star_type == 'character':
                results['four_star_characters'] += 1
                current_starlight += config['rewards']['characters']['four_star_starlight']
            else:
                results['four_star_weapons'] += 1
                current_starlight += config['rewards']['weapons']['starlight']
            
            pity_four_star = 0
        
        else:  # three_star
            results['three_star'] += 1
            #Aucun starlight pour les 3*
        
        # Convertir les starlight en pulls si activé
        if use_starlight:
            bonus_pulls = current_starlight // 20
            if bonus_pulls > 0:
                num_pulls += bonus_pulls
                results['bonus_pulls_from_starlight'] += bonus_pulls
                current_starlight -= bonus_pulls * 20
    
    results['total_starlight'] = current_starlight
    results['guarantee_active'] = five_star_guaranteed_status
    return results


def format_results(results: dict, num_pulls: int, game : str) -> str:
    """
    Formate les résultats de la simulation en chaîne lisible.
    
    Args:
        results: Dictionnaire des résultats
        num_pulls: Nombre de pulls effectués
        
    Returns:
        Chaîne formatée avec les résultats
    """
    output = f"\n{'='*50}\n"
    output += f"RÉSULTATS SIMULATION {game.upper()} - {results['total_pulls']} PULLS\n"
    if results['bonus_pulls_from_starlight'] > 0:
        output += f"({num_pulls} pulls initiaux + {results['bonus_pulls_from_starlight']} pulls bonus via starlight)\n"
    output += f"{'='*50}\n\n"
    
    # Afficher les conditions initiales
    output += "CONDITIONS INITIALES :\n"
    output += f"  • Pity 5* initial : {results['initial_pity_five_star']}/90\n"
    output += f"  • Garantie 5* active : {'OUI' if results['initial_guarantee'] else 'NON'}\n\n"
    
    output += "PERSONNAGES 5* (LIMITÉS) :\n"
    output += f"  • Désiré : {results['five_star_desired']}\n"
    output += f"  • Non désiré : {results['five_star_undesired']}\n"
    output += f"  • Total : {results['five_star_desired'] + results['five_star_undesired']}\n\n"
    
    output += "PERSONNAGES 4* :\n"
    output += f"  • Total : {results['four_star_characters']}\n\n"
    
    output += "ARMES 4* :\n"
    output += f"  • Total : {results['four_star_weapons']}\n\n"
    
    output += "DIVERS :\n"
    output += f"  • Objets 3* : {results['three_star']}\n"
    output += f"  • Starlight restant : {results['total_starlight']}\n"
    output += f"  • Garantie 5* active : {'OUI' if results['guarantee_active'] else 'NON'}\n"
    
    output += f"\n{'='*50}\n"
    return output


def main():
    """Fonction principale pour tester le simulateur."""
    # Chemin vers le fichier de configuration
    config_path = Path(__file__).parent.parent.parent / 'data' / 'honkai_starrail.json'
    
    # Charger la configuration
    config = load_gacha_config(str(config_path))
    
    num_pulls = 300
    
    # Simuler 90 pulls AVEC 40 pulls en pity ET garantie active
    print("\n" + "="*50)
    print("SIMULATION 4 : 90 PULLS AVEC 40 PITY ET GARANTIE ACTIVE")
    print("="*50)
    results_4 = simulate_pulls(num_pulls, config, banner_type='character', use_starlight=True, 
                               initial_pity_five_star=40, five_star_guaranteed=True)
    print(format_results(results_4, num_pulls, config['title']))


if __name__ == "__main__":
    main()