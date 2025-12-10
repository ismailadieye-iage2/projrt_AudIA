import json

# =========================
# CONFIGURATION
# =========================

CONFIG_FILE = r"C:\Users\HP\Desktop\Hackathon\Config_AI_Classification.json"
MEASURE_FILE = r"C:\Users\HP\Desktop\Hackathon\dps_analysis_pi3_exemple.json"
OUTPUT_TXT = r"C:\Users\HP\Desktop\Hackathon\rapport_sonalyze_complet.txt"

# =========================
# CHARGEMENT JSON
# =========================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# ANALYSE SONORE
# =========================

def analyze_noise(measures):
    if not measures or not isinstance(measures, list):
        return None, None

    decibels = {
        "Lmin": [],
        "Lmax": [],
        "Lpeak": [],
        "L10": [],
        "L50": [],
        "L90": [],
        "LAeq": []
    }
    labels_all = []

    for item in measures:
        if "Lmin_dB" in item: decibels["Lmin"].append(item["Lmin_dB"])
        if "Lmax_dB" in item: decibels["Lmax"].append(item["Lmax_dB"])
        if "LPeak_dB" in item: decibels["Lpeak"].append(item["LPeak_dB"])
        if "L10_dB" in item: decibels["L10"].append(item["L10_dB"])
        if "L50_dB" in item: decibels["L50"].append(item["L50_dB"])
        if "L90_dB" in item: decibels["L90"].append(item["L90_dB"])
        if "LAeq_segment_dB" in item: decibels["LAeq"].append(item["LAeq_segment_dB"])
        if "top_5_labels" in item:
            labels_all.extend(item["top_5_labels"])

    if not decibels["LAeq"]:
        return None, None

    avg_db = sum(decibels["LAeq"]) / len(decibels["LAeq"])

    # Attribution note globale
    if avg_db < 30: score = "A"
    elif avg_db < 40: score = "B"
    elif avg_db < 50: score = "C"
    elif avg_db < 60: score = "D"
    elif avg_db < 70: score = "E"
    elif avg_db < 80: score = "F"
    else: score = "G"

    # Classification des bruits
    families = {
        "Circulation": ["vehicle", "car", "engine", "traffic"],
        "Électroménager": ["appliance", "washing machine", "fridge"],
        "Voisinage": ["music", "voice", "steps", "cacophony"],
        "Plomberie": ["pipe", "plumbing", "water"],
        "Autres": []
    }

    label_counts = {}
    for label in labels_all:
        label_lower = label.lower()
        assigned = False
        for family, keywords in families.items():
            if any(k.lower() in label_lower for k in keywords):
                label_counts[family] = label_counts.get(family, 0) + 1
                assigned = True
                break
        if not assigned:
            label_counts["Autres"] = label_counts.get("Autres", 0) + 1

    return {
        "score": score,
        "avg_db": round(avg_db,2),
        "decibels": decibels,
        "labels": label_counts
    }, labels_all

# =========================
# INFOS LOGEMENT
# =========================

def extract_home_info(config):
    return {
        "type": config.get("home_type", "inconnu"),
        "room": config.get("room", "non renseignée"),
        "floor": config.get("floor", "non renseigné")
    }

# =========================
# CONSEILLER VIRTUEL
# =========================

def virtual_advisor(analysis, home_info):
    if analysis is None:
        return ["⚠️ Aucune donnée de décibel trouvée."], []

    insights = []
    recommendations = []

    # Interprétation globale
    insights.append(f"Votre logement obtient la note {analysis['score']} basée sur un niveau sonore moyen de {analysis['avg_db']} dB.")
    
    # Comparaison selon pièce
    piece = home_info.get("room","").lower()
    seuil = 25 if "chambre" in piece else 45
    if analysis['avg_db'] <= seuil:
        insights.append(f"Le niveau sonore est confortable pour votre {piece} (seuil recommandé {seuil} dB).")
    else:
        insights.append(f"Le niveau sonore est élevé pour votre {piece} (seuil recommandé {seuil} dB).")

    # Détail des indicateurs
    decibels = analysis.get("decibels", {})
    for key, values in decibels.items():
        if values:
            insights.append(f"{key} moyen : {round(sum(values)/len(values),2)} dB, min : {min(values):.2f}, max : {max(values):.2f}")

    # Analyse familles de bruits
    labels = analysis.get("labels", {})
    for family, count in labels.items():
        if count > 0:
            insights.append(f"{count} occurrences de bruits liés à {family.lower()}.")

    # Hypothèses faiblesses
    if labels.get("Circulation",0) > 3:
        insights.append("Bruit de circulation important → vos fenêtres/portes pourraient être améliorées.")
    if labels.get("Voisinage",0) > 3:
        insights.append("Bruits de voisinage fréquents → isolation du plafond/plancher à considérer.")
    if labels.get("Plomberie",0) > 0:
        insights.append("Bruits de plomberie → vérifier tuyauterie ou cloisons légères.")

    # Recommandations détaillées
    recommendations.extend([
        "Solutions low-cost : joints, rideaux épais, tapis pour réduire le bruit",
        "Travaux : double vitrage, renforcer cloisons, consulter un acousticien si nécessaire",
        "Vous pouvez choisir le niveau d'intervention selon votre budget et vos priorités"
    ])

    # Conclusion
    insights.append("Résumé à retenir : Comprendre les bruits de votre logement permet d’agir concrètement pour améliorer votre confort sonore.")

    return insights, recommendations

# =========================
# GENERATION RAPPORT DETAILLE
# =========================

def generate_report(analysis, home_info):
    insights, recommendations = virtual_advisor(analysis, home_info)

    report = f"""
===== RAPPORT SONALYZE COMPLÈT =====

Type de logement : {home_info['type']}
Pièce analysée : {home_info['room']}
Étage : {home_info['floor']}

Note globale : {analysis['score'] if analysis else 'N/A'}
Niveau moyen : {analysis['avg_db'] if analysis else 'N/A'} dB

===== INTERPRÉTATION DÉTAILLÉE =====
"""
    for line in insights:
        report += "- " + line + "\n"

    report += "\n===== RECOMMANDATIONS =====\n"
    for rec in recommendations:
        report += "- " + rec + "\n"

    return report

# =========================
# SESSION INTERACTIVE
# =========================

def interactive_session(analysis, home_info):
    insights, recommendations = virtual_advisor(analysis, home_info)
    print("\nBienvenue dans le conseiller virtuel Sonalyze !")
    print("Posez vos questions ou tapez 'quit' pour terminer.\n")

    while True:
        question = input("Votre question : ").strip().lower()
        if question in ["quit","exit","q"]:
            print("Session terminée. Merci !")
            break
        elif "note" in question or "pourquoi" in question:
            for line in insights:
                if "note" in line.lower() or "niveau" in line.lower():
                    print("- " + line)
        elif "bruit" in question or "problématique" in question:
            for line in insights:
                if "bruit" in line.lower():
                    print("- " + line)
        elif "faire" in question or "recommandation" in question:
            for rec in recommendations:
                print("- " + rec)
        else:
            print("- Désolé, je n'ai pas compris. Posez une autre question ou tapez 'quit'.")

# =========================
# MAIN
# =========================

def main():
    print("Chargement des fichiers JSON...")
    try:
        config_data = load_json(CONFIG_FILE)
        measures_data = load_json(MEASURE_FILE)
    except Exception as e:
        print("Erreur lors du chargement des fichiers :", e)
        return

    print("Analyse des données sonores...")
    analysis, _ = analyze_noise(measures_data)
    home_info = extract_home_info(config_data)

    # Étape 1 : Rapport complet
    report_text = generate_report(analysis, home_info)
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"✅ Rapport TXT généré : {OUTPUT_TXT}\n")
    print(report_text)

    # Étape 2 : Conseiller virtuel interactif
    interactive_session(analysis, home_info)

if __name__ == "__main__":
    main()

